#!/usr/bin/env python3
"""
main.py — Sistema de Gestión de Metadatos Quarto v2.0
======================================================
Punto de entrada único. Parsea los argumentos CLI y delega toda
la lógica a los módulos en lib/.

Uso:
    python main.py <comando> [opciones]

Comandos disponibles:
    create-config      Crea metadata_config.yml
    create-template    Genera la plantilla Excel
    update             Aplica cambios del Excel a los .qmd
    detect-new-fields  Detecta campos YAML no declarados
    add-columns        Agrega columnas nuevas al Excel
    find-differences   Muestra artículos con datos desincronizados
    sync-article       Sincroniza un artículo de forma interactiva
    sync-batch         Sincronización masiva interactiva

Comandos de tags (destino: un Excel .xlsx O un directorio de blogs):
    normalize-tags     Normaliza tags (minúsculas, sin tildes, snake_case)
    replace-tags       Reemplaza tags ("viejo:nuevo", admite varios)
    remove-tags        Elimina tags (alias: remove-tag)
    add-tags           Agrega tags (sin duplicados, respeta el orden)
    tag-stats          Estadísticas de tags de la colección
    audit-tags         Auditoría de taxonomía con recomendaciones

Comandos de sincronización desde la ruta (mismo doble destino):
    sync-dates         date desde la carpeta YYYY-MM-DD-titulo
    sync-pdf-urls      citation.pdf-url desde la ruta + URL base del blog
"""

import os
import sys
import argparse
from pathlib import Path
from openpyxl import Workbook

# Asegurar que el directorio del script esté en el path
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_config, create_default_config, VERSION, AUTHOR, EMAIL
from lib.collector import collect_index_files
from lib.excel_writer import (
    build_metadata_sheet,
    build_instructions_sheet,
    append_new_articles,
    add_columns_to_excel,
)
from lib.qmd_updater import update_from_excel
from lib.sync import (
    find_differences,
    sync_single_interactive,
    sync_batch_interactive,
    detect_new_fields,
)
from lib.tag_utils import parse_replacement_args
from lib.tag_operations import apply_tag_ops_to_files, apply_tag_ops_to_excel
from lib.tag_reports import (
    collect_tag_data_from_files,
    collect_tag_data_from_excel,
    print_tag_stats,
    print_tag_audit,
)
from lib.path_sync import (
    sync_dates_files,
    sync_dates_excel,
    sync_pdf_urls_files,
    sync_pdf_urls_excel,
)


# =============================================================================
# HELPERS
# =============================================================================

def _make_manager_config(base_path: str, config_file: str = None):
    """
    Construye el conjunto de parámetros de configuración que todos
    los comandos necesitan (ruta base, filtros, directorio de salida).
    """
    bp = Path(base_path).expanduser()
    if not bp.exists():
        print(f"❌ La ruta base no existe: {base_path}")
        sys.exit(1)

    cfg = load_config(config_file)
    allowed_blogs     = set(cfg.get("allowed_blogs", []))
    user_excluded     = set(cfg.get("excluded_folders", []))
    excel_output_dir  = Path(
        cfg.get("excel_output_dir", str(bp / "excel_databases"))
    ).expanduser()
    excel_output_dir.mkdir(parents=True, exist_ok=True)

    return bp, allowed_blogs, user_excluded, excel_output_dir


def _resolve_tag_target(target: str):
    """
    Determina el destino de un comando de tags:
      ('excel', Path)  si es un archivo .xlsx/.xlsm existente
      ('files', Path)  si es un directorio (raíz de blogs)
    Sale con error claro en cualquier otro caso.
    """
    path = Path(target).expanduser()
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        if not path.exists():
            print(f"❌ El Excel no existe: {target}")
            sys.exit(1)
        return "excel", path
    if path.is_dir():
        return "files", path
    print(f"❌ Destino inválido: '{target}' (se espera un .xlsx o un directorio)")
    sys.exit(2)


def _run_tag_operation(args, replacements=None, to_remove=None, to_add=None):
    """
    Despacha una operación de tags al backend correcto (Excel o archivos).
    Toda la lógica vive en lib/tag_operations; aquí solo se enruta.
    """
    mode, target = _resolve_tag_target(args.target)

    if mode == "excel":
        apply_tag_ops_to_excel(
            str(target),
            replacements=replacements,
            to_remove=to_remove,
            to_add=to_add,
            blog_filter=getattr(args, "blog", None),
            path_filter=getattr(args, "filter_path", None),
            dry_run=args.dry_run,
        )
    else:
        bp, allowed, excluded, _ = _make_manager_config(
            str(target), getattr(args, "config", None)
        )
        apply_tag_ops_to_files(
            bp, allowed, excluded,
            replacements=replacements,
            to_remove=to_remove,
            to_add=to_add,
            blog_filter=getattr(args, "blog", None),
            path_filter=getattr(args, "filter_path", None),
            dry_run=args.dry_run,
        )


