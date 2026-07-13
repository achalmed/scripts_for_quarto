"""
lib/field_mapper.py
===================
Conversiones bidireccionales entre los campos del Excel (nombres planos
como author_1_name, citation_type, numbered_lines) y la estructura YAML
anidada de los archivos index.qmd.

Funciones principales:
  extract_value(yaml_data, field_name) → Any
      Lee un campo del dict YAML y lo convierte al formato Excel.

  apply_row_to_yaml(yaml_data, row, changes) → Dict
      Aplica los valores de una fila pandas al dict YAML,
      respetando tipos, eliminando vacíos y registrando cambios.

No abre archivos; trabaja únicamente con dicts y Series en memoria.
"""

import json
import re
from typing import Any, Dict, List, Optional

import pandas as pd

from .config import YAML_FIELD_ORDER


# =============================================================================
# EXTRACCIÓN YAML → EXCEL (dict → valor simple)
# =============================================================================

# Campos directos YAML-key → Excel-column
_SIMPLE_YAML_TO_EXCEL: Dict[str, str] = {
    "title": "title", "shorttitle": "shorttitle", "subtitle": "subtitle",
    "date": "date", "draft": "draft", "abstract": "abstract",
    "description": "description", "image": "image", "eval": "eval",
    "bibliography": "bibliography", "course": "course",
    "professor": "professor", "duedate": "duedate", "note": "note",
    "journal": "journal", "volume": "volume",
    "copyrightnotice": "copyrightnotice", "copyrightext": "copyrightext",
    "floatsintext": "floatsintext", "mask": "mask",
}

# Campos con guion en YAML pero guion_bajo en Excel
_DASHED_YAML_TO_EXCEL = {
    "numbered_lines": "numbered-lines",
    "meta_analysis":  "meta-analysis",
}


def extract_value(yaml_data: Dict, field_name: str) -> Any:
    """
    Extrae un valor del YAML para una columna del Excel.
    Maneja campos simples, listas, citation, links y autores.
    """
    # --- Campos simples ---
    if field_name in _SIMPLE_YAML_TO_EXCEL:
        yaml_key = _SIMPLE_YAML_TO_EXCEL[field_name]
        value = yaml_data.get(yaml_key)
        # copyrightnotice siempre como int
        if field_name == "copyrightnotice" and value is not None:
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        return value

    # --- Campos con guión ---
    if field_name in _DASHED_YAML_TO_EXCEL:
        return yaml_data.get(_DASHED_YAML_TO_EXCEL[field_name])

    # --- Listas (keywords, tags, categories) ---
    if field_name in ("keywords", "tags", "categories"):
        v = yaml_data.get(field_name, [])
        if isinstance(v, list):
            return ", ".join(str(x) for x in v)
        return v

    # --- Citación ---
    if field_name.startswith("citation_"):
        citation = yaml_data.get("citation")
        if not isinstance(citation, dict):
            return None
        if field_name == "citation_type":
            return citation.get("type")
        if field_name == "citation_author":
            authors = citation.get("author", [])
            if isinstance(authors, list):
                return ", ".join(str(a) for a in authors)
            return authors
        if field_name == "citation_pdf_url":
            return citation.get("pdf-url")

    # --- Links ---
    if field_name == "links_enabled":
        links = yaml_data.get("links")
        return links is not None and links is not False
    if field_name == "links_data":
        links = yaml_data.get("links")
        if links and isinstance(links, (list, dict)):
            return json.dumps(links, ensure_ascii=False)

    # --- Autores (author_N_campo) ---
    if field_name.startswith("author_"):
        match = re.match(r"author_(\d+)_(.*)", field_name)
        if not match:
            return None
        idx = int(match.group(1)) - 1
        suffix = match.group(2)

        authors = yaml_data.get("author", [])
        if not isinstance(authors, list) or idx >= len(authors):
            return None
        author = authors[idx]

        if suffix == "name":
            return author.get("name")
        if suffix == "corresponding":
            corr = author.get("corresponding")
            if corr is True:
                return "TRUE"
            if corr is False:
                return "FALSE"
            return corr
        if suffix == "orcid":
            return author.get("orcid")
        if suffix == "email":
            return author.get("email")
        if suffix == "roles":
            roles = author.get("role", [])
            if isinstance(roles, list):
                return ", ".join(str(r) for r in roles)
            return roles
        if suffix.startswith("affiliation_"):
            aff_key = suffix.replace("affiliation_", "")
            affs = author.get("affiliations", [])
            if affs and isinstance(affs, list):
                for aff in affs:
                    if isinstance(aff, dict):
                        return aff.get(aff_key)

    return None


