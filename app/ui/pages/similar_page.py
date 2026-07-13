"""
similar_page.py — Página Contenido: generador de índices _contenido_*.qmd.

Flujo recomendado: ejecutar primero en modo simulación (dry-run), revisar
la salida en la consola y después aplicar.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QGroupBox, QGridLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QVBoxLayout, QWidget,
)

from app.controllers.tools_controller import ToolsController
from app.models.blog import Blog
from app.widgets.page_header import PageHeader


class SimilarPage(QWidget):
    def __init__(self, controlador: ToolsController, parent=None) -> None:
        super().__init__(parent)
        self._ctl = controlador

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(PageHeader(
            "Índices de contenido",
            "Genera los archivos _contenido_<subblog>.qmd con enlaces a artículo "
            "y PDF para cada sección de un blog.",
        ))

        caja = QGroupBox("Generación")
        grid = QGridLayout(caja)
        self._blog = QComboBox()
        self._base_url = QLineEdit()
        self._base_url.setPlaceholderText("(autodetectada si se deja vacío)")
        self._tipo = QComboBox()
        self._tipo.addItems(["auto", "website", "blog"])

        boton_simular = QPushButton("🔍 Simular (dry-run)")
        boton_simular.clicked.connect(lambda: self._generar(dry_run=True))
        boton_aplicar = QPushButton("✅ Generar índices")
        boton_aplicar.clicked.connect(lambda: self._generar(dry_run=False))

        grid.addWidget(QLabel("Blog:"), 0, 0)
        grid.addWidget(self._blog, 0, 1)
        grid.addWidget(QLabel("URL base:"), 1, 0)
        grid.addWidget(self._base_url, 1, 1)
        grid.addWidget(QLabel("Estructura:"), 2, 0)
        grid.addWidget(self._tipo, 2, 1)
        grid.addWidget(boton_simular, 3, 0)
        grid.addWidget(boton_aplicar, 3, 1)
        layout.addWidget(caja)
        layout.addStretch(1)

    def actualizar_blogs(self, blogs: list[Blog]) -> None:
        actual = self._blog.currentData()
        self._blog.clear()
        for blog in blogs:
            self._blog.addItem(blog.nombre, str(blog.ruta))
        idx = self._blog.findData(actual)
        if idx >= 0:
            self._blog.setCurrentIndex(idx)

    def _generar(self, dry_run: bool) -> None:
        blog_dir = self._blog.currentData()
        if not blog_dir:
            QMessageBox.information(self, "Contenido", "No hay blogs detectados todavía.")
            return
        if not dry_run and QMessageBox.question(
                self, "Generar índices",
                "Se sobrescribirán los _contenido_*.qmd del blog seleccionado.\n"
                "¿Ya revisaste la simulación?") != QMessageBox.Yes:
            return
        self._ctl.generar_similares(
            blog_dir, self._base_url.text().strip(), self._tipo.currentText(), dry_run)
