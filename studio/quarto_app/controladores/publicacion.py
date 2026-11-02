"""quarto_app/controladores/publicacion.py — la vista de publicación del sitio actual (reingeniería E8–E10).

Lo que se publica y a dónde: el proyecto, el dominio de destino, el estado de construcción (la regla de la puerta R6 de
`services/sitios.py`), los archivos que cambiarán, la última publicación, el historial y las comprobaciones de que el
destino corresponde al sitio (`services/publicacion.destino`). `motivoDestino()` es la guarda que el controlador de
operaciones consulta antes de publicar o empujar: si algo no coincide, no se ofrece. Solo lee git y el disco.
"""
from __future__ import annotations

from pathlib import Path

from gui_comun.modelos import ModeloTabla
from gui_comun.qt import QObject, Property, Signal, Slot

from quarto_app.services import publicacion as pub

COLUMNAS_ARCHIVOS = [("Archivo", "archivo"), ("Cambio", "estado"), ("Dónde", "donde")]
COLUMNAS_HISTORIAL = [("Commit", "commit"), ("Fecha", "fecha"), ("Mensaje", "mensaje"), ("Archivos", "archivos")]
NIVEL = {"M": "activo", "A": "positivo", "?": "positivo", "??": "positivo", "D": "negativo", "R": "neutro"}


class Publicacion(QObject):
    cambiado = Signal()

    def __init__(self, sitios, parent=None):
        super().__init__(parent)
        self.sitios = sitios
        self._destino: dict = {}
        self._pp: dict = {}
        self._ultima: dict = {}
        self._archivos = ModeloTabla(COLUMNAS_ARCHIVOS, parent=self)
        self._historial = ModeloTabla(COLUMNAS_HISTORIAL, parent=self)
        sitios.actualCambiado.connect(self.recargar)
        sitios.cambiado.connect(self.recargar)
        self.recargar()

    archivosModelo = Property(QObject, lambda self: self._archivos, constant=True)
    historialModelo = Property(QObject, lambda self: self._historial, constant=True)

    @Slot()
    def recargar(self) -> None:
        if not self.sitios.hayActual or not self.sitios.ruta:
            self._destino, self._pp, self._ultima = {}, {}, {}
            self._archivos.poner([])
            self._historial.poner([])
        else:
            sitio = Path(self.sitios.ruta)
            self._destino = pub.destino(sitio, self.sitios.dominio, self.sitios.repo)
            self._pp = pub.por_publicar(sitio)
            self._archivos.poner([dict(a, nivel=NIVEL.get(a["estado"], ""), habilitado=True) for a in self._pp["archivos"]])
            historial = pub.historial(sitio)
            self._historial.poner([dict(h, archivos=str(h["archivos"]), habilitado=True) for h in historial])
            self._ultima = historial[0] if historial else {}
        self.cambiado.emit()

    def motivoDestino(self) -> str:
        """"" si el destino corresponde al sitio actual; si no, por qué (la guarda de publicar y de commit y push)."""
        if not self._destino:
            return "no hay sitio elegido"
        return "" if self._destino.get("coincide") else self._destino.get("motivo", "")

    @Property(bool, notify=cambiado)
    def hayDestino(self) -> bool:
        return bool(self._destino)

    @Property(bool, notify=cambiado)
    def coincide(self) -> bool:
        return bool(self._destino.get("coincide"))

    @Property(str, notify=cambiado)
    def motivo(self) -> str:
        return self._destino.get("motivo", "")

    @Property(str, notify=cambiado)
    def dominio(self) -> str:
        return self._destino.get("dominio", "")

    @Property("QVariantList", notify=cambiado)
    def comprobaciones(self) -> list:
        return [dict(c, nivel="positivo" if c["ok"] is True else ("negativo" if c["ok"] is False else "neutro"))
                for c in self._destino.get("comprobaciones", [])]

    @Property(int, notify=cambiado)
    def totalArchivos(self) -> int:
        return int(self._pp.get("total", 0))

    @Property(str, notify=cambiado)
    def resumenArchivos(self) -> str:
        if not self._pp:
            return ""
        if not self._pp["total"]:
            return "Nada por publicar: lo confirmado ya está en el remoto"
        partes = []
        if self._pp["sin_confirmar"]:
            partes.append(f"{self._pp['sin_confirmar']} sin confirmar")
        if self._pp["por_empujar"]:
            partes.append(f"{self._pp['por_empujar']} en {self._pp['commits']} commit(s) sin empujar")
        return " · ".join(partes) + (f" (se listan {len(self._pp['archivos'])})" if len(self._pp["archivos"]) < self._pp["total"] else "")

    @Property("QVariantMap", notify=cambiado)
    def ultima(self) -> dict:
        return dict(self._ultima)

    @Property(str, notify=cambiado)
    def textoConfirmacion(self) -> str:
        """Lo que la confirmación de publicar dice además: el sitio, el dominio y cuántos archivos van."""
        if not self.sitios.hayActual:
            return ""
        return (f"Se publicará «{self.sitios.nombre}» en {self.dominio or 'un dominio sin declarar'}"
                f" con {self.totalArchivos} archivo(s) por publicar.")
