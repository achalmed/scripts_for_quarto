"""
new_blog_dialog.py — Diálogo «Crear nuevo blog», definido en Qt Designer
(resources/ui/new_blog_dialog.ui) y cargado en tiempo de ejecución.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QVBoxLayout

_UI_FILE = Path(__file__).resolve().parents[1] / "resources" / "ui" / "new_blog_dialog.ui"


class NewBlogDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Crear nuevo blog — Quarto Studio")

        self._ui = QUiLoader().load(str(_UI_FILE))
        # Reparentar el contenido del .ui dentro de este QDialog
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)
        self._ui.botones.accepted.connect(self._validar)
        self._ui.botones.rejected.connect(self.reject)

    def _validar(self) -> None:
        if self.nombre():
            self.accept()
        else:
            self._ui.editorNombre.setFocus()

    def nombre(self) -> str:
        return self._ui.editorNombre.text().strip()

    def titulo(self) -> str:
        return self._ui.editorTitulo.text().strip()
