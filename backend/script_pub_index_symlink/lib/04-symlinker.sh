#!/usr/bin/env bash
# =============================================================================
# 04-symlinker.sh
# -----------------------------------------------------------------------------
# Crea/actualiza los symlinks dentro de "04 index/<AÑO>/<nombre-original>"
# apuntando a las carpetas de publicación reales encontradas por el scanner.
#
# Reglas:
#   - Si el symlink ya existe y apunta correctamente -> se omite (sin tocar).
#   - Si el symlink ya existe pero apunta a otro destino -> se actualiza.
#   - Si existe un archivo/carpeta real (no symlink) con ese nombre -> se
#     reporta como conflicto y NO se toca (para no perder datos del usuario).
#   - Si no existe nada -> se crea el symlink nuevo.
# =============================================================================

if [[ -n "${PUBINDEX_SYMLINKER_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_SYMLINKER_LOADED=1

# Contadores globales de la corrida (se resetean en symlinker_reset_counters)
PUBINDEX_COUNT_CREATED=0
PUBINDEX_COUNT_SKIPPED=0
PUBINDEX_COUNT_UPDATED=0
PUBINDEX_COUNT_CONFLICT=0

symlinker_reset_counters() {
    PUBINDEX_COUNT_CREATED=0
    PUBINDEX_COUNT_SKIPPED=0
    PUBINDEX_COUNT_UPDATED=0
    PUBINDEX_COUNT_CONFLICT=0
}

# Procesa UNA publicación: crea/actualiza/omite su symlink en 04 index/<año>/
# $1 = ruta absoluta real de la carpeta de publicación
# $2 = ruta absoluta de la carpeta "04 index"
# $3 = "1" para modo dry-run (no escribe nada, solo reporta), "0" para ejecutar
symlinker_process_publication() {
    local real_path="$1"
    local index_dir="$2"
    local dry_run="$3"

    local base_name
    base_name="$(basename "$real_path")"
    local year
    year="$(utils_extract_year "$base_name")"

    local year_dir="$index_dir/$year"
    local link_path="$year_dir/$base_name"

    # Crea la carpeta del año si no existe
    if [[ ! -d "$year_dir" ]]; then
        if [[ "$dry_run" == "1" ]]; then
            log_info "[dry-run] Crearía carpeta de año: $year_dir"
        else
            mkdir -p "$year_dir"
        fi
    fi

    if [[ -L "$link_path" ]]; then
        # Ya existe un symlink con ese nombre: comparamos destino
        local current_target
        current_target="$(readlink -f "$link_path" 2>/dev/null || true)"
        local expected_target
        expected_target="$(readlink -f "$real_path" 2>/dev/null || echo "$real_path")"

        if [[ "$current_target" == "$expected_target" ]]; then
            PUBINDEX_COUNT_SKIPPED=$((PUBINDEX_COUNT_SKIPPED + 1))
            return 0
        else
            # Apunta a otro lado: actualizar
            if [[ "$dry_run" == "1" ]]; then
                log_info "[dry-run] Actualizaría symlink: $link_path -> $real_path"
            else
                ln -sfn "$real_path" "$link_path"
                log_ok "Symlink actualizado: $year/$base_name"
            fi
            PUBINDEX_COUNT_UPDATED=$((PUBINDEX_COUNT_UPDATED + 1))
            return 0
        fi
    elif [[ -e "$link_path" ]]; then
        # Existe algo real (no symlink) con ese nombre: conflicto, no tocar
        log_warn "Conflicto (existe archivo/carpeta real, no symlink): $year/$base_name"
        PUBINDEX_COUNT_CONFLICT=$((PUBINDEX_COUNT_CONFLICT + 1))
        return 0
    else
        # No existe nada: crear symlink nuevo
        if [[ "$dry_run" == "1" ]]; then
            log_info "[dry-run] Crearía symlink: $year/$base_name"
        else
            ln -s "$real_path" "$link_path"
            log_ok "Symlink creado: $year/$base_name"
        fi
        PUBINDEX_COUNT_CREATED=$((PUBINDEX_COUNT_CREATED + 1))
        return 0
    fi
}

# Procesa una lista completa de publicaciones (rutas, una por línea via stdin)
# $1 = ruta absoluta de "04 index"
# $2 = "1" para dry-run, "0" para ejecutar
symlinker_process_all() {
    local index_dir="$1"
    local dry_run="$2"
    local real_path

    while IFS= read -r real_path; do
        [[ -z "$real_path" ]] && continue
        symlinker_process_publication "$real_path" "$index_dir" "$dry_run"
    done
}