def _collect_tag_data(args):
    """Obtiene el DataFrame de tags desde el destino (Excel o archivos)."""
    mode, target = _resolve_tag_target(args.target)
    if mode == "excel":
        return collect_tag_data_from_excel(
            str(target), blog_filter=getattr(args, "blog", None)
        )
    bp, allowed, excluded, _ = _make_manager_config(
        str(target), getattr(args, "config", None)
    )
    return collect_tag_data_from_files(
        bp, allowed, excluded, blog_filter=getattr(args, "blog", None)
    )


# =============================================================================
# COMANDO: create-config
# =============================================================================

def cmd_create_config(args):
    create_default_config(args.base_path, args.output)


# =============================================================================
# COMANDO: create-template
# =============================================================================

def cmd_create_template(args):
    bp, allowed, excluded, out_dir = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )

    output_filename = args.output
    if args.blog:
        name, ext = os.path.splitext(output_filename)
        output_filename = f"{name}_{args.blog}{ext}"

    output_path = out_dir / output_filename

    print("🔍 Recolectando archivos index.qmd...")
    print("   (Solo se incluirán artículos con fecha en su carpeta)\n")

    df_files = collect_index_files(
        bp, allowed, excluded, blog_name=args.blog, verbose=True
    )

    if df_files.empty:
        print("⚠️  No se encontraron artículos válidos")
        return

    # MODO INCREMENTAL
    if args.incremental and output_path.exists():
        print("\n🔄 MODO INCREMENTAL: Preservando datos existentes")
        print("   Solo se agregarán artículos nuevos\n")
        success = append_new_articles(output_path, df_files, bp)
        if not success:
            # Falló o no había nada nuevo; continuar con creación normal
            return
        print(
            f"\n💡 Tip: Usa '--incremental' para agregar solo artículos nuevos:\n"
            f"   python main.py create-template {args.base_path} "
            f"--config {getattr(args,'config','metadata_config.yml')} --incremental\n"
        )
        return

    # MODO NORMAL: desde cero
    wb = Workbook()
    wb.remove(wb.active)
    build_metadata_sheet(wb, df_files, bp)
    build_instructions_sheet(wb)
    wb.save(output_path)

    print(f"✅ Plantilla Excel creada: {output_path}")
    print(f"📊 Total de artículos: {len(df_files)}")
    print(f"📁 Hojas: METADATOS (todos los artículos), INSTRUCCIONES")
    print(f"\n💡 Próximos pasos:")
    print(f"   1. Abrir: {output_path}")
    print(f"   2. Editar metadatos en hoja METADATOS")
    print(f"   3. Guardar")
    print(f"   4. Actualizar: python main.py update \\")
    print(f"      {bp} {output_path}")
    print(
        f"\n💡 Tip: Usa '--incremental' para agregar solo artículos nuevos:\n"
        f"   python main.py create-template {args.base_path} "
        f"--config {getattr(args,'config','metadata_config.yml')} --incremental\n"
    )


# =============================================================================
# COMANDO: update
# =============================================================================

def cmd_update(args):
    bp, *_ = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )
    update_from_excel(
        bp,
        args.excel_file,
        blog_filter=getattr(args, "blog", None),
        path_filter=getattr(args, "filter_path", None),
        dry_run=args.dry_run,
    )


# =============================================================================
# COMANDO: detect-new-fields
# =============================================================================

def cmd_detect_new_fields(args):
    bp, allowed, excluded, _ = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )
    detect_new_fields(bp, allowed, excluded)


# =============================================================================
# COMANDO: add-columns
# =============================================================================

def cmd_add_columns(args):
    bp, *_ = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )
    add_columns_to_excel(
        args.excel_file,
        args.fields,
        bp,
        dry_run=args.dry_run,
    )


# =============================================================================
# COMANDO: find-differences
# =============================================================================

def cmd_find_differences(args):
    bp, *_ = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )
    find_differences(
        bp,
        args.excel_file,
        blog_filter=getattr(args, "blog", None),
        path_filter=getattr(args, "filter_path", None),
        max_show=getattr(args, "max_show", 10),
    )


