"""
lib/tag_utils.py
================
Funciones puras para manipular listas de tags: normalización unicode,
deduplicación, reemplazos, altas/bajas y similitud de cadenas.

Absorbe la lógica de normalización del antiguo script_tag_manager
(QMDTagManager.normalize_tag) para que exista UNA sola implementación.

No abre archivos ni toca Excel; trabaja únicamente con strings y listas.
"""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


# =============================================================================
# NORMALIZACIÓN
# =============================================================================

def normalize_tag(tag: str) -> str:
    """
    Normaliza un tag según las reglas del proyecto:
      - minúsculas
      - sin tildes (descomposición NFD, se eliminan las marcas diacríticas)
      - sin caracteres especiales
      - espacios y guiones → guión bajo
      - sin guiones bajos múltiples ni en los extremos

    Ejemplo: "Gestión Empresarial" → "gestion_empresarial"
    """
    tag = str(tag).lower().strip()

    tag = "".join(
        c for c in unicodedata.normalize("NFD", tag)
        if unicodedata.category(c) != "Mn"
    )

    tag = re.sub(r"[^\w\s-]", "", tag)
    tag = re.sub(r"[\s-]+", "_", tag)
    tag = tag.strip("_")
    tag = re.sub(r"_+", "_", tag)

    return tag


def dedupe_tags(tags: List[str]) -> List[str]:
    """Elimina duplicados exactos preservando el orden de aparición."""
    seen = set()
    unique = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique.append(tag)
    return unique


def normalize_tag_list(tags: List[str]) -> List[str]:
    """
    Normaliza toda una lista y elimina duplicados resultantes.
    "economia, Economía, ECONOMIA" → ["economia"]
    Los tags que quedan vacíos tras normalizar se descartan.
    """
    normalized = [normalize_tag(t) for t in tags]
    return dedupe_tags([t for t in normalized if t])


# =============================================================================
# OPERACIONES SOBRE LISTAS
# =============================================================================

def apply_replacements(
    tags: List[str], replacements: Dict[str, str]
) -> Tuple[List[str], List[str]]:
    """
    Reemplaza tags según un dict {viejo: nuevo}. La comparación se hace en
    espacio normalizado, así "Gestión" también matchea "gestion".

    Devuelve (lista_resultante, lista_de_cambios_descritos).
    """
    changes = []
    normalized_map = {
        normalize_tag(old): normalize_tag(new)
        for old, new in replacements.items()
    }

    result = []
    for tag in tags:
        replacement = normalized_map.get(normalize_tag(tag))
        if replacement is not None and replacement != tag:
            changes.append(f"'{tag}' → '{replacement}'")
            result.append(replacement)
        else:
            result.append(tag)

    return result, changes


def remove_tags(
    tags: List[str], to_remove: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Elimina de la lista los tags indicados (comparación normalizada).
    Devuelve (lista_resultante, tags_efectivamente_eliminados).
    """
    remove_set = {normalize_tag(t) for t in to_remove}
    kept, removed = [], []
    for tag in tags:
        if normalize_tag(tag) in remove_set:
            removed.append(tag)
        else:
            kept.append(tag)
    return kept, removed


def add_tags(
    tags: List[str], to_add: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Agrega tags nuevos al final, evitando duplicados (comparación
    normalizada) y respetando el orden existente.
    Devuelve (lista_resultante, tags_efectivamente_agregados).
    """
    existing = {normalize_tag(t) for t in tags}
    result = list(tags)
    added = []
    for tag in to_add:
        normalized = normalize_tag(tag)
        if normalized and normalized not in existing:
            result.append(normalized)
            existing.add(normalized)
            added.append(normalized)
    return result, added


def transform_tags(
    tags: List[str],
    replacements: Optional[Dict[str, str]] = None,
    to_remove: Optional[List[str]] = None,
    to_add: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """
    Pipeline completo de una operación de tags (mismo orden que el antiguo
    Tag Manager): normalizar → reemplazar → eliminar → agregar → dedup.

    Toda operación normaliza la lista completa: es el comportamiento
    heredado que garantiza la deduplicación case/tilde-insensitive.

    Devuelve (tags_finales, descripciones_de_cambios).
    """
    changes: List[str] = []

    result = normalize_tag_list(tags)
    if result != list(tags):
        changes.append(f"normalizados: {len(tags)} → {len(result)} tags")

    if replacements:
        result, replaced = apply_replacements(result, replacements)
        changes.extend(f"reemplazo {c}" for c in replaced)

    if to_remove:
        result, removed = remove_tags(result, to_remove)
        if removed:
            changes.append(f"eliminados: {', '.join(removed)}")

    if to_add:
        result, added = add_tags(result, to_add)
        if added:
            changes.append(f"agregados: {', '.join(added)}")

    result = dedupe_tags(result)
    return result, changes


# =============================================================================
# PARSING DE ARGUMENTOS Y CELDAS
# =============================================================================

def parse_replacement_args(args: List[str]) -> Dict[str, str]:
    """
    Convierte ["viejo:nuevo", ...] en {viejo: nuevo}.
    Lanza ValueError ante formato inválido para que el CLI lo reporte.
    """
    replacements = {}
    for arg in args:
        if ":" not in arg:
            raise ValueError(
                f"Formato inválido para reemplazo: '{arg}' (use 'viejo:nuevo')"
            )
        old, new = arg.split(":", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError(f"Reemplazo con lado vacío: '{arg}'")
        replacements[old] = new
    return replacements


def tags_from_cell(value) -> List[str]:
    """
    Convierte el valor de una celda Excel ("a, b, c") en lista de tags.
    Misma convención comma-separated que usa field_mapper.
    """
    if value is None:
        return []
    return [t.strip() for t in str(value).split(",") if t.strip()]


def tags_to_cell(tags: List[str]) -> Optional[str]:
    """Convierte una lista de tags al formato de celda Excel ("a, b, c")."""
    return ", ".join(tags) if tags else None


def tags_from_yaml_value(value) -> Optional[List[str]]:
    """
    Interpreta el campo tags de un dict YAML.
    Devuelve None si el campo no existe (distinto de lista vacía: la regla
    heredada del Tag Manager es NO crear tags donde nunca los hubo).
    """
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(t) for t in value]
    return None


# =============================================================================
# SIMILITUD (para estadísticas y auditoría)
# =============================================================================

def tag_similarity(a: str, b: str) -> float:
    """Ratio de similitud [0..1] entre dos tags (difflib)."""
    return SequenceMatcher(None, a, b).ratio()


def is_plural_pair(a: str, b: str) -> bool:
    """True si un tag parece el plural del otro (heurística español: -s/-es)."""
    shorter, longer = sorted((a, b), key=len)
    return longer in (f"{shorter}s", f"{shorter}es")


def find_similar_pairs(
    tags: List[str], threshold: float = 0.8
) -> List[Tuple[str, str, float]]:
    """
    Encuentra pares de tags distintos con similitud >= threshold
    (candidatos a typos, variantes o singular/plural).
    Devuelve [(tag_a, tag_b, ratio)] ordenado por ratio descendente.
    """
    pairs = []
    sorted_tags = sorted(set(tags))
    for i, a in enumerate(sorted_tags):
        for b in sorted_tags[i + 1:]:
            # Poda barata: si difieren mucho en longitud no pueden superar
            # el umbral y el ratio de difflib es costoso en O(n²) pares
            if abs(len(a) - len(b)) > max(len(a), len(b)) * (1 - threshold):
                continue
            ratio = tag_similarity(a, b)
            if ratio >= threshold:
                pairs.append((a, b, ratio))
    return sorted(pairs, key=lambda p: -p[2])
