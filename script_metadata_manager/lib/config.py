"""
lib/config.py
=============
Constantes globales, lista de campos, carpetas/archivos excluidos
y carga del archivo metadata_config.yml.

Todos los demás módulos importan sus constantes desde aquí.
Nada en este archivo depende de otros módulos del proyecto.
"""

from pathlib import Path
from typing import Dict, Optional
import yaml


# =============================================================================
# VERSIÓN
# =============================================================================
VERSION = "2.0.0"
AUTHOR  = "Edison Achalma"
EMAIL   = "elmer.achalma.09@unsch.edu.pe"


# =============================================================================
# CARPETAS Y ARCHIVOS EXCLUIDOS
# =============================================================================

# Carpetas del sistema que NUNCA se procesan
SYSTEM_EXCLUDED_FOLDERS = {
    "_site", "_freeze", "site_libs", ".git", ".quarto",
    "node_modules", "__pycache__", "_extensions", ".venv",
    "venv", "env", "assets", "_partials",
    "title-block-link-buttons", "Excalidraw",
}

# Archivos index.qmd que son configuración (no artículos)
EXCLUDED_INDEX_FILES = {
    "_contenido-inicio.qmd", "_contenido-final.qmd",
    "_contenido_posts.qmd", "_contenido_economia-preuniversitaria.qmd",
    "_contenido_inteligencia-comercial.qmd", "_contenido_talk.qmd",
    "_contenido_teching.qmd", "404.qmd", "contact.qmd",
    "accessibility.qmd", "license.qmd", "_index.md", "index.md",
}

# Directorios que se reconocen como "secciones" (no artículos)
SECTION_DIRS = {
    "blog", "posts", "talk", "teching", "publication",
    "about", "beschikbaarheid", "appointment",
}


# =============================================================================
# CAMPOS DE LA PLANTILLA EXCEL (ALL_FIELDS)
# =============================================================================
ALL_FIELDS = [
    # Identificadores (solo lectura en Excel)
    "ruta_archivo", "blog_nombre", "tipo_documento",
    # Título
    "title", "shorttitle", "subtitle",
    # Publicación
    "date", "draft",
    # Contenido
    "abstract", "description",
    # Clasificación
    "keywords", "tags", "categories",
    # Media y código
    "image", "eval",
    # Referencias
    "bibliography",
    # Citación
    "citation_type", "citation_author", "citation_pdf_url",
    # Links
    "links_enabled", "links_data",
    # Específicos STU
    "course", "professor", "duedate", "note",
    # Específicos JOU
    "journal", "volume", "copyrightnotice", "copyrightext",
    # Específicos MAN/DOC
    "floatsintext", "numbered_lines", "meta_analysis", "mask",
    # Autor 1
    "author_1_name", "author_1_corresponding", "author_1_orcid",
    "author_1_email", "author_1_affiliation_name",
    "author_1_affiliation_department", "author_1_affiliation_city",
    "author_1_affiliation_region", "author_1_affiliation_country",
    "author_1_roles",
    # Autor 2
    "author_2_name", "author_2_orcid",
    "author_2_affiliation_name", "author_2_roles",
    # Autor 3
    "author_3_name", "author_3_orcid",
    "author_3_affiliation_name", "author_3_roles",
]

# Orden en que se escriben los campos en el YAML resultante
YAML_FIELD_ORDER = [
    "documentmode", "course", "professor", "duedate", "note",
    "journal", "volume", "copyrightnotice", "copyrightext",
    "image", "title", "subtitle", "shorttitle", "abstract",
    "keywords", "categories", "tags", "author-note", "description",
    "eval", "citation", "date", "draft", "bibliography",
    "floatsintext", "numbered-lines", "meta-analysis", "mask", "author",
]


# =============================================================================
# CARGA DE CONFIGURACIÓN
# =============================================================================

def load_config(config_file: Optional[str]) -> Dict:
    """
    Carga el archivo metadata_config.yml (si existe).
    Devuelve dict vacío si no hay archivo o hay error de parsing.
    """
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Error leyendo configuración {config_file}: {e}")
    return {}


def create_default_config(base_path: str, output_path: str = "metadata_config.yml"):
    """
    Genera un metadata_config.yml con valores sensatos para el entorno de Edison.
    Actualiza los nombres de blogs al formato pub_* actual.
    """
    config = {
        "allowed_blogs": [
            "pub_actus-mercator", "pub_aequilibria", "pub_axiomata",
            "pub_chaska", "pub_dialectica-y-mercado", "pub_epsilon-y-beta",
            "pub_methodica", "pub_numerus-scriptum", "pub_optimums",
            "pub_pecunia-fluxus", "pub_res-publica",
            "website-achalma",
        ],
        "excluded_folders": [
            "apa", "notas", "borradores",
            "propuesta bicentenario",
            "taller unsch como elaborar tesis de pregrado",
            "practicas preprofesionales",
        ],
        "excel_output_dir": (
            "~/Documents/scripts/scripts_for_quarto/"
            "script_metadata_manager/excel_databases"
        ),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"✅ Configuración creada: {output_path}")
    print("   Edita allowed_blogs y excluded_folders según tu entorno")
