"""
lib/qmd_updater.py
==================
Actualiza archivos index.qmd con los valores del Excel.

Responsabilidades:
  - Leer el Excel, aplicar filtros de blog/ruta.
  - Comparar valores actuales vs nuevos para cada artículo.
  - Escribir YAML actualizado preservando el contenido del documento.
  - Reportar cambios con detalle o en modo simulación (dry-run).

Depende de: config, yaml_parser, field_mapper.
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from .config import ALL_FIELDS
from .field_mapper import apply_row_to_yaml


# =============================================================================
# ESCRITURA DE UN SOLO ARCHIVO
# =============================================================================

def _write_yaml_to_qmd(file_path: Path, updated_yaml: dict, original_content: str, match_end: int):
    """
    Serializa el YAML actualizado y reconstruye el archivo .qmd,
    preservando el contenido del documento (todo lo que viene después del ---).
    """
    new_yaml_str = yaml.dump(
        updated_yaml,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
        width=80,
        default_style=(
            '"'
            if any(
                isinstance(v, str) and "\n" in v
                for v in updated_yaml.values()
            )
            else None
        ),
    )

    # Limpiar saltos de línea extras en campos de texto largo
    for field in ("abstract", "description"):
        new_yaml_str = re.sub(
            rf"{field}: '([^']+)'\s+",
            lambda m, f=field: f"{f}: '{m.group(1).strip()}'\n",
            new_yaml_str,
        )

    new_content = f"---\n{new_yaml_str}---{original_content[match_end:]}"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


# =============================================================================
# ACTUALIZACIÓN DE UN ARTÍCULO
# =============================================================================

def update_single_qmd(
    file_path: Path,
    row: pd.Series,
    dry_run: bool,
    current: int,
    total: int,
) -> bool:
    """
    Aplica los cambios de una fila del Excel a un archivo index.qmd.

    Devuelve True si se aplicaron (o simularían) cambios, False si ya
    estaba sincronizado.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ No se pudo leer {file_path}: {e}")
        return False

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False

    yaml_data = yaml.safe_load(match.group(1)) or {}
    changes = []
    updated_yaml = apply_row_to_yaml(yaml_data, row, changes)

    if not changes:
        print(
            f"[{current}/{total}] ⏭️  Sin cambios: "
            f"{file_path.parent.name}/{file_path.name}"
        )
        return False

    icon   = "🔍" if dry_run else "✅"
    action = "Simulando" if dry_run else "Actualizando"
    print(
        f"\n[{current}/{total}] {icon} {action}: "
        f"{file_path.parent.name}/{file_path.name}"
    )
    print(f"   📝 Cambios detectados: {len(changes)}")
    for i, change in enumerate(changes[:10], 1):
        print(f"      {i}. {change}")
    if len(changes) > 10:
        print(f"      ... y {len(changes) - 10} cambios más")

    if dry_run:
        return True

    _write_yaml_to_qmd(file_path, updated_yaml, content, match.end())
    return True


# =============================================================================
# ACTUALIZACIÓN MASIVA (comando update)
# =============================================================================

def update_from_excel(
    base_path: Path,
    excel_path: str,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Lee el Excel y actualiza los index.qmd correspondientes.
    Soporta filtros por blog y por substring de ruta.
    """
    print(f"\n📖 Leyendo Excel: {excel_path}\n")

    try:
        df = pd.read_excel(excel_path, sheet_name="METADATOS")
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return

    if df.empty:
        print("⚠️  Excel vacío")
        return

    original_count = len(df)

    if blog_filter:
        df = df[df["blog_nombre"] == blog_filter]
        print(f"🔍 Filtro por blog '{blog_filter}': {len(df)}/{original_count} artículos")

    if path_filter:
        df = df[df["ruta_archivo"].str.contains(path_filter, case=False, na=False)]
        print(f"🔍 Filtro por ruta '{path_filter}': {len(df)}/{original_count} artículos")

    if df.empty:
        print("⚠️  No hay artículos después de aplicar filtros")
        return

    print(f"\n{'=' * 70}")
    print(f"{'🔍 MODO SIMULACION' if dry_run else '✅ ACTUALIZACION REAL'}")
    print(f"📊 Artículos a procesar: {len(df)}")
    print(f"{'=' * 70}\n")

    total_updated = total_skipped = total_errors = 0

    for i, (idx, row) in enumerate(df.iterrows(), 1):
        ruta = row.get("ruta_archivo")
        if pd.isna(ruta):
            continue

        file_path = base_path / ruta
        if not file_path.exists():
            print(f"❌ Archivo no encontrado: {ruta}")
            total_errors += 1
            continue

        try:
            result = update_single_qmd(file_path, row, dry_run, i, len(df))
            if result:
                total_updated += 1
            else:
                total_skipped += 1
        except Exception as e:
            print(f"❌ Error en {ruta}: {e}")
            total_errors += 1

    print(f"\n{'=' * 70}")
    print(f"{'🔍 RESUMEN DE SIMULACION' if dry_run else '✅ RESUMEN DE ACTUALIZACION'}")
    print(f"{'=' * 70}")
    print(f"✅ Actualizados:  {total_updated}")
    print(f"⏭️  Sin cambios:  {total_skipped}")
    print(f"❌ Errores:       {total_errors}")
    print(f"{'=' * 70}\n")

    if dry_run and total_updated > 0:
        print("💡 Para aplicar cambios, ejecuta sin --dry-run\n")
