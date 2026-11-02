"""quarto_app/controladores/flujo.py — las tablas de las vistas del flujo (Entradas y metadatos; Índice del vault; Índices
de contenido), leídas tal cual (`servicios.datos`), y el elemento actual: la entrada con su frontmatter frente a su fila
del Excel (pestaña Metadatos), el enlace del índice, el fragmento en texto. Elegir una entrada fija el sitio actual (sin
cambiar de vista). Solo lee."""
from __future__ import annotations

from pathlib import Path

from gui_comun.modelos import ModeloFiltrado, ModeloTabla
from gui_comun.qt import QObject, Property, Signal, Slot

from quarto_app.models import filas as mod
from quarto_app.services import datos, paths

VISTAS_DATOS = ("entradas", "indice", "contenido")
MAX_TEXTO = 200_000


class Flujo(QObject):
    cambiado = Signal()
    elementoCambiado = Signal()
    aviso = Signal(str, str)

    def __init__(self, espacio, sitios, ajustes, consola, hub: Path | None = None, parent=None):
        super().__init__(parent)
        self.espacio, self.sitios, self.ajustes, self.consola = espacio, sitios, ajustes, consola
        self._hub = Path(hub) if hub else None
        self._tablas = {v: ModeloTabla(mod.COLUMNAS[v], parent=self) for v in VISTAS_DATOS}
        self._modelos = {v: ModeloFiltrado(self._tablas[v], parent=self) for v in VISTAS_DATOS}
        self._excel: dict[str, dict] = {}
        self._hay_excel = False
        self._elemento: dict = {}
        self._vista_elemento = ""
        self._texto = ""
        self._comparacion: list = []
        sitios.cambiado.connect(lambda: self.recargar("entradas"))
        self.recargarTodo()

    @Slot(str, result=QObject)
    def modeloDe(self, vista: str):
        return self._modelos.get(vista)

    def _ruta_excel(self) -> Path:
        return Path(self.ajustes.excel or paths.excel_por_defecto())

    @Slot()
    def recargarTodo(self) -> None:
        for v in VISTAS_DATOS:
            self.recargar(v)

    @Slot(str)
    def recargar(self, vista: str) -> None:
        if vista == "entradas":
            self._excel = datos.leer_excel(self._ruta_excel())
            self._hay_excel = bool(self._excel)
            filas = [mod.fila_entrada(f) for f in datos.entradas(self.sitios.blogs(), set(self._excel) if self._hay_excel else None)]
        elif vista == "indice":
            filas = [mod.fila_enlace(f) for f in datos.enlaces_indice(paths.indice_dir(self._hub), self.sitios._docs)]
        elif vista == "contenido":
            filas = [mod.fila_fragmento(f) for f in datos.fragmentos(self.sitios.blogs())]
        else:
            return
        self._tablas[vista].poner(filas)
        self.cambiado.emit()
        if self._vista_elemento == vista:
            self._fijar(vista, -1)

    @Property(bool, notify=cambiado)
    def hayExcel(self) -> bool:
        return self._hay_excel

    @Property(str, notify=cambiado)
    def avisoExcel(self) -> str:
        if self._hay_excel:
            return ""
        if not datos.hay_openpyxl():
            return "Sin openpyxl no se lee el Excel: crea el entorno del studio (Ajustes dice cómo)."
        return f"No se encontró el Excel de metadatos ({self._ruta_excel().name}): «Plantilla del Excel» lo genera."

    @Property("QVariantMap", notify=cambiado)
    def contadores(self) -> dict:
        c = {v: self._tablas[v].filas for v in VISTAS_DATOS}
        c["indice_rotos"] = sum(1 for f in self._tablas["indice"].todas() if f.get("estado") == "roto")
        c["sin_excel"] = sum(1 for f in self._tablas["entradas"].todas() if f.get("excel") == "no")
        return c

    @Property("QVariantList", notify=cambiado)
    def filasNavegacion(self) -> list:
        c = self.contadores
        return [{"nombre": "entradas", "texto": "Entradas y metadatos", "icono": "text-markdown", "contador": c["entradas"]},
                {"nombre": "indice", "texto": "Índice del vault", "icono": "emblem-symbolic-link", "contador": c["indice_rotos"] or ""},
                {"nombre": "contenido", "texto": "Índices de contenido", "icono": "view-list-text", "contador": c["contenido"]}]

    # --------------------------------------------------------------- el elemento
    @Slot(str, int)
    def fijarFila(self, vista: str, fila: int) -> None:
        self._fijar(vista, fila)

    def _fijar(self, vista: str, fila: int) -> None:
        self._vista_elemento = vista
        modelo = self._modelos.get(vista)
        if modelo is None or fila < 0 or fila >= modelo.rowCount():
            self._elemento, self._texto, self._comparacion = {}, "", []
        else:
            self._elemento = dict(self._tablas[vista].fila(modelo.filaOrigen(fila)))
            self._texto = self._leer_texto(self._elemento.get("ruta", "")) if vista == "contenido" else ""
            self._comparacion = []
            if vista == "entradas":
                self._comparacion = datos.comparar(self._elemento.get("frontmatter") or {}, self._excel.get(self._elemento.get("ruta_relativa", ""), {}))
                self.sitios.fijarPorNombre(self._elemento.get("sitio", ""))
                self.sitios.fijarEntradaRuta(self._elemento.get("ruta", ""))
            elif vista == "contenido":
                self.sitios.fijarPorNombre(self._elemento.get("sitio", ""))
        self.elementoCambiado.emit()

    def _leer_texto(self, ruta: str) -> str:
        p = Path(ruta) if ruta else None
        if not p or not p.is_file():
            return ""
        try:
            if p.stat().st_size > MAX_TEXTO:
                return "(archivo grande: ábrelo con Intro)"
            return p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    @Property(bool, notify=elementoCambiado)
    def hayElemento(self) -> bool:
        return bool(self._elemento)

    @Property(str, notify=elementoCambiado)
    def vistaElemento(self) -> str:
        return self._vista_elemento

    @Property(str, notify=elementoCambiado)
    def elementoTitulo(self) -> str:
        e = self._elemento
        return str(e.get("titulo") or e.get("enlace") or e.get("fragmento") or "") if e else ""

    @Property(str, notify=elementoCambiado)
    def elementoSubtitulo(self) -> str:
        e = self._elemento
        if not e:
            return ""
        if self._vista_elemento == "entradas":
            return f"{e.get('sitio', '')} · {e.get('seccion', '')}/{e.get('carpeta', '')}"
        if self._vista_elemento == "indice":
            return f"{e.get('anio', '')} → {e.get('destino', '')}"
        return f"{e.get('sitio', '')} · {e.get('subblog', '')}"

    @Property(str, notify=elementoCambiado)
    def elementoRuta(self) -> str:
        return str(self._elemento.get("ruta", "")) if self._elemento else ""

    @Property("QVariantList", notify=elementoCambiado)
    def elementoCampos(self) -> list:
        return mod.campos_elemento(self._elemento, mod.COLUMNAS.get(self._vista_elemento, [])) if self._elemento else []

    @Property(str, notify=elementoCambiado)
    def elementoTexto(self) -> str:
        return self._texto

    @Property("QVariantList", notify=elementoCambiado)
    def frontmatterCampos(self) -> list:
        fm = (self._elemento or {}).get("frontmatter") or {}
        return [{"campo": k, "valor": ", ".join(str(x) for x in v) if isinstance(v, list) else str(v)} for k, v in fm.items()]

    @Property("QVariantList", notify=elementoCambiado)
    def comparacion(self) -> list:
        return list(self._comparacion)

    @Property(bool, notify=elementoCambiado)
    def enExcel(self) -> bool:
        return bool(self._elemento) and self._elemento.get("excel") == "sí"

    @Property(int, notify=elementoCambiado)
    def nDiferencias(self) -> int:
        return sum(1 for c in self._comparacion if c["difiere"])

    @Slot()
    def abrirElemento(self) -> None:
        ruta = self.elementoRuta
        if ruta:
            self.espacio.abrir(ruta)

    @Slot()
    def abrirCarpetaElemento(self) -> None:
        if self.elementoRuta:
            self.espacio.abrirDolphin(self.elementoRuta)

    @Slot()
    def abrirExcel(self) -> None:
        ruta = self._ruta_excel()
        if ruta.is_file():
            self.espacio.abrir(str(ruta))
        else:
            self.aviso.emit(f"No existe el Excel {ruta}: «Plantilla del Excel» lo genera.", "aviso")