# =============================================================================
# COMANDO: sync-article
# =============================================================================

def cmd_sync_article(args):
    bp, *_ = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )
    file_path = bp / args.article_path
    if not file_path.exists():
        print(f"❌ Artículo no encontrado: {file_path}")
        sys.exit(1)
    sync_single_interactive(bp, file_path, args.excel_file, args.dry_run)


# =============================================================================
# COMANDO: sync-batch
# =============================================================================

def cmd_sync_batch(args):
    bp, *_ = _make_manager_config(
        args.base_path, getattr(args, "config", None)
    )
    sync_batch_interactive(
        bp,
        args.excel_file,
        blog_filter=getattr(args, "blog", None),
        path_filter=getattr(args, "filter_path", None),
        dry_run=args.dry_run,
    )


# =============================================================================
# COMANDOS DE TAGS
# =============================================================================

def cmd_normalize_tags(args):
    _run_tag_operation(args)


def cmd_replace_tags(args):
    try:
        replacements = parse_replacement_args(args.replacements)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(2)
    _run_tag_operation(args, replacements=replacements)


def cmd_remove_tags(args):
    _run_tag_operation(args, to_remove=args.tags)


def cmd_add_tags(args):
    _run_tag_operation(args, to_add=args.tags)


def cmd_tag_stats(args):
    df = _collect_tag_data(args)
    print_tag_stats(df, top=args.top)


def cmd_audit_tags(args):
    df = _collect_tag_data(args)
    print_tag_audit(df, threshold=args.threshold)


# =============================================================================
# COMANDOS DE SINCRONIZACIÓN DESDE LA RUTA
# =============================================================================

def cmd_sync_dates(args):
    mode, target = _resolve_tag_target(args.target)
    if mode == "excel":
        sync_dates_excel(
            str(target),
            blog_filter=getattr(args, "blog", None),
            path_filter=getattr(args, "filter_path", None),
            dry_run=args.dry_run,
        )
    else:
        bp, allowed, excluded, _ = _make_manager_config(
            str(target), getattr(args, "config", None)
        )
        sync_dates_files(
            bp, allowed, excluded,
            blog_filter=getattr(args, "blog", None),
            path_filter=getattr(args, "filter_path", None),
            dry_run=args.dry_run,
        )


def cmd_sync_pdf_urls(args):
    # blog_base_urls es opcional: sin él, la URL base de cada blog se
    # resuelve por mayoría de los pdf-url existentes
    cfg = load_config(getattr(args, "config", None))
    configured_urls = cfg.get("blog_base_urls", {})

    mode, target = _resolve_tag_target(args.target)
    if mode == "excel":
        sync_pdf_urls_excel(
            str(target),
            configured_urls=configured_urls,
            blog_filter=getattr(args, "blog", None),
            path_filter=getattr(args, "filter_path", None),
            dry_run=args.dry_run,
        )
    else:
        bp, allowed, excluded, _ = _make_manager_config(
            str(target), getattr(args, "config", None)
        )
        sync_pdf_urls_files(
            bp, allowed, excluded,
            configured_urls=configured_urls,
            blog_filter=getattr(args, "blog", None),
            path_filter=getattr(args, "filter_path", None),
            dry_run=args.dry_run,
        )


