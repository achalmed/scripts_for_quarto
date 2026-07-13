"""
metadata_controller.py — Controlador de la sección Metadata (Excel ↔ YAML).
"""

from __future__ import annotations

from PySide6.QtCore import QObject

from app.controllers.main_controller import MainController
from app.services import metadata_service as svc


class MetadataController(QObject):
    def __init__(self, principal: MainController, parent=None) -> None:
        super().__init__(parent)
        self._principal = principal

    # Plantilla / configuración
    def create_config(self) -> None:
        self._principal.ejecutar(svc.create_config())

    def create_template(self, blog: str, incremental: bool) -> None:
        self._principal.ejecutar(svc.create_template(blog, incremental))

    # Sincronización Excel ↔ archivos
    def update(self, excel: str, blog: str, filtro: str, dry_run: bool) -> None:
        self._principal.ejecutar(svc.update(excel, blog, filtro, dry_run))

    def find_differences(self, excel: str, blog: str, filtro: str) -> None:
        self._principal.ejecutar(svc.find_differences(excel, blog, filtro))

    def detect_new_fields(self) -> None:
        self._principal.ejecutar(svc.detect_new_fields())

    # Tags
    def normalize_tags(self, usar_excel: bool, excel: str, blog: str, dry_run: bool) -> None:
        self._principal.ejecutar(svc.normalize_tags(usar_excel, excel, blog=blog, dry_run=dry_run))

    def replace_tags(self, usar_excel: bool, excel: str, reemplazos: list[str],
                     blog: str, dry_run: bool) -> None:
        self._principal.ejecutar(
            svc.replace_tags(usar_excel, excel, reemplazos, blog=blog, dry_run=dry_run))

    def remove_tags(self, usar_excel: bool, excel: str, tags: list[str],
                    blog: str, dry_run: bool) -> None:
        self._principal.ejecutar(
            svc.remove_tags(usar_excel, excel, tags, blog=blog, dry_run=dry_run))

    def add_tags(self, usar_excel: bool, excel: str, tags: list[str],
                 blog: str, dry_run: bool) -> None:
        self._principal.ejecutar(
            svc.add_tags(usar_excel, excel, tags, blog=blog, dry_run=dry_run))

    def tag_stats(self, usar_excel: bool, excel: str, blog: str, top: int) -> None:
        self._principal.ejecutar(svc.tag_stats(usar_excel, excel, top=top, blog=blog))

    def audit_tags(self, usar_excel: bool, excel: str, blog: str, umbral: float) -> None:
        self._principal.ejecutar(svc.audit_tags(usar_excel, excel, umbral=umbral, blog=blog))

    # Sincronización desde la ruta
    def sync_dates(self, usar_excel: bool, excel: str, blog: str, dry_run: bool) -> None:
        self._principal.ejecutar(svc.sync_dates(usar_excel, excel, blog=blog, dry_run=dry_run))

    def sync_pdf_urls(self, usar_excel: bool, excel: str, blog: str, dry_run: bool) -> None:
        self._principal.ejecutar(svc.sync_pdf_urls(usar_excel, excel, blog=blog, dry_run=dry_run))
