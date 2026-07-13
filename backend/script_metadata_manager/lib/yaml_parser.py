"""
lib/yaml_parser.py
==================
Lectura, extracción y fusión de YAML desde archivos index.qmd y
_metadata.yml.  También detecta el tipo de documento (stu/man/jou/doc).

No toca Excel ni el sistema de archivos más allá de leer ficheros .qmd/.yml.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Set

import yaml

from .config import SECTION_DIRS


# =============================================================================
# LECTURA YAML DESDE ARCHIVOS
# =============================================================================

def read_yaml_from_file(file_path: Path) -> Optional[Dict]:
    """
    Lee y parsea un archivo YAML puro (como _metadata.yml).
    Devuelve None si hay error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️  Error leyendo {file_path.name}: {e}")
        return None


def extract_frontmatter(file_path: Path) -> Optional[str]:
    """
    Extrae el bloque YAML (entre --- y ---) de un archivo .qmd.
    Devuelve el string crudo del YAML, o None si no hay frontmatter.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        return match.group(1) if match else None
    except Exception as e:
        print(f"⚠️  Error leyendo {file_path.name}: {e}")
        return None


def parse_frontmatter(raw: str) -> Optional[Dict]:
    """Parsea un string de YAML en un dict. Devuelve None si falla."""
    try:
        return yaml.safe_load(raw) or {}
    except Exception as e:
        print(f"⚠️  Error parseando YAML: {e}")
        return None


# =============================================================================
# EXTRACCIÓN CON / SIN FUSIÓN
# =============================================================================

def extract_yaml_only_index(file_path: Path) -> Optional[Dict]:
    """
    Extrae SÓLO el YAML del propio index.qmd (sin considerar _metadata.yml).
    Ideal para saber qué está explícitamente escrito en el artículo.
    """
    raw = extract_frontmatter(file_path)
    return parse_frontmatter(raw) if raw is not None else None


def extract_yaml_merged(
    file_path: Path, base_path: Path
) -> Optional[Dict]:
    """
    Extrae YAML con fusión inteligente index.qmd + _metadata.yml más cercano.
    Prioridad: valores de index.qmd sobrescriben los de _metadata.yml.
    Útil para visualizar el conjunto completo de metadatos efectivos.
    """
    index_yaml = extract_yaml_only_index(file_path)
    if index_yaml is None:
        return None

    metadata_path = find_metadata_yml(file_path, base_path)
    if metadata_path is None:
        return index_yaml

    base_yaml = read_yaml_from_file(metadata_path) or {}
    result = base_yaml.copy()
    for key, value in index_yaml.items():
        if value is not None:
            result[key] = value
    return result


# =============================================================================
# BÚSQUEDA DE _metadata.yml
# =============================================================================

def find_metadata_yml(qmd_path: Path, base_path: Path) -> Optional[Path]:
    """
    Sube recursivamente desde la carpeta del index.qmd buscando
    el _metadata.yml más cercano, sin pasar de base_path.
    """
    current = qmd_path.parent
    while current >= base_path:
        candidate = current / "_metadata.yml"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


# =============================================================================
# DETECCIÓN DE TIPO DE DOCUMENTO
# =============================================================================

def detect_document_mode(file_path: Path, default: str = "jou") -> str:
    """
    Detecta el tipo de documento (stu/man/jou/doc) leyendo SÓLO el
    index.qmd (no mezcla con _metadata.yml).

    Orden de prioridad:
    1. Campo 'documentmode' directo
    2. format.apaquarto-pdf.documentmode
    3. Inferir por campos presentes (course → stu, journal+volume → jou)
    4. Valor `default` si no hay indicios
    """
    raw = extract_frontmatter(file_path)
    if not raw:
        return default

    yaml_data = parse_frontmatter(raw)
    if not yaml_data:
        return default

    valid_modes = {"stu", "man", "jou", "doc"}

    # 1. documentmode directo
    mode = yaml_data.get("documentmode")
    if mode in valid_modes:
        return mode

    # 2. format.apaquarto-pdf.documentmode
    fmt = yaml_data.get("format", {})
    if isinstance(fmt, dict):
        apa = fmt.get("apaquarto-pdf", {})
        if isinstance(apa, dict):
            mode = apa.get("documentmode")
            if mode in valid_modes:
                return mode

    # 3. Inferir por campos
    if "course" in yaml_data or "professor" in yaml_data:
        return "stu"
    if "journal" in yaml_data and "volume" in yaml_data:
        return "jou"
    if "meta-analysis" in yaml_data or "meta_analysis" in yaml_data:
        return "man"

    return default


# =============================================================================
# DETECCIÓN DE ARTÍCULO vs CONFIGURACIÓN
# =============================================================================

def is_article_index(file_path: Path) -> bool:
    """
    Devuelve True si el index.qmd corresponde a un artículo/publicación
    real.  Criterio: la carpeta padre debe comenzar con fecha YYYY-MM-DD.
    Los index.qmd dentro de carpetas de sección (blog/, posts/, etc.)
    NO son artículos.
    """
    parent_name = file_path.parent.name

    # Carpeta padre empieza con fecha ISO
    if re.match(r"^\d{4}-\d{2}-\d{2}", parent_name):
        return True

    # Está directamente dentro de una sección
    if parent_name in SECTION_DIRS:
        return False

    return False


# =============================================================================
# APLANADO DE CLAVES YAML (para detección de campos nuevos)
# =============================================================================

def flatten_yaml_keys(yaml_data: Dict, prefix: str = "") -> Set[str]:
    """
    Aplana un diccionario YAML en un set de claves planas.
    Ejemplo:
      {'author': [{'name': 'X', 'affiliations': [{'name': 'Y'}]}]}
      → {'author_1_name', 'author_1_affiliations_1_name'}
    """
    fields: Set[str] = set()
    for key, value in yaml_data.items():
        full_key = f"{prefix}_{key}" if prefix else key

        if isinstance(value, list) and value and isinstance(value[0], dict):
            for i, item in enumerate(value, 1):
                if isinstance(item, dict):
                    fields.update(flatten_yaml_keys(item, f"{full_key}_{i}"))
        elif isinstance(value, dict):
            fields.update(flatten_yaml_keys(value, full_key))
        else:
            fields.add(full_key)

    return fields