# =============================================================================
# CLI PARSER
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Sistema de Gestión de Metadatos Quarto v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Ejemplos:

  # Crear configuración inicial
  python main.py create-config ~/Documents

  # Crear plantilla Excel con todos los blogs
  python main.py create-template ~/Documents --config metadata_config.yml

  # Agregar solo artículos nuevos (modo incremental)
  python main.py create-template ~/Documents --config metadata_config.yml --incremental

  # Simular actualización (sin aplicar cambios)
  python main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run

  # Actualizar todos los artículos
  python main.py update ~/Documents excel_databases/quarto_metadata.xlsx

  # Actualizar solo un blog
  python main.py update ~/Documents excel.xlsx --blog pub_axiomata

  # Actualizar solo rutas que contengan "2025-06"
  python main.py update ~/Documents excel.xlsx --filter-path "2025-06"

  # Detectar campos YAML no declarados
  python main.py detect-new-fields ~/Documents --config metadata_config.yml

  # Agregar columnas nuevas al Excel
  python main.py add-columns ~/Documents excel.xlsx campo1 campo2

  # Ver diferencias entre Excel y archivos
  python main.py find-differences ~/Documents excel.xlsx --blog pub_axiomata

  # Sincronizar un artículo (interactivo)
  python main.py sync-article ~/Documents excel.xlsx \\
      pub_axiomata/posts/2025-01-01-mi-articulo/index.qmd

  # Sincronización masiva interactiva
  python main.py sync-batch ~/Documents excel.xlsx --blog pub_axiomata

  # --- TAGS (destino: Excel .xlsx O directorio de blogs) ---

  # Normalizar la columna tags del Excel (los archivos no se tocan)
  python main.py normalize-tags excel_databases/quarto_metadata.xlsx --dry-run

  # Normalizar tags directamente en los index.qmd
  python main.py normalize-tags ~/Documents --config metadata_config.yml --dry-run

  # Reemplazos masivos (varios a la vez)
  python main.py replace-tags excel.xlsx "gestion:administracion" "python:data_science"

  # Eliminar y agregar tags
  python main.py remove-tags excel.xlsx tag_obsoleto otro_tag
  python main.py add-tags ~/Documents nuevo_tag --blog pub_axiomata --dry-run

  # Estadísticas y auditoría de taxonomía
  python main.py tag-stats ~/Documents --top 30
  python main.py audit-tags excel.xlsx --threshold 0.85

  # --- SINCRONIZACIÓN DESDE LA RUTA ---

  # Fechas: date = carpeta YYYY-MM-DD-titulo (formato MM/DD/YYYY)
  python main.py sync-dates ~/Documents --config metadata_config.yml --dry-run
  python main.py sync-dates excel_databases/quarto_metadata.xlsx --dry-run

  # PDF: citation.pdf-url = URL base del blog + ruta del artículo
  python main.py sync-pdf-urls ~/Documents --config metadata_config.yml --dry-run
  python main.py sync-pdf-urls excel.xlsx --blog chaska

