"""
ansi.py — Limpieza de códigos ANSI de la salida de los scripts.

Los scripts Bash emiten colores/escapes de terminal; la consola Qt los
elimina (o podría mapearlos a HTML en el futuro).
"""

import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07|\r")


def limpiar(texto: str) -> str:
    """Elimina secuencias de escape ANSI y retornos de carro."""
    return _ANSI_RE.sub("", texto)
