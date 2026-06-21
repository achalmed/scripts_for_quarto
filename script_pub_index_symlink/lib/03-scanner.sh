#!/usr/bin/env bash
# =============================================================================
# 03-scanner.sh
# -----------------------------------------------------------------------------
# Recorre:
#   1) Todas las carpetas "pub_*" dentro de Documents, buscando en CUALQUIER
#      nivel de profundidad carpetas cuyo nombre empiece con YYYY-MM-DD-,
#      ignorando las carpetas técnicas (_freeze, _site, .git, etc.)
#   2) La carpeta "website-achalma", solo dentro de blog/posts y talk.
#
# Resultado: imprime, una ruta absoluta por línea, todas las carpetas de
# publicación encontradas. No crea ni modifica nada — es de solo lectura.
# =============================================================================

if [[ -n "${PUBINDEX_SCANNER_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_SCANNER_LOADED=1

# Construye la expresión "-name X -o -name Y ..." para que find pode (prune)
# las carpetas ignoradas en cualquier nivel.
_scanner_build_prune_expr() {
    local expr=()
    local first=1
    local dir
    for dir in "${PUBINDEX_IGNORE_DIRS[@]}"; do
        if [[ $first -eq 1 ]]; then
            expr+=(-name "$dir")
            first=0
        else
            expr+=(-o -name "$dir")
        fi
    done
    printf '%s\n' "${expr[@]}"
}

# Escanea un proyecto pub_* completo: busca en cualquier profundidad
# carpetas que calcen con el patrón de fecha, podando las carpetas técnicas.
# $1 = ruta absoluta del proyecto pub_*
scanner_scan_pub_project() {
    local project_dir="$1"
    local -a prune_expr
    mapfile -t prune_expr < <(_scanner_build_prune_expr)

    # find: poda (no entra) en carpetas ignoradas, y de las que SÍ recorre,
    # imprime las que son directorios con nombre que calza el patrón de fecha.
    # IMPORTANTE: el regex usa [^/]* (no .*) al final para anclar el patrón
    # al ÚLTIMO componente de la ruta (el nombre de carpeta en sí). Si se
    # usara .*, también calzarían subcarpetas internas como
    # ".../2025-05-10-mi-post/index_files" o "/index_files/figure-pdf",
    # porque .* consume cualquier cosa después de la fecha, incluyendo
    # más segmentos de ruta con más "/".
    find "$project_dir" -mindepth 1 \
        \( -type d \( "${prune_expr[@]}" \) -prune \) -o \
        \( -type d -regextype posix-extended -regex ".*/[0-9]{4}-[0-9]{2}-[0-9]{2}-[^/]*" -print \)
}

# Escanea las subcarpetas específicas de website-achalma (blog/posts, talk).
# Solo busca un nivel: carpetas directas dentro de esas subcarpetas.
# $1 = ruta absoluta de website-achalma
scanner_scan_website_project() {
    local website_dir="$1"
    local sub
    for sub in "${PUBINDEX_WEBSITE_SUBDIRS[@]}"; do
        local full_sub="$website_dir/$sub"
        [[ -d "$full_sub" ]] || continue
        find "$full_sub" -mindepth 1 -maxdepth 1 -type d \
            -regextype posix-extended -regex ".*/[0-9]{4}-[0-9]{2}-[0-9]{2}-[^/]*" -print
    done
}

# Función principal de escaneo: recorre Documents buscando todos los
# proyectos pub_* + website-achalma, y devuelve (stdout) la lista completa
# de rutas absolutas de publicaciones encontradas, una por línea.
# $1 = ruta absoluta de Documents
scanner_find_all_publications() {
    local docs_dir="$1"
    local project_dir

    # --- Proyectos pub_* (un nivel dentro de Documents) ---
    while IFS= read -r -d '' project_dir; do
        scanner_scan_pub_project "$project_dir"
    done < <(find "$docs_dir" -mindepth 1 -maxdepth 1 -type d -name "${PUBINDEX_PROJECT_PREFIX}*" -print0)

    # --- website-achalma (caso especial) ---
    local website_dir="$docs_dir/$PUBINDEX_WEBSITE_PROJECT"
    if [[ -d "$website_dir" ]]; then
        scanner_scan_website_project "$website_dir"
    else
        log_warn "No se encontró la carpeta '$PUBINDEX_WEBSITE_PROJECT' dentro de $docs_dir (se omite)"
    fi
}
