#!/bin/bash

################################################################################
# build.sh - Script de gestión de publicaciones con Quarto
# Autor: Edison Achalma
# Fecha: 2025-12-28
# 
# Script para gestionar múltiples blogs y sitios web creados con Quarto
# Ubicación: /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh
################################################################################

set -e  # Salir si hay errores

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

PUBLICACIONES_DIR="/home/achalmaedison/Documents/publicaciones"
SCRIPT_DIR="/home/achalmaedison/Documents/scripts/scripts_for_quarto"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Función para listar todos los blogs
list_blogs() {
    print_header "Blogs Disponibles"
    echo ""
    local counter=1
    
    for blog in "$PUBLICACIONES_DIR"/*/; do
        if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
            local blog_name=$(basename "$blog")
            echo -e "${MAGENTA}$counter.${NC} ${GREEN}$blog_name${NC}"
            
            # Mostrar información adicional si existe _quarto.yml
            if [ -f "$blog/_quarto.yml" ]; then
                local title=$(grep "title:" "$blog/_quarto.yml" | head -1 | sed 's/.*title: *//')
                if [ ! -z "$title" ]; then
                    echo "   📖 $title"
                fi
            fi
            
            counter=$((counter + 1))
        fi
    done
    echo ""
}

# Función para listar posts de un blog
list_posts() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Posts en $blog_name"
    echo ""
    
    local counter=1
    
    # Buscar en directorios comunes de posts
    for posts_dir in "$blog_path/posts" "$blog_path/"*"-"*; do
        if [ -d "$posts_dir" ]; then
            for post in "$posts_dir"/*/index.qmd; do
                if [ -f "$post" ]; then
                    local post_dir=$(dirname "$post")
                    local post_name=$(basename "$post_dir")
                    echo -e "${MAGENTA}$counter.${NC} ${GREEN}$post_name${NC}"
                    
                    # Extraer título del post
                    local title=$(grep -m 1 "title:" "$post" | sed 's/.*title: *//' | tr -d '"')
                    if [ ! -z "$title" ]; then
                        echo "   📄 $title"
                    fi
                    echo "   📂 $post_dir"
                    
                    counter=$((counter + 1))
                fi
            done
        fi
    done
    echo ""
}

# Función para verificar si Quarto está instalado
check_quarto() {
    if ! command -v quarto &> /dev/null; then
        print_error "Quarto no está instalado"
        echo "Por favor instala Quarto desde: https://quarto.org/docs/get-started/"
        exit 1
    fi
    
    local version=$(quarto --version)
    print_info "Quarto versión: $version"
}

# =============================================================================
# FUNCIONES DE QUARTO
# =============================================================================

# Renderizar blog completo
render_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Renderizando: $blog_name"
    
    cd "$blog_path"
    
    if quarto render; then
        print_success "Blog renderizado exitosamente"
    else
        print_error "Error al renderizar el blog"
        return 1
    fi
}

# Preview del blog
preview_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    local port="${2:-4200}"
    
    print_header "Preview: $blog_name (Puerto: $port)"
    print_info "Presiona Ctrl+C para detener el servidor"
    
    cd "$blog_path"
    quarto preview --port "$port" --no-browser
}

# Preview con browser
preview_blog_browser() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    local port="${2:-4200}"
    
    print_header "Preview: $blog_name (Puerto: $port)"
    print_info "Se abrirá en el navegador automáticamente"
    
    cd "$blog_path"
    quarto preview --port "$port"
}

# Publicar blog
publish_blog() {
    local blog_path="$1"
    local target="${2:-gh-pages}"
    local blog_name=$(basename "$blog_path")
    
    print_header "Publicando: $blog_name"
    
    cd "$blog_path"
    
    case "$target" in
        gh-pages)
            quarto publish gh-pages
            ;;
        netlify)
            quarto publish netlify
            ;;
        quarto-pub)
            quarto publish quarto-pub
            ;;
        confluence)
            quarto publish confluence
            ;;
        *)
            print_error "Target de publicación desconocido: $target"
            return 1
            ;;
    esac
    
    print_success "Blog publicado en $target"
}

