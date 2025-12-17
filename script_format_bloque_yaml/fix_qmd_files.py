#!/usr/bin/env python3
"""
Script de Reparación para archivos .qmd
Corrige el problema del separador --- pegado al contenido

FORMATO CORRECTO:
---
yaml_content
---

## Contenido del documento

El script es idempotente: ejecutarlo múltiples veces produce el mismo resultado.
"""

import os
import re
from pathlib import Path
import argparse


def fix_yaml_separator(filepath: Path, dry_run: bool = False) -> bool:
    """
    Repara el formato del bloque YAML frontmatter.
    
    Formato correcto:
    ---
    yaml_content
    ---
    
    ## Contenido
    
    Donde hay EXACTAMENTE una línea en blanco entre --- y el contenido.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Primero, normalizar el caso donde --- está pegado a la línea anterior
        # Buscar patrones como: "draft: false---" o "text---"
        content_normalized = re.sub(
            r'([^\n])---\s*\n',
            r'\1\n---\n',
            content
        )
        
        # Ahora buscar el bloque YAML completo
        # Patrón más flexible que captura el YAML y todo lo que sigue
        match = re.match(r'^---\s*\n(.*?)\n---\s*(.*)$', content_normalized, re.DOTALL)
        
        if not match:
            print(f"⚠️  No se encontró bloque YAML válido en: {filepath}")
            return False
        
        yaml_content = match.group(1)  # Contenido entre los ---
        after_yaml = match.group(2)     # Todo después del segundo ---
        
        # Limpiar espacios en blanco al inicio del contenido después de ---
        after_yaml = after_yaml.lstrip('\n\r\t ')
        
        # Construir el formato correcto
        if after_yaml:
            # Si hay contenido, debe haber exactamente una línea en blanco después de ---
            correct_format = f"---\n{yaml_content}\n---\n\n{after_yaml}"
        else:
            # Si no hay contenido después del YAML
            correct_format = f"---\n{yaml_content}\n---\n"
        
        # Comparar con el contenido original
        if content != correct_format:
            print(f"🔧 Corrigiendo formato YAML en: {filepath}")
            
            # Mostrar qué se va a cambiar
            if after_yaml:
                preview = after_yaml[:60].replace('\n', '\\n')
                print(f"   Contenido después de ---: '{preview}...'")
            
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(correct_format)
                print(f"   ✅ Archivo corregido")
            else:
                print(f"   🔍 [DRY RUN] Se corregiría este archivo")
            
            return True
        else:
            print(f"✓ OK (formato correcto): {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Repara el formato YAML en archivos .qmd',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Reparar archivos en el directorio actual
  python fix_qmd_files.py

  # Ver qué se cambiaría sin modificar archivos
  python fix_qmd_files.py --dry-run

  # Reparar en directorio específico
  python fix_qmd_files.py --directory ./posts

  # Reparar recursivamente todos los subdirectorios
  python fix_qmd_files.py --directory ./posts --recursive

  # Reparar un archivo específico
  python fix_qmd_files.py --file mi_archivo.qmd

FORMATO CORRECTO que genera el script:
---
yaml_content
---

## Contenido del documento

(Una línea en blanco entre --- y el contenido)
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default='.',
        help='Directorio con archivos .qmd (por defecto: directorio actual)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular cambios sin modificar archivos'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Procesar subdirectorios recursivamente'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Reparar un archivo específico'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("🔧 REPARADOR DE FORMATO YAML EN ARCHIVOS QMD")
    print("="*70)
    print(f"📁 Directorio: {os.path.abspath(args.directory)}")
    if args.dry_run:
        print("🔍 Modo: DRY RUN (simulación)")
    print("="*70)
    print()
    
    # Procesar archivo específico o directorio
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: El archivo '{file_path}' no existe")
            return
        
        files_to_process = [file_path]
    else:
        directory = Path(args.directory)
        pattern = "**/*.qmd" if args.recursive else "*.qmd"
        files_to_process = list(directory.glob(pattern))
    
    if not files_to_process:
        print(f"⚠️  No se encontraron archivos .qmd")
        return
    
    print(f"🔍 Encontrados {len(files_to_process)} archivo(s) .qmd\n")
    
    fixed_count = 0
    ok_count = 0
    error_count = 0
    
    for qmd_file in files_to_process:
        result = fix_yaml_separator(qmd_file, dry_run=args.dry_run)
        
        if result is True:
            fixed_count += 1
        elif result is False:
            ok_count += 1
        else:
            error_count += 1
        
        if args.verbose or result is True:
            print()
    
    print("="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Archivos corregidos: {fixed_count}")
    print(f"✓  Archivos ya correctos: {ok_count}")
    if error_count > 0:
        print(f"❌ Errores: {error_count}")
    print(f"📁 Total procesados: {len(files_to_process)}")
    
    if args.dry_run:
        print("\n🔍 Modo DRY RUN - No se realizaron cambios permanentes")
        print("   Ejecuta sin --dry-run para aplicar los cambios")


if __name__ == "__main__":
    main()