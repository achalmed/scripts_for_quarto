"""quarto_app/controladores/sitios.py — la vista Sitios: la tabla de los trece sitios con su estado (`servicios.sitios`,
la regla de la puerta R6) y los filtros por estado; el sitio actual con sus detalles (Resumen, sus entradas, los
problemas de su último render y el registro de su última corrida, guardados por sitio en la caché del studio); la
entrada actual (de la pestaña Entradas o de la vista Entradas); la entrada nueva (`post_service`, la única lógica
portada del asistente de terminal). Solo lee; render, publicar y lo demás son de `operaciones`."""
from __future__ import annotations

from pathlib import Path

from gui_comun.modelos import ModeloFiltrado, ModeloLista, ModeloTabla
from gui_comun.qt import QObject, QStandardPaths, Property, Signal, Slot

from quarto_app.models import filas as mod
from quarto_app.models.blog import Blog
from quarto_app.services import paths, post_service, project_scanner, render as svc_render
from quarto_app.services import sitios as svc

ROLES_PROBLEMAS = ("nivel", "mensaje", "archivo", "linea", "detalle")


def cache_del_studio() -> Path:
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation) or (Path.home() / ".cache" / "quarto-studio"))


class Sitios(QObject):
    cambiado = Signal()                 # la tabla, los estados y los contadores
    actualCambiado = Signal()           # el sitio actual
    entradaCambiada = Signal()          # la entrada actual
    seleccionar = Signal(int)           # QML: selecciona esa fila visible de la tabla
    aviso = Signal(str, str)

    def __init__(self, espacio, consola, env, cache: Path | None = None, docs_dir: Path | None = None, parent=None):
        super().__init__(parent)
        self.espacio, self.consola, self.env = espacio, consola, env
        self._docs = Path(docs_dir) if docs_dir else Path(env.DOCS_ROOT)
        self._cache = (cache or cache_del_studio()) / "sitios"
        self._tabla = ModeloTabla(mod.COLUMNAS["sitios"], parent=self)
        self._modelo = ModeloFiltrado(self._tabla, parent=self)
        self._entradas = ModeloTabla(mod.COLUMNAS_ENTRADAS_SITIO, parent=self)
        self._problemas = ModeloLista(ROLES_PROBLEMAS, parent=self)
        self._blogs: dict[str, Blog] = {}
        self._estados: dict[str, dict] = {}
        self._pubs: dict = {}
        self._orden: list[str] = []
        self._contadores: dict = {}
        self._actual = ""
        self._entrada = ""
        self._registro = ""
        self._modelo.aceptar_con(self._acepta)
        espacio.filtroCambiado.connect(lambda: self._modelo.aceptar_con(self._acepta))
        self.recargar()

    modelo = Property(QObject, lambda self: self._modelo, constant=True)
    entradasModelo = Property(QObject, lambda self: self._entradas, constant=True)
    problemasModelo = Property(QObject, lambda self: self._problemas, constant=True)

    # ------------------------------------------------------------------ la tabla
    def _registro_pubs(self) -> dict:
        try:
            return {p.nombre: p for p in paths.pubs_registro().pubs()}
        except Exception:          # noqa: BLE001  sin registro, sin tema ni dominio
            return {}

    @Slot()
    def recargar(self) -> None:
        """Relee los sitios del registro y el hub, sus entradas y su estado (F6, o al terminar una operación)."""
        self._pubs = self._registro_pubs()
        blogs = project_scanner.descubrir_blogs(self._docs)
        self._blogs = {b.nombre: b for b in blogs}
        self._estados = {b.nombre: svc.estado_sitio(b.ruta) for b in blogs}
        self._orden = [b.nombre for b in blogs]
        self._tabla.poner([mod.fila_sitio(b, self._estados[b.nombre], self._pubs.get(b.nombre)) for b in blogs])
        self._contadores = svc.contar(list(self._estados.values()))
        self.cambiado.emit()
        if self._actual:
            self._fijar_actual(self._actual if self._actual in self._blogs else "")

    @Slot(str)
    def refrescar(self, nombre: str) -> None:
        """Vuelve a leer un solo sitio (tras renderizarlo, publicarlo o limpiarlo)."""
        b = self._blogs.get(nombre)
        if b is None:
            self.recargar()
            return
        b.posts = project_scanner.listar_posts(b.ruta)
        self._estados[nombre] = svc.estado_sitio(b.ruta)
        for i, f in enumerate(self._tabla.todas()):
            if f.get("sitio") == nombre:
                self._tabla.actualizar(i, **mod.fila_sitio(b, self._estados[nombre], self._pubs.get(nombre)))
        self._contadores = svc.contar(list(self._estados.values()))
        self.cambiado.emit()
        if nombre == self._actual:
            self._fijar_actual(nombre)

    def blogs(self) -> list[Blog]:
        return [self._blogs[n] for n in self._orden]

    def estados(self) -> list[tuple[str, str, dict]]:
        return [(n, str(self._blogs[n].ruta), self._estados[n]) for n in self._orden]

    def _acepta(self, fila_origen: int) -> bool:
        f = self.espacio.filtro
        return f == "todos" or self._tabla.fila(fila_origen).get("clave") == f

    @Property("QVariantList", notify=cambiado)
    def proyectos(self) -> list:
        """El panel de proyectos (reingeniería E2): el hub primero y luego los pubs, con su estado R6 y su dominio."""
        salida = []
        for n in sorted(self._orden, key=lambda n: (not self._blogs[n].es_website, n)):
            e, pub = self._estados[n], self._pubs.get(n)
            salida.append({"nombre": n, "esHub": self._blogs[n].es_website, "estado": e["texto_estado"], "clave": e["estado"], "nivel": e["nivel"],
                           "motivo": e["motivo"], "entradas": self._blogs[n].num_posts,
                           "dominio": (getattr(pub, "url", "") or "").replace("https://", "").rstrip("/"),
                           "tema": getattr(pub, "tema", "") or ("el hub" if self._blogs[n].es_website else "")})
        return salida

    @Property(int, notify=cambiado)
    def total(self) -> int:
        return len(self._orden)

    @Property("QVariantMap", notify=cambiado)
    def contadores(self) -> dict:
        return dict(self._contadores)

    @Property(str, notify=cambiado)
    def resumen(self) -> str:
        return svc.resumen(self._contadores)

    @Property("QVariantList", notify=cambiado)
    def filasNavegacion(self) -> list:
        return [{"nombre": "sitios" if f == "todos" else f"sitios.{f}", "texto": t, "icono": mod.ICONO_SITIO if f == "todos" else "",
                 "contador": self._contadores.get(f, 0)} for f, t in mod.FILTROS]

    @Property("QVariantList", notify=cambiado)
    def filasFlujo(self) -> list:
        c = self._contadores
        return [{"nombre": "flujo.render", "texto": "Render", "icono": "run-build", "contador": c.get("sin_render", 0) or ""},
                {"nombre": "flujo.publicar", "texto": "Publicar", "icono": "cloud-upload", "contador": c.get("sin_publicar", 0) or ""}]

    @Property("QVariantList", notify=cambiado)
    def nombres(self) -> list:
        return list(self._orden)

    # -------------------------------------------------------------- el sitio actual
    @Slot(int)
    def fijarFila(self, fila: int) -> None:
        if fila < 0 or fila >= self._modelo.rowCount():
            self._fijar_actual("")
        else:
            self._fijar_actual(self._tabla.fila(self._modelo.filaOrigen(fila)).get("sitio", ""))

    @Slot(str)
    def fijarPorNombre(self, nombre: str) -> None:
        if nombre in self._blogs and nombre != self._actual:
            self._fijar_actual(nombre)

    def _fijar_actual(self, nombre: str) -> None:
        self._actual = nombre if nombre in self._blogs else ""
        b = self._blogs.get(self._actual)
        self._entradas.poner([mod.fila_entrada_sitio(p) for p in (b.posts if b else [])])
        self._problemas.poner(svc_render.problemas_de(self._leer(self._actual, "render")) if self._actual else [])
        self._registro = self._leer(self._actual, "registro") if self._actual else ""
        if self._entrada and not (b and any(str(p.ruta / "index.qmd") == self._entrada for p in b.posts)):
            self._entrada = ""                                     # la entrada era de otro sitio (los pubs cuelgan del hub)
            self.entradaCambiada.emit()
        self.actualCambiado.emit()

    @Slot(str, result=int)
    def filaDe(self, nombre: str) -> int:
        for i, f in enumerate(self._tabla.todas()):
            if f.get("sitio") == nombre:
                return self._modelo.filaVisible(i)
        return -1

    @Slot(str, result=bool)
    def irA(self, nombre: str) -> bool:
        """Selecciona el sitio en la vista Sitios (filtro Todos si el actual lo oculta): la paleta y la vista Entradas."""
        if nombre not in self._blogs:
            return False
        self.espacio.fijarVista("sitios")
        if self.filaDe(nombre) < 0:
            self.espacio.fijarFiltro("todos")
        fila = self.filaDe(nombre)
        self._fijar_actual(nombre)
        self.seleccionar.emit(fila)
        return True

    def _estado(self) -> dict:
        return self._estados.get(self._actual, {})

    @Property(bool, notify=actualCambiado)
    def hayActual(self) -> bool:
        return bool(self._actual)

    @Property(str, notify=actualCambiado)
    def nombre(self) -> str:
        return self._actual

    @Property(str, notify=actualCambiado)
    def ruta(self) -> str:
        return str(self._blogs[self._actual].ruta) if self._actual else ""

    @Property(str, notify=actualCambiado)
    def rutaCorta(self) -> str:
        """La carpeta del sitio relativa a la raíz del espacio de trabajo."""
        if not self._actual:
            return ""
        try:
            return str(self._blogs[self._actual].ruta.relative_to(self._docs))
        except ValueError:
            return str(self._blogs[self._actual].ruta)

    @Property(str, notify=actualCambiado)
    def dominio(self) -> str:
        p = self._pubs.get(self._actual)
        return (p.url if p else "") or ""

    @Property(str, notify=actualCambiado)
    def tema(self) -> str:
        p = self._pubs.get(self._actual)
        if p:
            return p.tema
        return "el hub" if self._actual and self._blogs[self._actual].es_website else ""

    @Property(str, notify=actualCambiado)
    def repo(self) -> str:
        p = self._pubs.get(self._actual)
        return f"achalmed/{p.repo}" if p else ""

    @Property(bool, notify=actualCambiado)
    def esHub(self) -> bool:
        return bool(self._actual) and self._blogs[self._actual].es_website

    @Property(str, notify=actualCambiado)
    def estadoTexto(self) -> str:
        return self._estado().get("texto_estado", "")

    @Property(str, notify=actualCambiado)
    def estadoClave(self) -> str:
        return self._estado().get("estado", "")

    @Property(str, notify=actualCambiado)
    def estadoNivel(self) -> str:
        return self._estado().get("nivel", "")

    @Property(str, notify=actualCambiado)
    def motivo(self) -> str:
        return self._estado().get("motivo", "")

    @Property(str, notify=actualCambiado)
    def rama(self) -> str:
        return self._estado().get("rama", "") or "—"

    @Property(int, notify=actualCambiado)
    def cambios(self) -> int:
        return int(self._estado().get("cambios", 0))

    @Property(str, notify=actualCambiado)
    def porEmpujar(self) -> str:
        e = self._estado()
        if e.get("sin_remoto"):
            return "la rama no sigue a ningún remoto"
        return str(e.get("por_empujar", 0))

    @Property(str, notify=actualCambiado)
    def fechaRender(self) -> str:
        return self._estado().get("fecha_render", "—")

    @Property(str, notify=actualCambiado)
    def fechaFuentes(self) -> str:
        return self._estado().get("fecha_fuentes", "—")

    @Property(bool, notify=actualCambiado)
    def hayQuartoYml(self) -> bool:
        return bool(self._estado().get("quarto_yml"))

    @Property(bool, notify=actualCambiado)
    def hayGit(self) -> bool:
        return bool(self._estado().get("git"))

    @Property(bool, notify=actualCambiado)
    def haySite(self) -> bool:
        return bool(self._estado().get("site"))

    @Property(int, notify=actualCambiado)
    def nEntradas(self) -> int:
        return self._blogs[self._actual].num_posts if self._actual else 0

    @Property(int, notify=actualCambiado)
    def nProblemas(self) -> int:
        return self._problemas.filas

    @Property(str, notify=actualCambiado)
    def resumenProblemas(self) -> str:
        return svc_render.resumen_problemas(self._problemas.todas()) if self._actual else ""

    @Property(str, notify=actualCambiado)
    def registro(self) -> str:
        return self._registro

    # ------------------------------------------------------------- la entrada actual
    @Slot(int)
    def fijarEntradaFila(self, fila: int) -> None:
        self.fijarEntradaRuta(self._entradas.fila(fila)["ruta"] if 0 <= fila < self._entradas.filas else "")

    @Slot(str)
    def fijarEntradaRuta(self, ruta: str) -> None:
        if ruta != self._entrada:
            self._entrada = ruta
            self.entradaCambiada.emit()

    @Property(bool, notify=entradaCambiada)
    def hayEntrada(self) -> bool:
        return bool(self._entrada) and Path(self._entrada).is_file()

    @Property(str, notify=entradaCambiada)
    def entrada(self) -> str:
        return self._entrada

    @Property(str, notify=entradaCambiada)
    def entradaNombre(self) -> str:
        return Path(self._entrada).parent.name if self._entrada else ""

    @Slot()
    def abrirEntrada(self) -> None:
        if self.hayEntrada:
            self.espacio.abrir(self._entrada)

    @Slot(int)
    def abrirEntradaFila(self, fila: int) -> None:
        self.fijarEntradaFila(fila)
        self.abrirEntrada()

    @Slot(int)
    def abrirProblema(self, fila: int) -> None:
        """Intro en Problemas: el archivo del problema (dentro del sitio) con la aplicación del sistema."""
        if not (0 <= fila < self._problemas.filas) or not self._actual:
            return
        archivo = self._problemas.fila(fila).get("archivo", "")
        if archivo:
            ruta = Path(archivo) if Path(archivo).is_absolute() else self._blogs[self._actual].ruta / archivo
            self.espacio.abrir(str(ruta))

    # ------------------------------------------------------------------ acciones
    @Slot()
    def abrirNavegador(self) -> None:
        if self.dominio:
            self.espacio.abrirEnlace(self.dominio)
        elif self._actual:
            self.aviso.emit("Este sitio no tiene dominio en el registro _pubs/pubs.yml.", "aviso")

    @Slot()
    def abrirCarpeta(self) -> None:
        if self._actual:
            self.espacio.abrirDolphin(self.ruta)

    @Slot()
    def abrirTerminal(self) -> None:
        if self._actual:
            self.espacio.abrirTerminal(self.ruta)

    @Slot()
    def copiarRuta(self) -> None:
        self.espacio.copiar(self._entrada or self.ruta)

    @Slot(result="QVariantList")
    def carpetasDeEntradas(self) -> list:
        """Las carpetas del sitio actual que contienen entradas (para el diálogo de la entrada nueva)."""
        if not self._actual:
            return ["posts"]
        b = self._blogs[self._actual]
        carpetas = sorted({p.ruta.parent.relative_to(b.ruta).as_posix() for p in b.posts})
        return carpetas or ["posts"]

    @Slot("QVariantMap", result=str)
    def crearEntrada(self, datos: dict) -> str:
        """La entrada nueva (`post_service`, el mismo index.qmd que el asistente de terminal); devuelve la ruta o el error."""
        if not self._actual:
            return "Elige primero un sitio."
        d = post_service.DatosPost()
        for clave, valor in dict(datos).items():
            if hasattr(d, clave):
                actual = getattr(d, clave)
                if isinstance(actual, list):
                    valor = [x.strip() for x in str(valor).split(",") if x.strip()]
                elif isinstance(actual, bool):
                    valor = bool(valor)
                else:
                    valor = str(valor).strip()
                setattr(d, clave, valor)
        if not d.titulo:
            return "El título es obligatorio."
        try:
            ruta = post_service.crear_post(self._blogs[self._actual].ruta, d)
        except (FileExistsError, OSError) as e:
            return str(e)
        self.consola.registrar("ok", f"Entrada creada: {ruta}")
        self.refrescar(self._actual)
        self.fijarEntradaRuta(str(ruta / "index.qmd"))
        return ""

    # ------------------------------------------------------- la caché por sitio
    def _archivo(self, nombre: str, clase: str) -> Path:
        return self._cache / f"{nombre}.{clase}.txt"

    def _leer(self, nombre: str, clase: str) -> str:
        try:
            return self._archivo(nombre, clase).read_text(encoding="utf-8")
        except OSError:
            return ""

    def guardarCorrida(self, nombre: str, texto: str, es_render: bool) -> None:
        """La salida íntegra de la última corrida sobre un sitio; si fue un render, también sus problemas."""
        try:
            self._cache.mkdir(parents=True, exist_ok=True)
            self._archivo(nombre, "registro").write_text(texto, encoding="utf-8")
            if es_render:
                self._archivo(nombre, "render").write_text(texto, encoding="utf-8")
        except OSError as e:
            self.consola.registrar("warn", f"No se pudo guardar el registro de {nombre}: {e}")
        if nombre == self._actual:
            self._fijar_actual(nombre)

    def entradas_paleta(self, _texto: str) -> list[dict]:
        return [{"nombre": f"sitio.{n}", "texto": f"Sitio: {n}", "grupo": "Sitios", "icono": mod.ICONO_SITIO, "ejecutar": lambda n=n: self.irA(n)}
                for n in self._orden]
