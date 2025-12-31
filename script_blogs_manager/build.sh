#!/bin/bash

################################################################################
# build.sh - Script de gestión avanzada de publicaciones con Quarto
# Autor: Edison Achalma
# Versión: 2.0
# Fecha: 2026-01-28
# 
# Script mejorado para gestionar múltiples blogs y sitios web con Quarto
# Ubicación: /home/achalmaedison/Documents/scripts/scripts_for_quarto/script_blogs_manager/build.sh
################################################################################

set -e  # Salir si hay errores

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

PUBLICACIONES_DIR="/home/achalmaedison/Documents/publicaciones"
SCRIPT_DIR="/home/achalmaedison/Documents/scripts/scripts_for_quarto/script_blogs_manager"

# Blogs a excluir
EXCLUDED_BLOGS=(
    "apa"
    "borradores"
    "notas"
    "practicas preprofesionales"
    "propuesta bicentenario"
    "taller unsch como elaborar tesis de pregrado"
)

# Colores para output mejorado
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Emojis para mejor visualización
EMOJI_SUCCESS="✅"
EMOJI_ERROR="❌"
EMOJI_WARNING="⚠️"
EMOJI_INFO="ℹ️"
EMOJI_ROCKET="🚀"
EMOJI_FOLDER="📁"
EMOJI_FILE="📄"
EMOJI_BOOK="📚"
EMOJI_GEAR="⚙️"
EMOJI_CLEAN="🧹"
EMOJI_PREVIEW="👁️"
EMOJI_PUBLISH="🌍"
EMOJI_GIT="🐙"

# =============================================================================
# FUNCIONES AUXILIARES MEJORADAS
# =============================================================================

print_header() {
    local width=80
    echo ""
    echo -e "${CYAN}$( printf '═%.0s' $(seq 1 $width) )${NC}"
    echo -e "${CYAN}${BOLD}  $EMOJI_ROCKET $1${NC}"
    echo -e "${CYAN}$( printf '═%.0s' $(seq 1 $width) )${NC}"
    echo ""
}

print_subheader() {
    echo ""
    echo -e "${BLUE}${BOLD}── $1${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}  $EMOJI_SUCCESS${NC} $1"
}

print_error() {
    echo -e "${RED}  $EMOJI_ERROR${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}  $EMOJI_WARNING${NC} $1"
}

print_info() {
    echo -e "${BLUE}  $EMOJI_INFO${NC} $1"
}

print_step() {
    echo -e "${WHITE}${BOLD}→${NC} $1"
}

