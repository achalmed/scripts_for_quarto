"""
main_controller.py — Controlador raíz de la aplicación.

Posee el ProcessRunner compartido (una operación a la vez), el escáner de
proyectos (QThread) y el historial de operaciones. Los controladores de
cada funcionalidad ejecutan sus Command a través de este controlador, de
modo que consola, logs, barra de progreso y dashboard escuchan un único
origen de señales.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.models.blog import Blog
from app.models.operation import Operacion
from app.services.command import Command
from app.settings import settings
from app.workers.process_runner import ProcessRunner
from app.workers.scan_worker import ScanWorker


class MainController(QObject):
    blogs_actualizados = Signal(list)      # list[Blog]
    operacion_rechazada = Signal(str)      # ya hay una operación en curso
    operacion_registrada = Signal(object)  # Operacion

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.runner = ProcessRunner(self)
        self.runner.terminado.connect(self._registrar_operacion)
        self._blogs: list[Blog] = []
        self._scanner: ScanWorker | None = None

    # ------------------------------------------------------------- ejecución
    def ejecutar(self, cmd: Command) -> bool:
        """Lanza un comando backend; False (+señal) si el runner está ocupado."""
        if not self.runner.ejecutar(cmd):
            self.operacion_rechazada.emit(
                "Ya hay una operación en curso. Detenla o espera a que termine."
            )
            return False
        return True

    def detener(self) -> None:
        self.runner.detener()

    # --------------------------------------------------------------- escaneo
    def escanear_proyectos(self) -> None:
        """Escanea Documents en un QThread y emite blogs_actualizados."""
        if self._scanner and self._scanner.isRunning():
            return
        self._scanner = ScanWorker(settings().docs_dir(), self)
        self._scanner.resultado.connect(self._al_escanear)
        self._scanner.start()

    def blogs(self) -> list[Blog]:
        return self._blogs

    def _al_escanear(self, blogs: list) -> None:
        self._blogs = blogs
        self.blogs_actualizados.emit(blogs)

    # -------------------------------------------------------------- historial
    def _registrar_operacion(self, op: Operacion) -> None:
        settings().registrar_operacion(op.como_dict())
        self.operacion_registrada.emit(op)
