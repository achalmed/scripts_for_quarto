"""
page_header.py — Cabecera estándar de cada página (título + descripción).
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PageHeader(QWidget):
    def __init__(self, titulo: str, descripcion: str = "", parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("tituloPagina")
        layout.addWidget(etiqueta)
        if descripcion:
            sub = QLabel(descripcion)
            sub.setObjectName("descripcionPagina")
            sub.setWordWrap(True)
            layout.addWidget(sub)