# Limpiar archivos generados
clean_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Limpiando: $blog_name"
    
    cd "$blog_path"
    
    # Eliminar directorios de salida comunes
    for dir in _site _freeze .quarto; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_success "Eliminado: $dir"
        fi
    done
    
    print_success "Limpieza completada"
}

# Renderizar un post específico
render_post() {
    local post_path="$1"
    
    if [ ! -f "$post_path" ]; then
        print_error "Post no encontrado: $post_path"
        return 1
    fi
    
    local post_name=$(basename "$(dirname "$post_path")")
    print_header "Renderizando post: $post_name"
    
    cd "$(dirname "$post_path")"
    
    if quarto render "$(basename "$post_path")"; then
        print_success "Post renderizado exitosamente"
    else
        print_error "Error al renderizar el post"
        return 1
    fi
}

# Crear nuevo post
create_post() {
    local blog_path="$1"
    local post_title="$2"
    local blog_name=$(basename "$blog_path")
    
    if [ -z "$post_title" ]; then
        read -p "Título del post: " post_title
    fi
    
    # Crear nombre del directorio basado en la fecha y título
    local date=$(date +%Y-%m-%d)
    local post_slug=$(echo "$post_title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
    local post_dir="$blog_path/posts/$date-$post_slug"
    
    print_header "Creando nuevo post"
    print_info "Blog: $blog_name"
    print_info "Título: $post_title"
    print_info "Directorio: $post_dir"
    
    # Crear directorio
    mkdir -p "$post_dir"
    
    # Crear index.qmd con plantilla
    cat > "$post_dir/index.qmd" << EOF
---
title: "$post_title"
author: "Edison Achalma"
date: "$date"
categories: []
description: ""
draft: true
---

## Introducción

Tu contenido aquí...

EOF
    
    print_success "Post creado en: $post_dir/index.qmd"
    
    # Preguntar si desea abrir el archivo
    read -p "¿Deseas abrir el archivo? (s/n): " open_file
    if [ "$open_file" = "s" ] || [ "$open_file" = "S" ]; then
        ${EDITOR:-nano} "$post_dir/index.qmd"
    fi
}

# Verificar proyecto
check_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Verificando: $blog_name"
    
    cd "$blog_path"
    quarto check
}

# Convertir documento
convert_document() {
    local input_file="$1"
    local output_format="${2:-html}"
    
    if [ ! -f "$input_file" ]; then
        print_error "Archivo no encontrado: $input_file"
        return 1
    fi
    
    print_header "Convirtiendo documento"
    print_info "Entrada: $input_file"
    print_info "Formato: $output_format"
    
    quarto convert "$input_file" --output "$output_format"
    print_success "Documento convertido"
}

# Inspeccionar proyecto
inspect_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Inspeccionando: $blog_name"
    
    cd "$blog_path"
    quarto inspect
}

# =============================================================================
# FUNCIONES DE GIT
# =============================================================================

# Inicializar repositorio Git
git_init() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Inicializando Git: $blog_name"
    
    cd "$blog_path"
    
    if [ -d ".git" ]; then
        print_warning "Ya existe un repositorio Git"
        return 0
    fi
    
    git init
    
    # Crear .gitignore si no existe
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << EOF
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

# Commit y push
git_commit_push() {
    local blog_path="$1"
    local message="${2:-Update blog}"
    local blog_name=$(basename "$blog_path")
    
    print_header "Git Commit & Push: $blog_name"
    
    cd "$blog_path"
    
    if [ ! -d ".git" ]; then
        print_error "No es un repositorio Git"
        return 1
    fi
    
    # Agregar todos los cambios
    git add .
    print_info "Archivos agregados"
    
    # Commit
    git commit -m "$message"
    print_success "Commit realizado"
    
    # Push
    if git push; then
        print_success "Push exitoso"
    else
        print_warning "No se pudo hacer push. ¿Necesitas configurar el remote?"
    fi
}

