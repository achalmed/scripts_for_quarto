"""
project_scanner.py — Escaneo de proyectos Quarto (Python puro, sin Qt).

Replica la lógica de detección del blogs_manager: proyectos pub_* y
website-achalma dentro de Documents, con sus carpetas de posts
YYYY-MM-DD-titulo. Lo consume ScanWorker (QThread) para no bloquear la UI.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.models.blog import Blog, Post

# Carpetas técnicas que nunca son carpetas de posts (mismo criterio que
# QBLOG_IGNORE_DIRS en script_blogs_manager/lib/00-config.sh)
IGNORAR_DIRS = {
    "_freeze", "_partials", "_site", "_extensions", ".quarto",
    ".git", "site_libs", "node_modules", "assets",
}

_FECHA_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
_TITULO_RE = re.compile(r'^title:\s*["\']?(.*?)["\']?\s*$', re.MULTILINE)


def descubrir_blogs(docs_dir: Path) -> list[Blog]:
    """Encuentra todos los proyectos pub_* y website-achalma."""
    candidatos: list[Path] = sorted(docs_dir.glob("pub_*"))
    website = docs_dir / "website-achalma"
    if website.is_dir():
        candidatos.append(website)

    blogs = []
    for ruta in candidatos:
        if not ruta.is_dir():
            continue
        blog = Blog(
            ruta=ruta,
            posts=listar_posts(ruta),
            tiene_git=(ruta / ".git").is_dir(),
            tiene_quarto_yml=(ruta / "_quarto.yml").is_file(),
        )
        blogs.append(blog)
    return blogs


def listar_posts(blog_dir: Path) -> list[Post]:
    """Posts = carpetas YYYY-MM-DD-* con index.qmd, en cualquier subcarpeta de primer/segundo nivel."""
    posts: list[Post] = []
    for index_qmd in blog_dir.glob("*/**/index.qmd"):
        carpeta = index_qmd.parent
        # descartar rutas dentro de carpetas técnicas
        if any(parte in IGNORAR_DIRS for parte in carpeta.relative_to(blog_dir).parts):
            continue
        m = _FECHA_RE.match(carpeta.name)
        if not m:
            continue
        posts.append(Post(ruta=carpeta, fecha=m.group(1), titulo=_leer_titulo(index_qmd)))
    posts.sort(key=lambda p: p.fecha, reverse=True)
    return posts


def _leer_titulo(index_qmd: Path) -> str:
    """Extrae `title:` del frontmatter sin parsear YAML completo (rápido)."""
    try:
        cabecera = index_qmd.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return ""
    m = _TITULO_RE.search(cabecera)
    return m.group(1).strip() if m else ""
