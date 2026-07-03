#!/usr/bin/env bash
# =============================================================================
# main.sh — Generador de Índices de Contenido para Blogs Quarto
# -----------------------------------------------------------------------------
# Versión 4.0 — Reestructuración modular del antiguo generar_indices.sh
# monolítico. Conserva TODAS las funciones originales (detección de
# estructura website/blog, generación de _contenido_<subblog>.qmd con
# enlaces a artículo y PDF, limpieza de índices vacíos, resumen final),
# reorganizadas en módulos independientes dentro de lib/. El directorio
# del blog ahora se pasa como argumento en vez de editarse en el código.
#
# Uso:
#   ./main.sh BLOG_DIR [opciones]
#   ./main.sh ~/Documents/pub_axiomata
#   ./main.sh ~/Documents/website-achalma/teching --dry-run
#   ./main.sh --help
# =============================================================================

set -uo pipefail

# --- Localización del propio script (para poder ejecutarse desde cualquier
#     directorio) ---------------------------------------------------------------
GENIDX_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENIDX_LIB_DIR="$GENIDX_SCRIPT_DIR/lib"

# --- Carga de módulos en orden --------------------------------------------------
# shellcheck source=lib/00-config.sh
source "$GENIDX_LIB_DIR/00-config.sh"
# shellcheck source=lib/01-logging.sh
source "$GENIDX_LIB_DIR/01-logging.sh"
# shellcheck source=lib/02-cli.sh
source "$GENIDX_LIB_DIR/02-cli.sh"
# shellcheck source=lib/03-validator.sh
source "$GENIDX_LIB_DIR/03-validator.sh"
# shellcheck source=lib/04-detector.sh
source "$GENIDX_LIB_DIR/04-detector.sh"
# shellcheck source=lib/05-linker.sh
source "$GENIDX_LIB_DIR/05-linker.sh"
# shellcheck source=lib/06-generator.sh
source "$GENIDX_LIB_DIR/06-generator.sh"

main() {
    parse_arguments "$@"
    validate_environment

    if [[ "$GENIDX_BLOG_TYPE" == "auto" ]]; then
        GENIDX_BLOG_TYPE="$(detect_blog_structure "$GENIDX_BLOG_DIR")"
        log_info "Estructura detectada automáticamente: $GENIDX_BLOG_TYPE"
    else
        log_info "Usando estructura especificada: $GENIDX_BLOG_TYPE"
    fi

    log_info "Iniciando procesamiento del blog: $GENIDX_BLOG_DIR"
    log_info "URL base configurada: $GENIDX_BASE_URL"
    if [[ "$GENIDX_DRY_RUN" -eq 1 ]]; then
        log_info "Modo dry-run activado: no se modificará ningún archivo"
    fi

    generate_all_indices
    print_summary
}

main "$@"
