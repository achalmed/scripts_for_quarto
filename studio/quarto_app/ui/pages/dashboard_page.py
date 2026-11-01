"""
dashboard_page.py — Página inicial «Inicio»: cifras de la familia de blogs, mosaicos de las herramientas y las
últimas operaciones, con las piezas comunes de gui_comun.widgets.tarjetas.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QListWidgetItem, QVBoxLayout, QWidget

from gui_comun.widgets.tarjetas import (Cifra, ListaConVacio, Mosaico, Tarjeta, encabezado, pagina_desplazable,
                                        rejilla_pareja, seccion)
from quarto_app.application import icono_app
from quarto_app.models.blog import Blog
from quarto_app.models.operation import Operacion
from quarto_app.settings import settings

# (título, para qué sirve, icono, sección)
_HERRAMIENTAS = [
    ("Blogs", "Renderiza, publica y crea blogs y posts", "blogs", "blogs"),
    ("Metadata", "Edita en masa los metadatos desde el Excel", "metadata", "metadata"),
    ("YAML", "Normaliza el frontmatter de los posts", "yaml", "yaml"),
    ("Índices", "Enlaces simbólicos del índice de publicaciones", "indices", "indices"),
    ("Contenido", "Índices de contenido y publicaciones similares", "similares", "similares"),
]


class DashboardPage(QWidget):
    ir_a_seccion = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        contenido = QWidget()
        root = QVBoxLayout(contenido)
        root.setSpacing(14)
        root.addWidget(encabezado("Inicio", "La familia de blogs Quarto: render, publicación, metadatos e índices."))

        # --- Cifras -----------------------------------------------------------------
        cifras = rejilla_pareja(4)
        self._t_blogs = Cifra("Blogs", detalle="Sitios Quarto encontrados")
        self._t_posts = Cifra("Publicaciones", detalle="Posts en todos los blogs")
        self._t_git = Cifra("Con repositorio git", detalle="Blogs versionados")
        self._t_docs = Cifra("Directorio de trabajo", detalle="Raíz del escaneo")
        self._t_docs.lbl_valor.setStyleSheet("font-size: 14px; font-weight: 600;")
        self._t_docs.lbl_valor.setWordWrap(True)
        self._t_docs.poner(str(settings().docs_dir()))
        for i, c in enumerate((self._t_blogs, self._t_posts, self._t_git, self._t_docs)):
            cifras.addWidget(c, 0, i)
        root.addLayout(cifras)

        # --- Herramientas -------------------------------------------------------------
        root.addSpacing(4)
        root.addWidget(seccion("Herramientas"))
        rejilla = rejilla_pareja(3)
        for i, (titulo, descripcion, icono, sec) in enumerate(_HERRAMIENTAS):
            rejilla.addWidget(Mosaico(icono_app(icono), titulo, descripcion,
                                      lambda s=sec: self.ir_a_seccion.emit(s)), i // 3, i % 3)
        root.addLayout(rejilla)

        # --- Últimas operaciones ------------------------------------------------------
        root.addSpacing(4)
        self._lista = ListaConVacio("Todavía no hay operaciones.\nLo que hagan las herramientas aparecerá aquí.")
        self._recientes = self._lista.lista
        tarjeta = Tarjeta("Últimas operaciones")
        tarjeta.setMinimumHeight(220)
        tarjeta.cuerpo.addWidget(self._lista, 1)
        root.addWidget(tarjeta, 1)

        fuera = QVBoxLayout(self)
        fuera.setContentsMargins(0, 0, 0, 0)
        fuera.addWidget(pagina_desplazable(contenido))
        self._cargar_historial()

    # -------------------------------------------------------------------- slots
    def actualizar_blogs(self, blogs: list[Blog]) -> None:
        self._t_blogs.poner(str(len(blogs)))
        self._t_posts.poner(f"{sum(b.num_posts for b in blogs):,}".replace(",", " "))
        self._t_git.poner(str(sum(1 for b in blogs if b.tiene_git)))
        self._t_docs.poner(str(settings().docs_dir()))

    def registrar_operacion(self, op: Operacion) -> None:
        self._recientes.insertItem(0, self._fila(op.exitosa, op.timestamp, op.descripcion, op.duracion_seg))
        self._lista.actualizar()

    def _cargar_historial(self) -> None:
        for registro in settings().operaciones_recientes():
            self._recientes.addItem(self._fila(registro.get("codigo_salida") == 0, registro.get("timestamp", ""),
                                               registro.get("descripcion", ""), registro.get("duracion_seg", 0)))
        self._lista.actualizar()

    @staticmethod
    def _fila(exitosa: bool, cuando: str, descripcion: str, segundos: float) -> QListWidgetItem:
        item = QListWidgetItem(f"{'✓' if exitosa else '✕'}  {descripcion}\n      {cuando} · {segundos:.1f} s")
        item.setData(Qt.UserRole, exitosa)
        return item
