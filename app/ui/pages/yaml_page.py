"""
yaml_page.py — Página YAML: formateador de frontmatter de archivos .qmd.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QGroupBox, QGridLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from app.controllers.tools_controller import ToolsController
from app.settings import settings
from app.widgets.page_header import PageHeader


class YamlPage(QWidget):
    def __init__(self, controlador: ToolsController, parent=None) -> None:
        super().__init__(parent)
        self._ctl = controlador

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(PageHeader(
            "Formateador YAML",
            "Repara el bloque YAML de los .qmd (separador --- y línea en blanco). "
            "Es idempotente: ejecutarlo varias veces produce el mismo resultado.",
        ))

        caja = QGroupBox("Formatear directorio")
        grid = QGridLayout(caja)
        self._dir = QLineEdit(str(settings().docs_dir()))
        boton_dir = QPushButton("…")
        boton_dir.setFixedWidth(32)
        boton_dir.clicked.connect(self._elegir_dir)
        self._recursivo = QCheckBox("Recursivo")
        self._recursivo.setChecked(True)
        self._dry = QCheckBox("Dry-run (simular)")
        self._dry.setChecked(True)
        boton_ejecutar = QPushButton("🧹 Formatear directorio")
        boton_ejecutar.clicked.connect(self._formatear_dir)

        grid.addWidget(QLabel("Directorio:"), 0, 0)
        grid.addWidget(self._dir, 0, 1)
        grid.addWidget(boton_dir, 0, 2)
        grid.addWidget(self._recursivo, 1, 1)
        grid.addWidget(self._dry, 2, 1)
        grid.addWidget(boton_ejecutar, 3, 1)
        layout.addWidget(caja)

        caja_archivo = QGroupBox("Formatear un archivo")
        grid2 = QGridLayout(caja_archivo)
        self._archivo = QLineEdit()
        boton_archivo = QPushButton("…")
        boton_archivo.setFixedWidth(32)
        boton_archivo.clicked.connect(self._elegir_archivo)
        boton_ejec_archivo = QPushButton("🧹 Formatear archivo")
        boton_ejec_archivo.clicked.connect(self._formatear_archivo)
        grid2.addWidget(QLabel("Archivo .qmd:"), 0, 0)
        grid2.addWidget(self._archivo, 0, 1)
        grid2.addWidget(boton_archivo, 0, 2)
        grid2.addWidget(boton_ejec_archivo, 1, 1)
        layout.addWidget(caja_archivo)
        layout.addStretch(1)

    def _elegir_dir(self) -> None:
        ruta = QFileDialog.getExistingDirectory(self, "Directorio con .qmd", self._dir.text())
        if ruta:
            self._dir.setText(ruta)

    def _elegir_archivo(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Archivo .qmd", str(settings().docs_dir()), "Quarto (*.qmd)")
        if ruta:
            self._archivo.setText(ruta)

    def _formatear_dir(self) -> None:
        directorio = self._dir.text().strip()
        if not directorio:
            return
        if not self._dry.isChecked() and QMessageBox.question(
                self, "Formatear YAML",
                "Se modificarán los archivos .qmd del directorio.\n¿Continuar?") \
                != QMessageBox.Yes:
            return
        self._ctl.formatear_directorio(directorio, self._recursivo.isChecked(), self._dry.isChecked())

    def _formatear_archivo(self) -> None:
        archivo = self._archivo.text().strip()
        if archivo:
            self._ctl.formatear_archivo(archivo, self._dry.isChecked())
