"""
metadata_page.py — Página Metadata: base Excel, sincronización y tags.

Flujo: generar plantilla → editar en Excel → ver diferencias → aplicar
(update). Todas las operaciones destructivas parten con dry-run activado.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QGroupBox, QGridLayout, QHBoxLayout,
    QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
    QWidget,
)

from app.controllers.metadata_controller import MetadataController
from app.models.blog import Blog
from app.settings import settings
from app.widgets.page_header import PageHeader


class MetadataPage(QWidget):
    def __init__(self, controlador: MetadataController, parent=None) -> None:
        super().__init__(parent)
        self._ctl = controlador

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(PageHeader(
            "Metadata",
            "Gestión masiva de metadatos YAML mediante la base Excel "
            "(fuente de la verdad para ediciones en lote).",
        ))

        # --- Base Excel y filtros ---------------------------------------------
        caja_base = QGroupBox("Base de datos y filtros")
        grid = QGridLayout(caja_base)

        self._excel = QLineEdit(str(settings().excel_file() or ""))
        boton_excel = QPushButton("…")
        boton_excel.setFixedWidth(32)
        boton_excel.clicked.connect(self._elegir_excel)
        boton_abrir = QPushButton("Abrir en Excel/Calc")
        boton_abrir.clicked.connect(self._abrir_excel)

        self._blog = QComboBox()
        self._blog.addItem("(todos los blogs)", "")
        self._filtro = QLineEdit()
        self._filtro.setPlaceholderText("filtro de ruta, ej. 2025-06")
        self._dry_run = QCheckBox("Dry-run (simular sin aplicar)")
        self._dry_run.setChecked(True)
        self._destino_excel = QCheckBox("Operar sobre el Excel (no sobre los .qmd)")

        grid.addWidget(QLabel("Archivo Excel:"), 0, 0)
        grid.addWidget(self._excel, 0, 1)
        grid.addWidget(boton_excel, 0, 2)
        grid.addWidget(boton_abrir, 0, 3)
        grid.addWidget(QLabel("Blog:"), 1, 0)
        grid.addWidget(self._blog, 1, 1)
        grid.addWidget(self._filtro, 1, 2, 1, 2)
        grid.addWidget(self._dry_run, 2, 1)
        grid.addWidget(self._destino_excel, 2, 2, 1, 2)
        layout.addWidget(caja_base)

        # --- Plantilla y sincronización ------------------------------------------
        caja_sync = QGroupBox("Plantilla y sincronización Excel ↔ archivos")
        fila_sync = QHBoxLayout(caja_sync)
        for texto, manejador in [
            ("📋 Generar plantilla", lambda: self._ctl.create_template(self._blog_sel(), False)),
            ("➕ Plantilla incremental", lambda: self._ctl.create_template(self._blog_sel(), True)),
            ("🔍 Ver diferencias", self._diferencias),
            ("⬇ Aplicar Excel → .qmd", self._update),
            ("🆕 Detectar campos nuevos", self._ctl.detect_new_fields),
            ("⚙ Crear configuración", self._ctl.create_config),
        ]:
            boton = QPushButton(texto)
            boton.clicked.connect(manejador)
            fila_sync.addWidget(boton)
        layout.addWidget(caja_sync)

        # --- Tags ----------------------------------------------------------------
        caja_tags = QGroupBox("Tags (taxonomía)")
        fila_tags = QHBoxLayout(caja_tags)
        for texto, manejador in [
            ("🧼 Normalizar", self._normalizar_tags),
            ("🔁 Reemplazar…", self._reemplazar_tags),
            ("➖ Eliminar…", self._eliminar_tags),
            ("➕ Agregar…", self._agregar_tags),
            ("📈 Estadísticas", self._stats_tags),
            ("🕵 Auditoría", self._audit_tags),
        ]:
            boton = QPushButton(texto)
            boton.clicked.connect(manejador)
            fila_tags.addWidget(boton)
        layout.addWidget(caja_tags)

        # --- Sincronización desde la ruta ------------------------------------------
        caja_ruta = QGroupBox("Sincronización derivada de la ruta")
        fila_ruta = QHBoxLayout(caja_ruta)
        boton_fechas = QPushButton("📅 Sincronizar fechas (carpeta → date)")
        boton_fechas.clicked.connect(
            lambda: self._ctl.sync_dates(*self._destino(), self._blog_sel(), self._es_dry()))
        boton_pdf = QPushButton("🔗 Sincronizar citation.pdf-url")
        boton_pdf.clicked.connect(
            lambda: self._ctl.sync_pdf_urls(*self._destino(), self._blog_sel(), self._es_dry()))
        fila_ruta.addWidget(boton_fechas)
        fila_ruta.addWidget(boton_pdf)
        fila_ruta.addStretch(1)
        layout.addWidget(caja_ruta)
        layout.addStretch(1)

    # ------------------------------------------------------------------ helpers
    def actualizar_blogs(self, blogs: list[Blog]) -> None:
        actual = self._blog.currentData()
        self._blog.clear()
        self._blog.addItem("(todos los blogs)", "")
        for blog in blogs:
            self._blog.addItem(blog.nombre, blog.nombre)
        idx = self._blog.findData(actual)
        if idx >= 0:
            self._blog.setCurrentIndex(idx)

    def _blog_sel(self) -> str:
        return self._blog.currentData() or ""

    def _es_dry(self) -> bool:
        return self._dry_run.isChecked()

    def _destino(self) -> tuple[bool, str]:
        return self._destino_excel.isChecked(), self._excel_path()

    def _excel_path(self) -> str:
        ruta = self._excel.text().strip()
        if not ruta or not Path(ruta).is_file():
            QMessageBox.warning(self, "Metadata", "Selecciona un archivo Excel válido.")
            raise ValueError("Excel inválido")
        settings().set("metadata/excel_file", ruta)
        return ruta

    def _elegir_excel(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar base Excel", self._excel.text(),
            "Hojas de cálculo (*.xlsx *.xlsm)")
        if ruta:
            self._excel.setText(ruta)
            settings().set("metadata/excel_file", ruta)

    def _abrir_excel(self) -> None:
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._excel_path()))
        except ValueError:
            pass

    # ------------------------------------------------------------------- acciones
    def _diferencias(self) -> None:
        try:
            self._ctl.find_differences(self._excel_path(), self._blog_sel(), self._filtro.text().strip())
        except ValueError:
            pass

    def _update(self) -> None:
        try:
            excel = self._excel_path()
        except ValueError:
            return
        if not self._es_dry() and QMessageBox.question(
                self, "Aplicar cambios",
                "Se aplicarán los cambios del Excel a los archivos .qmd.\n¿Continuar?") \
                != QMessageBox.Yes:
            return
        self._ctl.update(excel, self._blog_sel(), self._filtro.text().strip(), self._es_dry())

    def _normalizar_tags(self) -> None:
        try:
            self._ctl.normalize_tags(*self._destino(), self._blog_sel(), self._es_dry())
        except ValueError:
            pass

    def _pedir_lista(self, titulo: str, texto: str) -> list[str]:
        entrada, ok = QInputDialog.getText(self, titulo, texto)
        return [t.strip() for t in entrada.split()] if ok and entrada.strip() else []

    def _reemplazar_tags(self) -> None:
        pares = self._pedir_lista(
            "Reemplazar tags", "Reemplazos «viejo:nuevo» separados por espacio:")
        if pares:
            try:
                self._ctl.replace_tags(*self._destino(), pares, self._blog_sel(), self._es_dry())
            except ValueError:
                pass

    def _eliminar_tags(self) -> None:
        tags = self._pedir_lista("Eliminar tags", "Tags a eliminar (separados por espacio):")
        if tags:
            try:
                self._ctl.remove_tags(*self._destino(), tags, self._blog_sel(), self._es_dry())
            except ValueError:
                pass

    def _agregar_tags(self) -> None:
        tags = self._pedir_lista("Agregar tags", "Tags a agregar (separados por espacio):")
        if tags:
            try:
                self._ctl.add_tags(*self._destino(), tags, self._blog_sel(), self._es_dry())
            except ValueError:
                pass

    def _stats_tags(self) -> None:
        try:
            self._ctl.tag_stats(*self._destino(), self._blog_sel(), 30)
        except ValueError:
            pass

    def _audit_tags(self) -> None:
        try:
            self._ctl.audit_tags(*self._destino(), self._blog_sel(), 0.8)
        except ValueError:
            pass
