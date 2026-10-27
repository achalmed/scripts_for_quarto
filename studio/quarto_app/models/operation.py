"""
operation.py — Registro de una operación ejecutada (para historial y logs).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Operacion:
    """Resultado de la ejecución de un Command, para el panel de logs."""

    descripcion: str
    linea_comando: str
    codigo_salida: int
    duracion_seg: float
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def exitosa(self) -> bool:
        return self.codigo_salida == 0

    def como_dict(self) -> dict:
        return asdict(self)
