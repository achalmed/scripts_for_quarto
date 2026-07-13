"""
lib/tag_operations.py
=====================
Operaciones masivas de tags sobre dos destinos:

  - Archivos .qmd  → localiza artículos con collector (mismas exclusiones
    que el resto del sistema), transforma la lista con tag_utils y escribe
    con write_yaml_to_qmd (el único escritor YAML del proyecto).

  - Excel          → transforma solo la columna 'tags' de la hoja METADATOS;
    los archivos no se tocan hasta que el usuario ejecute 'update'.

Regla heredada del antiguo Tag Manager: los artículos SIN campo tags se
omiten siempre (nunca se crean tags donde no existían).

Depende de: config, yaml_parser, field_mapper, qmd_updater, collector, tag_utils.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

from .collector import collect_index_files
from .excel_writer import open_metadata_sheets
from .field_mapper import reorder_yaml
from .qmd_updater import write_yaml_to_qmd
from .tag_utils import (
    tags_from_cell,
    tags_from_yaml_value,
    tags_to_cell,
    transform_tags,
)


# =============================================================================
# OPERACIONES SOBRE ARCHIVOS .QMD
# =============================================================================

def _apply_to_single_qmd(
    file_path: Path,
    replacements: Optional[Dict[str, str]],
    to_remove: Optional[List[str]],
    to_add: Optional[List[str]],
    dry_run: bool,
) -> Optional[bool]:
    """
    Aplica la operación de tags a un archivo.
    Devuelve True si hubo (o se simularían) cambios, False si estaba al
    día, None si el archivo se omitió (sin frontmatter o sin tags).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ No se pudo leer {file_path}: {e}")
        return None

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        yaml_data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"⚠️  YAML inválido en {file_path}: {e}")
        return None

    current_tags = tags_from_yaml_value(yaml_data.get("tags"))
    if current_tags is None or not current_tags:
        return None

    new_tags, changes = transform_tags(
        current_tags, replacements, to_remove, to_add
    )

    if new_tags == current_tags:
        return False

    icon = "🔍" if dry_run else "✅"
    print(f"\n{icon} {file_path.parent.name}/{file_path.name}")
    print(f"   Antes:   {current_tags}")
    print(f"   Después: {new_tags}")
    for change in changes:
        print(f"   • {change}")

    if dry_run:
        return True

    if new_tags:
        yaml_data["tags"] = new_tags
    else:
        # La operación dejó la lista vacía (p.ej. remove de todos):
        # se elimina el campo, igual que hace update con celdas vacías
        del yaml_data["tags"]

    yaml_data = reorder_yaml(yaml_data)
    write_yaml_to_qmd(file_path, yaml_data, content, match.end())
    return True


