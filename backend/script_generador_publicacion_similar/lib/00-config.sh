#!/usr/bin/env bash
# =============================================================================
# 00-config.sh
# -----------------------------------------------------------------------------
# Configuración central del generador de índices. Define versión, valores
# por defecto y la lista de carpetas ignoradas. Ningún otro módulo debe
# "hardcodear" estos valores: todo se referencia desde aquí.
# =============================================================================

if [[ -n "${GENIDX_CONFIG_LOADED:-}" ]]; then
    return 0
fi
GENIDX_CONFIG_LOADED=1

# --- Identidad del script -----------------------------------------------------
GENIDX_VERSION="4.0.0"
GENIDX_SCRIPT_NAME="generar-indices"

# --- Valores por defecto (sobrescribibles por CLI) ----------------------------
# URL base sin barra final. El validador normaliza si el usuario la incluye.
GENIDX_DEFAULT_BASE_URL="https://achalmaedison.netlify.app"

# Tipo de estructura: "auto" delega en lib/04-detector.sh.
#   website → URLs con el segmento de la sección: base/<seccion>/<subblog>/<post>
#   blog    → URLs de proyecto independiente:     base/<subblog>/<post>
GENIDX_DEFAULT_BLOG_TYPE="auto"

# --- Formato de salida ----------------------------------------------------------
# Prefijo de los archivos de índice generados: _contenido_<subblog>.qmd
GENIDX_OUTPUT_PREFIX="_contenido_"

# Shortcode de Font Awesome usado como icono de enlace al PDF.
GENIDX_PDF_ICON='{{< fa regular file-pdf >}}'

# --- Carpetas que nunca se tratan como subblogs -------------------------------
# Las carpetas que empiezan con "." o "_" se ignoran siempre (regla aparte
# en is_ignored_dir). Esta lista cubre los casos que no siguen esa convención.
GENIDX_IGNORE_DIRS=(
    "site_libs"
    "beschikbaarheid"
    "assets"
    "node_modules"
)
