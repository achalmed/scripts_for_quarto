"""
blogs_controller.py — Controlador de la sección Blogs.

Traduce acciones de la vista a Commands del blog_service, y gestiona la
creación de posts (post_service, en Python) y de blogs nuevos.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.controllers.main_controller import MainController
from app.models.operation import Operacion
from app.services import blog_service, post_service
from app.services.command import Command


class BlogsController(QObject):
    post_creado = Signal(str)      # ruta del post nuevo
    error = Signal(str)
    # Una simulación terminó bien: (pregunta, Command que aplica). La vista pregunta
    # y, si el usuario confirma, llama a aplicar(cmd).
    aplicacion_propuesta = Signal(str, object)

    def __init__(self, principal: MainController, parent=None) -> None:
        super().__init__(parent)
        self._principal = principal
        self._pendiente: tuple[str, Command, str] | None = None   # (línea simulada, aplicación, pregunta)
        principal.runner.terminado.connect(self._al_terminar)

    # ------------------------------------------- simular primero, aplicar al confirmar
    def _simular(self, simulacion: Command, aplicacion: Command, pregunta: str) -> None:
        if self._principal.ejecutar(simulacion):
            self._pendiente = (simulacion.linea(), aplicacion, pregunta)

    def _al_terminar(self, op: Operacion) -> None:
        if not self._pendiente or op.linea_comando != self._pendiente[0]:
            return
        _, aplicacion, pregunta = self._pendiente
        self._pendiente = None
        if op.exitosa:
            self.aplicacion_propuesta.emit(pregunta, aplicacion)

    def aplicar(self, cmd: Command) -> None:
        self._principal.ejecutar(cmd)

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
        self._simular(blog_service.publish(blog), blog_service.publish(blog, aplicar=True),
                      f"La simulación de la publicación de {blog} está en la consola "
                      "(puerta R6 y lo que se empujaría). ¿Publicar de verdad?")

    def check(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.check(blog))

    def listar_posts(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.listar_posts(blog))

    def git_status(self, blog: str) -> None:
        self._principal.ejecutar(blog_service.git_status(blog))

    def git_commit(self, blog: str, mensaje: str) -> None:
        self._simular(blog_service.git_commit(blog, mensaje),
                      blog_service.git_commit(blog, mensaje, aplicar=True),
                      f"La simulación del commit en {blog} está en la consola (qué se añade y qué "
                      "queda fuera). ¿Confirmar y empujar de verdad?")

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
