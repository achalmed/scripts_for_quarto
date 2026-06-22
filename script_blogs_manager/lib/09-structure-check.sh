#!/usr/bin/env bash
# =============================================================================
# 09-structure-check.sh
# -----------------------------------------------------------------------------
# Verifica y reporta la integridad estructural de todos los blogs
# gestionables: archivos esenciales, directorios, configuración Git,
# sintaxis YAML. Equivalente al antiguo check-structure.sh.
# =============================================================================

if [[ -n "${QBLOG_STRUCTURE_CHECK_LOADED:-}" ]]; then
    return 0
fi
QBLOG_STRUCTURE_CHECK_LOADED=1

# Verifica un solo blog y muestra el detalle. Devuelve por stdout (al final,
# via echo) la cantidad de issues encontrados, para que el llamador lo capture.
# $1 = ruta absoluta del blog
_structure_check_one_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"
    local issues=0

    echo "" >&2
    echo -e "${QBLOG_BLUE}📁 $blog_name${QBLOG_NC}" >&2

    if [[ -f "$blog_path/_quarto.yml" ]]; then
        print_success "_quarto.yml existe" >&2
    else
        print_error "_quarto.yml NO encontrado" >&2
        issues=$((issues + 1))
    fi

    if [[ -f "$blog_path/index.qmd" ]]; then
        print_success "index.qmd existe" >&2
    else
        print_error "index.qmd NO encontrado" >&2
        issues=$((issues + 1))
    fi

    if [[ -d "$blog_path/posts" ]]; then
        local post_count
        post_count=$(find "$blog_path/posts" -name "index.qmd" 2>/dev/null | wc -l)
        print_success "Directorio posts/ existe ($post_count posts encontrados)" >&2
    else
        print_warning "Directorio posts/ no existe" >&2
    fi

    if [[ -d "$blog_path/assets" ]]; then
        print_success "Directorio assets/ existe" >&2
    else
        print_warning "Directorio assets/ no existe" >&2
    fi

    if [[ -f "$blog_path/.gitignore" ]]; then
        print_success ".gitignore existe" >&2
    else
        print_warning ".gitignore no existe" >&2
    fi

    if [[ -d "$blog_path/.git" ]]; then
        print_success "Es un repositorio Git" >&2

        cd "$blog_path" || true
        if git remote -v 2>/dev/null | grep -q "origin"; then
            local remote
            remote=$(git remote get-url origin 2>/dev/null)
            print_success "Remote configurado: $remote" >&2
        else
            print_warning "No hay remote configurado" >&2
        fi
    else
        print_warning "No es un repositorio Git" >&2
    fi

    if [[ -d "$blog_path/_site" ]]; then
        local size
        size=$(du -sh "$blog_path/_site" 2>/dev/null | cut -f1)
        print_info "Sitio generado existe ($size)" >&2
    fi

    if command -v yq &> /dev/null; then
        if yq eval "$blog_path/_quarto.yml" > /dev/null 2>&1; then
            print_success "YAML válido" >&2
        else
            print_error "YAML tiene errores de sintaxis" >&2
            issues=$((issues + 1))
        fi
    fi

    if [[ $issues -eq 0 ]]; then
        echo -e "  ${QBLOG_GREEN}Estado: OK${QBLOG_NC}" >&2
    elif [[ $issues -le 2 ]]; then
        echo -e "  ${QBLOG_YELLOW}Estado: Revisar${QBLOG_NC}" >&2
    else
        echo -e "  ${QBLOG_RED}Estado: Requiere atención${QBLOG_NC}" >&2
    fi

    echo "$issues"
}

# Verifica todos los blogs gestionables y muestra un resumen general.
# $1 = ruta absoluta de Documents
check_structure_all() {
    local docs_dir="$1"
    print_header "Verificación de Estructura de Blogs"

    local total_blogs=0
    local total_issues=0
    local blogs_ok=0
    local blogs_warning=0
    local blogs_error=0
    local blog issues

    while IFS= read -r blog; do
        [[ -z "$blog" ]] && continue
        issues="$(_structure_check_one_blog "$blog")"

        total_blogs=$((total_blogs + 1))
        total_issues=$((total_issues + issues))

        if [[ $issues -eq 0 ]]; then
            blogs_ok=$((blogs_ok + 1))
        elif [[ $issues -le 2 ]]; then
            blogs_warning=$((blogs_warning + 1))
        else
            blogs_error=$((blogs_error + 1))
        fi
    done < <(utils_list_projects "$docs_dir")

    echo ""
    print_header "Resumen General"
    echo ""
    echo -e "Total de blogs: ${QBLOG_CYAN}$total_blogs${QBLOG_NC}"
    echo -e "${QBLOG_GREEN}✓ OK:${QBLOG_NC} $blogs_ok"
    echo -e "${QBLOG_YELLOW}⚠ Revisar:${QBLOG_NC} $blogs_warning"
    echo -e "${QBLOG_RED}✗ Problemas:${QBLOG_NC} $blogs_error"
    echo ""
    echo -e "Total de issues encontrados: $total_issues"
    echo ""

    if [[ $blogs_warning -gt 0 ]] || [[ $blogs_error -gt 0 ]]; then
        echo -e "${QBLOG_YELLOW}Recomendaciones:${QBLOG_NC}"
        echo "  • Para crear archivos faltantes, usa: main.sh init-blog NOMBRE"
        echo "  • Para inicializar Git: main.sh git-init BLOG"
        echo "  • Para verificar sintaxis: main.sh check BLOG"
    fi
}
