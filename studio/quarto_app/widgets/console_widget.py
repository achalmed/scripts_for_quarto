"""
console_widget.py — Consola integrada.

Muestra sin ocultar nada: comando ejecutado, stdout, stderr (en rojo),
código de salida y tiempo. Incluye botones para detener el proceso y
limpiar la consola.
"""

from __future__ import annotations

from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from app.models.operation import Operacion
from app.services.command import Command


class ConsoleWidget(QWidget):
    """Vista de la salida de los procesos backend."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("consola")

        self._texto = QPlainTextEdit(readOnly=True)
        self._texto.setObjectName("consolaTexto")
        self._texto.setMaximumBlockCount(20000)
        fuente = QFont("Monospace")
        fuente.setStyleHint(QFont.TypeWriter)
        self._texto.setFont(fuente)

        self._estado = QLabel("Listo")
        self._estado.setObjectName("consolaEstado")

        self.boton_detener = QPushButton("■ Detener")
        self.boton_detener.setEnabled(False)
        boton_limpiar = QPushButton("Limpiar")
        boton_limpiar.clicked.connect(self._texto.clear)

        barra = QHBoxLayout()
        barra.setContentsMargins(6, 4, 6, 2)
        barra.addWidget(self._estado, stretch=1)
        barra.addWidget(self.boton_detener)
        barra.addWidget(boton_limpiar)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(barra)
        layout.addWidget(self._texto)

    # ------------------------------------------------- slots del ProcessRunner
    def al_iniciar(self, cmd: Command) -> None:
        self._agregar_html(
            f'<br><span style="color:#4f9cf5">▶ {cmd.descripcion}</span><br>'
            f'<span style="color:#8a919e">$ {cmd.linea()}</span>'
        )
        self._estado.setText(f"Ejecutando: {cmd.descripcion}")
        self.boton_detener.setEnabled(True)

    def al_recibir_linea(self, texto: str, es_stderr: bool) -> None:
        if es_stderr:
            self._agregar_html(f'<span style="color:#e06c75">{_esc(texto)}</span>')
        else:
            self._agregar_texto(texto)

    def al_terminar(self, op: Operacion) -> None:
        color = "#98c379" if op.exitosa else "#e06c75"
        icono = "✔" if op.exitosa else "✘"
        self._agregar_html(
            f'<span style="color:{color}">{icono} terminado '
            f'(código {op.codigo_salida}, {op.duracion_seg:.1f} s)</span>'
        )
        self._estado.setText("Listo")
        self.boton_detener.setEnabled(False)

    # ---------------------------------------------------------------- interno
    def _agregar_texto(self, texto: str) -> None:
        self._texto.appendPlainText(texto)
        self._desplazar()

    def _agregar_html(self, html: str) -> None:
        self._texto.appendHtml(html)
        self._desplazar()

    def _desplazar(self) -> None:
        self._texto.moveCursor(QTextCursor.End)


def _esc(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
