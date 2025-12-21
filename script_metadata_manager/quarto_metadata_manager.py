#!/usr/bin/env python3
"""
Sistema de Gestión de Metadatos para Blogs Quarto
Autor: Edison Achalma
Fecha: Diciembre 2024

Este sistema permite administrar metadatos de múltiples blogs Quarto desde archivos Excel.
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import json


class QuartoMetadataManager:
    """Gestor principal de metadatos de blogs Quarto"""
    
    # Carpetas a excluir
    EXCLUDED_FOLDERS = {'_site', '_freeze', 'site_libs', '.git', '.quarto', 
                       'node_modules', '__pycache__', '_extensions'}
    
    # Archivos index.qmd a excluir (sin metadatos relevantes)
    EXCLUDED_INDEX_FILES = {'_contenido-inicio.qmd', '_contenido-final.qmd', 
                           '_contenido_posts.qmd', '_contenido_economia-preuniversitaria.qmd',
                           '_contenido_inteligencia-comercial.qmd', '_contenido_talk.qmd',
                           '_contenido_teching.qmd', '404.qmd',
                           'contact.qmd', 'accessibility.qmd', 'license.qmd'}
    
    # Campos comunes para todos los tipos de documentos (OBLIGATORIOS)
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
    
    def __init__(self, base_path: str):
        """Inicializa el gestor de metadatos"""
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            raise ValueError(f"La ruta base no existe: {base_path}")
    
    def should_exclude_folder(self, folder_path: Path) -> bool:
        """Determina si una carpeta debe ser excluida"""
        parts = folder_path.parts
        return any(excluded in parts for excluded in self.EXCLUDED_FOLDERS)
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Determina si un archivo index.qmd debe ser excluido"""
        return file_path.name in self.EXCLUDED_INDEX_FILES
    
    def extract_yaml_from_qmd(self, file_path: Path) -> Optional[Dict]:
        """Extrae el YAML frontmatter de un archivo .qmd"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                return yaml.safe_load(yaml_content)
            return None
        except Exception as e:
            print(f"Error extrayendo YAML de {file_path}: {e}")
            return None
    
    def detect_document_mode(self, yaml_data: Dict) -> str:
        """Detecta el tipo de documento (stu, man, jou, doc)"""
        if 'format' in yaml_data:
            formats = yaml_data['format']
            if isinstance(formats, dict) and 'apaquarto-pdf' in formats:
                apa_config = formats['apaquarto-pdf']
                if isinstance(apa_config, dict) and 'documentmode' in apa_config:
                    return apa_config['documentmode']
        
        # Detectar por campos específicos
        if 'course' in yaml_data or 'professor' in yaml_data:
            return 'stu'
        elif 'journal' in yaml_data or 'volume' in yaml_data:
            return 'jou'
        elif 'meta-analysis' in yaml_data:
            return 'man'
        
        return 'doc'
    
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
            blogs_to_process = [d for d in self.base_path.iterdir() 
                              if d.is_dir() and not d.name.startswith('.')]
        
        for blog_dir in blogs_to_process:
            print(f"📂 Procesando blog: {blog_dir.name}")
            
            for root, dirs, files in os.walk(blog_dir):
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
                            'draft': yaml_data.get('draft', False)
                        })
        
        df = pd.DataFrame(index_files)
        
        if not df.empty:
            df = df.sort_values(['blog_nombre', 'tipo_documento', 'fecha_creacion'], 
                              ascending=[True, True, False])
        
        return df
    
    def create_excel_template(self, output_path: str, blog_name: Optional[str] = None):
        """Crea una plantilla Excel con los archivos index.qmd encontrados"""
        print("🔍 Recolectando archivos index.qmd...")
        df_files = self.collect_index_files(blog_name)
        
        if df_files.empty:
            print("⚠️  No se encontraron archivos index.qmd")
            return
        
        print(f"✅ Se encontraron {len(df_files)} archivos")
        
        wb = Workbook()
        wb.remove(wb.active)
        
        for doc_type in sorted(df_files['tipo_documento'].unique()):
            df_type = df_files[df_files['tipo_documento'] == doc_type]
            
            ws = wb.create_sheet(f"{doc_type.upper()}")
            
            columns = self.COMMON_FIELDS.copy()
            columns.extend(self.AUTHOR_FIELDS)
            columns.extend(self.SPECIFIC_FIELDS.get(doc_type, []))
            
            for col_idx, col_name in enumerate(columns, 1):
                cell = ws.cell(1, col_idx, col_name)
                cell.font = Font(bold=True, color='FFFFFF')
                cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            for row_idx, (_, row_data) in enumerate(df_type.iterrows(), 2):
                ws.cell(row_idx, 1, row_data['ruta_archivo'])
                ws.cell(row_idx, 2, row_data['blog_nombre'])
                ws.cell(row_idx, 3, row_data['tipo_documento'])
                
                file_path = self.base_path / row_data['ruta_archivo']
                yaml_data = self.extract_yaml_from_qmd(file_path)
                
                if yaml_data:
                    self._fill_excel_row_from_yaml(ws, row_idx, yaml_data, columns)
            
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
        """Crea hoja de instrucciones"""
        ws = wb.create_sheet("INSTRUCCIONES", 0)
        
        instructions = [
            ["=== GUÍA DE USO DEL SISTEMA DE GESTIÓN DE METADATOS ==="],
            [""],
            ["📋 INSTRUCCIONES GENERALES"],
            [""],
            ["1. NO MODIFICAR estas columnas (son de solo lectura):"],
            ["   - ruta_archivo: Ubicación del archivo"],
            ["   - blog_nombre: Nombre del blog"],
            ["   - tipo_documento: Tipo (STU/MAN/JOU/DOC)"],
            [""],
            ["2. EDITAR libremente las demás columnas según necesidad"],
            [""],
            ["3. Para AGREGAR nuevos artículos:"],
            ["   - Ejecutar: python quarto_metadata_manager.py create-template [ruta]"],
            ["   - Esto actualizará el Excel con nuevos archivos"],
            [""],
            ["4. Para APLICAR cambios:"],
            ["   - Guardar este archivo Excel"],
            ["   - Ejecutar: python quarto_metadata_manager.py update [ruta] [excel]"],
            [""],
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            ["📝 FORMATO DE CAMPOS"],
            [""],
            ["Campos TRUE/FALSE (booleanos):"],
            ["   - Escribir: TRUE o FALSE (mayúsculas)"],
            ["   - Ejemplo: draft = TRUE"],
            ["   - Ejemplo: eval = FALSE"],
            [""],
            ["Campos de lista (separados por comas):"],
            ["   - keywords: ciencia, tecnología, innovación"],
            ["   - tags: python, análisis, datos"],
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
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            ["📋 CAMPOS OBLIGATORIOS (presentes en todos los tipos)"],
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
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            ["📚 CAMPOS ESPECÍFICOS POR TIPO DE DOCUMENTO"],
            [""],
            ["╔═══════════════════════════════════════════════════════════╗"],
            ["║ MODO ESTUDIANTE (STU)                                     ║"],
            ["╚═══════════════════════════════════════════════════════════╝"],
            ["Uso: Trabajos académicos, tareas, proyectos estudiantiles"],
            [""],
            ["  • course: Nombre del curso"],
            ["    Ejemplo: Metodología de la Investigación (ECON 101)"],
            [""],
            ["  • professor: Nombre del profesor/instructor"],
            ["    Ejemplo: Dr. Edison Achalma"],
            [""],
            ["  • duedate: Fecha de entrega"],
            ["    Ejemplo: 12/25/2025"],
            [""],
            ["  • note: Nota adicional del estudiante"],
            ["    Ejemplo: Código de estudiante: 2020123456\\nSección: A"],
            [""],
            ["╔═══════════════════════════════════════════════════════════╗"],
            ["║ MODO REVISTA (JOU)                                        ║"],
            ["╚═══════════════════════════════════════════════════════════╝"],
            ["Uso: Artículos publicados, formato profesional de revista"],
            [""],
            ["  • journal: Nombre de la revista"],
            ["    Ejemplo: Revista Peruana de Economía"],
            [""],
            ["  • volume: Volumen, número y páginas"],
            ["    Ejemplo: 2025, Vol. 7, No. 1, 1--25"],
            [""],
            ["  • copyrightnotice: Año de copyright"],
            ["    Ejemplo: © 2025"],
            [""],
            ["  • copyrightext: Texto completo de copyright"],
            ["    Ejemplo: Universidad Nacional de San Cristóbal de Huamanga"],
            [""],
            ["╔═══════════════════════════════════════════════════════════╗"],
            ["║ MODO MANUSCRITO (MAN)                                     ║"],
            ["╚═══════════════════════════════════════════════════════════╝"],
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
            ["╔═══════════════════════════════════════════════════════════╗"],
            ["║ MODO DOCUMENTO (DOC)                                      ║"],
            ["╚═══════════════════════════════════════════════════════════╝"],
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
            ["👥 CAMPOS DE AUTORES"],
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
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            ["⚠️  PRECAUCIONES"],
            [""],
            ["1. SIEMPRE hacer backup antes de actualizar"],
            ["2. Probar primero con --dry-run para ver cambios"],
            ["3. NO modificar archivos en carpetas _site o _freeze"],
            ["4. Verificar formato de fechas y booleanos"],
            ["5. Las listas deben separarse con comas"],
            ["6. Guardar en formato .xlsx (no .xls ni .csv)"],
            [""],
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            ["🔧 COMANDOS ÚTILES"],
            [""],
            ["Ver cambios sin aplicar:"],
            ["  python quarto_metadata_manager.py update [ruta] [excel] --dry-run"],
            [""],
            ["Actualizar solo un blog:"],
            ["  python quarto_metadata_manager.py update [ruta] [excel] --blog axiomata"],
            [""],
            ["Crear template solo para un blog:"],
            ["  python quarto_metadata_manager.py create-template [ruta] --blog axiomata"],
            [""],
            ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
            [""],
            ["📞 SOPORTE"],
            [""],
            ["Si encuentra problemas:"],
            ["1. Verificar que el formato de los datos sea correcto"],
            ["2. Revisar la salida del comando para mensajes de error"],
            ["3. Usar --dry-run para diagnosticar problemas"],
            ["4. Consultar la documentación de Quarto/Apaquarto"],
            [""],
            ["Autor: Edison Achalma"],
            ["Email: achalmaedison@gmail.com"],
            ["Versión: 1.0.0"],
        ]
        
        for row_idx, instruction in enumerate(instructions, 1):
            cell = ws.cell(row_idx, 1, instruction[0])
            if row_idx == 1:
                cell.font = Font(bold=True, size=14, color='FFFFFF')
                cell.fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
            elif "═══" in instruction[0] or "━━━" in instruction[0]:
                cell.font = Font(bold=True, color='1F4E78')
            elif instruction[0].startswith("  •") or instruction[0].startswith("  -"):
                cell.font = Font(color='333333')
        
        ws.column_dimensions['A'].width = 90
    
    def _fill_excel_row_from_yaml(self, ws, row_idx: int, yaml_data: Dict, columns: List[str]):
        """Llena una fila de Excel con datos del YAML"""
        for col_idx, col_name in enumerate(columns, 1):
            value = self._extract_yaml_value(yaml_data, col_name)
            if value is not None:
                ws.cell(row_idx, col_idx, value)
    
    def _extract_yaml_value(self, yaml_data: Dict, field_name: str) -> Any:
        """Extrae un valor específico del YAML"""
        # Campos simples directos
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
        
        # Citation
        if field_name.startswith('citation_'):
            citation = yaml_data.get('citation', {})
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
            return 'links' in yaml_data and yaml_data['links'] is not None
        elif field_name == 'links_data':
            links = yaml_data.get('links')
            if links:
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
        """Actualiza archivos index.qmd desde el Excel"""
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
        
        print(f"\n{'🔍 SIMULACIÓN' if dry_run else '✅ ACTUALIZACIÓN'} COMPLETADA")
        print(f"  📝 Actualizados: {total_updated}")
        print(f"  ⏭️  Omitidos: {total_skipped}")
        print(f"  ❌ Errores: {total_errors}")
        
        if dry_run and total_updated > 0:
            print(f"\n💡 Para aplicar los cambios, ejecute sin --dry-run")
    
    def _update_single_qmd(self, file_path: Path, row: pd.Series, dry_run: bool) -> bool:
        """Actualiza un solo archivo .qmd"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            print(f"  ⚠️  No se encontró YAML en: {file_path.name}")
            return False
        
        yaml_content = yaml_match.group(1)
        yaml_data = yaml.safe_load(yaml_content)
        
        changes = []
        updated_yaml = self._apply_excel_row_to_yaml(yaml_data, row, changes)
        
        if not changes:
            # print(f"  ⏭️  Sin cambios: {file_path.name}")
            return False
        
        print(f"  📝 {'Simulando' if dry_run else 'Actualizando'}: {file_path.name}")
        for change in changes[:5]:  # Mostrar solo primeros 5 cambios
            print(f"     • {change}")
        if len(changes) > 5:
            print(f"     ... y {len(changes) - 5} cambios más")
        
        if dry_run:
            return True
        
        new_yaml_str = yaml.dump(updated_yaml, allow_unicode=True, 
                                default_flow_style=False, sort_keys=False)
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
            if 'citation' not in yaml_data:
                yaml_data['citation'] = {}
            new_type = row['citation_type']
            old_type = yaml_data['citation'].get('type')
            if old_type != new_type:
                yaml_data['citation']['type'] = new_type
                changes.append(f"citation.type: {old_type} → {new_type}")
        
        if 'citation_pdf_url' in row and not pd.isna(row['citation_pdf_url']):
            if 'citation' not in yaml_data:
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


