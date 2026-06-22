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

from .config import SYSTEM_EXCLUDED_FOLDERS, EXCLUDED_INDEX_FILES
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
        candidate = base_path / blog_name
        if not candidate.exists():
            # Intentar con prefijo pub_ si no se encuentra exacto
            candidate = base_path / f"pub_{blog_name}"
        if not candidate.is_dir():
            print(f"⚠️  El blog '{blog_name}' no existe en {base_path}")
            return pd.DataFrame()
        blogs_to_process = [candidate]
    else:
        all_dirs = [
            d for d in base_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        if allowed_blogs:
            blogs_to_process = [d for d in all_dirs if d.name in allowed_blogs]
        else:
            blogs_to_process = all_dirs

    total_found = total_articles = total_skipped = 0

    for blog_dir in blogs_to_process:
        print(f"\n📂 Procesando blog: {blog_dir.name}")
        blog_articles = blog_skipped = 0

        for root, dirs, files in os.walk(blog_dir):
            root_path = Path(root)
            dirs[:] = [
                d for d in dirs
                if not should_exclude_folder(
                    root_path / d, SYSTEM_EXCLUDED_FOLDERS, user_excluded_folders
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
                yaml_data = extract_yaml_merged(file_path, base_path)
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
                    "blog_nombre":    blog_dir.name,
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
