"""
settings.py — Configuración persistente de Quarto Studio (QSettings).

Único punto de acceso a las preferencias del usuario. Ningún otro módulo
debe instanciar QSettings directamente: todo pasa por AppSettings.
"""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QSettings

from app import APP_NAME, ORG_NAME
from app.services import paths


class AppSettings:
    """Envoltorio tipado sobre QSettings con valores por defecto sensatos."""

    # claves y defaults centralizados
    _DEFAULTS = {
        "general/docs_dir": "",              # vacío → autodetección
        "general/editor": "",                # vacío → aplicación por defecto del sistema
        "general/tema": "oscuro",            # "claro" | "oscuro"
        "general/iconos": "estandar",
        "rutas/quarto": "quarto",
        "rutas/python": "python3",
        "rutas/backup_dir": "",              # vacío → default del blog manager
        "ejecucion/max_procesos": 1,
        "blogs/preview_port": 4200,
        "blogs/publish_target": "gh-pages",
        "metadata/excel_file": "",
        "dashboard/operaciones_recientes": "[]",   # JSON
        "dashboard/favoritos": "[]",               # JSON
    }

    def __init__(self) -> None:
        self._qs = QSettings(ORG_NAME, APP_NAME)

    # ------------------------------------------------------------------ base
    def get(self, clave: str) -> str:
        return str(self._qs.value(clave, self._DEFAULTS.get(clave, "")))

    def get_int(self, clave: str) -> int:
        try:
            return int(self._qs.value(clave, self._DEFAULTS.get(clave, 0)))
        except (TypeError, ValueError):
            return int(self._DEFAULTS.get(clave, 0))

    def set(self, clave: str, valor) -> None:
        self._qs.setValue(clave, valor)

    # ------------------------------------------------------- rutas derivadas
    def docs_dir(self) -> Path:
        """Directorio ~/Documents (raíz de los blogs). Configurado o autodetectado."""
        configurado = self.get("general/docs_dir")
        if configurado and Path(configurado).is_dir():
            return Path(configurado)
        return paths.detectar_docs_dir()

    def excel_file(self) -> Path | None:
        valor = self.get("metadata/excel_file")
        if valor and Path(valor).is_file():
            return Path(valor)
        default = paths.metadata_manager().parent / "excel_databases" / "quarto_metadata.xlsx"
        return default if default.is_file() else None

    # ------------------------------------------------- historial de operaciones
    def operaciones_recientes(self) -> list[dict]:
        try:
            return json.loads(self.get("dashboard/operaciones_recientes"))
        except json.JSONDecodeError:
            return []

    def registrar_operacion(self, registro: dict, maximo: int = 30) -> None:
        historial = self.operaciones_recientes()
        historial.insert(0, registro)
        self.set("dashboard/operaciones_recientes", json.dumps(historial[:maximo], ensure_ascii=False))

    def favoritos(self) -> list[str]:
        try:
            return json.loads(self.get("dashboard/favoritos"))
        except json.JSONDecodeError:
            return []

    def set_favoritos(self, ids: list[str]) -> None:
        self.set("dashboard/favoritos", json.dumps(ids, ensure_ascii=False))


# Instancia compartida (se crea perezosamente en application.py)
_instancia: AppSettings | None = None


def settings() -> AppSettings:
    global _instancia
    if _instancia is None:
        _instancia = AppSettings()
    return _instancia
