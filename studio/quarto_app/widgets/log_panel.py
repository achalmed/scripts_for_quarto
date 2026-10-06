"""
log_panel.py — Panel de historial de operaciones (tabla).

Cada Command ejecutado se registra con hora, descripción, comando, código
de salida y duración. También ofrece acceso a los logs en disco del
script_pub_index_symlink.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.models.operation import Operacion
from app.services import paths

_COLUMNAS = ["Hora", "Operación", "Comando", "Código", "Duración"]


class LogPanel(QWidget):
    """Tabla de operaciones de la sesión (y las persistidas del historial)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._tabla = QTableWidget(0, len(_COLUMNAS))
        self._tabla.setHorizontalHeaderLabels(_COLUMNAS)
        self._tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)

        boton_logs = QPushButton("Abrir logs de symlinks…")
        boton_logs.clicked.connect(self._abrir_logs_disco)
        barra = QHBoxLayout()
        barra.setContentsMargins(6, 4, 6, 2)
        barra.addStretch(1)
        barra.addWidget(boton_logs)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(barra)
        layout.addWidget(self._tabla)

    def registrar(self, op: Operacion) -> None:
        fila = 0
        self._tabla.insertRow(fila)
        valores = [
            op.timestamp,
            op.descripcion,
            op.linea_comando,
            str(op.codigo_salida),
            f"{op.duracion_seg:.1f} s",
        ]
        for col, valor in enumerate(valores):
            item = QTableWidgetItem(valor)
            if col == 3:
                item.setForeground(Qt.darkGreen if op.exitosa else Qt.red)
            self._tabla.setItem(fila, col, item)

    def _abrir_logs_disco(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(paths.pub_index_logs_dir())))
