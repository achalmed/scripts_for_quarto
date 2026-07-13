#!/usr/bin/env bash
# =============================================================================
# 00-config.sh
# -----------------------------------------------------------------------------
# Configuración central del gestor de publicaciones Quarto. Define rutas,
# colores, emojis y la lista de proyectos excluidos. Ningún otro módulo debe
# "hardcodear" estos valores: todo se referencia desde aquí.
# =============================================================================

if [[ -n "${QBLOG_CONFIG_LOADED:-}" ]]; then
    return 0
fi
QBLOG_CONFIG_LOADED=1

# --- Directorio base de Documents -------------------------------------------
# Se autodetecta subiendo desde la ubicación de este script hasta encontrar
# una carpeta que contenga al menos un proyecto pub_* o "website-achalma".
# Si la autodetección falla, se puede forzar con la variable de entorno
# QBLOG_DOCS_DIR antes de ejecutar main.sh, ej:
#   QBLOG_DOCS_DIR=/home/achalmaedison/Documents ./main.sh list
QBLOG_DOCS_DIR="${QBLOG_DOCS_DIR:-}"

# --- Prefijo de carpetas de proyectos de publicaciones (blogs) --------------
QBLOG_PROJECT_PREFIX="pub_"

# --- Proyecto especial que también se gestiona como "blog" -------------------
QBLOG_WEBSITE_PROJECT="website-achalma"

# --- Proyectos excluidos de las operaciones masivas (render-all, clean-all,
#     list, etc.) -------------------------------------------------------------
# Vacío por defecto: todos los pub_* y website-achalma se gestionan.
# Añade aquí el nombre EXACTO de la carpeta si alguna vez quieres excluir un
# proyecto puntual, ej: QBLOG_EXCLUDED_PROJECTS=("pub_borradores")
QBLOG_EXCLUDED_PROJECTS=()

# --- Carpetas técnicas/generadas que nunca se tratan como "carpetas de
#     posts" al detectar la estructura de un blog --------------------------
QBLOG_IGNORE_DIRS=(
    "_freeze"
    "_partials"
    "_site"
    "_extensions"
    ".quarto"
    ".git"
    "site_libs"
    "node_modules"
    "assets"
)

# --- Configuración de Git -----------------------------------------------------
QBLOG_GIT_USER_NAME="Edison Achalma"
QBLOG_GIT_USER_EMAIL="elmer.achalma.09@unsch.edu.pe"

# --- Configuración de publicación y preview -----------------------------------
QBLOG_DEFAULT_PUBLISH_TARGET="gh-pages"
QBLOG_DEFAULT_PREVIEW_PORT=4200

# --- Configuración de autor por defecto (usado por init y _metadata.yml) ----
QBLOG_DEFAULT_AUTHOR="Edison Achalma"
QBLOG_DEFAULT_AUTHOR_URL="https://achalmaedison.netlify.app"
QBLOG_DEFAULT_AUTHOR_ORCID="0000-0001-6996-3364"
QBLOG_DEFAULT_AUTHOR_EMAIL="elmer.achalma.09@unsch.edu.pe"
QBLOG_DEFAULT_INSTITUTION="Universidad Nacional de San Cristóbal de Huamanga"
QBLOG_DEFAULT_DEPARTMENT="Escuela Profesional de Economía"
QBLOG_DEFAULT_CITY="Ayacucho"
QBLOG_DEFAULT_REGION="AYA"
QBLOG_DEFAULT_COUNTRY="Perú"
QBLOG_DEFAULT_AFFILIATION_ID="unsch"

# --- Editor preferido para abrir archivos -------------------------------------
QBLOG_EDITOR="${EDITOR:-nano}"

# --- Colores para salida en terminal (se desactivan si no hay TTY) ----------
if [[ -t 1 ]]; then
    QBLOG_RED='\033[0;31m'
    QBLOG_GREEN='\033[0;32m'
    QBLOG_YELLOW='\033[1;33m'
    QBLOG_BLUE='\033[0;34m'
    QBLOG_MAGENTA='\033[0;35m'
    QBLOG_CYAN='\033[0;36m'
    QBLOG_WHITE='\033[1;37m'
    QBLOG_BOLD='\033[1m'
    QBLOG_DIM='\033[2m'
    QBLOG_NC='\033[0m'
else
    QBLOG_RED=""; QBLOG_GREEN=""; QBLOG_YELLOW=""; QBLOG_BLUE=""
    QBLOG_MAGENTA=""; QBLOG_CYAN=""; QBLOG_WHITE=""; QBLOG_BOLD=""
    QBLOG_DIM=""; QBLOG_NC=""
fi

# --- Emojis para mejor visualización ------------------------------------------
QBLOG_E_SUCCESS="✅"
QBLOG_E_ERROR="❌"
QBLOG_E_WARNING="⚠️"
QBLOG_E_INFO="ℹ️"
QBLOG_E_ROCKET="🚀"
QBLOG_E_FOLDER="📁"
QBLOG_E_FILE="📄"
QBLOG_E_BOOK="📚"
QBLOG_E_GEAR="⚙️"
QBLOG_E_CLEAN="🧹"
QBLOG_E_PREVIEW="👁️"
QBLOG_E_PUBLISH="🌍"
QBLOG_E_GIT="🐙"