def apply_tag_ops_to_files(
    base_path: Path,
    allowed_blogs: Set[str],
    user_excluded_folders: Set[str],
    replacements: Optional[Dict[str, str]] = None,
    to_remove: Optional[List[str]] = None,
    to_add: Optional[List[str]] = None,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Aplica una operación de tags a todos los artículos de la colección.
    Sin replacements/to_remove/to_add equivale a normalizar (la
    normalización + dedup es parte de todo pipeline de transform_tags).
    """
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '🏷️  OPERACIÓN DE TAGS'} SOBRE ARCHIVOS\n")
    print("=" * 70)

    df_files = collect_index_files(
        base_path, allowed_blogs, user_excluded_folders,
        blog_name=blog_filter, verbose=False,
    )

    if df_files.empty:
        print("⚠️  No se encontraron artículos")
        return

    if path_filter:
        df_files = df_files[
            df_files["ruta_archivo"].str.contains(path_filter, case=False, na=False)
        ]
        print(f"🔍 Filtro por ruta '{path_filter}': {len(df_files)} artículos")

    total_changed = total_unchanged = total_skipped = 0

    for _, row in df_files.iterrows():
        file_path = base_path / row["ruta_archivo"]
        if not file_path.exists():
            total_skipped += 1
            continue
        result = _apply_to_single_qmd(
            file_path, replacements, to_remove, to_add, dry_run
        )
        if result is None:
            total_skipped += 1
        elif result:
            total_changed += 1
        else:
            total_unchanged += 1

    print(f"\n{'=' * 70}")
    print(f"{'🔍 RESUMEN DE SIMULACIÓN' if dry_run else '✅ RESUMEN'}")
    print(f"   ✅ Modificados:            {total_changed}")
    print(f"   ⏭️  Sin cambios:            {total_unchanged}")
    print(f"   ⚠️  Omitidos (sin tags):    {total_skipped}")
    print(f"{'=' * 70}\n")

    if dry_run and total_changed > 0:
        print("💡 Para aplicar cambios, ejecuta sin --dry-run\n")


# =============================================================================
# OPERACIONES SOBRE EXCEL
# =============================================================================

def apply_tag_ops_to_excel(
    excel_path: str,
    replacements: Optional[Dict[str, str]] = None,
    to_remove: Optional[List[str]] = None,
    to_add: Optional[List[str]] = None,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Aplica una operación de tags SOLO a la columna 'tags' de la hoja
    METADATOS. Los archivos .qmd no se modifican: eso queda para el
    comando 'update', manteniendo el Excel como fuente de verdad.
    """
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '🏷️  OPERACIÓN DE TAGS'} SOBRE EXCEL\n")
    print("=" * 70)

    try:
        wb, ws, ws_values = open_metadata_sheets(excel_path)
    except Exception as e:
        print(f"❌ Error abriendo Excel: {e}")
        return

    headers = {
        ws.cell(1, col).value: col for col in range(1, ws.max_column + 1)
    }
    for required in ("tags", "ruta_archivo", "blog_nombre"):
        if required not in headers:
            print(f"❌ El Excel no tiene columna '{required}' en METADATOS")
            return

    tags_col = headers["tags"]
    ruta_col = headers["ruta_archivo"]
    blog_col = headers["blog_nombre"]

    total_changed = total_unchanged = total_empty = 0

    for row_idx in range(2, ws.max_row + 1):
        ruta = ws_values.cell(row_idx, ruta_col).value
        if not ruta:
            continue
        if blog_filter and ws_values.cell(row_idx, blog_col).value != blog_filter:
            continue
        if path_filter and path_filter.lower() not in str(ruta).lower():
            continue

        current_tags = tags_from_cell(ws_values.cell(row_idx, tags_col).value)
        if not current_tags:
            total_empty += 1
            continue

        new_tags, changes = transform_tags(
            current_tags, replacements, to_remove, to_add
        )

        if new_tags == current_tags:
            total_unchanged += 1
            continue

        total_changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} Fila {row_idx}: {ruta}")
        print(f"   Antes:   {', '.join(current_tags)}")
        print(f"   Después: {', '.join(new_tags) if new_tags else '(vacío)'}")
        for change in changes:
            print(f"   • {change}")

        if not dry_run:
            ws.cell(row_idx, tags_col, tags_to_cell(new_tags))

    print(f"\n{'=' * 70}")
    print(f"{'🔍 RESUMEN DE SIMULACIÓN' if dry_run else '✅ RESUMEN'}")
    print(f"   ✅ Filas modificadas:      {total_changed}")
    print(f"   ⏭️  Sin cambios:            {total_unchanged}")
    print(f"   ⚪ Sin tags:               {total_empty}")
    print(f"{'=' * 70}\n")

    if dry_run:
        if total_changed > 0:
            print("💡 Para aplicar cambios, ejecuta sin --dry-run\n")
        return

    if total_changed > 0:
        wb.save(excel_path)
        print(f"✅ Excel guardado: {excel_path}")
        print("💡 Los archivos .qmd NO fueron modificados. Para aplicar:")
        print(f"   python main.py update ~/Documents {excel_path}\n")
