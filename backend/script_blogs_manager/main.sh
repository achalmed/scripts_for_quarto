#!/usr/bin/env bash
# =============================================================================
# main.sh — Gestor de Publicaciones Quarto (blog-manager)
# -----------------------------------------------------------------------------
# Reestructuración modular del antiguo build.sh monolítico (la versión de la
# suite, QBLOG_VERSION, se declara una sola vez en lib/00-config.sh).
# Conserva TODAS las funciones originales (listado, render, preview, clean,
# publish, asistente de creación de posts APAQuarto, operaciones Git,
# operaciones masivas, init-blog, check-structure, backups, menú
# interactivo), reorganizadas en módulos independientes dentro de lib/, y
# adaptadas para escanear website-achalma y sus submódulos
# website-achalma/_pubs/pub_* dentro de ~/Documents (en vez de una carpeta
# "publicaciones/" separada).
#
# Uso:
#   ./main.sh                       Modo interactivo (menú)
#   ./main.sh list                  Lista todos los blogs
#   ./main.sh help                  Ayuda completa
#   ./main.sh publish <blog>        Simula: corre la puerta R6 y dice qué empujaría
#   ./main.sh publish <blog> --aplicar
#   ./main.sh git-commit <blog> "mensaje" [--aplicar]
#
# Variables de entorno opcionales:
#   DOCS_ROOT          Fuerza la raíz del workspace (por defecto, la de core/env.sh)
#   QBLOG_BACKUP_DIR   Fuerza la ruta del directorio de backups
# =============================================================================

set -uo pipefail

# --- Localización del propio script ------------------------------------------
QBLOG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QBLOG_LIB_DIR="$QBLOG_SCRIPT_DIR/lib"

# --- Raíz del workspace: core/env.sh da DOCS_ROOT e INDEX_DIR (normativa 5.1-5.2) --
# Se sube desde la carpeta del script hasta hallar core/env.sh; un DOCS_ROOT previo
# en el entorno se respeta (así lo fija la GUI). Sin core/ la suite no arranca.
_core_d="$QBLOG_SCRIPT_DIR"
while [[ "$_core_d" != / && ! -f "$_core_d/core/env.sh" ]]; do _core_d="$(dirname "$_core_d")"; done
# shellcheck source=/dev/null
source "$_core_d/core/env.sh" || { echo "blogs_manager: no encuentro core/env.sh (exporta DOCS_ROOT)" >&2; exit 1; }
unset _core_d

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
DOCS_ROOT="$(utils_detect_docs_dir)" || {
    print_error "No se pudo resolver la raíz del workspace (core/env.sh)."
    print_error "Defínela manualmente, ej: DOCS_ROOT=\"\$HOME/Documents\" ./main.sh"
    exit 1
}

# --- Directorio de backups (autodetectado relativo a Documents, salvo override)
QBLOG_BACKUP_DIR="${QBLOG_BACKUP_DIR:-$DOCS_ROOT/06 archives/backups-publicaciones}"

# Helper interno: resuelve un nombre de blog ingresado por el usuario a su
# ruta absoluta, dejándola en la variable global QBLOG_RESOLVED_PATH. Si no
# existe, imprime un error claro y termina el script. IMPORTANTE: se usa
# como una sentencia normal (no via "$(...)") precisamente para que el
# exit se propague al proceso principal en vez de quedar atrapado en una
# subshell de command substitution.
QBLOG_RESOLVED_PATH=""
_resolve_or_die() {
    local input_name="$1"
    if ! QBLOG_RESOLVED_PATH="$(utils_resolve_project_path "$DOCS_ROOT" "$input_name")"; then
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
        interactive_mode "$DOCS_ROOT" "$QBLOG_BACKUP_DIR"
        exit 0
    fi

    case "$1" in
        list)
            list_blogs "$DOCS_ROOT"
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
            render_all_blogs "$DOCS_ROOT"
            ;;
        clean-all)
            clean_all_blogs "$DOCS_ROOT"
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
            init_blog "$DOCS_ROOT" "$2" "${3:-}"
            ;;
        check-structure)
            check_structure_all "$DOCS_ROOT"
            ;;
        backup)
            backup_blogs_interactive "$DOCS_ROOT" "$QBLOG_BACKUP_DIR"
            ;;
        interactive|-i)
            interactive_mode "$DOCS_ROOT" "$QBLOG_BACKUP_DIR"
            ;;
        help|-h|--help)
            show_help "$DOCS_ROOT" "$QBLOG_BACKUP_DIR"
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

# --- Simular primero: `--aplicar` (en cualquier posición) es lo único que deja
#     actuar a `publish` y `git-commit`; `--dry-run` se acepta y simula (normativa 5.10).
_qblog_args=()
_qblog_banderas=0
for _qblog_a in "$@"; do
    case "$_qblog_a" in
        --aplicar) QBLOG_APLICAR=1; _qblog_banderas=1 ;;
        --dry-run|--simular) QBLOG_APLICAR=0; _qblog_banderas=1 ;;
        *) _qblog_args+=("$_qblog_a") ;;
    esac
done
set -- "${_qblog_args[@]}"
# Una bandera sin comando no abre el menú: no hay nada que simular ni que aplicar.
if [[ $# -eq 0 && $_qblog_banderas -eq 1 ]]; then
    print_info "Sin comando: nada que simular ni aplicar. Usa 'main.sh help'."
    (( QBLOG_APLICAR )) && exit 2
    exit 0
fi
unset _qblog_a _qblog_args _qblog_banderas

main "$@"
