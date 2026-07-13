"""
scan_worker.py — Escaneo de proyectos en segundo plano (QThread).

Recorrer ~12 blogs con cientos de posts toca miles de archivos: se hace
fuera del hilo de la UI y se entrega el resultado por señal.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from app.models.blog import Blog
from app.services.project_scanner import descubrir_blogs


class ScanWorker(QThread):
    """Escanea Documents y emite la lista de blogs encontrados."""

    resultado = Signal(list)   # list[Blog]
    fallo = Signal(str)

    def __init__(self, docs_dir: Path, parent=None) -> None:
        super().__init__(parent)
        self._docs_dir = docs_dir

    def run(self) -> None:
        try:
            blogs: list[Blog] = descubrir_blogs(self._docs_dir)
            self.resultado.emit(blogs)
        except Exception as e:  # noqa: BLE001 — se reporta a la UI
            self.fallo.emit(str(e))