# =============================================================================
# APLICACIÓN EXCEL → YAML (fila pandas → dict actualizado)
# =============================================================================

def _is_empty(value) -> bool:
    """Devuelve True si el valor de Excel está vacío o es NaN."""
    if value is None:
        return True
    if isinstance(value, float):
        import math
        return math.isnan(value)
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _to_bool(value) -> Optional[bool]:
    """Convierte 'TRUE'/'FALSE' (Excel) a bool Python. None si no es booleano."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.upper() in ("TRUE", "FALSE"):
        return value.upper() == "TRUE"
    if isinstance(value, (int, float)):
        return bool(int(value))
    return None


def reorder_yaml(yaml_data: Dict) -> Dict:
    """
    Reconstruye el dict YAML siguiendo YAML_FIELD_ORDER.
    Público: también lo usa tag_operations para mantener el orden
    canónico al reescribir archivos.
    """
    ordered: Dict = {}
    for field in YAML_FIELD_ORDER:
        if field in yaml_data:
            ordered[field] = yaml_data[field]
    for key, value in yaml_data.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def apply_row_to_yaml(
    yaml_data: Dict,
    row: pd.Series,
    changes: List[str],
) -> Dict:
    """
    Aplica los valores de una fila del Excel al dict YAML.

    Reglas:
    - Si la celda está vacía → el campo se ELIMINA del YAML.
    - TRUE/FALSE en Excel → bool Python.
    - Listas en Excel (comma-separated) → list Python.
    - Autores: solo se actualizan si ya existen en el index.qmd.
    - El dict resultante sigue el orden definido en YAML_FIELD_ORDER.
    - Registra cada cambio real en la lista `changes`.
    """
    # Reordenar antes de modificar
    yaml_data = reorder_yaml(yaml_data)

    # --- Campos simples ---
    for excel_field, yaml_key in _SIMPLE_YAML_TO_EXCEL.items():
        if excel_field not in row:
            continue
        new_val = row[excel_field]
        old_val = yaml_data.get(yaml_key)

        if _is_empty(new_val):
            if yaml_key in yaml_data:
                del yaml_data[yaml_key]
                changes.append(f"{yaml_key}: ELIMINADO (vacío en Excel)")
            continue

        # Booleanos
        bool_val = _to_bool(new_val)
        if bool_val is not None:
            new_val = bool_val

        # copyrightnotice → int
        if excel_field == "copyrightnotice":
            try:
                new_val = int(float(new_val))
            except (ValueError, TypeError):
                pass

        # Limpiar texto en abstract / description
        if excel_field in ("abstract", "description") and isinstance(new_val, str):
            new_val = " ".join(new_val.split())

        if old_val != new_val:
            yaml_data[yaml_key] = new_val
            changes.append(
                f"{yaml_key}: {repr(old_val)[:50]} → {repr(new_val)[:50]}"
            )

    # --- Campos con guión (numbered-lines, meta-analysis) ---
    for excel_field, yaml_key in _DASHED_YAML_TO_EXCEL.items():
        if excel_field not in row:
            continue
        new_val = row[excel_field]
        if _is_empty(new_val):
            if yaml_key in yaml_data:
                del yaml_data[yaml_key]
                changes.append(f"{yaml_key}: ELIMINADO")
            continue
        bool_val = _to_bool(new_val)
        new_val = bool_val if bool_val is not None else new_val
        old_val = yaml_data.get(yaml_key)
        if old_val != new_val:
            yaml_data[yaml_key] = new_val
            changes.append(f"{yaml_key}: {old_val} → {new_val}")

    # --- tipo_documento (documentmode) ---
    if "tipo_documento" in row and not _is_empty(row["tipo_documento"]):
        new_type = str(row["tipo_documento"]).lower()
        if new_type in ("stu", "man", "jou", "doc"):
            old_type = (
                yaml_data.get("documentmode")
                or (
                    yaml_data.get("format", {})
                    .get("apaquarto-pdf", {})
                    .get("documentmode")
                )
                or "jou"
            )
            if old_type != new_type:
                if new_type != "jou":
                    new_ordered = {"documentmode": new_type}
                    new_ordered.update(
                        {k: v for k, v in yaml_data.items() if k != "documentmode"}
                    )
                    yaml_data = new_ordered
                    changes.append(
                        f"documentmode: {old_type} → {new_type} (AGREGADO AL INICIO)"
                    )
                elif "documentmode" in yaml_data:
                    yaml_data["documentmode"] = new_type
                    changes.append(f"documentmode: {old_type} → {new_type}")

    # --- Listas (keywords, tags, categories) ---
    for field in ("keywords", "tags", "categories"):
        if field not in row:
            continue
        new_val = row[field]
        if _is_empty(new_val):
            if field in yaml_data:
                del yaml_data[field]
                changes.append(f"{field}: ELIMINADO")
            continue
        if isinstance(new_val, str):
            new_list = [x.strip() for x in new_val.split(",") if x.strip()]
        else:
            new_list = [str(new_val)]
        old_list = yaml_data.get(field, [])
        if set(old_list) != set(new_list):
            yaml_data[field] = new_list
            changes.append(f"{field}: actualizado ({len(new_list)} items)")

    # --- Citación ---
    if any(f in row for f in ("citation_type", "citation_pdf_url")):
        if "citation" not in yaml_data or not isinstance(yaml_data["citation"], dict):
            yaml_data["citation"] = {}
        if "citation_type" in row and not _is_empty(row["citation_type"]):
            old = yaml_data["citation"].get("type")
            new = row["citation_type"]
            if old != new:
                yaml_data["citation"]["type"] = new
                changes.append(f"citation.type: {old} → {new}")
        if "citation_pdf_url" in row and not _is_empty(row["citation_pdf_url"]):
            old = yaml_data["citation"].get("pdf-url")
            new = row["citation_pdf_url"]
            if old != new:
                yaml_data["citation"]["pdf-url"] = new
                changes.append("citation.pdf-url actualizada")

    # --- Autores (solo si ya existen en index.qmd) ---
    if "author" in yaml_data:
        authors_data = []
        for i in range(1, 4):
            prefix = f"author_{i}_"
            name_field = f"{prefix}name"
            if name_field not in row or _is_empty(row[name_field]):
                continue

            author: Dict = {"name": row[name_field]}

            corr_field = f"{prefix}corresponding"
            if corr_field in row and not _is_empty(row[corr_field]):
                author["corresponding"] = _to_bool(row[corr_field]) or False

            for simple_field in ("orcid", "email"):
                full = f"{prefix}{simple_field}"
                if full in row and not _is_empty(row[full]):
                    author[simple_field] = row[full]

            aff: Dict = {}
            for aff_key in ("name", "department", "city", "region", "country"):
                full = f"{prefix}affiliation_{aff_key}"
                if full in row and not _is_empty(row[full]):
                    aff[aff_key] = row[full]
            if aff:
                author["affiliations"] = [aff]

            roles_field = f"{prefix}roles"
            if roles_field in row and not _is_empty(row[roles_field]):
                roles_str = row[roles_field]
                if isinstance(roles_str, str):
                    author["role"] = [r.strip() for r in roles_str.split(",")]

            authors_data.append(author)

        if authors_data:
            old_authors = yaml_data.get("author", [])
            if old_authors != authors_data:
                yaml_data["author"] = authors_data
                changes.append(
                    f"author: actualizado ({len(authors_data)} autores)"
                )

    return yaml_data
