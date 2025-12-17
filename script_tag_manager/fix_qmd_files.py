#!/usr/bin/env python3
"""
Script de Reparación para archivos .qmd
Corrige el problema del separador --- pegado al contenido
"""

import os
import re
from pathlib import Path
import argparse


def fix_yaml_separator(filepath: Path, dry_run: bool = False) -> bool:
    """
    Repara el separador YAML de cierre cuando está pegado al contenido
    o cuando no hay línea en blanco después del bloque YAML.
    NO modifica el --- de apertura.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changed = False

        # 1. Caso principal: --- pegado al final de una línea (ej: comentario---\n## Título)
        if re.search(r'([^\n])---\s*\n', content, re.MULTILINE):
            content = re.sub(r'([^\n])---\s*\n', r'\1\n---\n', content, flags=re.MULTILINE)
            changed = True

        # 2. Asegurar línea en blanco DESPUÉS del --- de cierre (pero NO antes del primero)
        # Buscamos el bloque YAML completo: desde primer --- hasta segundo ---
        yaml_block_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_block_match:
            end_pos = yaml_block_match.end()
            after_yaml = content[end_pos:]

            # Si después del --- de cierre no hay al menos una línea en blanco antes del contenido real
            if not re.match(r'\s*\n\s*\n', after_yaml):  # no hay \n\n o equivalente
                # Insertamos una línea en blanco justo después del --- de cierre
                content = content[:end_pos] + '\n' + content[end_pos:]
                changed = True

        # 3. Caso raro: contenido pegado directamente sin salto (---Titulo)
        if re.search(r'---([^\s\n])', content):
            content = re.sub(r'---([^\s\n])', r'---\n\1', content)
            changed = True

        if changed:
            print(f"🔧 Reparando separador YAML en: {filepath}")
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f" ✅ Archivo reparado: {filepath}")
            else:
                print(f" 🔍 [DRY RUN] Se repararía: {filepath}")
            return True
        else:
            print(f"✓ OK (separador correcto): {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False

def remove_unwanted_tags(filepath: Path, dry_run: bool = False) -> bool:
    """
    Elimina la sección de tags de archivos que originalmente no la tenían
    (para archivos que fueron modificados incorrectamente con --add)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar encabezado YAML
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.match(yaml_pattern, content, re.DOTALL)
        
        if not match:
            return False
        
        yaml_content = match.group(1)
        
        # Buscar sección de tags
        tags_pattern = r'\ntags:\s*\n(?:  - .*\n)*'
        
        if re.search(tags_pattern, yaml_content):
            print(f"📋 Encontrados tags en: {filepath}")
            print(f"   ¿Deseas eliminar los tags de este archivo? (s/n): ", end='')
            
            if not dry_run:
                response = input().strip().lower()
                if response == 's':
                    # Eliminar sección de tags
                    new_yaml = re.sub(tags_pattern, '\n', yaml_content)
                    new_content = content.replace(yaml_content, new_yaml)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"   ✅ Tags eliminados")
                    return True
                else:
                    print(f"   ⏭️  Omitido")
            else:
                print(f"   🔍 [DRY RUN] Se preguntaría para eliminar tags")
            
        return False
            
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Repara archivos .qmd modificados incorrectamente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Reparar separadores YAML en el directorio actual
  python fix_qmd_files.py --fix-separator

  # Reparar en directorio específico (dry-run)
  python fix_qmd_files.py --fix-separator --directory ./posts --dry-run

  # Eliminar tags de archivos que no deberían tenerlos
  python fix_qmd_files.py --remove-unwanted-tags --directory ./posts

  # Hacer ambas reparaciones
  python fix_qmd_files.py --fix-separator --remove-unwanted-tags
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default='.',
        help='Directorio con archivos .qmd (por defecto: directorio actual)'
    )
    
    parser.add_argument(
        '--fix-separator',
        action='store_true',
        help='Reparar separadores YAML --- pegados al contenido'
    )
    
    parser.add_argument(
        '--remove-unwanted-tags',
        action='store_true',
        help='Eliminar tags de archivos que no deberían tenerlos (interactivo)'
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
    
    args = parser.parse_args()
    
    if not args.fix_separator and not args.remove_unwanted_tags:
        parser.error('Debe especificar al menos una opción: --fix-separator o --remove-unwanted-tags')
    
    print("="*70)
    print("🔧 REPARADOR DE ARCHIVOS QMD")
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
    
    fixed_separator = 0
    removed_tags = 0
    
    for qmd_file in files_to_process:
        if args.fix_separator:
            if fix_yaml_separator(qmd_file, dry_run=args.dry_run):
                fixed_separator += 1
        
        if args.remove_unwanted_tags:
            if remove_unwanted_tags(qmd_file, dry_run=args.dry_run):
                removed_tags += 1
        
        print()
    
    print("="*70)
    print("📊 RESUMEN")
    print("="*70)
    
    if args.fix_separator:
        print(f"✅ Separadores reparados: {fixed_separator}/{len(files_to_process)}")
    
    if args.remove_unwanted_tags:
        print(f"✅ Archivos con tags eliminados: {removed_tags}")
    
    if args.dry_run:
        print("🔍 Modo DRY RUN - No se realizaron cambios permanentes")


if __name__ == "__main__":
    main()
