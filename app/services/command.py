"""
command.py — Representación pura de un comando de backend.

Los servicios construyen objetos Command (datos, sin Qt); los workers los
ejecutan. Así la UI nunca conoce rutas de scripts ni argumentos.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field


@dataclass
class Command:
    """Comando listo para ejecutar por ProcessRunner."""

    programa: str                       # ejecutable (bash, python3, ...)
    args: list[str] = field(default_factory=list)
    cwd: str | None = None
    stdin_data: str | None = None       # respuestas para prompts (confirmaciones)
    descripcion: str = ""               # texto humano para consola/historial
    entorno: dict[str, str] = field(default_factory=dict)

    def linea(self) -> str:
        """Representación shell-quoted del comando (para mostrar en consola)."""
        return " ".join(shlex.quote(p) for p in [self.programa, *self.args])
