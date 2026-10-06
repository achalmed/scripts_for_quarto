"""
similar_service.py — Servicio del generador de índices de contenido
(script_generador_publicacion_similar). Genera _contenido_<subblog>.qmd.
"""

from __future__ import annotations

from app.services import paths
from app.services.command import Command


def generar(blog_dir: str, base_url: str = "", tipo: str = "auto", dry_run: bool = False) -> Command:
    args = [str(paths.generador_similar()), blog_dir]
    if base_url:
        args += ["--base-url", base_url]
    if tipo and tipo != "auto":
        args += ["--type", tipo]
    if dry_run:
        args.append("--dry-run")
    desc = f"Generar índices de contenido en {blog_dir}" + (" (simulación)" if dry_run else "")
    return Command(programa="bash", args=args, descripcion=desc)
