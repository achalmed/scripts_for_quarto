"""
preferences_dialog.py — Ventana de preferencias (persistidas con QSettings).
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout,
)

from app.application import aplicar_tema
from app.settings import settings


class _SelectorRuta(QHBoxLayout):
    """LineEdit + botón «…» para elegir un directorio o archivo."""

    def __init__(self, valor: str, directorio: bool = True) -> None:
        super().__init__()
        self.editor = QLineEdit(valor)
        boton = QPushButton("…")
        boton.setFixedWidth(32)
        boton.clicked.connect(self._elegir)
        self._directorio = directorio
        self.addWidget(self.editor)
        self.addWidget(boton)

    def _elegir(self) -> None:
        if self._directorio:
            ruta = QFileDialog.getExistingDirectory(None, "Seleccionar directorio", self.editor.text())
        else:
            ruta, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo", self.editor.text())
        if ruta:
            self.editor.setText(ruta)


class PreferencesDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferencias — Quarto Studio")
        self.setMinimumWidth(560)
        st = settings()

        # --- General ---------------------------------------------------------
        caja_general = QGroupBox("General")
        form_general = QFormLayout(caja_general)
        self._docs = _SelectorRuta(st.get("general/docs_dir"))
        self._editor = _SelectorRuta(st.get("general/editor"), directorio=False)
        self._tema = QComboBox()
        self._tema.addItems(["oscuro", "claro"])
        self._tema.setCurrentText(st.get("general/tema"))
        form_general.addRow("Directorio de trabajo (Documents):", self._docs)
        form_general.addRow("Editor favorito:", self._editor)
        form_general.addRow("Tema:", self._tema)

        # --- Rutas de ejecutables ------------------------------------------------
        caja_rutas = QGroupBox("Ejecutables")
        form_rutas = QFormLayout(caja_rutas)
        self._quarto = QLineEdit(st.get("rutas/quarto"))
        self._python = QLineEdit(st.get("rutas/python"))
        form_rutas.addRow("Quarto:", self._quarto)
        form_rutas.addRow("Python:", self._python)

        # --- Ejecución y blogs ----------------------------------------------------
        caja_ejec = QGroupBox("Ejecución")
        form_ejec = QFormLayout(caja_ejec)
        self._procesos = QSpinBox()
        self._procesos.setRange(1, 8)
        self._procesos.setValue(st.get_int("ejecucion/max_procesos"))
        self._puerto = QSpinBox()
        self._puerto.setRange(1024, 65535)
        self._puerto.setValue(st.get_int("blogs/preview_port"))
        self._publish = QLineEdit(st.get("blogs/publish_target"))
        self._backups = _SelectorRuta(st.get("rutas/backup_dir"))
        form_ejec.addRow("Número de procesos:", self._procesos)
        form_ejec.addRow("Puerto de preview:", self._puerto)
        form_ejec.addRow("Destino de publicación:", self._publish)
        form_ejec.addRow("Directorio de backups:", self._backups)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self._guardar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(caja_general)
        layout.addWidget(caja_rutas)
        layout.addWidget(caja_ejec)
        layout.addWidget(botones)

    def _guardar(self) -> None:
        st = settings()
        st.set("general/docs_dir", self._docs.editor.text().strip())
        st.set("general/editor", self._editor.editor.text().strip())
        st.set("rutas/quarto", self._quarto.text().strip() or "quarto")
        st.set("rutas/python", self._python.text().strip() or "python3")
        st.set("rutas/backup_dir", self._backups.editor.text().strip())
        st.set("ejecucion/max_procesos", self._procesos.value())
        st.set("blogs/preview_port", self._puerto.value())
        st.set("blogs/publish_target", self._publish.text().strip() or "gh-pages")
        aplicar_tema(self._tema.currentText())
        self.accept()