# Status de Git
git_status_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Git Status: $blog_name"
    
    cd "$blog_path"
    
    if [ ! -d ".git" ]; then
        print_error "No es un repositorio Git"
        return 1
    fi
    
    git status
}

# =============================================================================
# FUNCIONES BATCH (OPERACIONES MÚLTIPLES)
# =============================================================================

# Renderizar todos los blogs
render_all_blogs() {
    print_header "Renderizando TODOS los blogs"
    
    local success_count=0
    local fail_count=0
    
    for blog in "$PUBLICACIONES_DIR"/*/; do
        if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
            local blog_name=$(basename "$blog")
            echo ""
            print_info "Procesando: $blog_name"
            
            if render_blog "$blog"; then
                success_count=$((success_count + 1))
            else
                fail_count=$((fail_count + 1))
            fi
        fi
    done
    
    echo ""
    print_header "Resumen"
    print_success "Exitosos: $success_count"
    if [ $fail_count -gt 0 ]; then
        print_error "Fallidos: $fail_count"
    fi
}

# Limpiar todos los blogs
clean_all_blogs() {
    print_header "Limpiando TODOS los blogs"
    
    read -p "¿Estás seguro? Esta acción eliminará todos los archivos generados (s/n): " confirm
    if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
        print_warning "Operación cancelada"
        return 0
    fi
    
    for blog in "$PUBLICACIONES_DIR"/*/; do
        if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
            clean_blog "$blog"
        fi
    done
    
    print_success "Limpieza completa finalizada"
}

# =============================================================================
# MENÚ INTERACTIVO
# =============================================================================

show_menu() {
    clear
    print_header "🚀 Gestor de Publicaciones Quarto"
    echo ""
    echo -e "${CYAN}Directorio:${NC} $PUBLICACIONES_DIR"
    echo ""
    echo -e "${YELLOW}Opciones principales:${NC}"
    echo "  1) Listar todos los blogs"
    echo "  2) Renderizar blog específico"
    echo "  3) Preview de blog"
    echo "  4) Limpiar archivos generados"
    echo "  5) Publicar blog"
    echo ""
    echo -e "${YELLOW}Posts:${NC}"
    echo "  6) Crear nuevo post"
    echo "  7) Renderizar post específico"
    echo "  8) Listar posts de un blog"
    echo ""
    echo -e "${YELLOW}Operaciones múltiples:${NC}"
    echo "  9) Renderizar todos los blogs"
    echo " 10) Limpiar todos los blogs"
    echo ""
    echo -e "${YELLOW}Git:${NC}"
    echo " 11) Git status de blog"
    echo " 12) Git commit & push"
    echo " 13) Inicializar Git en blog"
    echo ""
    echo -e "${YELLOW}Utilidades:${NC}"
    echo " 14) Verificar blog (quarto check)"
    echo " 15) Inspeccionar blog"
    echo " 16) Convertir documento"
    echo ""
    echo "  0) Salir"
    echo ""
}

