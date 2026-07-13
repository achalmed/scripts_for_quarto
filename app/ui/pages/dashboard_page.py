"""
dashboard_page.py — Página inicial: estado del proyecto, estadísticas,
últimas operaciones y accesos rápidos.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QPushButton,
    QVBoxLayout, QWidget,
)

from app.models.blog import Blog
from app.models.operation import Operacion
from app.settings import settings
from app.widgets.page_header import PageHeader


class _Tarjeta(QFrame):
    """Tarjeta de estadística (número grande + etiqueta)."""

    def __init__(self, etiqueta: str) -> None:
        super().__init__()
        self.setObjectName("tarjeta")
        layout = QVBoxLayout(self)
        self.valor = QLabel("—")
        self.valor.setObjectName("tarjetaValor")
        texto = QLabel(etiqueta)
        texto.setObjectName("tarjetaEtiqueta")
        layout.addWidget(self.valor)
        layout.addWidget(texto)


class DashboardPage(QWidget):
    ir_a_seccion = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(PageHeader(
            "Dashboard",
            "Estado general de la familia de blogs Quarto.",
        ))

        # --- Tarjetas de estadísticas -----------------------------------------
        self._t_blogs = _Tarjeta("Blogs")
        self._t_posts = _Tarjeta("Publicaciones")
        self._t_git = _Tarjeta("Con repositorio git")
        self._t_docs = _Tarjeta("Directorio de trabajo")
        self._t_docs.valor.setText(str(settings().docs_dir()))
        self._t_docs.valor.setStyleSheet("font-size: 13px;")

        tarjetas = QGridLayout()
        tarjetas.addWidget(self._t_blogs, 0, 0)
        tarjetas.addWidget(self._t_posts, 0, 1)
        tarjetas.addWidget(self._t_git, 0, 2)
        tarjetas.addWidget(self._t_docs, 0, 3)
        layout.addLayout(tarjetas)

        # --- Accesos rápidos ----------------------------------------------------
        accesos = QHBoxLayout()
        for texto, seccion in [
            ("📚 Gestionar blogs", "blogs"),
            ("📊 Metadata (Excel)", "metadata"),
            ("🧹 Formatear YAML", "yaml"),
            ("🔗 Índice de symlinks", "indices"),
            ("📑 Índices de contenido", "similares"),
        ]:
            boton = QPushButton(texto)
            boton.clicked.connect(lambda _=False, s=seccion: self.ir_a_seccion.emit(s))
            accesos.addWidget(boton)
        accesos.addStretch(1)
        layout.addLayout(accesos)

        # --- Últimas operaciones -------------------------------------------------
        layout.addWidget(QLabel("Últimas operaciones:"))
        self._recientes = QListWidget()
        layout.addWidget(self._recientes, stretch=1)
        self._cargar_historial()

    # -------------------------------------------------------------------- slots
    def actualizar_blogs(self, blogs: list[Blog]) -> None:
        self._t_blogs.valor.setText(str(len(blogs)))
        self._t_posts.valor.setText(str(sum(b.num_posts for b in blogs)))
        self._t_git.valor.setText(str(sum(1 for b in blogs if b.tiene_git)))
        self._t_docs.valor.setText(str(settings().docs_dir()))

    def registrar_operacion(self, op: Operacion) -> None:
        icono = "✔" if op.exitosa else "✘"
        self._recientes.insertItem(0, f"{icono}  {op.timestamp}  ·  {op.descripcion}  ({op.duracion_seg:.1f} s)")

    def _cargar_historial(self) -> None:
        for registro in settings().operaciones_recientes():
            icono = "✔" if registro.get("codigo_salida") == 0 else "✘"
            self._recientes.addItem(
                f"{icono}  {registro.get('timestamp', '')}  ·  "
                f"{registro.get('descripcion', '')}  ({registro.get('duracion_seg', 0):.1f} s)"
            )
