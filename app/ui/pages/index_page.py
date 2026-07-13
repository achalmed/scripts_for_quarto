"""
index_page.py — Página Índices: mantenimiento de symlinks de "04 index".
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QVBoxLayout, QWidget,
)

from app.controllers.tools_controller import ToolsController
from app.widgets.page_header import PageHeader


class IndexPage(QWidget):
    def __init__(self, controlador: ToolsController, parent=None) -> None:
        super().__init__(parent)
        self._ctl = controlador

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(PageHeader(
            "Índice de publicaciones (04 index)",
            "Mantiene los symlinks de Obsidian organizados por año hacia todas "
            "las carpetas de publicación. No edites los symlinks a mano: regenera aquí.",
        ))

        self._dry = QCheckBox("Dry-run (simular)")
        self._dry.setChecked(True)
        layout.addWidget(self._dry)

        caja = QGroupBox("Operaciones")
        fila = QHBoxLayout(caja)
        for texto, manejador in [
            ("🔄 Sincronizar", lambda: self._ctl.sincronizar_indice(self._dry.isChecked())),
            ("🔎 Detectar rotos", self._ctl.detectar_rotos),
            ("🗑 Eliminar rotos", self._limpiar_rotos),
            ("📊 Resumen por año", self._ctl.resumen_indice),
        ]:
            boton = QPushButton(texto)
            boton.clicked.connect(manejador)
            fila.addWidget(boton)
        fila.addStretch(1)
        layout.addWidget(caja)

        layout.addWidget(QLabel(
            "Los logs diarios de esta herramienta están disponibles en el panel Logs."))
        layout.addStretch(1)

    def _limpiar_rotos(self) -> None:
        if QMessageBox.question(
                self, "Eliminar symlinks rotos",
                "Se eliminarán los symlinks rotos de '04 index' (con limpieza de "
                "carpetas de año vacías).\n¿Continuar?") == QMessageBox.Yes:
            self._ctl.limpiar_rotos()
