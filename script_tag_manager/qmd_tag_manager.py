#!/usr/bin/env python3
"""
QMD Tag Manager
===============
Script para gestionar tags en archivos .qmd de Quarto

Funcionalidades:
- Normalizar tags (minúsculas, sin tildes, separados por guión bajo)
- Renombrar tags específicos
- Eliminar tags
- Agregar nuevos tags
- Detectar y evitar duplicados
- Procesar archivos individuales o directorios completos

Autor: Edison Achalma
"""

import os
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Set, Optional
import argparse
import yaml


class QMDTagManager:
    """Gestor de tags para archivos Quarto (.qmd)"""
    
    def __init__(self, directory: str = "."):
        self.directory = Path(directory)
        self.changes_log = []
        
    @staticmethod
    def normalize_tag(tag: str) -> str:
        """
        Normaliza un tag según las reglas:
        - Convierte a minúsculas
        - Elimina tildes y caracteres especiales
        - Reemplaza espacios y caracteres no alfanuméricos por guión bajo
        - Elimina guiones bajos múltiples
        """
        # Convertir a minúsculas
        tag = tag.lower().strip()
        
        # Remover tildes
        tag = ''.join(
            c for c in unicodedata.normalize('NFD', tag)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Reemplazar espacios y caracteres especiales por guión bajo
        tag = re.sub(r'[^\w\s-]', '', tag)
        tag = re.sub(r'[\s-]+', '_', tag)
        
        # Eliminar guiones bajos al inicio y final
        tag = tag.strip('_')
        
        # Eliminar guiones bajos múltiples
        tag = re.sub(r'_+', '_', tag)
        
        return tag
    
    def extract_yaml_header(self, content: str) -> tuple:
        """
        Extrae el encabezado YAML de un archivo .qmd
        Retorna: (yaml_content, yaml_end_position, content_after_yaml)
        """
        # Buscar el bloque YAML entre ---
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(yaml_pattern, content, re.DOTALL)
        
        if not match:
            return None, 0, content
        
        yaml_content = match.group(1)
        yaml_end = match.end()
        content_after = content[yaml_end:]
        
        return yaml_content, yaml_end, content_after
    
    def parse_tags_from_yaml(self, yaml_content: str) -> tuple:
        """
        Extrae los tags del contenido YAML
        Retorna: (tags_list, yaml_dict)
        """
        try:
            yaml_dict = yaml.safe_load(yaml_content)
            tags = yaml_dict.get('tags', [])
            
            if tags is None:
                tags = []
            elif isinstance(tags, str):
                tags = [tags]
            
            return tags, yaml_dict
        except yaml.YAMLError as e:
            print(f"Error al parsear YAML: {e}")
            return [], {}
    
    def update_tags_in_yaml(self, yaml_content: str, new_tags: List[str]) -> str:
        """
        Actualiza los tags en el contenido YAML
        """
        # Buscar la sección de tags
        tags_pattern = r'^tags:\s*\n((?:  - .*\n)*)'
        
        # Si no hay tags, buscar dónde insertar
        if not re.search(tags_pattern, yaml_content, re.MULTILINE):
            # Buscar después de categories o keywords
            insert_after = None
            for key in ['categories', 'keywords', 'abstract']:
                pattern = rf'^{key}:.*?(?=\n\w|$)'
                match = re.search(pattern, yaml_content, re.MULTILINE | re.DOTALL)
                if match:
                    insert_after = match.end()
                    break
            
            if insert_after:
                tags_section = "\ntags:\n" + "\n".join(f"  - {tag}" for tag in new_tags) + "\n"
                yaml_content = yaml_content[:insert_after] + tags_section + yaml_content[insert_after:]
            else:
                # Agregar al final
                tags_section = "tags:\n" + "\n".join(f"  - {tag}" for tag in new_tags) + "\n"
                yaml_content += "\n" + tags_section
        else:
            # Reemplazar tags existentes
            new_tags_section = "tags:\n" + "\n".join(f"  - {tag}" for tag in new_tags)
            yaml_content = re.sub(tags_pattern, new_tags_section + "\n", yaml_content, flags=re.MULTILINE)
        
        return yaml_content
    
    def process_file(
        self, 
        filepath: Path,
        replacements: Dict[str, str] = None,
        tags_to_remove: List[str] = None,
        tags_to_add: List[str] = None,
        normalize_only: bool = True,
        dry_run: bool = False
    ) -> bool:
        """
        Procesa un archivo .qmd aplicando las operaciones especificadas
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer YAML header
            yaml_content, yaml_end, content_after = self.extract_yaml_header(content)
            
            if yaml_content is None:
                print(f"❌ No se encontró encabezado YAML en {filepath}")
                return False
            
            # Extraer tags actuales
            current_tags, yaml_dict = self.parse_tags_from_yaml(yaml_content)
            
            if not current_tags and not tags_to_add:
                print(f"⚠️  No hay tags en {filepath}")
                return False
            
            print(f"\n📄 Procesando: {filepath}")
            print(f"   Tags actuales: {current_tags}")
            
            # Normalizar tags
            normalized_tags = [self.normalize_tag(tag) for tag in current_tags]
            
            # Aplicar reemplazos
            if replacements:
                for old_tag, new_tag in replacements.items():
                    old_normalized = self.normalize_tag(old_tag)
                    new_normalized = self.normalize_tag(new_tag)
                    
                    if old_normalized in normalized_tags:
                        normalized_tags = [
                            new_normalized if tag == old_normalized else tag 
                            for tag in normalized_tags
                        ]
                        print(f"   🔄 Reemplazado: '{old_normalized}' → '{new_normalized}'")
            
            # Eliminar tags
            if tags_to_remove:
                tags_to_remove_normalized = [self.normalize_tag(tag) for tag in tags_to_remove]
                original_count = len(normalized_tags)
                normalized_tags = [
                    tag for tag in normalized_tags 
                    if tag not in tags_to_remove_normalized
                ]
                removed_count = original_count - len(normalized_tags)
                if removed_count > 0:
                    print(f"   🗑️  Eliminados: {removed_count} tag(s)")
            
            # Agregar nuevos tags
            if tags_to_add:
                for tag in tags_to_add:
                    normalized_tag = self.normalize_tag(tag)
                    if normalized_tag not in normalized_tags:
                        normalized_tags.append(normalized_tag)
                        print(f"   ➕ Agregado: '{normalized_tag}'")
                    else:
                        print(f"   ⚠️  Tag duplicado omitido: '{normalized_tag}'")
            
            # Eliminar duplicados preservando orden
            seen = set()
            unique_tags = []
            for tag in normalized_tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            
            if len(normalized_tags) != len(unique_tags):
                print(f"   🔍 Duplicados eliminados: {len(normalized_tags) - len(unique_tags)}")
            
            print(f"   Tags finales: {unique_tags}")
            
            # Actualizar YAML
            updated_yaml = self.update_tags_in_yaml(yaml_content, unique_tags)
            
            # Reconstruir archivo
            new_content = f"---\n{updated_yaml}---\n{content_after}"
            
            # Guardar cambios
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"   ✅ Archivo actualizado exitosamente")
            else:
                print(f"   🔍 [DRY RUN] No se guardaron cambios")
            
            self.changes_log.append({
                'file': str(filepath),
                'original_tags': current_tags,
                'final_tags': unique_tags
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error procesando {filepath}: {e}")
            return False
    
    def process_directory(
        self,
        replacements: Dict[str, str] = None,
        tags_to_remove: List[str] = None,
        tags_to_add: List[str] = None,
        normalize_only: bool = True,
        dry_run: bool = False,
        recursive: bool = False
    ):
        """
        Procesa todos los archivos .qmd en el directorio
        """
        pattern = "**/*.qmd" if recursive else "*.qmd"
        qmd_files = list(self.directory.glob(pattern))
        
        if not qmd_files:
            print(f"⚠️  No se encontraron archivos .qmd en {self.directory}")
            return
        
        print(f"🔍 Encontrados {len(qmd_files)} archivo(s) .qmd")
        
        successful = 0
        for qmd_file in qmd_files:
            if self.process_file(
                qmd_file,
                replacements=replacements,
                tags_to_remove=tags_to_remove,
                tags_to_add=tags_to_add,
                normalize_only=normalize_only,
                dry_run=dry_run
            ):
                successful += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Procesados exitosamente: {successful}/{len(qmd_files)} archivos")
        
        if dry_run:
            print("🔍 Modo DRY RUN - No se realizaron cambios permanentes")


def main():
    parser = argparse.ArgumentParser(
        description='Gestor de tags para archivos Quarto (.qmd)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Normalizar tags en el directorio actual
  python qmd_tag_manager.py --normalize

  # Reemplazar tags específicos
  python qmd_tag_manager.py --replace "Gestión Empresarial:gestion_empresarial" "Cadena de suministros:cadena_de_suministros"

  # Eliminar tags
  python qmd_tag_manager.py --remove "tag_obsoleto" "otro_tag"

  # Agregar nuevos tags
  python qmd_tag_manager.py --add "nuevo_tag" "otro_tag_nuevo"

  # Combinación de operaciones
  python qmd_tag_manager.py --replace "old:new" --remove "obsoleto" --add "nuevo"

  # Procesar directorio específico
  python qmd_tag_manager.py --directory "/ruta/a/directorio" --normalize

  # Modo dry-run (simular sin guardar cambios)
  python qmd_tag_manager.py --normalize --dry-run

  # Procesar recursivamente subdirectorios
  python qmd_tag_manager.py --normalize --recursive
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default='.',
        help='Directorio donde se encuentran los archivos .qmd (por defecto: directorio actual)'
    )
    
    parser.add_argument(
        '-n', '--normalize',
        action='store_true',
        help='Normalizar todos los tags (minúsculas, sin tildes, con guiones bajos)'
    )
    
    parser.add_argument(
        '-r', '--replace',
        nargs='+',
        metavar='OLD:NEW',
        help='Reemplazar tags. Formato: "tag_viejo:tag_nuevo" (puede especificar múltiples)'
    )
    
    parser.add_argument(
        '--remove',
        nargs='+',
        metavar='TAG',
        help='Eliminar tags específicos (puede especificar múltiples)'
    )
    
    parser.add_argument(
        '-a', '--add',
        nargs='+',
        metavar='TAG',
        help='Agregar nuevos tags (puede especificar múltiples)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular cambios sin guardar (modo de prueba)'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Procesar subdirectorios recursivamente'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Procesar un archivo específico en lugar de todo el directorio'
    )
    
    args = parser.parse_args()
    
    # Validar que se especificó al menos una operación
    if not any([args.normalize, args.replace, args.remove, args.add]):
        parser.error('Debe especificar al menos una operación: --normalize, --replace, --remove o --add')
    
    # Procesar reemplazos
    replacements = None
    if args.replace:
        replacements = {}
        for replacement in args.replace:
            if ':' not in replacement:
                print(f"⚠️  Formato inválido para reemplazo: '{replacement}'. Use 'viejo:nuevo'")
                continue
            old, new = replacement.split(':', 1)
            replacements[old.strip()] = new.strip()
    
    # Crear gestor
    manager = QMDTagManager(directory=args.directory)
    
    print("="*60)
    print("🏷️  QMD TAG MANAGER")
    print("="*60)
    print(f"📁 Directorio: {manager.directory.absolute()}")
    if args.dry_run:
        print("🔍 Modo: DRY RUN (simulación)")
    print("="*60)
    
    # Procesar archivo específico o directorio
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: El archivo '{file_path}' no existe")
            return
        if file_path.suffix != '.qmd':
            print(f"❌ Error: El archivo '{file_path}' no es un archivo .qmd")
            return
        
        manager.process_file(
            file_path,
            replacements=replacements,
            tags_to_remove=args.remove,
            tags_to_add=args.add,
            normalize_only=args.normalize,
            dry_run=args.dry_run
        )
    else:
        manager.process_directory(
            replacements=replacements,
            tags_to_remove=args.remove,
            tags_to_add=args.add,
            normalize_only=args.normalize,
            dry_run=args.dry_run,
            recursive=args.recursive
        )


if __name__ == "__main__":
    main()
