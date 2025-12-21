#!/usr/bin/env python3
"""
Sistema de Gestión de Metadatos para Blogs Quarto - Versión 1.1
Autor: Edison Achalma
Fecha: Diciembre 2024

Mejoras v1.1:
- Soporte para _metadata.yml (herencia de configuración)
- Detección mejorada de documentmode
- Configuración manual de blogs y carpetas a excluir
- Corrección de bugs con citation (bool vs dict)
- Preservación de indentación YAML
- Guardado de Excel en ubicación configurable
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
import re
import json


class QuartoMetadataManager:
    """Gestor principal de metadatos de blogs Quarto"""
    
    # Carpetas a excluir SIEMPRE (no se pueden configurar)
    SYSTEM_EXCLUDED_FOLDERS = {'_site', '_freeze', 'site_libs', '.git', '.quarto', 
                               'node_modules', '__pycache__', '_extensions',
                               '.venv', 'venv', 'env'}
    
    # Archivos index.qmd a excluir
    EXCLUDED_INDEX_FILES = {
        '_contenido-inicio.qmd', '_contenido-final.qmd', 
        '_contenido_posts.qmd', '_contenido_economia-preuniversitaria.qmd',
        '_contenido_inteligencia-comercial.qmd', '_contenido_talk.qmd',
        '_contenido_teching.qmd', '404.qmd', 'contact.qmd', 
        'accessibility.qmd', 'license.qmd', '_index.md', 'index.md'
    }
    
    # Campos comunes obligatorios
    COMMON_FIELDS = [
        'ruta_archivo', 'blog_nombre', 'tipo_documento', 
        'title', 'shorttitle', 'subtitle', 
        'date', 'draft', 
        'abstract', 'description',
        'keywords', 'tags', 'categories',
        'image', 'eval',
        'citation_type', 'citation_author', 'citation_pdf_url',
        'links_enabled', 'links_data',
        'bibliography'
    ]
    
    # Campos específicos por tipo de documento
    SPECIFIC_FIELDS = {
        'stu': ['course', 'professor', 'duedate', 'note'],
        'jou': ['journal', 'volume', 'copyrightnotice', 'copyrightext'],
        'man': ['floatsintext', 'numbered_lines', 'meta_analysis', 'mask'],
        'doc': ['floatsintext', 'numbered_lines']
    }
    
    # Campos de autor (pueden repetirse para múltiples autores)
    AUTHOR_FIELDS = [
        'author_1_name', 'author_1_corresponding', 'author_1_orcid', 'author_1_email',
        'author_1_affiliation_name', 'author_1_affiliation_department',
        'author_1_affiliation_city', 'author_1_affiliation_region',
        'author_1_affiliation_country', 'author_1_roles',
        'author_2_name', 'author_2_corresponding', 'author_2_orcid', 'author_2_email',
        'author_2_affiliation_name', 'author_2_roles',
        'author_3_name', 'author_3_orcid', 'author_3_affiliation_name', 'author_3_roles'
    ]
    
    def __init__(self, base_path: str, config_file: Optional[str] = None):
        """
        Inicializa el gestor de metadatos
        
        Args:
            base_path: Ruta base donde están los blogs
            config_file: Archivo de configuración opcional
        """
        self.base_path = Path(base_path).expanduser()
        if not self.base_path.exists():
            raise ValueError(f"La ruta base no existe: {base_path}")
        
        # Configuración personalizable
        self.config = self._load_config(config_file)
        self.user_excluded_folders = set(self.config.get('excluded_folders', []))
        self.allowed_blogs = set(self.config.get('allowed_blogs', []))
        self.excel_output_dir = Path(self.config.get('excel_output_dir', '.')).expanduser()
        
        # Crear directorio de salida si no existe
        self.excel_output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Carga archivo de configuración si existe"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def should_exclude_folder(self, folder_path: Path) -> bool:
        """Determina si una carpeta debe ser excluida"""
        parts = set(folder_path.parts)
        
        # Excluir carpetas del sistema
        if parts & self.SYSTEM_EXCLUDED_FOLDERS:
            return True
        
        # Excluir carpetas del usuario
        if parts & self.user_excluded_folders:
            return True
        
        return False
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Determina si un archivo index.qmd debe ser excluido"""
        return file_path.name in self.EXCLUDED_INDEX_FILES
    
    def is_allowed_blog(self, blog_name: str) -> bool:
        """Verifica si el blog está en la lista permitida"""
        if not self.allowed_blogs:
            return True  # Si no hay lista, permitir todos
        return blog_name in self.allowed_blogs
    
    def find_metadata_yml(self, qmd_path: Path) -> Optional[Path]:
        """
        Busca el archivo _metadata.yml más cercano al .qmd
        
        Args:
            qmd_path: Ruta del archivo .qmd
            
        Returns:
            Path del _metadata.yml o None
        """
        current_dir = qmd_path.parent
        
        # Buscar hacia arriba hasta llegar a base_path
        while current_dir >= self.base_path:
            metadata_file = current_dir / '_metadata.yml'
            if metadata_file.exists():
                return metadata_file
            current_dir = current_dir.parent
        
        return None
    
    def load_metadata_yml(self, metadata_path: Path) -> Dict:
        """Carga el contenido de _metadata.yml"""
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Error leyendo {metadata_path}: {e}")
            return {}
    
    def merge_yaml_data(self, base_yaml: Dict, index_yaml: Dict) -> Dict:
        """
        Fusiona datos de _metadata.yml con index.qmd
        Los valores en index.qmd tienen prioridad
        
        Args:
            base_yaml: Datos de _metadata.yml
            index_yaml: Datos de index.qmd
            
        Returns:
            Diccionario fusionado
        """
        # Crear copia del base
        merged = base_yaml.copy()
        
        # Actualizar con valores de index (prioridad)
        for key, value in index_yaml.items():
            if value is not None:
                merged[key] = value
        
        return merged
    
    def extract_yaml_from_qmd(self, file_path: Path) -> Optional[Dict]:
        """Extrae el YAML frontmatter de un archivo .qmd"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                index_yaml = yaml.safe_load(yaml_content) or {}
                
                # Buscar _metadata.yml
                metadata_path = self.find_metadata_yml(file_path)
                if metadata_path:
                    base_yaml = self.load_metadata_yml(metadata_path)
                    # Fusionar con prioridad al index.qmd
                    return self.merge_yaml_data(base_yaml, index_yaml)
                
                return index_yaml
            return None
        except Exception as e:
            print(f"⚠️  Error extrayendo YAML de {file_path}: {e}")
            return None
    
    def detect_document_mode(self, yaml_data: Dict) -> str:
        """
        Detecta el tipo de documento (stu, man, jou, doc) con soporte para _metadata.yml
        
        Args:
            yaml_data: Diccionario con datos YAML (ya fusionado)
            
        Returns:
            Tipo de documento
        """
        # 1. Buscar en format.apaquarto-pdf.documentmode
        if 'format' in yaml_data:
            formats = yaml_data['format']
            if isinstance(formats, dict):
                if 'apaquarto-pdf' in formats:
                    apa_config = formats['apaquarto-pdf']
                    if isinstance(apa_config, dict) and 'documentmode' in apa_config:
                        mode = apa_config['documentmode']
                        if mode in ['stu', 'man', 'jou', 'doc']:
                            return mode
        
        # 2. Detectar por campos específicos
        if 'course' in yaml_data or 'professor' in yaml_data:
            return 'stu'
        elif 'journal' in yaml_data or 'volume' in yaml_data:
            return 'jou'
        elif 'meta-analysis' in yaml_data:
            return 'man'
        
        # 3. Por defecto jou (según tu configuración en _metadata.yml)
        return 'jou'
    
    def collect_index_files(self, blog_name: Optional[str] = None) -> pd.DataFrame:
        """Recolecta todos los archivos index.qmd"""
        index_files = []
        
        if blog_name:
            blog_path = self.base_path / blog_name
            if not blog_path.exists():
                print(f"⚠️  El blog '{blog_name}' no existe")
                return pd.DataFrame()
            blogs_to_process = [blog_path]
        else:
            # Filtrar por blogs permitidos
            all_dirs = [d for d in self.base_path.iterdir() 
                       if d.is_dir() and not d.name.startswith('.')]
            
            if self.allowed_blogs:
                blogs_to_process = [d for d in all_dirs if d.name in self.allowed_blogs]
            else:
                blogs_to_process = all_dirs
        
        for blog_dir in blogs_to_process:
            if not self.is_allowed_blog(blog_dir.name):
                continue
            
            print(f"📂 Procesando blog: {blog_dir.name}")
            
            for root, dirs, files in os.walk(blog_dir):
                # Filtrar directorios excluidos
                dirs[:] = [d for d in dirs if not self.should_exclude_folder(Path(root) / d)]
                
                for file in files:
                    if file == 'index.qmd':
                        file_path = Path(root) / file
                        
                        if self.should_exclude_file(file_path):
                            continue
                        
                        yaml_data = self.extract_yaml_from_qmd(file_path)
                        if not yaml_data:
                            continue
                        
                        doc_type = self.detect_document_mode(yaml_data)
                        
                        try:
                            creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                        except:
                            creation_time = datetime.now()
                        
                        rel_path = file_path.relative_to(self.base_path)
                        
                        index_files.append({
                            'blog_nombre': blog_dir.name,
                            'ruta_archivo': str(rel_path),
                            'tipo_documento': doc_type,
                            'fecha_creacion': creation_time,
                            'titulo': yaml_data.get('title', ''),
                            'draft': yaml_data.get('draft', True)
                        })
        
        df = pd.DataFrame(index_files)
        
        if not df.empty:
            df = df.sort_values(['blog_nombre', 'tipo_documento', 'fecha_creacion'], 
                              ascending=[True, True, False])
        
        return df
    
    def create_excel_template(self, output_filename: str, blog_name: Optional[str] = None):
        """Crea una plantilla Excel con los archivos index.qmd encontrados"""
        print("🔍 Recolectando archivos index.qmd...")
        df_files = self.collect_index_files(blog_name)
        
        if df_files.empty:
            print("⚠️  No se encontraron archivos index.qmd")
            return
        
        print(f"✅ Se encontraron {len(df_files)} archivos")
        
        # Ruta completa de salida
        output_path = self.excel_output_dir / output_filename
        
        wb = Workbook()
        wb.remove(wb.active)
        
        for doc_type in sorted(df_files['tipo_documento'].unique()):
            df_type = df_files[df_files['tipo_documento'] == doc_type]
            
            ws = wb.create_sheet(f"{doc_type.upper()}")
            
            columns = self.COMMON_FIELDS.copy()
            columns.extend(self.AUTHOR_FIELDS)
            columns.extend(self.SPECIFIC_FIELDS.get(doc_type, []))
            
            # Encabezados
            for col_idx, col_name in enumerate(columns, 1):
                cell = ws.cell(1, col_idx, col_name)
                cell.font = Font(bold=True, color='FFFFFF')
                cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # Datos
            for row_idx, (_, row_data) in enumerate(df_type.iterrows(), 2):
                ws.cell(row_idx, 1, row_data['ruta_archivo'])
                ws.cell(row_idx, 2, row_data['blog_nombre'])
                ws.cell(row_idx, 3, row_data['tipo_documento'])
                
                file_path = self.base_path / row_data['ruta_archivo']
                yaml_data = self.extract_yaml_from_qmd(file_path)
                
                if yaml_data:
                    self._fill_excel_row_from_yaml(ws, row_idx, yaml_data, columns)
            
            # Ajustar columnas
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max(max_length + 2, 15), 60)
                ws.column_dimensions[column].width = adjusted_width
            
            ws.freeze_panes = 'A2'
        
        self._create_instructions_sheet(wb)
        
        wb.save(output_path)
        print(f"\n✅ Plantilla Excel creada: {output_path}")
        print(f"📊 Total de archivos: {len(df_files)}")
        print(f"📁 Hojas creadas: {', '.join([ws.title for ws in wb.worksheets if ws.title != 'INSTRUCCIONES'])}")
        print(f"\n💡 Próximos pasos:")
        print(f"   1. Abrir el archivo: {output_path}")
        print(f"   2. Editar los metadatos en las hojas correspondientes")
        print(f"   3. Guardar el archivo")
        print(f"   4. Ejecutar: python quarto_metadata_manager.py update {self.base_path} {output_path}")
    
    def _create_instructions_sheet(self, wb: Workbook):
        """Crea hoja de instrucciones con formato compatible con LibreOffice"""
        ws = wb.create_sheet("INSTRUCCIONES", 0)
        
        instructions = [
            ["=== GUIA DE USO DEL SISTEMA DE GESTION DE METADATOS ==="],
            [""],
            [">>> INSTRUCCIONES GENERALES <<<"],
            [""],
            ["1. NO MODIFICAR estas columnas (son de solo lectura):"],
            ["   - ruta_archivo: Ubicacion del archivo"],
            ["   - blog_nombre: Nombre del blog"],
            ["   - tipo_documento: Tipo (STU/MAN/JOU/DOC)"],
            [""],
            ["2. EDITAR libremente las demas columnas segun necesidad"],
            [""],
            ["3. Para AGREGAR nuevos articulos:"],
            ["   - Ejecutar: python quarto_metadata_manager.py create-template [ruta]"],
            ["   - Esto actualizará el Excel con nuevos archivos"],
            [""],
            ["4. Para APLICAR cambios:"],
            ["   - Guardar este archivo Excel"],
            ["   - Ejecutar: python quarto_metadata_manager.py update [ruta] [excel]"],
            [""],
            ["========================================================================"],
            [""],
            [">>> FORMATO DE CAMPOS <<<"],
            [""],
            ["Campos TRUE/FALSE (booleanos):"],
            ["   - Escribir: TRUE o FALSE (mayusculas)"],
            ["   - Ejemplo: draft = TRUE"],
            ["   - Ejemplo: eval = FALSE"],
            [""],
            ["Campos de lista (separados por comas):"],
            ["   - keywords: ciencia, tecnologia, innovacion"],
            ["   - tags: python, analisis, datos"],
            ["   - categories: Tutorial, Programación"],
            [""],
            ["Fechas:"],
            ["   - Formato: MM/DD/YYYY o YYYY-MM-DD"],
            ["   - Ejemplo: 12/19/2025 o 2025-12-19"],
            [""],
            ["Links (JSON):"],
            ["   - links_enabled: TRUE o FALSE"],
            ["   - links_data: [{'icon': 'github', 'name': 'Repo', 'url': 'https://...'}]"],
            [""],
            ["========================================================================"],
            [""],
            [">>> CAMPOS OBLIGATORIOS <<<"],
            [""],
            ["IDENTIFICACIÓN:"],
            ["  • title: Título principal del documento"],
            ["  • shorttitle: Título corto para encabezado (máx 50 caracteres)"],
            ["  • subtitle: Subtítulo (opcional)"],
            [""],
            ["PUBLICACIÓN:"],
            ["  • date: Fecha de publicación (MM/DD/YYYY)"],
            ["  • draft: TRUE/FALSE (TRUE = borrador, no se publica)"],
            [""],
            ["DESCRIPCIÓN:"],
            ["  • abstract: Resumen académico (máx 250 palabras)"],
            ["  • description: Descripción breve para web/SEO"],
            [""],
            ["CLASIFICACIÓN:"],
            ["  • keywords: Palabras clave (3-5 recomendadas, separadas por comas)"],
            ["  • tags: Etiquetas/tags (separadas por comas)"],
            ["  • categories: Categorías del contenido (separadas por comas)"],
            [""],
            ["MEDIOS:"],
            ["  • image: Nombre del archivo de imagen (ej: featured.png)"],
            [""],
            ["CÓDIGO:"],
            ["  • eval: TRUE/FALSE (evaluar bloques de código)"],
            [""],
            ["CITACIÓN:"],
            ["  • citation_type: Tipo (article-journal, book, etc.)"],
            ["  • citation_author: Autor(es) para cita"],
            ["  • citation_pdf_url: URL del PDF"],
            [""],
            ["ENLACES:"],
            ["  • links_enabled: TRUE/FALSE (activar enlaces adicionales)"],
            ["  • links_data: Datos JSON de enlaces (si enabled=TRUE)"],
            [""],
            ["BIBLIOGRAFÍA:"],
            ["  • bibliography: Archivo .bib (ej: referencias.bib)"],
            [""],
            ["========================================================================"],
            [""],
            [">>> CAMPOS POR TIPO DE DOCUMENTO <<<"],
            [""],
            ["--- MODO ESTUDIANTE (STU) ---"],
            ["Uso: Trabajos academicos, tareas"],
            [""],
            ["  * course: Metodología de la Investigación (ECON 101)"],
            ["  * professor: Dr. Edison Achalma"],
            ["  * duedate: 12/25/2025"],
            ["  * note: Código de estudiante: 2020123456\\nSección: A"],
            [""],
            ["--- MODO REVISTA (JOU) ---"],
            ["Uso: Articulos publicados"],
            [""],
            ["  * journal: Revista Peruana de Economía"],
            ["  * volume: 2025, Vol. 7, No. 1, 1--25"],
            ["  * copyrightnotice: Año copyright"],
            ["  * copyrightext: Universidad Nacional de San Cristóbal de Huamanga"],
            [""],
            ["--- MODO MANUSCRITO (MAN) ---"],
            ["Uso: Manuscritos para envío a revistas, artículos formales"],
            [""],
            ["  • floatsintext: TRUE/FALSE"],
            ["    TRUE = Figuras/tablas en el texto"],
            ["    FALSE = Figuras/tablas al final (estándar para envío)"],
            [""],
            ["  • numbered_lines: TRUE/FALSE"],
            ["    TRUE = Numerar líneas (útil para revisión)"],
            ["    FALSE = Sin números de línea"],
            [""],
            ["  • meta_analysis: TRUE/FALSE"],
            ["    TRUE = Incluye meta-análisis"],
            ["    FALSE = No incluye meta-análisis"],
            [""],
            ["  • mask: TRUE/FALSE"],
            ["    TRUE = Ocultar info de autores (revisión ciega)"],
            ["    FALSE = Mostrar info completa"],
            [""],
            ["--- MODO DOCUMENTO (DOC) ---"],
            ["Uso: Documentos generales, informes, ensayos, working papers"],
            [""],
            ["  • floatsintext: TRUE/FALSE"],
            ["    TRUE = Figuras/tablas en el texto (recomendado)"],
            ["    FALSE = Figuras/tablas al final"],
            [""],
            ["  • numbered_lines: TRUE/FALSE"],
            ["    TRUE = Numerar líneas (útil para borradores)"],
            ["    FALSE = Sin números de línea"],
            [""],
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            [">>> AUTORES <<<"],
            [""],
            ["Se proporcionan campos para hasta 3 autores principales."],
            ["Para cada autor (1, 2, 3):"],
            [""],
            ["  • author_N_name: Nombre completo"],
            ["  • author_N_corresponding: TRUE/FALSE (solo UNO puede ser TRUE)"],
            ["  • author_N_orcid: ID ORCID (formato: 0000-0002-XXXX-XXXX)"],
            ["  • author_N_email: Email de contacto"],
            ["  • author_N_affiliation_name: Institución"],
            ["  • author_N_affiliation_department: Departamento/Facultad"],
            ["  • author_N_affiliation_city: Ciudad"],
            ["  • author_N_affiliation_region: Región/Estado"],
            ["  • author_N_affiliation_country: País"],
            ["  • author_N_roles: Roles CRediT (separados por comas)"],
            [""],
            ["Ejemplo de roles CRediT:"],
            ["  conceptualization, methodology, writing, analysis"],
            [""],
            ["========================================================================"],
            [""],
            [">>> PRECAUCIONES <<<"],
            [""],
            ["1. SIEMPRE hacer backup antes de actualizar"],
            ["2. Probar primero con --dry-run"],
            ["3. NO modificar carpetas _site o _freeze"],
            ["4. Verificar formato de booleanos (TRUE/FALSE)"],
            ["5. Separar listas con comas"],
            ["6. Guardar como .xlsx (no .xls ni .csv)"],
            [""],
            ["========================================================================"],
            [""],
            [">>> COMANDOS UTILES <<<"],
            [""],
            ["Ver cambios sin aplicar:"],
            ["  python quarto_metadata_manager.py update [ruta] [excel] --dry-run"],
            [""],
            ["Actualizar solo un blog:"],
            ["  python quarto_metadata_manager.py update [ruta] [excel] --blog axiomata"],
            [""],
            ["========================================================================"],
            [""],
            ["Autor: Edison Achalma"],
            ["Email: achalmaedison@gmail.com"],
            ["Version: 1.1.0"],
        ]
        
        for row_idx, instruction in enumerate(instructions, 1):
            cell = ws.cell(row_idx, 1, instruction[0])
            if row_idx == 1:
                cell.font = Font(bold=True, size=14, color='FFFFFF')
                cell.fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
            elif "===" in instruction[0] or ">>>" in instruction[0] or "---" in instruction[0]:
                cell.font = Font(bold=True, color='1F4E78')
        
        ws.column_dimensions['A'].width = 90
    
    def _fill_excel_row_from_yaml(self, ws, row_idx: int, yaml_data: Dict, columns: List[str]):
        """Llena fila de Excel con datos del YAML"""
        for col_idx, col_name in enumerate(columns, 1):
            try:
                value = self._extract_yaml_value(yaml_data, col_name)
                if value is not None:
                    ws.cell(row_idx, col_idx, value)
            except Exception as e:
                print(f"⚠️  Error extrayendo {col_name}: {e}")
                continue
    
    def _extract_yaml_value(self, yaml_data: Dict, field_name: str) -> Any:
        """Extrae valor del YAML con manejo robusto de tipos"""
        simple_mapping = {
            'title': 'title',
            'shorttitle': 'shorttitle',
            'subtitle': 'subtitle',
            'date': 'date',
            'draft': 'draft',
            'abstract': 'abstract',
            'description': 'description',
            'image': 'image',
            'eval': 'eval',
            'bibliography': 'bibliography',
            'course': 'course',
            'professor': 'professor',
            'duedate': 'duedate',
            'note': 'note',
            'journal': 'journal',
            'volume': 'volume',
            'copyrightnotice': 'copyrightnotice',
            'copyrightext': 'copyrightext',
            'floatsintext': 'floatsintext',
            'numbered_lines': 'numbered-lines',
            'meta_analysis': 'meta-analysis',
            'mask': 'mask'
        }
        
        if field_name in simple_mapping:
            return yaml_data.get(simple_mapping[field_name])
        
        # Listas
        if field_name in ['keywords', 'tags', 'categories']:
            value = yaml_data.get(field_name, [])
            if isinstance(value, list):
                return ', '.join([str(v) for v in value])
            return value
        
        # Citation - CORREGIDO para manejar bool
        if field_name.startswith('citation_'):
            citation = yaml_data.get('citation')
            
            # Si citation es bool o None, retornar None
            if not isinstance(citation, dict):
                return None
            
            if field_name == 'citation_type':
                return citation.get('type')
            elif field_name == 'citation_author':
                authors = citation.get('author', [])
                if isinstance(authors, list):
                    return ', '.join([str(a) for a in authors])
                return authors
            elif field_name == 'citation_pdf_url':
                return citation.get('pdf-url')
        
        # Links
        if field_name == 'links_enabled':
            links = yaml_data.get('links')
            return links is not None and links != False
        elif field_name == 'links_data':
            links = yaml_data.get('links')
            if links and isinstance(links, (list, dict)):
                return json.dumps(links, ensure_ascii=False)
        
        # Author fields
        if field_name.startswith('author_'):
            match = re.match(r'author_(\d+)_(.*)', field_name)
            if match:
                author_idx = int(match.group(1)) - 1
                field_suffix = match.group(2)
                
                authors = yaml_data.get('author', [])
                if not isinstance(authors, list) or author_idx >= len(authors):
                    return None
                
                author = authors[author_idx]
                
                if field_suffix == 'name':
                    return author.get('name')
                elif field_suffix == 'corresponding':
                    return author.get('corresponding')
                elif field_suffix == 'orcid':
                    return author.get('orcid')
                elif field_suffix == 'email':
                    return author.get('email')
                elif field_suffix == 'roles':
                    roles = author.get('role', [])
                    if isinstance(roles, list):
                        return ', '.join([str(r) for r in roles])
                    return roles
                elif field_suffix.startswith('affiliation_'):
                    aff_field = field_suffix.replace('affiliation_', '')
                    affiliations = author.get('affiliations', [])
                    if affiliations and isinstance(affiliations, list):
                        # Buscar en la primera afiliación que sea un dict
                        for aff in affiliations:
                            if isinstance(aff, dict):
                                return aff.get(aff_field)
        
        return None
    
    def update_yaml_from_excel(self, excel_path: str, blog_filter: Optional[str] = None, 
                              dry_run: bool = False):
        """Actualiza archivos index.qmd desde el Excel con preservación de formato YAML"""
        print(f"📖 Leyendo Excel: {excel_path}")
        
        try:
            xl_file = pd.ExcelFile(excel_path)
        except Exception as e:
            print(f"❌ Error leyendo Excel: {e}")
            return
        
        total_updated = 0
        total_skipped = 0
        total_errors = 0
        
        for sheet_name in xl_file.sheet_names:
            if sheet_name == 'INSTRUCCIONES':
                continue
            
            print(f"\n📄 Procesando hoja: {sheet_name}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            if df.empty:
                print("  ⚠️  Hoja vacía")
                continue
            
            if blog_filter:
                df = df[df['blog_nombre'] == blog_filter]
                if df.empty:
                    print(f"  ⚠️  No hay archivos del blog '{blog_filter}' en esta hoja")
                    continue
            
            for idx, row in df.iterrows():
                ruta_archivo = row.get('ruta_archivo')
                if pd.isna(ruta_archivo):
                    continue
                
                file_path = self.base_path / ruta_archivo
                
                if not file_path.exists():
                    print(f"  ❌ Archivo no encontrado: {ruta_archivo}")
                    total_errors += 1
                    continue
                
                try:
                    result = self._update_single_qmd(file_path, row, dry_run)
                    if result:
                        total_updated += 1
                    else:
                        total_skipped += 1
                except Exception as e:
                    print(f"  ❌ Error actualizando {ruta_archivo}: {e}")
                    total_errors += 1
        
        print(f"\n{'🔍 SIMULACION' if dry_run else '✅ ACTUALIZACION'} COMPLETADA")
        print(f"  📝 Actualizados: {total_updated}")
        print(f"  ⏭️  Omitidos: {total_skipped}")
        print(f"  ❌ Errores: {total_errors}")
        
        if dry_run and total_updated > 0:
            print(f"\n💡 Para aplicar los cambios, ejecute sin --dry-run")
    
    def _update_single_qmd(self, file_path: Path, row: pd.Series, dry_run: bool) -> bool:
        """Actualiza un solo archivo .qmd preservando formato"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            return False
        
        yaml_content = yaml_match.group(1)
        yaml_data = yaml.safe_load(yaml_content) or {}
        
        changes = []
        updated_yaml = self._apply_excel_row_to_yaml(yaml_data, row, changes)
        
        if not changes:
            return False
        
        print(f"  📝 {'Simulando' if dry_run else 'Actualizando'}: {file_path.name}")
        for change in changes[:5]:  # Mostrar solo primeros 5 cambios
            print(f"     • {change}")
        if len(changes) > 5:
            print(f"     ... y {len(changes) - 5} cambios más")
        
        if dry_run:
            return True
        
        # Generar YAML con mejor formato
        new_yaml_str = yaml.dump(
            updated_yaml, 
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=80
        )
        
        new_content = f"---\n{new_yaml_str}---{content[yaml_match.end():]}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    def _apply_excel_row_to_yaml(self, yaml_data: Dict, row: pd.Series, 
                                changes: List[str]) -> Dict:
        """Aplica cambios de una fila Excel a un diccionario YAML"""

        # Campos simples
        simple_fields = {
            'title': 'title',
            'shorttitle': 'shorttitle',
            'subtitle': 'subtitle',
            'date': 'date',
            'draft': 'draft',
            'abstract': 'abstract',
            'description': 'description',
            'image': 'image',
            'eval': 'eval',
            'bibliography': 'bibliography',
            'course': 'course',
            'professor': 'professor',
            'duedate': 'duedate',
            'note': 'note',
            'journal': 'journal',
            'volume': 'volume',
            'copyrightnotice': 'copyrightnotice',
            'copyrightext': 'copyrightext',
            'floatsintext': 'floatsintext',
            'mask': 'mask'
        }
        
        for excel_field, yaml_field in simple_fields.items():
            if excel_field in row and not pd.isna(row[excel_field]):
                new_value = row[excel_field]
                old_value = yaml_data.get(yaml_field)

                # Convertir booleanos
                if isinstance(new_value, str) and new_value.upper() in ['TRUE', 'FALSE']:
                    new_value = new_value.upper() == 'TRUE'
                
                if old_value != new_value:
                    yaml_data[yaml_field] = new_value
                    changes.append(f"{yaml_field}: {old_value} → {new_value}")
        
        # Campos con guiones
        if 'numbered_lines' in row and not pd.isna(row['numbered_lines']):
            new_value = row['numbered_lines']
            if isinstance(new_value, str):
                new_value = new_value.upper() == 'TRUE'
            old_value = yaml_data.get('numbered-lines')
            if old_value != new_value:
                yaml_data['numbered-lines'] = new_value
                changes.append(f"numbered-lines: {old_value} → {new_value}")
        
        if 'meta_analysis' in row and not pd.isna(row['meta_analysis']):
            new_value = row['meta_analysis']
            if isinstance(new_value, str):
                new_value = new_value.upper() == 'TRUE'
            old_value = yaml_data.get('meta-analysis')
            if old_value != new_value:
                yaml_data['meta-analysis'] = new_value
                changes.append(f"meta-analysis: {old_value} → {new_value}")
        
        # Listas
        for field in ['keywords', 'tags', 'categories']:
            if field in row and not pd.isna(row[field]):
                if isinstance(row[field], str):
                    new_value = [item.strip() for item in row[field].split(',') if item.strip()]
                else:
                    new_value = [str(row[field])]
                
                old_value = yaml_data.get(field, [])
                if old_value != new_value:
                    yaml_data[field] = new_value
                    changes.append(f"{field}: actualizado")
        
        # Citation
        if 'citation_type' in row and not pd.isna(row['citation_type']):
            if 'citation' not in yaml_data or not isinstance(yaml_data['citation'], dict):
                yaml_data['citation'] = {}
            new_type = row['citation_type']
            old_type = yaml_data['citation'].get('type')
            if old_type != new_type:
                yaml_data['citation']['type'] = new_type
                changes.append(f"citation.type: {old_type} → {new_type}")
        
        if 'citation_pdf_url' in row and not pd.isna(row['citation_pdf_url']):
            if 'citation' not in yaml_data or not isinstance(yaml_data['citation'], dict):
                yaml_data['citation'] = {}
            new_url = row['citation_pdf_url']
            old_url = yaml_data['citation'].get('pdf-url')
            if old_url != new_url:
                yaml_data['citation']['pdf-url'] = new_url
                changes.append(f"citation.pdf-url actualizada")
        
        # Authors (hasta 3 autores)
        authors_data = []
        for i in range(1, 4):
            prefix = f'author_{i}_'
            if f'{prefix}name' in row and not pd.isna(row[f'{prefix}name']):
                author = {'name': row[f'{prefix}name']}
                
                if f'{prefix}corresponding' in row and not pd.isna(row[f'{prefix}corresponding']):
                    corr_val = row[f'{prefix}corresponding']
                    if isinstance(corr_val, str):
                        corr_val = corr_val.upper() == 'TRUE'
                    author['corresponding'] = corr_val
                
                if f'{prefix}orcid' in row and not pd.isna(row[f'{prefix}orcid']):
                    author['orcid'] = row[f'{prefix}orcid']
                
                if f'{prefix}email' in row and not pd.isna(row[f'{prefix}email']):
                    author['email'] = row[f'{prefix}email']
                
                # Afiliación
                aff = {}
                for aff_field in ['name', 'department', 'city', 'region', 'country']:
                    full_field = f'{prefix}affiliation_{aff_field}'
                    if full_field in row and not pd.isna(row[full_field]):
                        aff[aff_field] = row[full_field]
                
                if aff:
                    author['affiliations'] = [aff]
                
                # Roles
                if f'{prefix}roles' in row and not pd.isna(row[f'{prefix}roles']):
                    roles_str = row[f'{prefix}roles']
                    if isinstance(roles_str, str):
                        author['role'] = [r.strip() for r in roles_str.split(',')]
                
                authors_data.append(author)
        
        if authors_data:
            old_authors = yaml_data.get('author', [])
            yaml_data['author'] = authors_data
            if old_authors != authors_data:
                changes.append(f"author: actualizado ({len(authors_data)} autores)")
        
        return yaml_data


