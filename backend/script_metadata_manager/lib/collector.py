"""
lib/collector.py
================
Recorre el árbol de blogs buscando archivos index.qmd que sean artículos
reales (carpeta con fecha), aplica los filtros de configuración (allowed_blogs,
excluded_folders) y devuelve un DataFrame ordenado con metadatos básicos.

Depende de: config, yaml_parser.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Set

import pandas as pd

from .config import SYSTEM_EXCLUDED_FOLDERS, EXCLUDED_INDEX_FILES, PUBS_SUBDIR
from .yaml_parser import (
    is_article_index,
    extract_yaml_merged,
    detect_document_mode,
)


# =============================================================================
# FILTROS DE CARPETAS Y ARCHIVOS
# =============================================================================

def should_exclude_folder(
    folder_path: Path,
    system_excluded: Set[str] = SYSTEM_EXCLUDED_FOLDERS,
    user_excluded: Set[str] = frozenset(),
) -> bool:
    """True si alguna parte de la ruta está en las listas de exclusión."""
    parts = set(folder_path.parts)
    return bool(parts & (system_excluded | user_excluded))


def should_exclude_file(file_path: Path) -> bool:
    """True si el nombre del archivo está en la lista de excluidos."""
    return file_path.name in EXCLUDED_INDEX_FILES


# =============================================================================
# LOCALIZACIÓN DE BLOGS
# =============================================================================
# Desde 2026-09-06 los blogs pub_* son submódulos de website-achalma
# (base_path / PUBS_SUBDIR / pub_x). Un nombre de blog se acepta como:
# "pub_x", "x", "website-achalma" o una ruta relativa ("website-achalma/blog").

def resolve_blog_dir(base_path: Path, name: str) -> Optional[Path]:
    """Devuelve la carpeta real de un blog a partir de su nombre o ruta relativa."""
    pubs = base_path / PUBS_SUBDIR
    for candidate in (
        base_path / name,
        pubs / name,
        base_path / f"pub_{name}",
        pubs / f"pub_{name}",
    ):
        if candidate.is_dir():
            return candidate
    return None


def discover_blog_dirs(base_path: Path, allowed_blogs: Set[str]) -> list:
    """Lista de carpetas de blog a procesar (respeta allowed_blogs si no está vacío)."""
    if allowed_blogs:
        dirs = []
        for name in sorted(allowed_blogs):
            found = resolve_blog_dir(base_path, name)
            if found is None:
                print(f"⚠️  Blog permitido no encontrado: {name}")
            else:
                dirs.append(found)
        return dirs
    dirs = [
        d for d in base_path.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]
    pubs = base_path / PUBS_SUBDIR
    if pubs.is_dir():
        dirs += [d for d in pubs.iterdir() if d.is_dir() and d.name.startswith("pub_")]
    return dirs


def blog_label(base_path: Path, blog_dir: Path) -> str:
    """Nombre lógico del blog: 'pub_x' o 'website-achalma'; para secciones anidadas, la ruta relativa."""
    if blog_dir.name.startswith("pub_") or blog_dir.parent == base_path:
        return blog_dir.name
    return str(blog_dir.relative_to(base_path))


# =============================================================================
# RECOLECCIÓN PRINCIPAL
# =============================================================================

def collect_index_files(
    base_path: Path,
    allowed_blogs: Set[str],
    user_excluded_folders: Set[str],
    blog_name: Optional[str] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Recorre base_path buscando index.qmd de artículos válidos.

    Parámetros
    ----------
    base_path            : Ruta raíz que contiene las carpetas de blogs.
    allowed_blogs        : Si no está vacío, solo se procesan estos blogs.
    user_excluded_folders: Carpetas adicionales a ignorar (según config.yml).
    blog_name            : Si se indica, limita la búsqueda a ese blog.
    verbose              : Mostrar progreso detallado.

    Devuelve
    --------
    DataFrame con columnas:
        blog_nombre, ruta_archivo, tipo_documento, fecha_creacion,
        titulo, draft
    Ordenado por (blog_nombre, tipo_documento, fecha_creacion desc).
    """
    index_files = []

    # Determinar qué blogs procesar
    if blog_name:
        candidate = resolve_blog_dir(base_path, blog_name)
        if candidate is None:
            print(f"⚠️  El blog '{blog_name}' no existe en {base_path} ni en {base_path / PUBS_SUBDIR}")
            return pd.DataFrame()
        blogs_to_process = [candidate]
    else:
        blogs_to_process = discover_blog_dirs(base_path, allowed_blogs)

    total_found = total_articles = total_skipped = 0

    for blog_dir in blogs_to_process:
        print(f"\n📂 Procesando blog: {blog_dir.name}")
        blog_articles = blog_skipped = 0

        for root, dirs, files in os.walk(blog_dir):
            root_path = Path(root)
            # Se evalúa la ruta RELATIVA al blog: así "_pubs" excluye los
            # submódulos al recorrer website-achalma, pero no a un pub_* que
            # se procesa como blog propio (su ruta absoluta contiene _pubs).
            dirs[:] = [
                d for d in dirs
                if not should_exclude_folder(
                    (root_path / d).relative_to(blog_dir),
                    SYSTEM_EXCLUDED_FOLDERS, user_excluded_folders,
                )
            ]

            for fname in files:
                if fname != "index.qmd":
                    continue

                file_path = root_path / fname
                total_found += 1

                # Excluir archivos especiales
                if should_exclude_file(file_path):
                    if verbose:
                        print(f"  ⏭️  Omitido (config): {fname}")
                    total_skipped += 1
                    blog_skipped += 1
                    continue

                # Solo artículos con fecha en carpeta
                if not is_article_index(file_path):
                    if verbose:
                        rel = file_path.relative_to(base_path)
                        print(f"  ⏭️  Omitido (no es artículo): {rel}")
                    total_skipped += 1
                    blog_skipped += 1
                    continue

                # Extraer YAML combinado (index + _metadata.yml)
                # El _metadata.yml se busca hacia arriba solo hasta la raíz del blog
                yaml_data = extract_yaml_merged(file_path, blog_dir)
                if not yaml_data:
                    if verbose:
                        print(f"  ⚠️  Sin YAML: {file_path.name}")
                    total_skipped += 1
                    blog_skipped += 1
                    continue

                doc_type = detect_document_mode(file_path)

                try:
                    ctime = datetime.fromtimestamp(file_path.stat().st_ctime)
                except Exception:
                    ctime = datetime.now()

                rel_path = file_path.relative_to(base_path)

                index_files.append({
                    "blog_nombre":    blog_label(base_path, blog_dir),
                    "ruta_archivo":   str(rel_path),
                    "tipo_documento": doc_type,
                    "fecha_creacion": ctime,
                    "titulo":         yaml_data.get("title", ""),
                    "draft":          yaml_data.get("draft", True),
                })

                total_articles += 1
                blog_articles += 1

                if verbose:
                    print(
                        f"  ✅ Artículo: "
                        f"{file_path.parent.name}/{file_path.name}"
                    )

        print(
            f"  📊 Blog '{blog_dir.name}': "
            f"{blog_articles} artículos, {blog_skipped} omitidos"
        )

    print(f"\n{'=' * 70}")
    print(f"📊 RESUMEN DE RECOLECCIÓN:")
    print(f"  📁 Total archivos encontrados: {total_found}")
    print(f"  ✅ Artículos válidos:          {total_articles}")
    print(f"  ⏭️  Omitidos:                  {total_skipped}")
    print(f"{'=' * 70}\n")

    df = pd.DataFrame(index_files)
    if not df.empty:
        df = df.sort_values(
            ["blog_nombre", "tipo_documento", "fecha_creacion"],
            ascending=[True, True, False],
        )
    return df
