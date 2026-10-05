#!/usr/bin/env bash
# =============================================================================
#  backend/script_pub_index_symlink/lib/00-config.sh — Módulo de configuración central
# -----------------------------------------------------------------------------
# Módulo de configuración central. Define rutas, patrones y constantes que
# usan todos los demás módulos. Ningún otro módulo debe "hardcodear" rutas:
# todo se referencia desde aquí.
# =============================================================================

# Evita que este archivo se cargue dos veces si algún módulo lo vuelve a "source"
if [[ -n "${PUBINDEX_CONFIG_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_CONFIG_LOADED=1

# --- Directorio base de Documents -------------------------------------------
# La raíz es DOCS_ROOT de core/env.sh, que main.sh carga antes que este módulo
# (ola 0, 2026-10-05: sin alias propio de la raíz). Para forzarla:
#   DOCS_ROOT="$HOME/Documents" ./main.sh

# --- Proyecto especial (no tiene el prefijo pub_) y sus subcarpetas de posts
# La carpeta del hub (repo website-achalma), relativa a la raíz: INDEX_DIR de core/env.
PUBINDEX_WEBSITE_PROJECT="${INDEX_DIR#"$DOCS_ROOT"/}"

# --- Carpeta destino donde se crean los symlinks organizados por año --------
# Desde 2026-09-06 la carpeta del hub es también el repo del hub Quarto;
# los symlinks por año van en su subcarpeta _indice/ (el guion bajo evita que
# Quarto la renderice y el .gitignore del hub la excluye).
PUBINDEX_TARGET_DIRNAME="$PUBINDEX_WEBSITE_PROJECT/_indice"

# --- Prefijo de carpetas de proyectos de publicaciones a escanear -----------
PUBINDEX_PROJECT_PREFIX="pub_"

# --- Subcarpeta (relativa a Documents) con los pub_* como submódulos del hub
#     (reorganización 2026-09-06). Forzable con PUBINDEX_PUBS_SUBDIR. ---------
PUBINDEX_PUBS_SUBDIR="${PUBINDEX_PUBS_SUBDIR:-$PUBINDEX_WEBSITE_PROJECT/_pubs}"
PUBINDEX_WEBSITE_SUBDIRS=("blog/posts" "talk")

# --- Carpetas técnicas/generadas que se deben ignorar siempre ---------------
# (independientemente de si su nombre calza con el patrón de fecha)
PUBINDEX_IGNORE_DIRS=(
    "_freeze"
    "_partials"
    "_site"
    "_extensions"
    ".quarto"
    ".git"
    "site_libs"
    "node_modules"
    "_indice"
    "_vault"
)

# --- Patrón de fecha que identifica una "publicación" ------------------------
# Carpetas cuyo NOMBRE empieza por YYYY-MM-DD seguido de un guion.
# Ej: 2022-09-12-01-introduccion-al-mundo-de-bi-y-la-suite-power
PUBINDEX_DATE_REGEX='^[0-9]{4}-[0-9]{2}-[0-9]{2}-'

# --- Archivo de log ------------------------------------------------------------
PUBINDEX_LOG_FILE=""   # se define dinámicamente en main.sh (dentro de logs/)

# --- Colores para salida en terminal (se desactivan si no hay TTY) ----------
if [[ -t 1 ]]; then
    PUBINDEX_C_RESET=$'\033[0m'
    PUBINDEX_C_GREEN=$'\033[0;32m'
    PUBINDEX_C_YELLOW=$'\033[0;33m'
    PUBINDEX_C_RED=$'\033[0;31m'
    PUBINDEX_C_BLUE=$'\033[0;34m'
    PUBINDEX_C_BOLD=$'\033[1m'
else
    PUBINDEX_C_RESET=""
    PUBINDEX_C_GREEN=""
    PUBINDEX_C_YELLOW=""
    PUBINDEX_C_RED=""
    PUBINDEX_C_BLUE=""
    PUBINDEX_C_BOLD=""
fi