interactive_mode() {
    while true; do
        show_menu
        read -p "Selecciona una opción: " option
        echo ""
        
        case $option in
            1)
                list_blogs
                read -p "Presiona Enter para continuar..."
                ;;
            2)
                list_blogs
                read -p "Nombre del blog: " blog_name
                render_blog "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            3)
                list_blogs
                read -p "Nombre del blog: " blog_name
                read -p "Puerto (default: 4200): " port
                port=${port:-4200}
                preview_blog "$PUBLICACIONES_DIR/$blog_name" "$port"
                ;;
            4)
                list_blogs
                read -p "Nombre del blog: " blog_name
                clean_blog "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            5)
                list_blogs
                read -p "Nombre del blog: " blog_name
                echo "Targets disponibles: gh-pages, netlify, quarto-pub, confluence"
                read -p "Target (default: gh-pages): " target
                target=${target:-gh-pages}
                publish_blog "$PUBLICACIONES_DIR/$blog_name" "$target"
                read -p "Presiona Enter para continuar..."
                ;;
            6)
                list_blogs
                read -p "Nombre del blog: " blog_name
                read -p "Título del post: " post_title
                create_post "$PUBLICACIONES_DIR/$blog_name" "$post_title"
                read -p "Presiona Enter para continuar..."
                ;;
            7)
                list_blogs
                read -p "Nombre del blog: " blog_name
                list_posts "$PUBLICACIONES_DIR/$blog_name"
                read -p "Ruta completa del index.qmd: " post_path
                render_post "$post_path"
                read -p "Presiona Enter para continuar..."
                ;;
            8)
                list_blogs
                read -p "Nombre del blog: " blog_name
                list_posts "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            9)
                render_all_blogs
                read -p "Presiona Enter para continuar..."
                ;;
            10)
                clean_all_blogs
                read -p "Presiona Enter para continuar..."
                ;;
            11)
                list_blogs
                read -p "Nombre del blog: " blog_name
                git_status_blog "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            12)
                list_blogs
                read -p "Nombre del blog: " blog_name
                read -p "Mensaje del commit: " message
                git_commit_push "$PUBLICACIONES_DIR/$blog_name" "$message"
                read -p "Presiona Enter para continuar..."
                ;;
            13)
                list_blogs
                read -p "Nombre del blog: " blog_name
                git_init "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            14)
                list_blogs
                read -p "Nombre del blog: " blog_name
                check_blog "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            15)
                list_blogs
                read -p "Nombre del blog: " blog_name
                inspect_blog "$PUBLICACIONES_DIR/$blog_name"
                read -p "Presiona Enter para continuar..."
                ;;
            16)
                read -p "Ruta del archivo: " input_file
                read -p "Formato de salida (html/pdf/docx): " format
                convert_document "$input_file" "$format"
                read -p "Presiona Enter para continuar..."
                ;;
            0)
                print_success "¡Hasta luego!"
                exit 0
                ;;
            *)
                print_error "Opción inválida"
                read -p "Presiona Enter para continuar..."
                ;;
        esac
    done
}

# =============================================================================
# FUNCIÓN DE AYUDA
# =============================================================================

