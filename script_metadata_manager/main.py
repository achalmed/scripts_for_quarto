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
