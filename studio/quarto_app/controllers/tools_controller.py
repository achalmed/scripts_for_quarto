"""
tools_controller.py — Controlador de las herramientas simples:
YAML formatter, índice de symlinks y generador de contenido similar.

Son tres backends pequeños con pocas acciones cada uno; un controlador
por cabeza sería puro boilerplate.
"""

from __future__ import annotations

from PySide6.QtCore import QObject

from app.controllers.main_controller import MainController
from app.services import index_service, similar_service, yaml_service


class ToolsController(QObject):
    def __init__(self, principal: MainController, parent=None) -> None:
        super().__init__(parent)
        self._principal = principal

    # --- YAML formatter -----------------------------------------------------
    def formatear_directorio(self, directorio: str, recursivo: bool, dry_run: bool) -> None:
        self._principal.ejecutar(
            yaml_service.formatear_directorio(directorio, recursivo, dry_run))

    def formatear_archivo(self, archivo: str, dry_run: bool) -> None:
        self._principal.ejecutar(yaml_service.formatear_archivo(archivo, dry_run))

    # --- Índice de symlinks ---------------------------------------------------
    def sincronizar_indice(self, dry_run: bool) -> None:
        self._principal.ejecutar(index_service.sincronizar(dry_run))

    def detectar_rotos(self) -> None:
        self._principal.ejecutar(index_service.detectar_rotos())

    def limpiar_rotos(self) -> None:
        self._principal.ejecutar(index_service.limpiar_rotos())

    def resumen_indice(self) -> None:
        self._principal.ejecutar(index_service.resumen())

    # --- Generador de contenido similar ---------------------------------------
    def generar_similares(self, blog_dir: str, base_url: str, tipo: str, dry_run: bool) -> None:
        self._principal.ejecutar(similar_service.generar(blog_dir, base_url, tipo, dry_run))
