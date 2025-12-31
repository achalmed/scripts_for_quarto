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
    
    print_header "🚀 Asistente de Creación de Posts - $blog_name"
    
    echo -e "${CYAN}Este asistente te guiará paso a paso para crear un post APAQuarto completo.${NC}"
    echo -e "${DIM}Presiona Enter para usar valores por defecto | Escribe 'omitir' para saltar secciones opcionales${NC}"
    echo ""
    read -p "Presiona Enter para comenzar..."
    
    # =========================================================================
    # PASO 0: Selección de carpeta de destino
    # =========================================================================
    
    clear
    print_header "📁 Paso 0/6: Carpeta de Destino"
    
    print_step "Detectando carpetas de posts..."
    local post_folders=($(detect_post_folders "$blog_path"))
    
    if [ ${#post_folders[@]} -eq 0 ]; then
        print_warning "No se detectaron carpetas de posts existentes"
        read -p "Nombre de la nueva carpeta de posts: " new_folder
        post_folders=("$new_folder")
    fi
    
    echo ""
    echo -e "${CYAN}Carpetas disponibles:${NC}"
    local i=1
    for folder in "${post_folders[@]}"; do
        echo -e "  ${MAGENTA}$i)${NC} ${GREEN}$folder${NC}"
        i=$((i + 1))
    done
    echo -e "  ${MAGENTA}$i)${NC} ${BOLD}Crear nueva carpeta${NC}"
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
    
    print_success "Carpeta seleccionada: $target_folder"
    sleep 1
    
    # =========================================================================
    # SECCIÓN 1: OPCIONES GENERALES
    # =========================================================================
    
    clear
    print_header "📝 Sección 1/6: Opciones Generales"
    
    # 1.1. Información del Título
    print_subheader "1.1. Información del Título"
    
    read -p "Title (título principal): " post_title
    while [ -z "$post_title" ]; do
        print_warning "El título es obligatorio"
        read -p "Title: " post_title
    done
    
    echo -e "${DIM}Ejemplo: \"Análisis Econométrico Avanzado: Modelos ARIMA\"${NC}"
    read -p "Subtitle (opcional, Enter para omitir): " post_subtitle
    
    local short_title
    echo -e "${DIM}Ejemplo: \"Análisis Econométrico\" (máx. 50 caracteres)${NC}"
    read -p "Shorttitle (Enter para auto-generar desde title): " short_title
    if [ -z "$short_title" ]; then
        short_title=$(echo "$post_title" | cut -c1-50)
    fi
    
    # 1.2. Opciones del Documento
    print_subheader "1.2. Opciones del Documento"
    
    echo -e "${DIM}Configuración avanzada del documento (Enter para valores por defecto)${NC}"
    echo ""
    
    read -p "Floatsintext - Figuras/tablas en texto (s/n, default: n): " floatsintext
    floatsintext=${floatsintext:-n}
    
    read -p "Numbered-lines - Números de línea (s/n, default: n): " numbered_lines
    numbered_lines=${numbered_lines:-n}
    
    read -p "No-ampersand-parenthetical - Usar 'y' en lugar de '&' (s/n, default: n): " no_ampersand
    no_ampersand=${no_ampersand:-n}
    
    echo -e "${DIM}Ejemplo: \"referencias.bib\" o \"bib1.bib, bib2.bib\"${NC}"
    read -p "Bibliography file(s) (Enter para 'references.bib'): " bibliography
    bibliography=${bibliography:-references.bib}
    
    read -p "Mask - Revisión ciega (s/n, default: n): " mask
    mask=${mask:-n}
    
    echo -e "${DIM}Ejemplo: \"@estudio1, @estudio2\" (para meta-análisis)${NC}"
    read -p "Nocite - Referencias no citadas (Enter para omitir): " nocite
    
    read -p "Meta-analysis - Marcar estudios con asterisco (s/n, default: n): " meta_analysis
    meta_analysis=${meta_analysis:-n}
    
    echo -e "${DIM}Ejemplo: \"Este estudio impacta la práctica clínica...\"${NC}"
    read -p "Impact-statement (Enter para omitir): " impact_statement
    
    # 1.3. Suprimir Elementos
    print_subheader "1.3. Suprimir Elementos (opcional)"
    
    echo -e "${YELLOW}¿Deseas configurar supresión de elementos? (s/n, default: n):${NC} "
    read suppress_config
    
    declare -A suppress_elements
    if [[ "$suppress_config" =~ ^[Ss]$ ]]; then
        echo ""
        echo -e "${DIM}Marca 's' para suprimir cada elemento:${NC}"
        
        for element in title-page title short-title author affiliation author-note orcid abstract keywords; do
            read -p "  Suppress-$element (s/n): " suppress_choice
            suppress_elements[$element]=$suppress_choice
        done
    fi
    
    print_success "Opciones generales configuradas"
    sleep 1
    
    # =========================================================================
    # SECCIÓN 2: OPCIONES DE FORMATO
    # =========================================================================
    
    clear
    print_header "🎨 Sección 2/6: Opciones de Formato"
    
    print_subheader "2.1. Tipo de Documento"
    
    echo ""
    echo -e "${MAGENTA}1)${NC} doc  - Documento general (flexible)"
    echo -e "${MAGENTA}2)${NC} jou  - Formato revista (2 columnas) ${YELLOW}[Recomendado]${NC}"
    echo -e "${MAGENTA}3)${NC} man  - Manuscrito formal"
    echo -e "${MAGENTA}4)${NC} stu  - Trabajo estudiantil"
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
    
    print_subheader "2.2. Formatos de Salida"
    
    echo -e "${DIM}Selecciona formatos a generar (s/n para cada uno):${NC}"
    
    read -p "  apaquarto-docx (Word) (s/n, default: s): " format_docx
    format_docx=${format_docx:-s}
    
    read -p "  apaquarto-html (Web) (s/n, default: s): " format_html
    format_html=${format_html:-s}
    
    read -p "  apaquarto-pdf (PDF) (s/n, default: s): " format_pdf
    format_pdf=${format_pdf:-s}
    
    read -p "  apaquarto-typst (Typst) (s/n, default: n): " format_typst
    format_typst=${format_typst:-n}
    
    # Configuración específica según formato
    local fontsize blank_lines_title blank_lines_author a4paper
    
    if [[ "$format_pdf" =~ ^[Ss]$ ]] || [[ "$format_typst" =~ ^[Ss]$ ]]; then
        echo ""
        echo -e "${DIM}Ejemplo: \"12pt\" (opciones: 10pt, 11pt, 12pt)${NC}"
        read -p "  Fontsize (Enter=12pt): " fontsize
        fontsize=${fontsize:-12pt}
        
        echo -e "${DIM}Ejemplo: 2 (líneas en blanco sobre el título)${NC}"
        read -p "  Blank-lines-above-title (Enter=2): " blank_lines_title
        blank_lines_title=${blank_lines_title:-2}
        
        read -p "  Blank-lines-above-author-note (Enter=2): " blank_lines_author
        blank_lines_author=${blank_lines_author:-2}
        
        read -p "  A4paper (s/n, default: n): " a4paper
        a4paper=${a4paper:-n}
    fi
    
    # Información específica del tipo de documento
    local journal_name volume_info course_name professor_name due_date student_note
    
    if [ "$doc_type" = "jou" ]; then
        print_subheader "2.3. Información de Revista (modo journal)"
        
        echo -e "${DIM}Ejemplo: \"Journal of Economic Psychology\"${NC}"
        read -p "Nombre de la revista: " journal_name
        
        echo -e "${DIM}Ejemplo: \"2025, Vol. 7, No. 1, 1--25\"${NC}"
        read -p "Volumen y número: " volume_info
        
        echo -e "${DIM}Ejemplo: \"© 2025\"${NC}"
        read -p "Copyright notice (Enter para omitir): " copyright_notice
        
        echo -e "${DIM}Ejemplo: \"Todos los derechos reservados\"${NC}"
        read -p "Copyright text (Enter para omitir): " copyright_text
        
    elif [ "$doc_type" = "stu" ]; then
        print_subheader "2.3. Información del Curso (modo estudiantil)"
        
        echo -e "${DIM}Ejemplo: \"Econometría Aplicada (ECON 5201)\"${NC}"
        read -p "Nombre del curso: " course_name
        
        echo -e "${DIM}Ejemplo: \"Dr. Juan Pérez\"${NC}"
        read -p "Profesor: " professor_name
        
        echo -e "${DIM}Ejemplo: \"15/12/2025\"${NC}"
        read -p "Fecha de entrega: " due_date
        
        echo -e "${DIM}Ejemplo: \"Student ID: 2020123456\"${NC}"
        read -p "Nota adicional (Enter para omitir): " student_note
    fi
    
    print_success "Opciones de formato configuradas"
    sleep 1
    
    # =========================================================================
    # SECCIÓN 3: AUTORES Y AFILIACIONES
    # =========================================================================
    
    clear
    print_header "👤 Sección 3/6: Autores y Afiliaciones"
    
    echo -e "${YELLOW}¿Usar autor predeterminado de _metadata.yml? (s/n):${NC} "
    read use_default_author
    
    local author_yaml=""
    local authors_data=()
    
    if [[ ! "$use_default_author" =~ ^[Ss]$ ]]; then
        print_subheader "3.1. Información del Autor Principal"
        
        echo -e "${DIM}Ejemplo: \"María González Pérez\"${NC}"
        read -p "Nombre completo: " author_name
        
        echo -e "${DIM}Ejemplo: \"0000-0002-1234-5678\"${NC}"
        read -p "ORCID (Enter para omitir): " author_orcid
        
        echo -e "${DIM}Ejemplo: \"maria.gonzalez@universidad.edu\"${NC}"
        read -p "Email: " author_email
        
        read -p "¿Es autor correspondiente? (s/n, default: s): " is_corresponding
        is_corresponding=${is_corresponding:-s}
        
        echo -e "${DIM}Ejemplo: \"https://investigador.com/maria\"${NC}"
        read -p "URL (Enter para omitir): " author_url
        
        # Roles CRediT
        print_subheader "3.2. Roles CRediT del Autor"
        
        echo -e "${DIM}Opciones: No, Yes, Lead, Supporting, Equal (Enter para No)${NC}"
        echo ""
        
        declare -A credit_roles
        for role in conceptualization "data-curation" "formal-analysis" "funding-acquisition" \
                    investigation methodology "project-administration" resources software \
                    supervision validation visualization writing editing; do
            role_display=$(echo "$role" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
            read -p "  $role_display (No/Yes/Lead/Supporting/Equal): " role_value
            if [ ! -z "$role_value" ] && [ "$role_value" != "No" ]; then
                credit_roles[$role]=$role_value
            fi
        done
        
        # Afiliación
        print_subheader "3.3. Afiliación Institucional"
        
        echo -e "${DIM}Ejemplo: \"unsch\"${NC}"
        read -p "ID de afiliación: " affiliation_id
        
        echo -e "${DIM}Ejemplo: \"Universidad Nacional de San Cristóbal de Huamanga\"${NC}"
        read -p "Nombre de la institución: " institution_name
        
        echo -e "${DIM}Ejemplo: \"Facultad de Ciencias Económicas\"${NC}"
        read -p "Departamento: " department
        
        echo -e "${DIM}Ejemplo: \"Av. Independencia 123\"${NC}"
        read -p "Dirección (Enter para omitir): " address
        
        echo -e "${DIM}Ejemplo: \"Ayacucho\"${NC}"
        read -p "Ciudad: " city
        
        echo -e "${DIM}Ejemplo: \"Ayacucho\"${NC}"
        read -p "Región/Estado: " region
        
        echo -e "${DIM}Ejemplo: \"Perú\"${NC}"
        read -p "País (Enter para omitir): " country
        
        echo -e "${DIM}Ejemplo: \"05001\"${NC}"
        read -p "Código postal (Enter para omitir): " postal_code
        
        # Guardar datos del autor
        authors_data+=("$author_name|$author_orcid|$author_email|$is_corresponding|$author_url")
    fi
    
    print_success "Información de autores configurada"
    sleep 1
    
    # =========================================================================
    # SECCIÓN 4: AUTHOR NOTE
    # =========================================================================
    
    clear
    print_header "📋 Sección 4/6: Author Note"
    
    print_subheader "4.1. Cambios de Estado"
    
    echo -e "${DIM}Ejemplo: \"María González ahora está en Temple University.\"${NC}"
    read -p "Affiliation-change (Enter para omitir): " affiliation_change
    
    echo -e "${DIM}Ejemplo: \"Juan Pérez falleció el 15 de enero de 2024.\"${NC}"
    read -p "Deceased (Enter para omitir): " deceased
    
    print_subheader "4.2. Disclosures"
    
    echo -e "${DIM}Ejemplo: \"Los autores no tienen conflictos de interés que declarar.\"${NC}"
    read -p "Conflict-of-interest: " conflict_of_interest
    conflict_of_interest=${conflict_of_interest:-Los autores no tienen conflictos de interés que declarar.}
    
    echo -e "${DIM}Ejemplo: \"Este estudio fue financiado por Grant XYZ-789...\"${NC}"
    read -p "Financial-support (Enter para omitir): " financial_support
    
    echo -e "${DIM}Ejemplo: \"Registrado en ClinicalTrials.gov (NCT123456).\"${NC}"
    read -p "Study-registration (Enter para omitir): " study_registration
    
    echo -e "${DIM}Ejemplo: \"Los datos están disponibles en https://osf.io/abc123.\"${NC}"
    read -p "Data-sharing (Enter para omitir): " data_sharing
    
    echo -e "${DIM}Ejemplo: \"Basado en la tesis doctoral de María González (2023).\"${NC}"
    read -p "Related-report (Enter para omitir): " related_report
    
    echo -e "${DIM}Ejemplo: \"Agradecemos a Dr. Pedro López por sus comentarios.\"${NC}"
    read -p "Gratitude (Enter para omitir): " gratitude
    
    echo -e "${DIM}Ejemplo: \"El orden de autoría refleja contribuciones iguales.\"${NC}"
    read -p "Authorship-agreements (Enter para omitir): " authorship_agreements
    
    print_success "Author Note configurada"
    sleep 1
    
    # =========================================================================
    # SECCIÓN 5: ABSTRACT Y KEYWORDS
    # =========================================================================
    
    clear
    print_header "📄 Sección 5/6: Abstract y Keywords"
    
    print_subheader "5.1. Abstract"
    
    echo -e "${DIM}Escribe el resumen (máximo 250 palabras). Presiona Enter dos veces para finalizar.${NC}"
    echo -e "${DIM}Ejemplo: \"Este estudio examina el impacto de X en Y utilizando datos de Z...\"${NC}"
    echo ""
    
    echo "Abstract:"
    local abstract=""
    local line
    while IFS= read -r line; do
        if [ -z "$line" ]; then
            break
        fi
        abstract="$abstract$line "
    done
    
    print_subheader "5.2. Keywords"
    
    echo -e "${DIM}Ejemplo: economía, política fiscal, crecimiento económico${NC}"
    read -p "Keywords (separadas por comas, 3-5 recomendadas): " keywords_input
    
    # Convertir a array
    IFS=',' read -ra keywords <<< "$keywords_input"
    
    print_subheader "5.3. Impact Statement (opcional)"
    
    echo -e "${DIM}Ejemplo: \"Los hallazgos tienen implicaciones directas para el diseño de políticas fiscales...\"${NC}"
    read -p "Impact-statement (Enter para omitir): " impact_statement_sec5
    
    read -p "Word-count - Mostrar conteo de palabras (s/n, default: n): " word_count
    word_count=${word_count:-n}
    
    print_success "Abstract y keywords configurados"
    sleep 1
    
    # =========================================================================
    # SECCIÓN 6: OPCIONES DE IDIOMA
    # =========================================================================
    
    clear
    print_header "🌍 Sección 6/6: Opciones de Idioma"
    
    echo -e "${DIM}Códigos: en (inglés), es (español), fr (francés), de (alemán), pt (portugués)${NC}"
    read -p "Lang (Enter=es): " lang
    lang=${lang:-es}
    
    if [ "$lang" != "en" ]; then
        print_subheader "6.1. Personalizaciones de Idioma"
        
        echo -e "${DIM}Para español: \"y\", para inglés: \"and\"${NC}"
        read -p "Citation-last-author-separator (Enter=\"y\"): " citation_separator
        citation_separator=${citation_separator:-y}
        
        echo -e "${DIM}Ejemplo: \"Cita Enmascarada\"${NC}"
        read -p "Citation-masked-author (Enter=Cita Enmascarada): " citation_masked
        citation_masked=${citation_masked:-Cita Enmascarada}
        
        echo -e "${DIM}Ejemplo: \"n.f.\" (no fecha)${NC}"
        read -p "Citation-masked-date (Enter=n.f.): " citation_date
        citation_date=${citation_date:-n.f.}
        
        echo -e "${DIM}Ejemplo: \"Nota de Autores\"${NC}"
        read -p "Title-block-author-note (Enter=Nota de Autores): " author_note_title
        author_note_title=${author_note_title:-Nota de Autores}
        
        echo -e "${DIM}¿Configurar más opciones de idioma? (s/n, default: n):${NC} "
        read more_lang_config
        
        local correspondence_note role_intro impact_title word_count_title meta_ref
        if [[ "$more_lang_config" =~ ^[Ss]$ ]]; then
            read -p "Title-block-correspondence-note: " correspondence_note
            read -p "Title-block-role-introduction: " role_intro
            read -p "Title-impact-statement: " impact_title
            read -p "Title-word-count: " word_count_title
            read -p "References-meta-analysis: " meta_ref
        fi
    fi
    
    print_success "Opciones de idioma configuradas"
    sleep 1
    
    # =========================================================================
    # INFORMACIÓN ADICIONAL
    # =========================================================================
    
    clear
    print_header "🏷️ Información Adicional"
    
    echo -e "${DIM}Ejemplo: análisis, econometría, tutorial${NC}"
    read -p "Tags (separados por comas): " tags_input
    
    echo -e "${DIM}Ejemplo: Análisis, Tutorial (máximo 2)${NC}"
    read -p "Categorías (separadas por comas, 1-2): " categories_input
    
    # Convertir a arrays
    IFS=',' read -ra tags <<< "$tags_input"
    IFS=',' read -ra categories <<< "$categories_input"
    
    print_success "Información adicional configurada"
    sleep 1
    
    # =========================================================================
    # GENERACIÓN DEL ARCHIVO INDEX.QMD
    # =========================================================================
    
    clear
    print_header "⚙️ Generando index.qmd..."
    
    # Crear nombre del directorio
    local date=$(date +%Y-%m-%d)
    local post_slug=$(echo "$post_title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
    local post_dir="$blog_path/$target_folder/$date-$post_slug"
    
    if [ -d "$post_dir" ]; then
        print_error "Ya existe un post con ese nombre"
        return 1
    fi
    
    mkdir -p "$post_dir"
    
    # Crear archivo index.qmd
    cat > "$post_dir/index.qmd" << EOF
---
title: "$post_title"
EOF
    
    # Añadir elementos opcionales de la sección 1.1
    [ ! -z "$post_subtitle" ] && echo "subtitle: \"$post_subtitle\"" >> "$post_dir/index.qmd"
    # Añadir shorttitle
    echo "shorttitle: \"$short_title\"" >> "$post_dir/index.qmd"
    
    # Añadir fecha
    echo "date: \"$date\"" >> "$post_dir/index.qmd"
    echo "date-modified: \"today\"" >> "$post_dir/index.qmd"
    
    # Añadir tags
    if [ ${#tags[@]} -gt 0 ]; then
        echo -n "tags: [" >> "$post_dir/index.qmd"
        for i in "${!tags[@]}"; do
            tag=$(echo "${tags[$i]}" | xargs)
            [ $i -eq 0 ] && echo -n "\"$tag\"" >> "$post_dir/index.qmd" || echo -n ", \"$tag\"" >> "$post_dir/index.qmd"
        done
        echo "]" >> "$post_dir/index.qmd"
    fi
    
    # Añadir categorías
    if [ ${#categories[@]} -gt 0 ]; then
        echo -n "categories: [" >> "$post_dir/index.qmd"
        for i in "${!categories[@]}"; do
            cat=$(echo "${categories[$i]}" | xargs)
            [ $i -eq 0 ] && echo -n "\"$cat\"" >> "$post_dir/index.qmd" || echo -n ", \"$cat\"" >> "$post_dir/index.qmd"
        done
        echo "]" >> "$post_dir/index.qmd"
    fi
    
    # Añadir imagen predeterminada
    echo "image: ../featured.jpg" >> "$post_dir/index.qmd"

    # Añadir bibliografía
    echo "bibliography: $bibliography" >> "$post_dir/index.qmd"

    # Añadir jupyter si es necesario
    echo "jupyter: python3" >> "$post_dir/index.qmd"
    
    # Opciones del documento (sección 1.2)
    [[ "$floatsintext" =~ ^[Ss]$ ]] && echo "floatsintext: true" >> "$post_dir/index.qmd"
    [[ "$numbered_lines" =~ ^[Ss]$ ]] && echo "numbered-lines: true" >> "$post_dir/index.qmd"
    [[ "$no_ampersand" =~ ^[Ss]$ ]] && echo "no-ampersand-parenthetical: true" >> "$post_dir/index.qmd"
    [[ "$mask" =~ ^[Ss]$ ]] && echo "mask: true" >> "$post_dir/index.qmd"
    [ ! -z "$nocite" ] && echo "nocite: \"$nocite\"" >> "$post_dir/index.qmd"
    [[ "$meta_analysis" =~ ^[Ss]$ ]] && echo "meta-analysis: true" >> "$post_dir/index.qmd"
    [ ! -z "$impact_statement" ] && echo "impact-statement: \"$impact_statement\"" >> "$post_dir/index.qmd"
    
    # Elementos suprimidos (sección 1.3)
    for element in "${!suppress_elements[@]}"; do
        [[ "${suppress_elements[$element]}" =~ ^[Ss]$ ]] && echo "suppress-$element: true" >> "$post_dir/index.qmd"
    done
    
    # Información específica del tipo de documento
    if [ "$doc_type" = "jou" ]; then
        [ ! -z "$journal_name" ] && echo "journal: \"$journal_name\"" >> "$post_dir/index.qmd"
        [ ! -z "$volume_info" ] && echo "volume: \"$volume_info\"" >> "$post_dir/index.qmd"
        [ ! -z "$copyright_notice" ] && echo "copyrightnotice: \"$copyright_notice\"" >> "$post_dir/index.qmd"
        [ ! -z "$copyright_text" ] && echo "copyrightext: \"$copyright_text\"" >> "$post_dir/index.qmd"
    elif [ "$doc_type" = "stu" ]; then
        [ ! -z "$course_name" ] && echo "course: \"$course_name\"" >> "$post_dir/index.qmd"
        [ ! -z "$professor_name" ] && echo "professor: \"$professor_name\"" >> "$post_dir/index.qmd"
        [ ! -z "$due_date" ] && echo "duedate: \"$due_date\"" >> "$post_dir/index.qmd"
        [ ! -z "$student_note" ] && echo "note: \"$student_note\"" >> "$post_dir/index.qmd"
    fi
    
    # Autor (solo si no usa predeterminado)
    if [[ ! "$use_default_author" =~ ^[Ss]$ ]]; then
        cat >> "$post_dir/index.qmd" << AUTHOR_EOF

author:
  - name: $author_name
AUTHOR_EOF
        [ ! -z "$author_orcid" ] && echo "    orcid: $author_orcid" >> "$post_dir/index.qmd"
        [ ! -z "$author_email" ] && echo "    email: $author_email" >> "$post_dir/index.qmd"
        [[ "$is_corresponding" =~ ^[Ss]$ ]] && echo "    corresponding: true" >> "$post_dir/index.qmd"
        [ ! -z "$author_url" ] && echo "    url: $author_url" >> "$post_dir/index.qmd"
        
        # Roles CRediT
        if [ ${#credit_roles[@]} -gt 0 ]; then
            echo "    role:" >> "$post_dir/index.qmd"
            for role in "${!credit_roles[@]}"; do
                echo "      - $role: ${credit_roles[$role]}" >> "$post_dir/index.qmd"
            done
        fi
        
        # Afiliación
        if [ ! -z "$institution_name" ]; then
            cat >> "$post_dir/index.qmd" << AFF_EOF
    affiliations:
      - id: $affiliation_id
        name: $institution_name
AFF_EOF
            [ ! -z "$department" ] && echo "        department: $department" >> "$post_dir/index.qmd"
            [ ! -z "$address" ] && echo "        address: $address" >> "$post_dir/index.qmd"
            [ ! -z "$city" ] && echo "        city: $city" >> "$post_dir/index.qmd"
            [ ! -z "$region" ] && echo "        region: $region" >> "$post_dir/index.qmd"
            [ ! -z "$country" ] && echo "        country: $country" >> "$post_dir/index.qmd"
            [ ! -z "$postal_code" ] && echo "        postal-code: $postal_code" >> "$post_dir/index.qmd"
        fi
    fi
    
    # Author Note (sección 4)
    cat >> "$post_dir/index.qmd" << NOTE_EOF

author-note:
NOTE_EOF
    
    if [ ! -z "$affiliation_change" ] || [ ! -z "$deceased" ]; then
        echo "  status-changes:" >> "$post_dir/index.qmd"
        [ ! -z "$affiliation_change" ] && echo "    affiliation-change: \"$affiliation_change\"" >> "$post_dir/index.qmd"
        [ ! -z "$deceased" ] && echo "    deceased: \"$deceased\"" >> "$post_dir/index.qmd"
    fi
    
    cat >> "$post_dir/index.qmd" << DISC_EOF
  disclosures:
    conflict-of-interest: "$conflict_of_interest"
DISC_EOF
    
    [ ! -z "$financial_support" ] && echo "    financial-support: \"$financial_support\"" >> "$post_dir/index.qmd"
    [ ! -z "$study_registration" ] && echo "    study-registration: \"$study_registration\"" >> "$post_dir/index.qmd"
    [ ! -z "$data_sharing" ] && echo "    data-sharing: \"$data_sharing\"" >> "$post_dir/index.qmd"
    [ ! -z "$related_report" ] && echo "    related-report: \"$related_report\"" >> "$post_dir/index.qmd"
    [ ! -z "$gratitude" ] && echo "    gratitude: \"$gratitude\"" >> "$post_dir/index.qmd"
    [ ! -z "$authorship_agreements" ] && echo "    authorship-agreements: \"$authorship_agreements\"" >> "$post_dir/index.qmd"
    
    # Abstract y keywords (sección 5)
    [ ! -z "$abstract" ] && echo "abstract: \"$abstract\"" >> "$post_dir/index.qmd"
    
    if [ ${#keywords[@]} -gt 0 ]; then
        echo -n "keywords: [" >> "$post_dir/index.qmd"
        for i in "${!keywords[@]}"; do
            kw=$(echo "${keywords[$i]}" | xargs)
            [ $i -eq 0 ] && echo -n "\"$kw\"" >> "$post_dir/index.qmd" || echo -n ", \"$kw\"" >> "$post_dir/index.qmd"
        done
        echo "]" >> "$post_dir/index.qmd"
    fi
    
    [ ! -z "$impact_statement_sec5" ] && echo "impact-statement: \"$impact_statement_sec5\"" >> "$post_dir/index.qmd"
    [[ "$word_count" =~ ^[Ss]$ ]] && echo "word-count: true" >> "$post_dir/index.qmd"
    
    # Idioma (sección 6)
    echo "lang: $lang" >> "$post_dir/index.qmd"
    
    if [ "$lang" != "en" ]; then
        cat >> "$post_dir/index.qmd" << LANG_EOF
language:
  citation-last-author-separator: "$citation_separator"
  citation-masked-author: "$citation_masked"
  citation-masked-date: "$citation_date"
  title-block-author-note: "$author_note_title"
LANG_EOF
        [ ! -z "$correspondence_note" ] && echo "  title-block-correspondence-note: \"$correspondence_note\"" >> "$post_dir/index.qmd"
        [ ! -z "$role_intro" ] && echo "  title-block-role-introduction: \"$role_intro\"" >> "$post_dir/index.qmd"
        [ ! -z "$impact_title" ] && echo "  title-impact-statement: \"$impact_title\"" >> "$post_dir/index.qmd"
        [ ! -z "$word_count_title" ] && echo "  title-word-count: \"$word_count_title\"" >> "$post_dir/index.qmd"
        [ ! -z "$meta_ref" ] && echo "  references-meta-analysis: \"$meta_ref\"" >> "$post_dir/index.qmd"
    fi
    
    # Cerrar YAML y añadir contenido
    cat >> "$post_dir/index.qmd" << 'CONTENT_EOF'
---

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
CONTENT_EOF
    
    # Crear archivo references.bib vacío
    touch "$post_dir/references.bib"
    
    # Resumen final
    clear
    print_header "✅ Post Creado Exitosamente"
    
    echo ""
    print_info "Ubicación: $post_dir"
    print_info "Archivo: index.qmd"
    print_info "Tipo: APAQuarto $doc_type"
    print_info "Carpeta: $target_folder"
    echo ""
    
    echo -e "${CYAN}Resumen de configuración:${NC}"
    echo -e "  ${DIM}• Título: $post_title${NC}"
    [ ! -z "$post_subtitle" ] && echo -e "  ${DIM}• Subtítulo: $post_subtitle${NC}"
    echo -e "  ${DIM}• Tipo de documento: $doc_type${NC}"
    echo -e "  ${DIM}• Tags: ${#tags[@]}${NC}"
    echo -e "  ${DIM}• Categorías: ${#categories[@]}${NC}"
    [ ! -z "$author_name" ] && echo -e "  ${DIM}• Autor: $author_name${NC}"
    echo ""

    # Preguntar si desea abrir el archivo
    read -p "¿Deseas abrir el archivo para editar? (s/n): " open_file
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

# Metadatos del Documento
date-modified: "today"
license: "CC BY-SA"
lang: es
search: true
lightbox: true

# Configuración del Bloque de Título
title-block-banner: true
is-particlejs-enabled: true

# =============================================================================
# INFORMACIÓN DEL AUTOR
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
      deceased: false
    roles:
      - conceptualización
      - redacción

# Nota del Autor
author-note:
  disclosures:
    conflict-of-interest: Los autores no tienen conflictos de intereses que revelar.

# =============================================================================
# CONFIGURACIÓN DE TABLA DE CONTENIDOS
# =============================================================================

toc: true
toc-title: " "
toc-location: left

# =============================================================================
# CONFIGURACIÓN DE REFERENCIAS Y CITAS
# =============================================================================

floatsintext: true
citation: true
google-scholar: true
link-citations: true
appendix-cite-as: display
citation-last-author-separator: "y"
citation-masked-author: "Cita Enmascarada"
citation-masked-title: "Título Enmascarado"
citation-masked-date: "n.f."

# Bloques de Títulos
title-block-author-note: "Nota de Autores"
title-block-correspondence-note: "La correspondencia relativa a este artículo debe dirigirse a"
title-block-role-introduction: "Los roles de autor se clasificaron utilizando la taxonomía de roles de colaborador (CRediT; https://credit.niso.org/) de la siguiente manera:"
references-meta-analysis: "Las referencias marcadas con un asterisco indican estudios incluidos en el metanálisis."

# =============================================================================
# CONFIGURACIÓN DE REFERENCIAS CRUZADAS
# =============================================================================

language:
  crossref-fig-title: Figura
  crossref-tbl-title: Tabla
  crossref-lst-title: "Listing"
  crossref-thm-title: "Teorema"
  crossref-lem-title: "Lema"
  crossref-cor-title: "Corolario"
  crossref-prp-title: "Proposición"
  crossref-cnj-title: "Conjetura"
  crossref-def-title: "Definición"
  crossref-exm-title: "Ejemplo"
  crossref-exr-title: "Ejercicio"
  crossref-ch-prefix: "Capítulo"
  crossref-apx-prefix: Anexo
  crossref-sec-prefix: "Sección"
  crossref-eq-prefix: Ecuación
  crossref-lof-title: "Lista de Figuras"
  crossref-lot-title: "Lista de Tablas"
  crossref-lol-title: "Lista de Listings"

# =============================================================================
# CONFIGURACIÓN DE VISIBILIDAD Y BORRADOR
# =============================================================================

mask: false
draft: true
draftfirst: false
draftall: false

# =============================================================================
# FORMATOS DE SALIDA
# =============================================================================

format:
  # ---------------------------------------------------------------------------
  # Formato HTML
  # ---------------------------------------------------------------------------
  html:
    toc-depth: 1
    toc-expand: 3
    smooth-scroll: true
    link-external-newwindow: true
    citations-hover: true
    footnotes-hover: true
    highlight-style: github
    code-copy: true
    code-fold: true
    code-summary: "Mostrar el código"
    code-overflow: scroll
    code-line-numbers: true
    code-tools:
      source: repo
      toggle: false
      caption: none
    mermaid:
      theme: neutral
    citation-location: document
    self-contained: true
    template-partials:
      - ../_partials/title-block-link-buttons/title-block.html
    theme: litera
    other-links:
      - text: Gravatar
        href: https://gravatar.com/achalmaedison
    format-links: true

  # ---------------------------------------------------------------------------
  # Formato PDF (APA Quarto)
  # ---------------------------------------------------------------------------
  apaquarto-pdf:
    documentmode: jou
    copyrightnotice: 2025
    copyrightext: Todos los derechos reservados
    toc: true
    list-of-figures: true
    list-of-tables: true
    keep-tex: true
    fontsize: 12pt
    a4paper: true
    numbered-lines: false
    number-sections: true
    colorlinks: true
    pdf-engine: xelatex
    keep-md: false

  # ---------------------------------------------------------------------------
  # Formato DOCX (APA Quarto)
  # ---------------------------------------------------------------------------
  apaquarto-docx:
    toc: true
    fontsize: 12pt
    a4paper: true
    numbered-lines: false
    number-sections: true
    keep-md: false

# =============================================================================
# CONFIGURACIÓN DEL ENTORNO DE EJECUCIÓN
# =============================================================================

jupyter: python3

# Editor
editor:
  # Modo preferido (source o visual)
  mode: source
  
  # Configuración de Markdown
  markdown:
    canonical: true      # Formato consistente. Usar formato Markdown canónico (mejor para control de versiones)
    wrap: 72            # 72 caracteres por línea
    references:
      location: section # Notas al pie por sección
    
    # Opciones de escritura
    auto-wrapping: true
    sentence-spacing: true

# =============================================================================
# CONFIGURACIÓN DE COMENTARIOS
# =============================================================================

comments:
  utterances:
    repo: achalmed/website-achalma
    issue-term: title
    theme: boxy-light
    label: "comments :crystal_ball:"

# =============================================================================
# CONFIGURACIÓN DE EJECUCIÓN
# =============================================================================

execute:
  freeze: true  # true: Nunca re-ejecutar durante el renderizado del proyecto. auto: Re-ejecutar solo cuando cambia el código fuente (fuciona solo si .qmd que tienen Python/R)
  keep-md: true  # Mantener archivos .md generados
  keep-ipynb: true 
  echo: true  # Mostrar comandos ejecutados
  output: true  # Mostrar resultados de la ejecución
  warning: false  # Ocultar advertencias
  error: false  # Ocultar errores
  enabled: false  # Deshabilita la ejecución de código por defecto. Habilitar la ejecución: quarto render notebook.ipynb --execute
  cache: true  # PARA RESULTADOS DE CALCULO: quarto render index.qmd --cache-refresh #singledoc quarto render --cache-refresh #entireproject
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
