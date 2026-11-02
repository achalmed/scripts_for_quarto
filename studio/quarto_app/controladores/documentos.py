"""quarto_app/controladores/documentos.py — los documentos del sitio actual y su vista previa (reingeniería E3 y E5).

La lista de documentos del sitio (`services/documentos.listar`), filtrable; el documento actual (lo que está en el
editor); su página renderizada en `_site/` para la vista previa (QtWebEngine del sistema si está; si no, QML muestra el
Markdown) y las páginas del sitio para navegar. Tras un render, la vista previa se recarga (`version`). Solo lee.
"""
from __future__ import annotations

from pathlib import Path

from gui_comun.modelos import ModeloFiltrado, ModeloLista
from gui_comun.qt import QObject, QUrl, Property, Signal, Slot

from quarto_app.services import documentos as docs

ROLES = ("ruta", "rel", "nombre", "carpeta", "tipo", "titulo", "fecha", "entrada", "icono")
ICONOS = {"qmd": "text-markdown", "md": "text-markdown", "yml": "text-x-yaml", "yaml": "text-x-yaml", "bib": "text-x-bibtex",
          "scss": "text-css", "css": "text-css", "lua": "text-x-script", "ipynb": "application-x-ipynb+json", "json": "application-json"}


def hay_webengine() -> bool:
    """¿Está el módulo QML de QtWebEngine del sistema (qml6-module-qtwebengine)?"""
    try:                                    # gui_comun.qt no exporta QLibraryInfo: del binding del sistema
        try:
            from PySide6.QtCore import QLibraryInfo
        except ImportError:                 # pragma: no cover  (PyQt6)
            from PyQt6.QtCore import QLibraryInfo
        base = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.QmlImportsPath))
    except Exception:          # noqa: BLE001
        return False
    return (base / "QtWebEngine" / "qmldir").is_file()


class Documentos(QObject):
    cambiado = Signal()                 # la lista de documentos del sitio
    actualCambiado = Signal()           # el documento actual y su página
    paginaCambiada = Signal()           # la versión de la vista previa (tras un render)

    def __init__(self, sitios, parent=None):
        super().__init__(parent)
        self.sitios = sitios
        self._filas = ModeloLista(ROLES, parent=self)
        self._modelo = ModeloFiltrado(self._filas, parent=self)
        self._texto = ""
        self._modelo.aceptar_con(self._acepta)
        self._actual = ""
        self._version = 0
        self._paginas: list[dict] = []
        self._webengine = hay_webengine()
        sitios.actualCambiado.connect(self.recargar)
        self.recargar()

    modelo = Property(QObject, lambda self: self._modelo, constant=True)

    def _sitio(self) -> Path | None:
        return Path(self.sitios.ruta) if self.sitios.hayActual and self.sitios.ruta else None

    @Slot()
    def recargar(self) -> None:
        sitio = self._sitio()
        filas = docs.listar(sitio) if sitio else []
        self._filas.poner([dict(f, icono=ICONOS.get(f["tipo"], "text-plain")) for f in filas])
        self._paginas = docs.paginas(sitio) if sitio else []
        if self._actual and sitio and not self._actual.startswith(str(sitio)):
            self._actual = ""
        self.cambiado.emit()
        self.actualCambiado.emit()

    def _acepta(self, i: int) -> bool:
        if not self._texto:
            return True
        f = self._filas.fila(i)
        t = self._texto.lower()
        return t in f["rel"].lower() or t in f["titulo"].lower()

    @Slot(str)
    def filtrar(self, texto: str) -> None:
        self._texto = (texto or "").strip()
        self._modelo.aceptar_con(self._acepta)

    @Property(int, notify=cambiado)
    def total(self) -> int:
        return self._filas.filas

    @Slot(int, result=str)
    def rutaDe(self, fila_visible: int) -> str:
        if 0 <= fila_visible < self._modelo.rowCount():
            return self._filas.fila(self._modelo.filaOrigen(fila_visible))["ruta"]
        return ""

    # --------------------------------------------------------------- el documento actual
    @Slot(str)
    def fijarActual(self, ruta: str) -> None:
        if ruta != self._actual:
            self._actual = ruta or ""
            self.actualCambiado.emit()

    @Property(str, notify=actualCambiado)
    def actual(self) -> str:
        return self._actual

    @Property(str, notify=actualCambiado)
    def relActual(self) -> str:
        sitio = self._sitio()
        try:
            return str(Path(self._actual).relative_to(sitio)) if self._actual and sitio else ""
        except ValueError:
            return Path(self._actual).name

    # --------------------------------------------------------------------- la vista previa
    @Property(bool, constant=True)
    def hayWebEngine(self) -> bool:
        return self._webengine

    def _pagina(self) -> Path | None:
        sitio = self._sitio()
        if not sitio:
            return None
        if self._actual:
            p = docs.pagina_de(sitio, self._actual)
            if p:
                return p
        portada = docs.carpeta_salida(sitio) / "index.html"
        return portada if portada.is_file() else None

    @Property(str, notify=actualCambiado)
    def urlPagina(self) -> str:
        p = self._pagina()
        return QUrl.fromLocalFile(str(p)).toString() if p else ""

    @Property(bool, notify=actualCambiado)
    def paginaDelDocumento(self) -> bool:
        """¿La página es la del documento actual (y no la portada, a falta de la suya)?"""
        sitio = self._sitio()
        return bool(self._actual and sitio and docs.pagina_de(sitio, self._actual))

    @Property(str, notify=actualCambiado)
    def textoDocumento(self) -> str:
        """El documento tal cual (la vista previa sin QtWebEngine o sin render)."""
        if not self._actual or Path(self._actual).suffix.lower() not in (".qmd", ".md"):
            return ""
        try:
            return Path(self._actual).read_text(encoding="utf-8", errors="replace")[:200_000]
        except OSError:
            return ""

    @Property("QVariantList", notify=actualCambiado)
    def paginas(self) -> list:
        return [{"rel": p["rel"], "url": QUrl.fromLocalFile(p["ruta"]).toString()} for p in self._paginas]

    @Property(int, notify=paginaCambiada)
    def version(self) -> int:
        return self._version

    @Slot()
    def renderTerminado(self) -> None:
        """Tras un render: las páginas pueden haber cambiado; la vista previa se recarga."""
        sitio = self._sitio()
        self._paginas = docs.paginas(sitio) if sitio else []
        self._version += 1
        self.actualCambiado.emit()
        self.paginaCambiada.emit()

    @Slot(str, result=str)
    def documentoDePagina(self, url: str) -> str:
        """El documento fuente de una página del sitio (para abrirlo desde la vista previa); "" si no hay."""
        sitio = self._sitio()
        if not sitio or not url.startswith("file://"):
            return ""
        html = Path(QUrl(url).toLocalFile())
        try:
            rel = html.relative_to(docs.carpeta_salida(sitio))
        except ValueError:
            return ""
        for ext in (".qmd", ".md", ".ipynb"):
            fuente = sitio / rel.with_suffix(ext)
            if fuente.is_file():
                return str(fuente)
        return ""
