"""quarto_app/controladores/metadatos.py — el diagnóstico de metadatos del sitio actual (reingeniería E7): el Excel frente
a los `.qmd` de todas sus entradas (`services/datos.diagnostico`) y la comparación campo a campo de la elegida. Nada se
sobrescribe: llevar el Excel a los documentos sigue siendo una operación del gestor de metadatos, que simula primero."""
from __future__ import annotations

from pathlib import Path

from gui_comun.modelos import ModeloTabla
from gui_comun.qt import QObject, Property, Signal, Slot

from quarto_app.services import datos

COLUMNAS = [("Fecha", "fecha"), ("Entrada", "titulo"), ("Frente al Excel", "texto"), ("Ruta", "ruta_relativa")]
COLUMNAS_CAMPOS = [("Campo", "campo"), ("En el documento", "archivo"), ("En el Excel", "excel")]
TEXTO = {"igual": "igual que el Excel", "difiere": "difiere del Excel", "sin fila": "sin fila en el Excel"}
NIVEL = {"igual": "positivo", "difiere": "neutro", "sin fila": "inactivo"}


class Metadatos(QObject):
    cambiado = Signal()
    actualCambiado = Signal()

    def __init__(self, sitios, flujo, parent=None):
        super().__init__(parent)
        self.sitios, self.flujo = sitios, flujo
        self._diag: dict = {}
        self._filas = ModeloTabla(COLUMNAS, parent=self)
        self._campos = ModeloTabla(COLUMNAS_CAMPOS, parent=self)
        self._actual = -1
        sitios.actualCambiado.connect(self.recargar)
        self.recargar()

    modelo = Property(QObject, lambda self: self._filas, constant=True)
    camposModelo = Property(QObject, lambda self: self._campos, constant=True)

    @Slot()
    def recargar(self) -> None:
        blog = self.sitios._blogs.get(self.sitios.nombre) if self.sitios.hayActual else None
        if blog is None:
            self._diag = {}
            self._filas.poner([])
        else:
            excel = datos.leer_excel(self.flujo._ruta_excel())
            self._diag = datos.diagnostico(blog, excel)
            self._filas.poner([{k: f[k] for k in ("ruta", "ruta_relativa", "titulo", "fecha", "estado", "diferencias")}
                               | {"nivel": NIVEL[f["estado"]], "texto": TEXTO[f["estado"]] + (f" ({f['diferencias']})" if f["diferencias"] else ""),
                                  "habilitado": True, "icono": {"titulo": "text-markdown"}}
                               for f in self._diag["filas"]])
        self.fijarFila(-1)
        self.cambiado.emit()

    @Property(str, notify=cambiado)
    def resumen(self) -> str:
        return self._diag.get("resumen", "")

    @Property("QVariantMap", notify=cambiado)
    def cuentas(self) -> dict:
        return dict(self._diag.get("cuentas", {}), solo_excel=len(self._diag.get("solo_excel", [])))

    @Property("QVariantList", notify=cambiado)
    def soloExcel(self) -> list:
        return list(self._diag.get("solo_excel", []))

    @Slot(int)
    def fijarFila(self, fila: int) -> None:
        self._actual = fila if 0 <= fila < len(self._diag.get("filas", [])) else -1
        campos = self._diag["filas"][self._actual]["campos"] if self._actual >= 0 else []
        self._campos.poner([dict(c, nivel="neutro" if c["difiere"] else "", habilitado=True) for c in campos])
        self.actualCambiado.emit()

    @Property(bool, notify=actualCambiado)
    def hayActual(self) -> bool:
        return self._actual >= 0

    @Property(str, notify=actualCambiado)
    def tituloActual(self) -> str:
        return self._diag["filas"][self._actual]["titulo"] if self._actual >= 0 else ""

    @Property(str, notify=actualCambiado)
    def rutaActual(self) -> str:
        return self._diag["filas"][self._actual]["ruta"] if self._actual >= 0 else ""
