#!/usr/bin/env bash
# =============================================================================
# 02-utils.sh
# -----------------------------------------------------------------------------
# Utilidades compartidas: autodetección de ~/Documents, listado de proyectos
# de publicación (pub_* + website-achalma), verificación de exclusión, y
# detección de carpetas de posts dentro de un proyecto.
# =============================================================================

if [[ -n "${QBLOG_UTILS_LOADED:-}" ]]; then
    return 0
fi
QBLOG_UTILS_LOADED=1

# Autodetecta ~/Documents subiendo desde la ubicación de este script hasta
# encontrar una carpeta que contenga al menos un proyecto pub_* o
# "website-achalma". Si no se encuentra, falla con mensaje claro.
utils_detect_docs_dir() {
    if [[ -n "$QBLOG_DOCS_DIR" ]]; then
        echo "$QBLOG_DOCS_DIR"
        return 0
    fi

    local candidate
    candidate="$(cd "$QBLOG_SCRIPT_DIR/.." && pwd)"

    local i
    for ((i = 0; i < 6; i++)); do
        if compgen -G "$candidate/${QBLOG_PROJECT_PREFIX}*" > /dev/null 2>&1 || \
           [[ -d "$candidate/$QBLOG_WEBSITE_PROJECT" ]]; then
            echo "$candidate"
            return 0
        fi
        candidate="$(cd "$candidate/.." && pwd)"
    done

    return 1
}

# Verifica si un nombre de proyecto está en la lista de exclusión.
# $1 = nombre del proyecto (basename de la carpeta)
utils_is_excluded() {
    local project_name="$1"
    local excluded
    for excluded in "${QBLOG_EXCLUDED_PROJECTS[@]}"; do
        if [[ "$project_name" == "$excluded" ]]; then
            return 0
        fi
    done
    return 1
}

# Imprime, una ruta absoluta por línea, todos los proyectos gestionables
# (pub_* + website-achalma) dentro de Documents, excluyendo los que estén
# en QBLOG_EXCLUDED_PROJECTS. Solo incluye proyectos que parezcan blogs de
# Quarto reales (tienen index.qmd o _quarto.yml).
# $1 = ruta absoluta de Documents
utils_list_projects() {
    local docs_dir="$1"
    local project_dir
    local project_name

    while IFS= read -r -d '' project_dir; do
        project_name="$(basename "$project_dir")"
        utils_is_excluded "$project_name" && continue
        if [[ -f "$project_dir/index.qmd" ]] || [[ -f "$project_dir/_quarto.yml" ]]; then
            echo "$project_dir"
        fi
    done < <(find "$docs_dir" -mindepth 1 -maxdepth 1 -type d \
        \( -name "${QBLOG_PROJECT_PREFIX}*" -o -name "$QBLOG_WEBSITE_PROJECT" \) -print0 | sort -z)
}

# Resuelve el nombre corto de un proyecto a su ruta absoluta completa.
# Acepta tanto el nombre exacto de carpeta (ej: "pub_axiomata",
# "website-achalma") como variantes sin el prefijo "pub_" por comodidad
# (ej: "axiomata" se resuelve a "pub_axiomata" si existe).
# $1 = ruta absoluta de Documents
# $2 = nombre corto o exacto ingresado por el usuario
utils_resolve_project_path() {
    local docs_dir="$1"
    local input_name="$2"

    # Coincidencia exacta primero (incluye website-achalma)
    if [[ -d "$docs_dir/$input_name" ]]; then
        echo "$docs_dir/$input_name"
        return 0
    fi

    # Intentar con el prefijo pub_ añadido
    if [[ -d "$docs_dir/${QBLOG_PROJECT_PREFIX}${input_name}" ]]; then
        echo "$docs_dir/${QBLOG_PROJECT_PREFIX}${input_name}"
        return 0
    fi

    return 1
}

# Verifica si un nombre de subcarpeta debe ignorarse al detectar carpetas
# de posts (carpetas técnicas/generadas).
# $1 = nombre de carpeta
utils_is_ignored_dir() {
    local dirname="$1"
    local ignored
    for ignored in "${QBLOG_IGNORE_DIRS[@]}"; do
        [[ "$dirname" == "$ignored" ]] && return 0
    done
    return 1
}

# Detecta carpetas que contienen posts dentro de un proyecto (blog).
# Imprime, un nombre por línea (relativo al proyecto), las carpetas que
# contienen posts. Para la mayoría de proyectos pub_* esto son subcarpetas
# de primer nivel (ej: "python", "r", "posts"). Para "website-achalma" se
# reconoce además el caso especial "blog/posts", ya que ahí los posts viven
# un nivel más abajo (blog_path/blog/posts/<fecha-slug>/index.qmd).
# $1 = ruta absoluta del proyecto/blog
utils_detect_post_folders() {
    local blog_path="$1"
    local dir
    local dir_name

    # Caso especial: website-achalma/blog/posts
    if [[ "$(basename "$blog_path")" == "$QBLOG_WEBSITE_PROJECT" ]] && [[ -d "$blog_path/blog/posts" ]]; then
        echo "blog/posts"
    fi
    if [[ "$(basename "$blog_path")" == "$QBLOG_WEBSITE_PROJECT" ]] && [[ -d "$blog_path/talk" ]]; then
        echo "talk"
    fi

    for dir in "$blog_path"/*/; do
        [[ -d "$dir" ]] || continue
        dir_name="$(basename "$dir")"
        utils_is_ignored_dir "$dir_name" && continue
        [[ "$dir_name" == .* ]] && continue
        # Evitar listar "blog" suelto cuando ya se manejó como "blog/posts"
        if [[ "$(basename "$blog_path")" == "$QBLOG_WEBSITE_PROJECT" ]] && [[ "$dir_name" == "blog" ]]; then
            continue
        fi

        if find "$dir" -maxdepth 2 -name "index.qmd" 2>/dev/null | grep -q . || \
           [[ -f "$dir/_metadata.yml" ]]; then
            echo "$dir_name"
        fi
    done
}

# Verifica que Quarto esté instalado, y muestra su versión.
utils_check_quarto() {
    if ! command -v quarto &> /dev/null; then
        print_error "Quarto no está instalado"
        echo "Por favor instala Quarto desde: https://quarto.org/docs/get-started/"
        exit 1
    fi

    local version
    version="$(quarto --version)"
    print_info "Quarto versión: $version"
}
