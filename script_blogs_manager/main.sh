#!/usr/bin/env bash
# =============================================================================
# main.sh — Gestor de Publicaciones Quarto (blog-manager)
# -----------------------------------------------------------------------------
# Versión 3.0 — Reestructuración modular del antiguo build.sh monolítico.
# Conserva TODAS las funciones originales (listado, render, preview, clean,
# publish, asistente de creación de posts APAQuarto, operaciones Git,
# operaciones masivas, init-blog, check-structure, backups, menú
# interactivo), reorganizadas en módulos independientes dentro de lib/, y
# adaptadas para escanear directamente los proyectos pub_* y
# website-achalma dentro de ~/Documents (en vez de una carpeta
# "publicaciones/" separada).
#
# Uso:
#   ./main.sh                       Modo interactivo (menú)
#   ./main.sh list                  Lista todos los blogs
#   ./main.sh help                  Ayuda completa
#
# Variables de entorno opcionales:
#   QBLOG_DOCS_DIR     Fuerza la ruta de ~/Documents si la autodetección falla
#   QBLOG_BACKUP_DIR   Fuerza la ruta del directorio de backups
# =============================================================================

set -uo pipefail

# --- Localización del propio script ------------------------------------------
QBLOG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QBLOG_LIB_DIR="$QBLOG_SCRIPT_DIR/lib"

# --- Carga de módulos en orden ------------------------------------------------
# shellcheck source=lib/00-config.sh
source "$QBLOG_LIB_DIR/00-config.sh"
# shellcheck source=lib/01-printing.sh
source "$QBLOG_LIB_DIR/01-printing.sh"
# shellcheck source=lib/02-utils.sh
source "$QBLOG_LIB_DIR/02-utils.sh"
# shellcheck source=lib/03-listing.sh
source "$QBLOG_LIB_DIR/03-listing.sh"
# shellcheck source=lib/04-quarto-ops.sh
source "$QBLOG_LIB_DIR/04-quarto-ops.sh"
# shellcheck source=lib/05-batch-ops.sh
source "$QBLOG_LIB_DIR/05-batch-ops.sh"
# shellcheck source=lib/06-git-ops.sh
source "$QBLOG_LIB_DIR/06-git-ops.sh"
# shellcheck source=lib/07-post-creator.sh
source "$QBLOG_LIB_DIR/07-post-creator.sh"
# shellcheck source=lib/08-init-blog.sh
source "$QBLOG_LIB_DIR/08-init-blog.sh"
# shellcheck source=lib/09-structure-check.sh
source "$QBLOG_LIB_DIR/09-structure-check.sh"
# shellcheck source=lib/10-backup.sh
source "$QBLOG_LIB_DIR/10-backup.sh"
# shellcheck source=lib/11-interactive-menu.sh
source "$QBLOG_LIB_DIR/11-interactive-menu.sh"
# shellcheck source=lib/12-help.sh
source "$QBLOG_LIB_DIR/12-help.sh"

# --- Detectar Documents -------------------------------------------------------
QBLOG_DOCS_DIR="$(utils_detect_docs_dir)" || {
    print_error "No se pudo autodetectar la carpeta Documents (que contenga pub_* o website-achalma)."
    print_error "Defínela manualmente, ej: QBLOG_DOCS_DIR=/home/achalmaedison/Documents ./main.sh"
    exit 1
}

# --- Directorio de backups (autodetectado relativo a Documents, salvo override)
QBLOG_BACKUP_DIR="${QBLOG_BACKUP_DIR:-$QBLOG_DOCS_DIR/06 archives/backups-publicaciones}"

# Helper interno: resuelve un nombre de blog ingresado por el usuario a su
# ruta absoluta, dejándola en la variable global QBLOG_RESOLVED_PATH. Si no
# existe, imprime un error claro y termina el script. IMPORTANTE: se usa
# como una sentencia normal (no via "$(...)") precisamente para que el
# exit se propague al proceso principal en vez de quedar atrapado en una
# subshell de command substitution.
QBLOG_RESOLVED_PATH=""
_resolve_or_die() {
    local input_name="$1"
    if ! QBLOG_RESOLVED_PATH="$(utils_resolve_project_path "$QBLOG_DOCS_DIR" "$input_name")"; then
        print_error "Blog no encontrado: $input_name"
        print_info "Usa 'main.sh list' para ver los blogs disponibles"
        exit 1
    fi
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    utils_check_quarto
    echo ""

    if [[ $# -eq 0 ]]; then
        interactive_mode "$QBLOG_DOCS_DIR" "$QBLOG_BACKUP_DIR"
        exit 0
    fi

    case "$1" in
        list)
            list_blogs "$QBLOG_DOCS_DIR"
            ;;
        render)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            render_blog "$QBLOG_RESOLVED_PATH"
            ;;
        preview)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            preview_blog "$QBLOG_RESOLVED_PATH" "${3:-$QBLOG_DEFAULT_PREVIEW_PORT}"
            ;;
        preview-browser)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            preview_blog_browser "$QBLOG_RESOLVED_PATH" "${3:-$QBLOG_DEFAULT_PREVIEW_PORT}"
            ;;
        clean)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            clean_blog "$QBLOG_RESOLVED_PATH"
            ;;
        publish)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            publish_blog "$QBLOG_RESOLVED_PATH" "${3:-$QBLOG_DEFAULT_PUBLISH_TARGET}"
            ;;
        check)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            check_blog "$QBLOG_RESOLVED_PATH"
            ;;
        inspect)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            inspect_blog "$QBLOG_RESOLVED_PATH"
            ;;
        list-posts)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            list_posts "$QBLOG_RESOLVED_PATH"
            ;;
        render-post)
            [[ -z "${2:-}" ]] && { print_error "Especifica la ruta del post"; exit 1; }
            render_post "$2"
            ;;
        new-post)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            create_post_interactive "$QBLOG_RESOLVED_PATH"
            ;;
        render-all)
            render_all_blogs "$QBLOG_DOCS_DIR"
            ;;
        clean-all)
            clean_all_blogs "$QBLOG_DOCS_DIR"
            ;;
        git-init)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            git_init "$QBLOG_RESOLVED_PATH"
            ;;
        git-status)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            git_status_blog "$QBLOG_RESOLVED_PATH"
            ;;
        git-commit)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del blog"; exit 1; }
            _resolve_or_die "$2"
            git_commit_push "$QBLOG_RESOLVED_PATH" "${3:-Update blog}"
            ;;
        convert)
            [[ -z "${2:-}" ]] && { print_error "Especifica el archivo a convertir"; exit 1; }
            convert_document "$2" "${3:-html}"
            ;;
        init-blog)
            [[ -z "${2:-}" ]] && { print_error "Especifica el nombre del nuevo blog"; exit 1; }
            init_blog "$QBLOG_DOCS_DIR" "$2" "${3:-}"
            ;;
        check-structure)
            check_structure_all "$QBLOG_DOCS_DIR"
            ;;
        backup)
            backup_blogs_interactive "$QBLOG_DOCS_DIR" "$QBLOG_BACKUP_DIR"
            ;;
        interactive|-i)
            interactive_mode "$QBLOG_DOCS_DIR" "$QBLOG_BACKUP_DIR"
            ;;
        help|-h|--help)
            show_help "$QBLOG_DOCS_DIR" "$QBLOG_BACKUP_DIR"
            ;;
        version|-v)
            quarto --version
            ;;
        *)
            print_error "Comando desconocido: $1"
            echo "Usa 'main.sh help' para ver la ayuda"
            exit 1
            ;;
    esac
}

main "$@"
