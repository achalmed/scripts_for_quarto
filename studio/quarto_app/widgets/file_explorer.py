"""
file_explorer.py — Explorador de proyectos integrado (QDockWidget lateral).

Árbol de archivos sobre Documents: navegar carpetas, abrir archivos con el
editor configurado (o el del sistema) y localizar recursos.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PySide6.QtCore import QDir, QModelIndex, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileSystemModel, QTreeView, QVBoxLayout, QWidget

from app.settings import settings


class FileExplorer(QWidget):
    """QTreeView + QFileSystemModel con doble clic para abrir archivos."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("explorador")

        self._modelo = QFileSystemModel(self)
        self._modelo.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self._arbol = QTreeView()
        self._arbol.setModel(self._modelo)
        self._arbol.setHeaderHidden(True)
        for col in range(1, 4):   # solo la columna de nombre
            self._arbol.hideColumn(col)
        self._arbol.doubleClicked.connect(self._abrir)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._arbol)

        self.establecer_raiz(settings().docs_dir())

    def establecer_raiz(self, ruta: Path) -> None:
        indice = self._modelo.setRootPath(str(ruta))
        self._arbol.setRootIndex(indice)

    def _abrir(self, indice: QModelIndex) -> None:
        ruta = Path(self._modelo.filePath(indice))
        if ruta.is_dir():
            return  # las carpetas se expanden con el propio árbol
        editor = settings().get("general/editor")
        if editor:
            subprocess.Popen([editor, str(ruta)])   # noqa: S603 — editor elegido por el usuario
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(ruta)))
