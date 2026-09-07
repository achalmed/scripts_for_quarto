#!/usr/bin/env python3
# main.py — script_format_yaml: repara el bloque YAML de los .qmd (orquestación; reglas en config.py, lógica en lib/formato.py).
#
#   main.py [--directory DIR] [--recursive] [--dry-run]     repara los .qmd de una carpeta
#   main.py --file archivo.qmd [--dry-run]                  repara un archivo
#
# Idempotente. --dry-run solo informa. (fix_qmd_files.py sigue funcionando como alias, FS3 2026-09-07.)
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config                       # noqa: E402
from lib import formato             # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Repara el formato YAML en archivos .qmd")
    ap.add_argument("-d", "--directory", default=".", help="carpeta con .qmd (por defecto, la actual)")
    ap.add_argument("--dry-run", action="store_true", help="simular sin modificar archivos")
    ap.add_argument("--recursive", action="store_true", default=config.RECURSIVO_DEFECTO, help="incluir subcarpetas")
    ap.add_argument("-f", "--file", help="reparar un archivo concreto")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    print("=" * 70 + "\n🔧 REPARADOR DE FORMATO YAML EN ARCHIVOS QMD\n" + "=" * 70)
    print(f"📁 Directorio: {os.path.abspath(a.directory)}" + ("\n🔍 Modo: DRY RUN (simulación)" if a.dry_run else "") + "\n" + "=" * 70 + "\n")
    if a.file:
        f = Path(a.file)
        if not f.exists():
            print(f"❌ Error: El archivo '{f}' no existe"); return 1
        lista = [f]
    else:
        lista = formato.archivos(Path(a.directory), a.recursive)
    if not lista:
        print("⚠️  No se encontraron archivos .qmd"); return 0
    print(f"🔍 Encontrados {len(lista)} archivo(s) .qmd\n")
    fixed = ok = err = 0
    for q in lista:
        r = formato.reparar(q, dry_run=a.dry_run)
        fixed += r is True; ok += r is False; err += r is None
        if a.verbose or r is True:
            print()
    print("=" * 70 + "\n📊 RESUMEN\n" + "=" * 70)
    print(f"✅ Archivos corregidos: {fixed}\n✓  Archivos ya correctos: {ok}" + (f"\n❌ Errores: {err}" if err else "") + f"\n📁 Total procesados: {len(lista)}")
    if a.dry_run:
        print("\n🔍 Modo DRY RUN - No se realizaron cambios permanentes\n   Ejecuta sin --dry-run para aplicar los cambios")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
