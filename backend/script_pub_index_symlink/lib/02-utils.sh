#!/usr/bin/env bash
# =============================================================================
# 02-utils.sh
# -----------------------------------------------------------------------------
# Funciones utilitarias pequeñas y reutilizables por otros módulos:
# extraer el año de un nombre de carpeta, saber si una ruta debe ignorarse,
# y autodetección del directorio Documents.
# =============================================================================

if [[ -n "${PUBINDEX_UTILS_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_UTILS_LOADED=1

# Extrae el año (YYYY) a partir de un nombre de carpeta tipo
# "2022-09-12-01-introduccion..."  →  "2022"
utils_extract_year() {
    local dirname="$1"
    echo "${dirname:0:4}"
}

# Devuelve 0 (verdadero) si $1 es un nombre de carpeta que debe ignorarse
# (carpetas técnicas/generadas definidas en PUBINDEX_IGNORE_DIRS)
utils_is_ignored_dir() {
    local dirname="$1"
    local ignored
    for ignored in "${PUBINDEX_IGNORE_DIRS[@]}"; do
        if [[ "$dirname" == "$ignored" ]]; then
            return 0
        fi
    done
    return 1
}

# Devuelve 0 (verdadero) si $1 (solo el nombre de carpeta, no la ruta completa)
# calza con el patrón de fecha de publicación YYYY-MM-DD-...
utils_matches_date_pattern() {
    local dirname="$1"
    [[ "$dirname" =~ $PUBINDEX_DATE_REGEX ]]
}

# Autodetecta el directorio ~/Documents subiendo desde la ubicación de este
# script hasta encontrar una carpeta que contenga "04 index". Si no se
# encuentra, falla con mensaje claro.
utils_detect_docs_dir() {
    if [[ -n "$PUBINDEX_DOCS_DIR" ]]; then
        echo "$PUBINDEX_DOCS_DIR"
        return 0
    fi

    local candidate
    candidate="$(cd "$PUBINDEX_SCRIPT_DIR/.." && pwd)"

    # Sube hasta 5 niveles buscando una carpeta que contenga "04 index"
    local i
    for ((i = 0; i < 5; i++)); do
        if [[ -d "$candidate/$PUBINDEX_TARGET_DIRNAME" ]]; then
            echo "$candidate"
            return 0
        fi
        candidate="$(cd "$candidate/.." && pwd)"
    done

    return 1
}

# Confirma con el usuario (s/n). Devuelve 0 si confirma, 1 si no.
utils_confirm() {
    local prompt="$1"
    local answer
    read -r -p "$prompt [s/N]: " answer
    [[ "$answer" =~ ^[sS]$ ]]
}
