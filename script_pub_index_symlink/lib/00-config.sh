#!/usr/bin/env bash
# =============================================================================
# 00-config.sh
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
# Se asume que main.sh se ejecuta desde dentro de pub-index-sync/, que a su
# vez vive en algún lugar dentro de ~/Documents. Por defecto se autodetecta
# subiendo desde la ubicación del script hasta encontrar "04 index".
# Si la autodetección falla, se puede forzar con la variable de entorno
# PUBINDEX_DOCS_DIR antes de ejecutar main.sh, ej:
#   PUBINDEX_DOCS_DIR=/home/achalmaedison/Documents ./main.sh
PUBINDEX_DOCS_DIR="${PUBINDEX_DOCS_DIR:-}"

# --- Carpeta destino donde se crean los symlinks organizados por año --------
PUBINDEX_TARGET_DIRNAME="04 index"

# --- Prefijo de carpetas de proyectos de publicaciones a escanear -----------
PUBINDEX_PROJECT_PREFIX="pub_"

# --- Proyecto especial (no tiene el prefijo pub_) y sus subcarpetas de posts
PUBINDEX_WEBSITE_PROJECT="website-achalma"
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