def main():
    """Función principal con CLI"""
    parser = argparse.ArgumentParser(
        description='Sistema de Gestión de Metadatos para Blogs Quarto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Crear plantilla Excel para todos los blogs
  python quarto_metadata_manager.py create-template /ruta/publicaciones

  # Crear plantilla solo para un blog
  python quarto_metadata_manager.py create-template /ruta/publicaciones --blog axiomata

  # Simular actualización (ver cambios sin aplicar)
  python quarto_metadata_manager.py update /ruta/publicaciones metadata.xlsx --dry-run

  # Actualizar metadatos desde Excel
  python quarto_metadata_manager.py update /ruta/publicaciones metadata.xlsx

  # Actualizar solo un blog
  python quarto_metadata_manager.py update /ruta/publicaciones metadata.xlsx --blog axiomata

Autor: Edison Achalma
Versión: 1.0.0
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: create-template
    parser_create = subparsers.add_parser('create-template', 
                                          help='Crear plantilla Excel')
    parser_create.add_argument('base_path', help='Ruta base de publicaciones')
    parser_create.add_argument('-o', '--output', default='quarto_metadata.xlsx',
                              help='Archivo Excel de salida')
    parser_create.add_argument('-b', '--blog', help='Blog específico (opcional)')
    
    # Comando: update
    parser_update = subparsers.add_parser('update',
                                         help='Actualizar desde Excel')
    parser_update.add_argument('base_path', help='Ruta base de publicaciones')
    parser_update.add_argument('excel_file', help='Archivo Excel')
    parser_update.add_argument('-b', '--blog', help='Blog específico (opcional)')
    parser_update.add_argument('--dry-run', action='store_true',
                              help='Simular sin aplicar cambios')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = QuartoMetadataManager(args.base_path)
        
        if args.command == 'create-template':
            output_path = args.output
            if args.blog:
                name, ext = os.path.splitext(output_path)
                output_path = f"{name}_{args.blog}{ext}"
            
            manager.create_excel_template(output_path, args.blog)
            
        elif args.command == 'update':
            manager.update_yaml_from_excel(args.excel_file, args.blog, args.dry_run)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
