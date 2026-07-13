#!/usr/bin/env bash
# =============================================================================
# 05-broken-detector.sh
# -----------------------------------------------------------------------------
# Detecta symlinks rotos dentro de "04 index" (es decir, symlinks cuyo
# destino ya no existe — por ejemplo porque borraste o moviste una carpeta
# de publicación en el proyecto original). Solo reporta; no borra nada salvo
# que se invoque explícitamente la función de limpieza desde main.sh con
# confirmación del usuario.
# =============================================================================

if [[ -n "${PUBINDEX_BROKEN_DETECTOR_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_BROKEN_DETECTOR_LOADED=1

# Busca todos los symlinks rotos dentro de "04 index" (recursivo, year/post).
# Imprime una ruta absoluta por línea (la ruta del symlink, no del destino).
# $1 = ruta absoluta de "04 index"
broken_detector_find_broken() {
    local index_dir="$1"
    # -xtype l con find: localiza symlinks cuyo destino final no existe.
    find "$index_dir" -mindepth 2 -maxdepth 2 -xtype l 2>/dev/null
}

# Reporta (log) los symlinks rotos encontrados. Devuelve por stdout el total.
# $1 = ruta absoluta de "04 index"
broken_detector_report() {
    local index_dir="$1"
    local broken_list
    broken_list="$(broken_detector_find_broken "$index_dir")"

    if [[ -z "$broken_list" ]]; then
        log_ok "No se encontraron symlinks rotos."
        echo 0
        return 0
    fi

    local count=0
    local link
    while IFS= read -r link; do
        [[ -z "$link" ]] && continue
        local target
        target="$(readlink "$link")"
        log_warn "Symlink roto: ${link#"$index_dir"/} (apuntaba a: $target)"
        count=$((count + 1))
    done <<< "$broken_list"

    echo "$count"
}

# Elimina los symlinks rotos encontrados (usar con confirmación previa).
# $1 = ruta absoluta de "04 index"
broken_detector_clean() {
    local index_dir="$1"
    local broken_list
    broken_list="$(broken_detector_find_broken "$index_dir")"

    [[ -z "$broken_list" ]] && return 0

    local link
    local removed=0
    while IFS= read -r link; do
        [[ -z "$link" ]] && continue
        rm -f "$link"
        log_ok "Symlink roto eliminado: ${link#"$index_dir"/}"
        removed=$((removed + 1))
    done <<< "$broken_list"

    echo "$removed"
}