def create_config_file(config_path: str, base_path: str):
    """Crea archivo de configuración de ejemplo"""
    config = {
        'allowed_blogs': [
            'axiomata',
            'aequilibria',
            'numerus-scriptum',
            'actus-mercator',
            'website-achalma',
            # Agregar más blogs según necesidad
        ],
        'excluded_folders': [
            'apa',
            'notas',
            'borradores',
            'propuesta bicentenario',
            'taller unsch como elaborar tesis de pregrado',
            'practicas preprofesionales',
            # Agregar más carpetas a excluir
        ],
        'excel_output_dir': '~/Documents/scripts/scripts_for_quarto/script_metadata_manager/excel_databases'
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ Archivo de configuración creado: {config_path}")
    print(f"📝 Edítelo para personalizar blogs y carpetas")


def main():
    """Función principal con CLI mejorado"""
    parser = argparse.ArgumentParser(
        description='Sistema de Gestión de Metadatos para Blogs Quarto v1.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Crear archivo de configuración
  python quarto_metadata_manager.py create-config ~/Documents/publicaciones
  
  # Crear plantilla con configuración
  python quarto_metadata_manager.py create-template ~/Documents/publicaciones \\
      --config config.yml
  
  # Crear plantilla para blog específico
  python quarto_metadata_manager.py create-template ~/Documents/publicaciones \\
      --blog axiomata
  
  # Simular actualización
  python quarto_metadata_manager.py update ~/Documents/publicaciones metadata.xlsx \\
      --dry-run
  
  # Actualizar
  python quarto_metadata_manager.py update ~/Documents/publicaciones metadata.xlsx

Autor: Edison Achalma
Versión: 1.1.0
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: create-config
    parser_config = subparsers.add_parser('create-config',
                                         help='Crear archivo de configuración')
    parser_config.add_argument('base_path', help='Ruta base de publicaciones')
    parser_config.add_argument('-o', '--output', default='metadata_config.yml',
                              help='Archivo de configuración')
    
    # Comando: create-template
    parser_create = subparsers.add_parser('create-template', 
                                          help='Crear plantilla Excel')
    parser_create.add_argument('base_path', help='Ruta base de publicaciones')
    parser_create.add_argument('-o', '--output', default='quarto_metadata.xlsx',
                              help='Archivo Excel de salida')
    parser_create.add_argument('-b', '--blog', help='Blog específico')
    parser_create.add_argument('-c', '--config', help='Archivo de configuración')
    
    # Comando: update
    parser_update = subparsers.add_parser('update',
                                         help='Actualizar desde Excel')
    parser_update.add_argument('base_path', help='Ruta base de publicaciones')
    parser_update.add_argument('excel_file', help='Archivo Excel')
    parser_update.add_argument('-b', '--blog', help='Blog específico')
    parser_update.add_argument('-c', '--config', help='Archivo de configuración')
    parser_update.add_argument('--dry-run', action='store_true',
                              help='Simular sin aplicar cambios')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'create-config':
            create_config_file(args.output, args.base_path)
            
        elif args.command == 'create-template':
            config_file = getattr(args, 'config', None)
            manager = QuartoMetadataManager(args.base_path, config_file)
            
            output_path = args.output
            if args.blog:
                name, ext = os.path.splitext(output_path)
                output_path = f"{name}_{args.blog}{ext}"
            
            manager.create_excel_template(output_path, args.blog)
            
        elif args.command == 'update':
            config_file = getattr(args, 'config', None)
            manager = QuartoMetadataManager(args.base_path, config_file)
            manager.update_yaml_from_excel(args.excel_file, args.blog, args.dry_run)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())