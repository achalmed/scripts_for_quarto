#!/usr/bin/env bash
# =============================================================================
#  backend/script_pub_index_symlink/lib/02-utils.sh — Funciones utilitarias pequeñas y reutilizables por otros módulos
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

# Devuelve ~/Documents: DOCS_ROOT de core/env.sh, que main.sh ya cargó (ola 0:
# sin alias propio ni búsqueda hacia arriba de reserva). Falla si no hay raíz.
utils_detect_docs_dir() {
    [[ -n "${DOCS_ROOT:-}" && -d "$DOCS_ROOT" ]] || return 1
    printf '%s\n' "$DOCS_ROOT"
}

# Confirma con el usuario (s/n). Devuelve 0 si confirma, 1 si no.
utils_confirm() {
    local prompt="$1"
    local answer
    read -r -p "$prompt [s/N]: " answer
    [[ "$answer" =~ ^[sS]$ ]]
}