Versión: {VERSION}
Autor:   {AUTHOR}
Email:   {EMAIL}
        """,
    )

    sub = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # create-config
    p = sub.add_parser("create-config", help="Crear metadata_config.yml")
    p.add_argument("base_path", help="Ruta raíz de los blogs")
    p.add_argument("-o", "--output", default="metadata_config.yml")

    # create-template
    p = sub.add_parser("create-template", help="Generar plantilla Excel")
    p.add_argument("base_path", help="Ruta raíz de los blogs")
    p.add_argument("-o", "--output", default="quarto_metadata.xlsx")
    p.add_argument("-b", "--blog", help="Limitar a un blog específico")
    p.add_argument("-c", "--config", help="Archivo de configuración")
    p.add_argument(
        "--incremental", action="store_true",
        help="Solo agregar artículos nuevos (preserva fórmulas existentes)"
    )

    # update
    p = sub.add_parser("update", help="Actualizar archivos desde Excel")
    p.add_argument("base_path")
    p.add_argument("excel_file")
    p.add_argument("-b", "--blog", help="Filtrar por blog")
    p.add_argument("-p", "--filter-path", help="Filtrar por substring en ruta")
    p.add_argument("-c", "--config")
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    # detect-new-fields
    p = sub.add_parser("detect-new-fields", help="Detectar campos YAML no declarados")
    p.add_argument("base_path")
    p.add_argument("-c", "--config")

    # add-columns
    p = sub.add_parser("add-columns", help="Agregar columnas nuevas al Excel")
    p.add_argument("base_path")
    p.add_argument("excel_file")
    p.add_argument("fields", nargs="+", help="Nombres de columnas a agregar")
    p.add_argument("-c", "--config")
    p.add_argument("--dry-run", action="store_true")

    # find-differences
    p = sub.add_parser("find-differences", help="Ver diferencias Excel vs archivos")
    p.add_argument("base_path")
    p.add_argument("excel_file")
    p.add_argument("-b", "--blog")
    p.add_argument("-p", "--filter-path")
    p.add_argument("-c", "--config")
    p.add_argument("--max-show", type=int, default=10)

    # sync-article
    p = sub.add_parser("sync-article", help="Sincronizar un artículo (interactivo)")
    p.add_argument("base_path")
    p.add_argument("excel_file")
    p.add_argument("article_path", help="Ruta relativa del index.qmd")
    p.add_argument("-c", "--config")
    p.add_argument("--dry-run", action="store_true")

    # sync-batch
    p = sub.add_parser("sync-batch", help="Sincronización masiva interactiva")
    p.add_argument("base_path")
    p.add_argument("excel_file")
    p.add_argument("-b", "--blog")
    p.add_argument("-p", "--filter-path")
    p.add_argument("-c", "--config")
    p.add_argument("--dry-run", action="store_true")

    # --- Comandos de tags ----------------------------------------------------
    # Todos aceptan como destino un Excel (.xlsx → modifica solo el Excel)
    # o un directorio de blogs (→ modifica los index.qmd directamente)

    def _add_tag_common_args(sp):
        sp.add_argument(
            "target",
            help="Destino: archivo .xlsx (modo Excel) o directorio de blogs (modo archivos)",
        )
        sp.add_argument("-b", "--blog", help="Filtrar por blog")
        sp.add_argument("-p", "--filter-path", help="Filtrar por substring en ruta")
        sp.add_argument("-c", "--config", help="Archivo de configuración (modo archivos)")

    p = sub.add_parser(
        "normalize-tags",
        help="Normalizar tags (minúsculas, sin tildes, snake_case, sin duplicados)",
    )
    _add_tag_common_args(p)
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    p = sub.add_parser(
        "replace-tags", help="Reemplazar tags masivamente (viejo:nuevo ...)"
    )
    _add_tag_common_args(p)
    p.add_argument(
        "replacements", nargs="+", metavar="VIEJO:NUEVO",
        help='Reemplazos, p.ej. "gestion:administracion" (admite varios)',
    )
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    p = sub.add_parser(
        "remove-tags", aliases=["remove-tag"],
        help="Eliminar tags en toda la colección",
    )
    _add_tag_common_args(p)
    p.add_argument("tags", nargs="+", metavar="TAG", help="Tags a eliminar")
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    p = sub.add_parser(
        "add-tags",
        help="Agregar tags (solo a artículos que ya tienen tags; sin duplicados)",
    )
    _add_tag_common_args(p)
    p.add_argument("tags", nargs="+", metavar="TAG", help="Tags a agregar")
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    p = sub.add_parser("tag-stats", help="Estadísticas de tags de la colección")
    _add_tag_common_args(p)
    p.add_argument("--top", type=int, default=20, help="Cuántos tags mostrar en el top")

    p = sub.add_parser(
        "audit-tags", help="Auditoría de taxonomía (variantes, typos, formato)"
    )
    _add_tag_common_args(p)
    p.add_argument(
        "--threshold", type=float, default=0.8,
        help="Umbral de similitud para detectar tags casi iguales (0-1)",
    )

    # --- Sincronización desde la ruta (mismo doble destino que tags) --------
    p = sub.add_parser(
        "sync-dates",
        help="Sincronizar date con la carpeta YYYY-MM-DD-titulo de cada artículo",
    )
    _add_tag_common_args(p)
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    p = sub.add_parser(
        "sync-pdf-urls",
        help="Sincronizar citation.pdf-url con la ruta real (URL base por blog)",
    )
    _add_tag_common_args(p)
    p.add_argument("--dry-run", action="store_true", help="Simular sin aplicar")

    return parser


# =============================================================================
# MAIN
# =============================================================================

COMMAND_MAP = {
    "create-config":      cmd_create_config,
    "create-template":    cmd_create_template,
    "update":             cmd_update,
    "detect-new-fields":  cmd_detect_new_fields,
    "add-columns":        cmd_add_columns,
    "find-differences":   cmd_find_differences,
    "sync-article":       cmd_sync_article,
    "sync-batch":         cmd_sync_batch,
    # Gestión de tags (absorbe el antiguo script_tag_manager)
    "normalize-tags":     cmd_normalize_tags,
    "replace-tags":       cmd_replace_tags,
    "remove-tags":        cmd_remove_tags,
    "remove-tag":         cmd_remove_tags,   # alias
    "add-tags":           cmd_add_tags,
    "tag-stats":          cmd_tag_stats,
    "audit-tags":         cmd_audit_tags,
    # Sincronización desde la ruta (absorbe los scripts legacy 1_ y 3_)
    "sync-dates":         cmd_sync_dates,
    "sync-pdf-urls":      cmd_sync_pdf_urls,
}


def main():
    parser = build_parser()
    args   = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    handler = COMMAND_MAP.get(args.command)
    if not handler:
        print(f"❌ Comando desconocido: {args.command}")
        return 1

    try:
        handler(args)
        return 0
    except KeyboardInterrupt:
        print("\n\n⏭️  Operación cancelada por el usuario")
        return 0
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
