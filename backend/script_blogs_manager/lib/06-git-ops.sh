#!/usr/bin/env bash
# =============================================================================
# 06-git-ops.sh
# -----------------------------------------------------------------------------
# Operaciones de Git sobre un blog/proyecto individual: status, commit+push,
# inicialización de repositorio.
# =============================================================================

if [[ -n "${QBLOG_GIT_OPS_LOADED:-}" ]]; then
    return 0
fi
QBLOG_GIT_OPS_LOADED=1

# Muestra el estado de Git de un blog.
# $1 = ruta absoluta del blog
git_status_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Git Status: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    if [[ ! -d ".git" ]]; then
        print_error "No es un repositorio Git"
        return 1
    fi

    git status
}

# Agrega todos los cambios, hace commit y push.
# $1 = ruta absoluta del blog
# $2 = mensaje de commit (opcional, default "Update blog")
git_commit_push() {
    local blog_path="$1"
    local message="${2:-Update blog}"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Git Commit & Push: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    if [[ ! -d ".git" ]]; then
        print_error "No es un repositorio Git"
        return 1
    fi

    git add .
    print_info "Archivos agregados"

    git commit -m "$message"
    print_success "Commit realizado"

    if git push; then
        print_success "Push exitoso"
    else
        print_warning "No se pudo hacer push. ¿Necesitas configurar el remote?"
    fi
}

# Inicializa un repositorio Git en un blog, creando .gitignore si no existe.
# $1 = ruta absoluta del blog
git_init() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Inicializando Git: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    if [[ -d ".git" ]]; then
        print_warning "Ya existe un repositorio Git"
        return 0
    fi

    git init

    if [[ ! -f ".gitignore" ]]; then
        cat > .gitignore << 'EOF'
/.quarto/
/_site/
/_freeze/
/.Rproj.user/
.Rhistory
.RData
.DS_Store
EOF
        print_success "Creado .gitignore"
    fi

    print_success "Repositorio Git inicializado"
}
