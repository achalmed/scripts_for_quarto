#!/usr/bin/env bash
# =============================================================================
# 03-listing.sh
# -----------------------------------------------------------------------------
# Listado de proyectos (blogs) y de posts dentro de un proyecto. Misma
# lógica y presentación visual del script original, adaptada para escanear
# directamente pub_* + website-achalma en lugar de una carpeta
# "publicaciones/" contenedora.
# =============================================================================

if [[ -n "${QBLOG_LISTING_LOADED:-}" ]]; then
    return 0
fi
QBLOG_LISTING_LOADED=1

# Lista todos los proyectos/blogs gestionables con información adicional:
# título (desde _quarto.yml), cantidad de posts, y estado de Git.
# $1 = ruta absoluta de Documents
list_blogs() {
    local docs_dir="$1"
    print_header "Blogs Disponibles"

    local counter=1
    local total_blogs=0
    local blog
    local blog_name

    while IFS= read -r blog; do
        [[ -z "$blog" ]] && continue
        blog_name="$(basename "$blog")"

        echo -e "${QBLOG_MAGENTA}${QBLOG_BOLD}$counter.${QBLOG_NC} ${QBLOG_GREEN}$QBLOG_E_BOOK $blog_name${QBLOG_NC}"

        # Mostrar título si existe _quarto.yml
        if [[ -f "$blog/_quarto.yml" ]]; then
            local title
            title="$(grep "^\s*title:" "$blog/_quarto.yml" | head -1 | sed 's/.*title:\s*//' | tr -d '"')"
            [[ -n "$title" ]] && echo -e "   ${QBLOG_DIM}$title${QBLOG_NC}"
        fi

        # Contar posts en todas las subcarpetas
        local post_count=0
        local subdir
        for subdir in "$blog"/*/; do
            [[ -d "$subdir" ]] || continue
            post_count=$((post_count + $(find "$subdir" -name "index.qmd" 2>/dev/null | wc -l)))
        done
        [[ $post_count -gt 0 ]] && echo -e "   ${QBLOG_DIM}$QBLOG_E_FILE $post_count posts${QBLOG_NC}"

        # Estado de Git
        [[ -d "$blog/.git" ]] && echo -e "   ${QBLOG_DIM}$QBLOG_E_GIT Git inicializado${QBLOG_NC}"

        echo ""
        counter=$((counter + 1))
        total_blogs=$((total_blogs + 1))
    done < <(utils_list_projects "$docs_dir")

    echo -e "${QBLOG_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${QBLOG_NC}"
    echo -e "${QBLOG_BOLD}Total: $total_blogs blogs${QBLOG_NC}"
    echo ""
}

# Lista todos los posts de un blog, agrupados por carpeta temática
# (python, r, latex, blog/posts, talk, etc.), mostrando título y fecha
# extraídos del YAML de cada index.qmd.
# $1 = ruta absoluta del blog
list_posts() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Posts en $blog_name"

    local post_folders=()
    local post_folder_names=()
    while IFS= read -r folder_name; do
        if [[ -n "$folder_name" ]]; then
            post_folders+=("$blog_path/$folder_name")
            post_folder_names+=("$folder_name")
        fi
    done < <(utils_detect_post_folders "$blog_path")

    if [[ ${#post_folders[@]} -eq 0 ]]; then
        print_warning "No se encontraron carpetas con posts"
        return
    fi

    local idx
    for idx in "${!post_folders[@]}"; do
        local folder="${post_folders[$idx]}"
        local folder_name="${post_folder_names[$idx]}"
        print_subheader "$QBLOG_E_FOLDER $folder_name"

        local counter=1
        local post
        for post in "$folder"/*/index.qmd; do
            [[ -f "$post" ]] || continue
            local post_dir
            post_dir="$(dirname "$post")"
            local post_name
            post_name="$(basename "$post_dir")"

            echo -e "${QBLOG_MAGENTA}  $counter.${QBLOG_NC} ${QBLOG_GREEN}$post_name${QBLOG_NC}"

            local title
            title="$(grep -m 1 "^title:" "$post" | sed 's/.*title:\s*//' | tr -d '"' | sed 's/^"\|"$//g')"
            [[ -n "$title" ]] && echo -e "     ${QBLOG_DIM}📝 $title${QBLOG_NC}"

            local post_date
            post_date="$(grep -m 1 "^date:" "$post" | sed 's/.*date:\s*//' | tr -d '"')"
            [[ -n "$post_date" ]] && echo -e "     ${QBLOG_DIM}📅 $post_date${QBLOG_NC}"

            echo -e "     ${QBLOG_DIM}📂 $post_dir${QBLOG_NC}"
            echo ""

            counter=$((counter + 1))
        done
    done
}