show_help() {
    cat << EOF
${CYAN}═══════════════════════════════════════════════════════════════${NC}
  🚀 Gestor de Publicaciones Quarto - Ayuda
${CYAN}═══════════════════════════════════════════════════════════════${NC}

${YELLOW}USO:${NC}
    $0 [COMANDO] [OPCIONES]

${YELLOW}COMANDOS PRINCIPALES:${NC}

  ${GREEN}Gestión de Blogs:${NC}
    list                    Lista todos los blogs disponibles
    render BLOG             Renderiza un blog completo
    preview BLOG [PORT]     Inicia preview del blog (puerto opcional)
    preview-browser BLOG    Preview con apertura automática del navegador
    clean BLOG              Limpia archivos generados (_site, _freeze, etc.)
    publish BLOG [TARGET]   Publica el blog (gh-pages, netlify, etc.)
    check BLOG              Verifica la configuración del blog
    inspect BLOG            Inspecciona la estructura del blog
    
  ${GREEN}Gestión de Posts:${NC}
    list-posts BLOG         Lista todos los posts de un blog
    render-post POST_PATH   Renderiza un post específico
    new-post BLOG [TITLE]   Crea un nuevo post
    
  ${GREEN}Operaciones Múltiples:${NC}
    render-all              Renderiza todos los blogs
    clean-all               Limpia todos los blogs
    
  ${GREEN}Git:${NC}
    git-init BLOG           Inicializa repositorio Git
    git-status BLOG         Muestra estado de Git
    git-commit BLOG [MSG]   Commit y push de cambios
    
  ${GREEN}Utilidades:${NC}
    convert FILE [FORMAT]   Convierte documento a otro formato
    interactive, -i         Modo interactivo (menú)
    help, -h, --help       Muestra esta ayuda
    version, -v            Muestra versión de Quarto

${YELLOW}EJEMPLOS:${NC}

  # Listar todos los blogs
  $0 list
  
  # Renderizar un blog específico
  $0 render website-achalma
  
  # Preview de un blog en puerto específico
  $0 preview epsilon-y-beta 4300
  
  # Crear nuevo post
  $0 new-post numerus-scriptum "Tutorial de Python"
  
  # Renderizar post específico
  $0 render-post /path/to/blog/posts/2025-12-28-mi-post/index.qmd
  
  # Limpiar y renderizar
  $0 clean axiomata && $0 render axiomata
  
  # Commit y push
  $0 git-commit website-achalma "Actualización de contenido"
  
  # Modo interactivo
  $0 -i

${YELLOW}UBICACIONES:${NC}
  Publicaciones: ${PUBLICACIONES_DIR}
  Scripts:       ${SCRIPT_DIR}

${YELLOW}NOTAS:${NC}
  - Los blogs deben tener un archivo index.qmd o _quarto.yml
  - El preview se ejecuta en puerto 4200 por defecto
  - La limpieza elimina: _site, _freeze, .quarto

Para más información sobre Quarto: https://quarto.org/docs/

EOF
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    # Verificar Quarto
    check_quarto
    echo ""
    
    # Si no hay argumentos, mostrar menú interactivo
    if [ $# -eq 0 ]; then
        interactive_mode
        exit 0
    fi
    
    # Procesar comandos
    case "$1" in
        list)
            list_blogs
            ;;
        render)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            render_blog "$PUBLICACIONES_DIR/$2"
            ;;
        preview)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            preview_blog "$PUBLICACIONES_DIR/$2" "${3:-4200}"
            ;;
        preview-browser)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            preview_blog_browser "$PUBLICACIONES_DIR/$2" "${3:-4200}"
            ;;
        clean)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            clean_blog "$PUBLICACIONES_DIR/$2"
            ;;
        publish)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            publish_blog "$PUBLICACIONES_DIR/$2" "${3:-gh-pages}"
            ;;
        check)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            check_blog "$PUBLICACIONES_DIR/$2"
            ;;
        inspect)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            inspect_blog "$PUBLICACIONES_DIR/$2"
            ;;
        list-posts)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            list_posts "$PUBLICACIONES_DIR/$2"
            ;;
        render-post)
            if [ -z "$2" ]; then
                print_error "Especifica la ruta del post"
                exit 1
            fi
            render_post "$2"
            ;;
        new-post)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            create_post "$PUBLICACIONES_DIR/$2" "$3"
            ;;
        render-all)
            render_all_blogs
            ;;
        clean-all)
            clean_all_blogs
            ;;
        git-init)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            git_init "$PUBLICACIONES_DIR/$2"
            ;;
        git-status)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            git_status_blog "$PUBLICACIONES_DIR/$2"
            ;;
        git-commit)
            if [ -z "$2" ]; then
                print_error "Especifica el nombre del blog"
                exit 1
            fi
            git_commit_push "$PUBLICACIONES_DIR/$2" "${3:-Update blog}"
            ;;
        convert)
            if [ -z "$2" ]; then
                print_error "Especifica el archivo a convertir"
                exit 1
            fi
            convert_document "$2" "${3:-html}"
            ;;
        interactive|-i)
            interactive_mode
            ;;
        help|-h|--help)
            show_help
            ;;
        version|-v)
            quarto --version
            ;;
        *)
            print_error "Comando desconocido: $1"
            echo "Usa '$0 help' para ver la ayuda"
            exit 1
            ;;
    esac
}

# Ejecutar script
main "$@"
