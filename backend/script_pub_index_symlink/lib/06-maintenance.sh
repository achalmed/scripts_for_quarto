#!/usr/bin/env bash
# =============================================================================
# 06-maintenance.sh
# -----------------------------------------------------------------------------
# Utilidades adicionales que complementan la gestión de symlinks:
#   - Eliminar carpetas de año ("04 index/2018", etc.) que quedaron vacías
#     después de limpiar symlinks rotos.
#   - Mostrar un resumen estadístico de cuántas publicaciones hay indexadas
#     por año.
# =============================================================================

if [[ -n "${PUBINDEX_MAINTENANCE_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_MAINTENANCE_LOADED=1

# Elimina subcarpetas de año dentro de "04 index" que estén vacías.
# $1 = ruta absoluta de "04 index"
maintenance_remove_empty_year_dirs() {
    local index_dir="$1"
    local removed=0
    local year_dir

    while IFS= read -r -d '' year_dir; do
        if [[ -z "$(ls -A "$year_dir" 2>/dev/null)" ]]; then
            rmdir "$year_dir"
            log_ok "Carpeta de año vacía eliminada: $(basename "$year_dir")"
            removed=$((removed + 1))
        fi
    done < <(find "$index_dir" -mindepth 1 -maxdepth 1 -type d -print0)

    echo "$removed"
}

# Muestra un resumen: cuántos symlinks (publicaciones) hay por año dentro
# de "04 index".
# $1 = ruta absoluta de "04 index"
maintenance_print_summary() {
    local index_dir="$1"

    log_section "Resumen de '04 index' por año"

    local year_dir
    local total=0
    while IFS= read -r -d '' year_dir; do
        local year
        year="$(basename "$year_dir")"
        local count
        count="$(find "$year_dir" -mindepth 1 -maxdepth 1 -type l | wc -l)"
        total=$((total + count))
        printf '  %s%s%s : %s publicaciones\n' "$PUBINDEX_C_BOLD" "$year" "$PUBINDEX_C_RESET" "$count"
    done < <(find "$index_dir" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

    printf '\n  %sTotal indexado: %s%s\n' "$PUBINDEX_C_BOLD" "$total" "$PUBINDEX_C_RESET"
}
