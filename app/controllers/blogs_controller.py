"""
blogs_controller.py — Controlador de la sección Blogs.

Traduce acciones de la vista a Commands del blog_service, y gestiona la
creación de posts (post_service, en Python) y de blogs nuevos.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.controllers.main_controller import MainController
from app.services import blog_service, post_service


class BlogsController(QObject):
    post_creado = Signal(str)      # ruta del post nuevo
    error = Signal(str)

    def __init__(self, principal: MainController, parent=None) -> None:
        super().__init__(parent)
        self._principal = principal

    # ------------------------------------------------ operaciones sobre un blog
    def render(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.render(blog))

    def preview(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.preview(blog))

    def detener_preview(self) -> None:
        self._principal.detener()

    def clean(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.clean(blog))

    def publish(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.publish(blog))

    def check(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.check(blog))

    def listar_posts(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.listar_posts(blog))

    def git_status(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.git_status(blog))

    def git_commit(self, blog: str, mensaje: str) -> None:
        self._principal.ejecutar(blog_service.git_commit(blog, mensaje))

    # ------------------------------------------------------ operaciones por lotes
    def render_all(self) -> None:
        self._principal.ejecutar(blog_service.render_all())

    def clean_all(self) -> None:
        self._principal.ejecutar(blog_service.clean_all())

    def check_structure(self) -> None:
        self._principal.ejecutar(blog_service.check_structure())

    def backup_todos(self) -> None:
        self._principal.ejecutar(blog_service.backup_todos())

    # ------------------------------------------------------------ creación
    def init_blog(self, nombre: str, titulo: str) -> None:
        self._principal.ejecutar(blog_service.init_blog(nombre, titulo))

    def crear_post(self, blog_dir: Path, datos: post_service.DatosPost) -> None:
        """Creación local (Python); no pasa por el runner porque es instantánea."""
        try:
            ruta = post_service.crear_post(blog_dir, datos)
            self.post_creado.emit(str(ruta))
            self._principal.escanear_proyectos()
        except (FileExistsError, OSError) as e:
            self.error.emit(str(e))
