"""
sidebar.py — Panel lateral de navegación (estilo VS Code / Qt Creator).
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from app.application import icono_app

# (id, etiqueta, icono)
SECCIONES = [
    ("dashboard", "Dashboard", "dashboard"),
    ("blogs", "Blogs", "blogs"),
    ("metadata", "Metadata", "metadata"),
    ("yaml", "YAML", "yaml"),
    ("indices", "Índices", "indices"),
    ("similares", "Contenido", "similares"),
]


class Sidebar(QListWidget):
    """Lista vertical de secciones; emite el id de la página seleccionada."""

    seccion_cambiada = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setIconSize(QSize(20, 20))
        self.setFixedWidth(170)
        self.setSpacing(2)

        for id_, etiqueta, icono in SECCIONES:
            item = QListWidgetItem(icono_app(icono), etiqueta)
            item.setData(256, id_)  # Qt.UserRole
            item.setSizeHint(QSize(0, 36))
            self.addItem(item)

        self.currentItemChanged.connect(
            lambda actual, _ant: actual and self.seccion_cambiada.emit(actual.data(256))
        )
        self.setCurrentRow(0)

    def seleccionar(self, id_seccion: str) -> None:
        for i in range(self.count()):
            if self.item(i).data(256) == id_seccion:
                self.setCurrentRow(i)
                return
