"""
yaml_service.py — Servicio del formateador YAML (script_format_yaml).
"""

from __future__ import annotations

from app.services import paths
from app.services.command import Command
from app.settings import settings


def formatear_directorio(directorio: str, recursivo: bool = True, dry_run: bool = False) -> Command:
    args = [str(paths.yaml_formatter()), "--directory", directorio]
    if recursivo:
        args.append("--recursive")
    if dry_run:
        args.append("--dry-run")
    desc = f"Formatear YAML en {directorio}" + (" (simulación)" if dry_run else "")
    return Command(programa=settings().get("rutas/python"), args=args, descripcion=desc)


def formatear_archivo(archivo: str, dry_run: bool = False) -> Command:
    args = [str(paths.yaml_formatter()), "--file", archivo]
    if dry_run:
        args.append("--dry-run")
    desc = f"Formatear YAML de {archivo}" + (" (simulación)" if dry_run else "")
    return Command(programa=settings().get("rutas/python"), args=args, descripcion=desc)
