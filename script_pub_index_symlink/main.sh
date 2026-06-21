#!/usr/bin/env bash
# =============================================================================
# main.sh — pub-index-sync
# -----------------------------------------------------------------------------
# Orquesta todos los módulos en lib/ para mantener "04 index" actualizado
# con symlinks (organizados por año) a todas las carpetas de publicación
# encontradas dentro de los proyectos pub_* y website-achalma/{blog/posts,talk}.
#
# Uso:
#   ./main.sh                  Ejecuta sincronización completa (modo normal)
#   ./main.sh --dry-run        Simula sin crear/modificar/borrar nada
#   ./main.sh --check-broken   Solo reporta symlinks rotos, no sincroniza
#   ./main.sh --clean-broken   Reporta y elimina symlinks rotos (con confirmación)
#   ./main.sh --summary        Solo muestra el resumen por año
#   ./main.sh --no-summary     Sincroniza pero omite el resumen final
#   ./main.sh --help           Muestra esta ayuda
#
# Variables de entorno opcionales:
#   PUBINDEX_DOCS_DIR   Fuerza la ruta de ~/Documents si la autodetección falla
# =============================================================================

set -uo pipefail

# --- Localización del propio script (para poder ejecutarse desde cualquier
#     directorio) -------------------------------------------------------------
PUBINDEX_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBINDEX_LIB_DIR="$PUBINDEX_SCRIPT_DIR/lib"

# --- Carga de módulos en orden ------------------------------------------------
# shellcheck source=lib/00-config.sh
source "$PUBINDEX_LIB_DIR/00-config.sh"
# shellcheck source=lib/01-logging.sh
source "$PUBINDEX_LIB_DIR/01-logging.sh"
# shellcheck source=lib/02-utils.sh
source "$PUBINDEX_LIB_DIR/02-utils.sh"
# shellcheck source=lib/03-scanner.sh
source "$PUBINDEX_LIB_DIR/03-scanner.sh"
# shellcheck source=lib/04-symlinker.sh
source "$PUBINDEX_LIB_DIR/04-symlinker.sh"
# shellcheck source=lib/05-broken-detector.sh
source "$PUBINDEX_LIB_DIR/05-broken-detector.sh"
# shellcheck source=lib/06-maintenance.sh
source "$PUBINDEX_LIB_DIR/06-maintenance.sh"

# --- Preparar carpeta de logs -------------------------------------------------
mkdir -p "$PUBINDEX_SCRIPT_DIR/logs"
PUBINDEX_LOG_FILE="$PUBINDEX_SCRIPT_DIR/logs/$(date '+%Y-%m-%d').log"

# --- Parseo de argumentos -----------------------------------------------------
PUBINDEX_MODE="sync"
PUBINDEX_DRY_RUN=0
PUBINDEX_SHOW_SUMMARY=1

print_help() {
    sed -n '2,21p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            PUBINDEX_DRY_RUN=1
            shift
            ;;
        --check-broken)
            PUBINDEX_MODE="check-broken"
            shift
            ;;
        --clean-broken)
            PUBINDEX_MODE="clean-broken"
            shift
            ;;
        --summary)
            PUBINDEX_MODE="summary"
            shift
            ;;
        --no-summary)
            PUBINDEX_SHOW_SUMMARY=0
            shift
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            log_error "Argumento desconocido: $1"
            print_help
            exit 1
            ;;
    esac
done

# --- Detectar Documents y carpeta destino "04 index" --------------------------
PUBINDEX_DOCS_DIR="$(utils_detect_docs_dir)" || {
    log_error "No se pudo autodetectar la carpeta Documents (que contenga '04 index')."
    log_error "Defínela manualmente, ej: PUBINDEX_DOCS_DIR=/home/achalmaedison/Documents ./main.sh"
    exit 1
}
PUBINDEX_INDEX_DIR="$PUBINDEX_DOCS_DIR/$PUBINDEX_TARGET_DIRNAME"

if [[ ! -d "$PUBINDEX_INDEX_DIR" ]]; then
    log_error "La carpeta destino no existe: $PUBINDEX_INDEX_DIR"
    exit 1
fi

log_info "Documents detectado en: $PUBINDEX_DOCS_DIR"
log_info "Carpeta índice: $PUBINDEX_INDEX_DIR"
[[ "$PUBINDEX_DRY_RUN" == "1" ]] && log_warn "Modo dry-run activado: no se escribirá ni borrará nada."

# =============================================================================
# Flujo principal según el modo
# =============================================================================

run_sync() {
    log_section "Escaneando proyectos pub_* y website-achalma"
    local publications
    publications="$(scanner_find_all_publications "$PUBINDEX_DOCS_DIR")"

    local total_found
    total_found="$(echo "$publications" | grep -c . || true)"
    log_info "Publicaciones encontradas: $total_found"

    log_section "Sincronizando symlinks en '04 index'"
    symlinker_reset_counters
    symlinker_process_all "$PUBINDEX_INDEX_DIR" "$PUBINDEX_DRY_RUN" < <(echo "$publications")

    log_section "Resultado de la sincronización"
    log_info "Creados:    $PUBINDEX_COUNT_CREATED"
    log_info "Actualizados: $PUBINDEX_COUNT_UPDATED"
    log_info "Omitidos (ya existían): $PUBINDEX_COUNT_SKIPPED"
    if [[ "$PUBINDEX_COUNT_CONFLICT" -gt 0 ]]; then
        log_warn "Conflictos (no symlink, requieren revisión manual): $PUBINDEX_COUNT_CONFLICT"
    fi

    log_section "Verificando symlinks rotos"
    broken_detector_report "$PUBINDEX_INDEX_DIR" > /dev/null

    if [[ "$PUBINDEX_SHOW_SUMMARY" == "1" ]]; then
        maintenance_print_summary "$PUBINDEX_INDEX_DIR"
    fi
}

run_check_broken() {
    log_section "Buscando symlinks rotos en '04 index'"
    local count
    count="$(broken_detector_report "$PUBINDEX_INDEX_DIR")"
    log_info "Total de symlinks rotos: $count"
}

run_clean_broken() {
    log_section "Buscando symlinks rotos en '04 index'"
    local count
    count="$(broken_detector_report "$PUBINDEX_INDEX_DIR")"

    if [[ "$count" -eq 0 ]]; then
        return 0
    fi

    log_warn "Se encontraron $count symlinks rotos."
    if [[ "$PUBINDEX_DRY_RUN" == "1" ]]; then
        log_info "[dry-run] No se eliminará nada."
        return 0
    fi

    if utils_confirm "¿Eliminar estos $count symlinks rotos?"; then
        local removed
        removed="$(broken_detector_clean "$PUBINDEX_INDEX_DIR")"
        log_ok "Symlinks rotos eliminados: $removed"

        log_section "Limpiando carpetas de año vacías"
        local removed_dirs
        removed_dirs="$(maintenance_remove_empty_year_dirs "$PUBINDEX_INDEX_DIR")"
        log_info "Carpetas de año eliminadas: $removed_dirs"
    else
        log_info "Operación cancelada por el usuario."
    fi
}

run_summary() {
    maintenance_print_summary "$PUBINDEX_INDEX_DIR"
}

case "$PUBINDEX_MODE" in
    sync)
        run_sync
        ;;
    check-broken)
        run_check_broken
        ;;
    clean-broken)
        run_clean_broken
        ;;
    summary)
        run_summary
        ;;
esac

log_info "Log guardado en: $PUBINDEX_LOG_FILE"