print_box() {
    local text="$1"
    local width=76
    local padding=$(( (width - ${#text}) / 2 ))
    
    echo -e "${CYAN}╔$( printf '═%.0s' $(seq 1 $width) )╗${NC}"
    printf "${CYAN}║${NC}%*s%s%*s${CYAN}║${NC}\n" $padding "" "$text" $padding ""
    echo -e "${CYAN}╚$( printf '═%.0s' $(seq 1 $width) )╝${NC}"
}

# Función para verificar si un blog está excluido
is_excluded_blog() {
    local blog_name="$1"
    for excluded in "${EXCLUDED_BLOGS[@]}"; do
        if [ "$blog_name" = "$excluded" ]; then
            return 0
        fi
    done
    return 1
}

# =============================================================================
# OPCIONES PRINCIPALES
# =============================================================================

# =============================================================================
# 1. Función para listar todos los blogs
# =============================================================================

list_blogs() {
    print_header "Blogs Disponibles"
    
    local counter=1
    local total_blogs=0
    
    for blog in "$PUBLICACIONES_DIR"/*/; do
        if [ ! -d "$blog" ]; then
            continue
        fi
        
        local blog_name=$(basename "$blog")
        
        # Verificar si está excluido
        if is_excluded_blog "$blog_name"; then
            continue
        fi
        
        if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
            echo -e "${MAGENTA}${BOLD}$counter.${NC} ${GREEN}$EMOJI_BOOK $blog_name${NC}"
            
            # Mostrar información adicional si existe _quarto.yml
            if [ -f "$blog/_quarto.yml" ]; then
                local title=$(grep "^\s*title:" "$blog/_quarto.yml" | head -1 | sed 's/.*title:\s*//' | tr -d '"')
                if [ ! -z "$title" ]; then
                    echo -e "   ${DIM}$title${NC}"
                fi
            fi
            
            # Mostrar cantidad de posts
            local post_count=0
            for subdir in "$blog"/*/; do
                if [ -d "$subdir" ]; then
                    post_count=$((post_count + $(find "$subdir" -name "index.qmd" 2>/dev/null | wc -l)))
                fi
            done
            
            if [ $post_count -gt 0 ]; then
                echo -e "   ${DIM}$EMOJI_FILE $post_count posts${NC}"
            fi
            
            # Mostrar estado de Git
            if [ -d "$blog/.git" ]; then
                echo -e "   ${DIM}$EMOJI_GIT Git inicializado${NC}"
            fi
            
            echo ""
            counter=$((counter + 1))
            total_blogs=$((total_blogs + 1))
        fi
    done
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}Total: $total_blogs blogs${NC}"
    echo ""
}

# =============================================================================
# Función para listar posts de un blog con detección automática de carpetas
# =============================================================================
list_posts() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Posts en $blog_name"
    
    # Detectar carpetas que contienen posts
    local post_folders=()
    
    for dir in "$blog_path"/*/; do
        if [ -d "$dir" ]; then
            local dir_name=$(basename "$dir")
            # Excluir carpetas del sistema
            if [[ ! "$dir_name" =~ ^(_|assets|site_libs|\.) ]]; then
                # Verificar si contiene index.qmd
                if find "$dir" -maxdepth 2 -name "index.qmd" 2>/dev/null | grep -q .; then
                    post_folders+=("$dir")
                fi
            fi
        fi
    done
    
    if [ ${#post_folders[@]} -eq 0 ]; then
        print_warning "No se encontraron carpetas con posts"
        return
    fi
    
    # Agrupar por carpeta
    for folder in "${post_folders[@]}"; do
        local folder_name=$(basename "$folder")
        print_subheader "$EMOJI_FOLDER $folder_name"
        
        local counter=1
        for post in "$folder"/*/index.qmd; do
            if [ -f "$post" ]; then
                local post_dir=$(dirname "$post")
                local post_name=$(basename "$post_dir")
                
                echo -e "${MAGENTA}  $counter.${NC} ${GREEN}$post_name${NC}"
                
                # Extraer y mostrar título del post
                local title=$(grep -m 1 "^title:" "$post" | sed 's/.*title:\s*//' | tr -d '"' | sed 's/^"\|"$//g')
                if [ ! -z "$title" ]; then
                    echo -e "     ${DIM}📝 $title${NC}"
                fi
                
                # Mostrar fecha si existe
                local date=$(grep -m 1 "^date:" "$post" | sed 's/.*date:\s*//' | tr -d '"')
                if [ ! -z "$date" ]; then
                    echo -e "     ${DIM}📅 $date${NC}"
                fi
                
                echo -e "     ${DIM}📂 $post_dir${NC}"
                echo ""
                
                counter=$((counter + 1))
            fi
        done
    done
}

# Función para detectar carpetas de posts en un blog
detect_post_folders() {
    local blog_path="$1"
    local folders=()
    
    for dir in "$blog_path"/*/; do
        if [ -d "$dir" ]; then
            local dir_name=$(basename "$dir")
            # Excluir carpetas del sistema
            if [[ ! "$dir_name" =~ ^(_|assets|site_libs|\.) ]]; then
                # Verificar si tiene estructura de posts
                if find "$dir" -maxdepth 2 -name "index.qmd" 2>/dev/null | grep -q . ||
                   [ -f "$dir/_metadata.yml" ]; then
                    folders+=("$dir_name")
                fi
            fi
        fi
    done
    
    printf '%s\n' "${folders[@]}"
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
# 2. Renderizar blog completo
# =============================================================================
render_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "$EMOJI_GEAR Renderizando: $blog_name"
    
    cd "$blog_path"
    
    if quarto render; then
        print_success "Blog renderizado exitosamente"
    else
        print_error "Error al renderizar el blog"
        return 1
    fi
}

# =============================================================================
# 3. Preview del blog
# =============================================================================

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


# =============================================================================
# 4. Limpiar archivos generados
# =============================================================================
clean_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "$EMOJI_CLEAN Limpiando: $blog_name"
    
    cd "$blog_path"
    
    local cleaned=0
    for dir in _site _freeze .quarto; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            print_success "Eliminado: $dir"
            cleaned=$((cleaned + 1))
        fi
    done
    
    if [ $cleaned -eq 0 ]; then
        print_info "No hay archivos para limpiar"
    else
        print_success "Limpieza completada ($cleaned directorios)"
    fi
}

# =============================================================================
# 5. Publicar blog
# =============================================================================
publish_blog() {
    local blog_path="$1"
    local target="${2:-gh-pages}"
    local blog_name=$(basename "$blog_path")
    
    print_header "$EMOJI_PUBLISH Publicando: $blog_name"
    print_info "Target: $target"
    
    cd "$blog_path"
    
    case "$target" in
        gh-pages|netlify|quarto-pub|confluence)
            if quarto publish "$target"; then
                print_success "Publicado en $target"
            else
                print_error "Error al publicar"
                return 1
            fi
            ;;
        *)
            print_error "Target desconocido: $target"
            print_info "Targets válidos: gh-pages, netlify, quarto-pub, confluence"
            return 1
            ;;
    esac
}

# =============================================================================
# POSTS
# =============================================================================

# =============================================================================
# 6. Crear nuevo post
# =============================================================================

create_post_interactive() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Crear Nuevo Post en $blog_name"
    
    # 1. Detectar y seleccionar carpeta de destino
    print_step "Detectando carpetas de posts..."
    local post_folders=($(detect_post_folders "$blog_path"))
    
    if [ ${#post_folders[@]} -eq 0 ]; then
        print_warning "No se detectaron carpetas de posts existentes"
        read -p "Nombre de la nueva carpeta de posts: " new_folder
        post_folders=("$new_folder")
    fi
    
    echo ""
    print_subheader "Carpetas disponibles"
    local i=1
    for folder in "${post_folders[@]}"; do
        echo -e "${MAGENTA}$i.${NC} $folder"
        i=$((i + 1))
    done
    echo -e "${MAGENTA}$i.${NC} ${BOLD}Crear nueva carpeta${NC}"
    echo ""
    
    read -p "Selecciona carpeta (1-$i): " folder_choice
    
    local target_folder
    if [ "$folder_choice" -eq "$i" ]; then
        read -p "Nombre de la nueva carpeta: " new_folder
        target_folder="$new_folder"
        mkdir -p "$blog_path/$target_folder"
        
        # Crear _metadata.yml si no existe
        if [ ! -f "$blog_path/$target_folder/_metadata.yml" ]; then
            create_metadata_file "$blog_path/$target_folder"
        fi
    else
        target_folder="${post_folders[$((folder_choice-1))]}"
    fi
    
    # 2. Información básica del post
    print_step "Información básica del post"
    echo ""
    
    read -p "Título del post: " post_title
    read -p "Subtítulo (opcional): " post_subtitle
    
    # Crear nombre del directorio
    local date=$(date +%Y-%m-%d)
    local post_slug=$(echo "$post_title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
    local post_dir="$blog_path/$target_folder/$date-$post_slug"
    
    if [ -d "$post_dir" ]; then
        print_error "Ya existe un post con ese nombre"
        return 1
    fi
    
    mkdir -p "$post_dir"
    
    # 3. Seleccionar tipo de documento APAQuarto
    print_step "Tipo de documento APAQuarto"
    echo ""
    echo -e "${MAGENTA}1.${NC} doc  - Documento general (flexible)"
    echo -e "${MAGENTA}2.${NC} jou  - Formato revista (2 columnas) ${YELLOW}[Por defecto]${NC}"
    echo -e "${MAGENTA}3.${NC} man  - Manuscrito formal"
    echo -e "${MAGENTA}4.${NC} stu  - Trabajo estudiantil"
    echo ""
    
    read -p "Selecciona tipo (1-4, Enter=jou): " doc_type_choice
    doc_type_choice=${doc_type_choice:-2}
    
    local doc_type
    case $doc_type_choice in
        1) doc_type="doc" ;;
        2) doc_type="jou" ;;
        3) doc_type="man" ;;
        4) doc_type="stu" ;;
        *) doc_type="jou" ;;
    esac
    
    # 4. Información adicional del post
    print_step "Información adicional"
    echo ""
    
    read -p "Tags (separados por comas): " tags_input
    read -p "Categorías (1-2, separadas por comas): " categories_input
    
    # Convertir a arrays
    IFS=',' read -ra tags <<< "$tags_input"
    IFS=',' read -ra categories <<< "$categories_input"
    
    # 5. Preguntar sobre autor
    echo ""
    read -p "¿Usar autor predeterminado de _metadata.yml? (s/n): " use_default_author
    
    local author_yaml=""
    if [[ ! "$use_default_author" =~ ^[Ss]$ ]]; then
        print_step "Información del autor"
        echo ""
        
        read -p "Nombre completo: " author_name
        read -p "Email: " author_email
        read -p "ORCID (opcional): " author_orcid
        
        # Construir YAML de autor
        author_yaml="author:
  - name: $author_name"
        
        if [ ! -z "$author_email" ]; then
            author_yaml="$author_yaml
    email: $author_email"
        fi
        
        if [ ! -z "$author_orcid" ]; then
            author_yaml="$author_yaml
    orcid: $author_orcid"
        fi
    fi
    
    # 6. Información específica según tipo de documento
    local specific_yaml=""
    
    if [ "$doc_type" = "jou" ]; then
        print_step "Información de revista (modo jou)"
        echo ""
        
        read -p "Nombre de la revista: " journal_name
        read -p "Volumen y número (ej: 2025, Vol. 7, No. 1): " volume_info
        
        specific_yaml="journal: \"$journal_name\"
volume: \"$volume_info\""
        
    elif [ "$doc_type" = "stu" ]; then
        print_step "Información del curso (modo stu)"
        echo ""
        
        read -p "Nombre del curso: " course_name
        read -p "Profesor: " professor_name
        read -p "Fecha de entrega: " due_date
        
        specific_yaml="course: \"$course_name\"
professor: \"$professor_name\"
duedate: \"$due_date\""
    fi
    
    # 7. Crear el archivo index.qmd
    print_step "Generando index.qmd..."
    
    cat > "$post_dir/index.qmd" << EOF
---
# =============================================================================
# POST: $post_title
# Tipo: APAQuarto $doc_type
# Creado: $date
# =============================================================================

# Información básica
title: "$post_title"
EOF

    # Añadir subtítulo si existe
    if [ ! -z "$post_subtitle" ]; then
        echo "subtitle: \"$post_subtitle\"" >> "$post_dir/index.qmd"
    fi

    # Añadir shorttitle
    local short_title=$(echo "$post_title" | cut -c1-50)
    echo "shorttitle: \"$short_title\"" >> "$post_dir/index.qmd"
    
    # Añadir fecha
    echo "date: \"$date\"" >> "$post_dir/index.qmd"
    echo "date-modified: \"today\"" >> "$post_dir/index.qmd"
    
    # Añadir tags
    if [ ${#tags[@]} -gt 0 ]; then
        echo -n "tags: [" >> "$post_dir/index.qmd"
        for i in "${!tags[@]}"; do
            tag=$(echo "${tags[$i]}" | xargs) # trim
            if [ $i -eq 0 ]; then
                echo -n "\"$tag\"" >> "$post_dir/index.qmd"
            else
                echo -n ", \"$tag\"" >> "$post_dir/index.qmd"
            fi
        done
        echo "]" >> "$post_dir/index.qmd"
    fi
    
    # Añadir categorías
    if [ ${#categories[@]} -gt 0 ]; then
        echo -n "categories: [" >> "$post_dir/index.qmd"
        for i in "${!categories[@]}"; do
            cat=$(echo "${categories[$i]}" | xargs) # trim
            if [ $i -eq 0 ]; then
                echo -n "\"$cat\"" >> "$post_dir/index.qmd"
            else
                echo -n ", \"$cat\"" >> "$post_dir/index.qmd"
            fi
        done
        echo "]" >> "$post_dir/index.qmd"
    fi
    
    # Añadir imagen predeterminada
    echo "image: ../featured.jpg" >> "$post_dir/index.qmd"
    
    # Añadir bibliografía
    echo "bibliography: references.bib" >> "$post_dir/index.qmd"
    
    # Añadir jupyter si es necesario
    echo "jupyter: python3" >> "$post_dir/index.qmd"
    
    # Añadir información específica del tipo de documento
    if [ ! -z "$specific_yaml" ]; then
        echo "" >> "$post_dir/index.qmd"
        echo "# Información específica" >> "$post_dir/index.qmd"
        echo "$specific_yaml" >> "$post_dir/index.qmd"
    fi
    
    # Añadir autor si no es predeterminado
    if [ ! -z "$author_yaml" ]; then
        echo "" >> "$post_dir/index.qmd"
        echo "# Autor" >> "$post_dir/index.qmd"
        echo "$author_yaml" >> "$post_dir/index.qmd"
    fi
    
    # Añadir note del author note mínimo
    cat >> "$post_dir/index.qmd" << 'EOF'

# Author Note
author-note:
  disclosures:
    conflict-of-interest: "El autor declara no tener conflictos de interés."

# Idioma
lang: es
---

<!-- ========================================================================== -->
<!-- CONTENIDO DEL POST -->
<!-- ========================================================================== -->

## Introducción

Escribe aquí la introducción de tu post...

## Desarrollo

### Sección 1

Contenido...

### Sección 2

Contenido...

## Conclusiones

Escribe tus conclusiones aquí...

## Referencias

Las referencias se generarán automáticamente desde references.bib
EOF
    
    # Crear archivo references.bib vacío
    touch "$post_dir/references.bib"
    
    # Resumen
    echo ""
    print_success "Post creado exitosamente"
    echo ""
    print_info "Ubicación: $post_dir"
    print_info "Archivo: index.qmd"
    print_info "Tipo: APAQuarto $doc_type"
    echo ""
    
    # Preguntar si desea abrir el archivo
    read -p "¿Deseas abrir el archivo? (s/n): " open_file
    if [[ "$open_file" =~ ^[Ss]$ ]]; then
        ${EDITOR:-nano} "$post_dir/index.qmd"
    fi
}

# Función para crear _metadata.yml
create_metadata_file() {
    local folder_path="$1"
    local metadata_file="$folder_path/_metadata.yml"
    
    print_info "Creando _metadata.yml..."
    
    cat > "$metadata_file" << 'EOF'
# =============================================================================
# CONFIGURACIÓN GENERAL DEL DOCUMENTO
# =============================================================================
date-modified: "today"
license: "CC BY-SA"
lang: es
search: true
lightbox: true
title-block-banner: true
is-particlejs-enabled: true

# =============================================================================
# INFORMACIÓN DEL AUTOR PREDETERMINADO
# =============================================================================
author:
  - name: Edison Achalma
    url: https://achalmaedison.netlify.app
    affiliation:
      - id: unsch
        name: Universidad Nacional de San Cristóbal de Huamanga
        department: Escuela Profesional de Economía
        city: Ayacucho
        region: AYA
        country: Perú
    affiliation-url: https://www.gob.pe/unsch
    orcid: 0000-0001-6996-3364
    email: elmer.achalma.09@unsch.edu.pe
    attributes:
      corresponding: true
      equal-contributor: true
    roles:
      - conceptualización
      - redacción

# =============================================================================
# CONFIGURACIÓN DE FORMATO
# =============================================================================
floatsintext: true
citation: true
google-scholar: true
link-citations: true

# =============================================================================
# FORMATOS DE SALIDA
# =============================================================================
format:
  html:
    toc: true
    toc-depth: 3
    code-fold: true
    code-summary: "Mostrar código"
    template-partials:
      - ../_partials/title-block-link-buttons/title-block.html
  
  apaquarto-pdf:
    documentmode: jou  # Por defecto: journal
    keep-tex: false
  
  apaquarto-docx: default

# =============================================================================
# CONFIGURACIÓN DE EJECUCIÓN
# =============================================================================
execute:
  freeze: true
  echo: false
  warning: false
  error: false
EOF
    
    print_success "Creado $metadata_file"
}



# =============================================================================
# 7. Renderizar un post específico
# =============================================================================
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

# =============================================================================
# OPERACIONES MULTIPLES
# =============================================================================

# =============================================================================
# 9. Renderizar todos los blogs
# =============================================================================

render_all_blogs() {
    print_header "Renderizando TODOS los blogs"
    
    local success_count=0
    local fail_count=0
    local skip_count=0
    
    for blog in "$PUBLICACIONES_DIR"/*/; do
        local blog_name=$(basename "$blog")
        
        # Verificar si está excluido
        if is_excluded_blog "$blog_name"; then
            skip_count=$((skip_count + 1))
            continue
        fi
        
        if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
            echo ""
            print_step "Procesando: $blog_name"
            
            if render_blog "$blog" 2>&1 | tail -5; then
                success_count=$((success_count + 1))
            else
                fail_count=$((fail_count + 1))
            fi
        fi
    done
    
    echo ""
    print_box "Resumen de Renderizado"
    echo ""
    echo -e "  ${GREEN}$EMOJI_SUCCESS Exitosos:${NC} $success_count"
    echo -e "  ${RED}$EMOJI_ERROR Fallidos:${NC} $fail_count"
    echo -e "  ${YELLOW}$EMOJI_WARNING Omitidos:${NC} $skip_count"
    echo ""
}



# =============================================================================
# FUNCIONES DE GIT
# =============================================================================

# =============================================================================
# 11 Status de Git
# =============================================================================
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
# 12 Commit y push
# =============================================================================

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

# =============================================================================
# 13 Inicializar repositorio Git
# =============================================================================
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

# =============================================================================
# UTILIDADES
# =============================================================================

# =============================================================================
# 14. Verificar proyecto
# =============================================================================
check_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "Verificando: $blog_name"
    
    cd "$blog_path"
    quarto check
}

# =============================================================================
# 15 Inspeccionar proyecto
# =============================================================================
inspect_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    
    print_header "$EMOJI_INFO Inspeccionando: $blog_name"
    
    cd "$blog_path"
    
    # Capturar solo información relevante
    echo -e "${DIM}"
    quarto inspect | grep -E "(Type|Engine|Formats|Output)" || quarto inspect | head -50
    echo -e "${NC}"
}

# =============================================================================
# 16 Convertir documento
# =============================================================================

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

# =============================================================================
# MENÚ INTERACTIVO MEJORADO
# =============================================================================

show_menu() {
    clear
    print_header "Gestor de Publicaciones Quarto v2.0"
    echo ""
    echo -e "${CYAN}Directorio:${NC} $PUBLICACIONES_DIR"
    echo ""
    
    echo -e "${CYAN}${BOLD}Gestión de Blogs:${NC}"
    echo -e "  ${WHITE}1)${NC} $EMOJI_BOOK Listar todos los blogs"
    echo -e "  ${WHITE}2)${NC} $EMOJI_GEAR Renderizar blog"
    echo -e "  ${WHITE}3)${NC} $EMOJI_PREVIEW Preview de blog"
    echo -e "  ${WHITE}4)${NC} $EMOJI_CLEAN Limpiar archivos"
    echo -e "  ${WHITE}5)${NC} $EMOJI_PUBLISH Publicar blog"
    echo ""
    
    echo -e "${CYAN}${BOLD}Gestión de Posts:${NC}"
    echo -e "  ${WHITE}6)${NC} $EMOJI_FILE Crear nuevo post"
    echo -e "  ${WHITE}7)${NC} $EMOJI_GEAR Renderizar post específico"
    echo -e "  ${WHITE}8)${NC} $EMOJI_FILE Listar posts"
    echo ""
    
    echo -e "${CYAN}${BOLD}Operaciones Múltiples:${NC}"
    echo -e "  ${WHITE}9)${NC} $EMOJI_GEAR Renderizar todos los blogs"
    echo -e "  ${WHITE}10)${NC} $EMOJI_CLEAN Limpiar todos los blogs"
    echo ""
    
    echo -e "${CYAN}${BOLD}Git:${NC}"
    echo -e "  ${WHITE}11)${NC} $EMOJI_GIT Git status de blog"
    echo -e "  ${WHITE}12)${NC} $EMOJI_GIT Git commit & push"
    echo -e "  ${WHITE}13)${NC} $EMOJI_GIT Inicializar Git en blog"
    echo ""
    
    echo -e "${CYAN}${BOLD}Utilidades:${NC}"
    echo -e "  ${WHITE}14)${NC} $EMOJI_INFO Verificar blog (quarto check)"
    echo -e "  ${WHITE}15)${NC} $EMOJI_INFO Inspeccionar blog"
    echo -e "  ${WHITE}16)${NC} $EMOJI_INFO Convertir documento"
    echo ""
    
    echo -e "  ${WHITE}0)${NC} ${RED}Salir${NC}"
    echo ""
}

interactive_mode() {
    while true; do
        show_menu
        read -p "$(echo -e ${WHITE}${BOLD}→${NC}) Selecciona una opción: " option
        
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
                create_post_interactive "$PUBLICACIONES_DIR/$blog_name"
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
                read -p "¿Estás seguro? (s/n): " confirm
                if [[ "$confirm" =~ ^[Ss]$ ]]; then
                    for blog in "$PUBLICACIONES_DIR"/*/; do
                        local blog_name=$(basename "$blog")
                        if ! is_excluded_blog "$blog_name"; then
                            clean_blog "$blog"
                        fi
                    done
                fi
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
                echo ""
                print_success "¡Hasta luego!"
                echo ""
                exit 0
                ;;
            *)
                print_error "Opción inválida"
                sleep 2
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
