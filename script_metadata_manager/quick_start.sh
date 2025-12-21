#!/bin/bash

################################################################################
# Script de Inicio Rápido - Sistema de Gestión de Metadatos Quarto
# Versión: 1.2.0
# Autor: Edison Achalma
# Fecha: Diciembre 2024
################################################################################

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

# Verificar entorno conda
check_conda() {
    if command -v conda &> /dev/null; then
        if [ -n "$CONDA_DEFAULT_ENV" ]; then
            if [ "$CONDA_DEFAULT_ENV" = "metadata_manager" ]; then
                return 0
            else
                print_warning "Entorno actual: $CONDA_DEFAULT_ENV"
                print_info "Cambiando a metadata_manager..."
                eval "$(conda shell.bash hook)"
                conda activate metadata_manager
                return 0
            fi
        else
            print_warning "Entorno conda no activado"
            print_info "Activando metadata_manager..."
            eval "$(conda shell.bash hook)"
            conda activate metadata_manager
            return 0
        fi
    fi
    return 1
}

# Verificar Python y dependencias
check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 no encontrado"
        return 1
    fi
    
    if ! python3 -c "import pandas, openpyxl, yaml" 2>/dev/null; then
        print_error "Dependencias faltantes"
        print_info "Ejecuta: ./install.sh"
        return 1
    fi
    
    return 0
}

# Banner
show_banner() {
    clear
    print_header "🚀 INICIO RÁPIDO - GESTIÓN DE METADATOS QUARTO v1.2"
    echo ""
    echo -e "${CYAN}Autor:${NC} Edison Achalma"
    echo -e "${CYAN}Versión:${NC} 1.2.0"
    echo ""
}

# Menú principal
show_menu() {
    print_header "📋 MENÚ PRINCIPAL"
    echo ""
    echo -e "${GREEN}CREAR BASES DE DATOS${NC}"
    echo -e "  ${CYAN}1)${NC} Crear base general (todos los blogs)"
    echo -e "  ${CYAN}2)${NC} Crear base de un blog específico"
    echo ""
    echo -e "${YELLOW}ACTUALIZAR METADATOS${NC}"
    echo -e "  ${CYAN}3)${NC} Simular actualización (--dry-run)"
    echo -e "  ${CYAN}4)${NC} Actualizar desde Excel"
    echo -e "  ${CYAN}5)${NC} Actualizar solo un blog"
    echo -e "  ${CYAN}6)${NC} Actualizar con filtro de ruta"
    echo ""
    echo -e "${PURPLE}UTILIDADES${NC}"
    echo -e "  ${CYAN}7)${NC} Crear configuración"
    echo -e "  ${CYAN}8)${NC} Ver ayuda"
    echo -e "  ${CYAN}9)${NC} Abrir Excel generado"
    echo ""
    echo -e "${BLUE}0)${NC} Salir"
    echo ""
}

# Obtener ruta base
get_base_path() {
    if [ -f "metadata_config.yml" ]; then
        BASE_PATH=$(grep "excel_output_dir" metadata_config.yml | cut -d':' -f2- | xargs | sed 's|/excel_databases||' | sed "s|~|$HOME|")
        if [ -z "$BASE_PATH" ]; then
            BASE_PATH="$HOME/Documents/publicaciones"
        fi
    else
        BASE_PATH="$HOME/Documents/publicaciones"
    fi
    
    echo -e "${PURPLE}Ruta actual:${NC} $BASE_PATH"
    read -p "¿Usar esta ruta? (S/n): " USE_DEFAULT
    
    if [ "$USE_DEFAULT" = "n" ] || [ "$USE_DEFAULT" = "N" ]; then
        read -p "Ingresa la ruta: " CUSTOM_PATH
        if [ -n "$CUSTOM_PATH" ]; then
            BASE_PATH="${CUSTOM_PATH/#\~/$HOME}"
        fi
    fi
    
    if [ ! -d "$BASE_PATH" ]; then
        print_error "La ruta no existe: $BASE_PATH"
        read -p "¿Crear directorio? (s/N): " CREATE_DIR
        if [ "$CREATE_DIR" = "s" ] || [ "$CREATE_DIR" = "S" ]; then
            mkdir -p "$BASE_PATH"
            print_success "Directorio creado"
        else
            return 1
        fi
    fi
    
    return 0
}

# Opción 1: Crear base general
option_create_all() {
    print_header "📊 CREAR BASE GENERAL"
    echo ""
    
    get_base_path || return
    
    print_step "Creando base de datos de todos los blogs..."
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        python3 quarto_metadata_manager.py create-template "$BASE_PATH" \
            --config metadata_config.yml
    else
        python3 quarto_metadata_manager.py create-template "$BASE_PATH"
    fi
    
    echo ""
    print_success "Base de datos creada"
    read -p "Presiona Enter para continuar..."
}

# Opción 2: Crear base de blog específico
option_create_blog() {
    print_header "📁 CREAR BASE DE BLOG ESPECÍFICO"
    echo ""
    
    get_base_path || return
    
    echo ""
    read -p "Nombre del blog (ej: axiomata): " BLOG_NAME
    
    if [ -z "$BLOG_NAME" ]; then
        print_error "Nombre de blog requerido"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Creando base de datos de '$BLOG_NAME'..."
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        python3 quarto_metadata_manager.py create-template "$BASE_PATH" \
            --blog "$BLOG_NAME" \
            --config metadata_config.yml
    else
        python3 quarto_metadata_manager.py create-template "$BASE_PATH" \
            --blog "$BLOG_NAME"
    fi
    
    echo ""
    print_success "Base de datos creada"
    read -p "Presiona Enter para continuar..."
}

# Opción 3: Simular actualización
option_dry_run() {
    print_header "🔍 SIMULAR ACTUALIZACIÓN"
    echo ""
    
    get_base_path || return
    
    echo ""
    echo "Archivos Excel disponibles:"
    ls -1 excel_databases/*.xlsx 2>/dev/null | nl || {
        print_error "No hay archivos Excel"
        read -p "Presiona Enter para continuar..."
        return
    }
    
    echo ""
    read -p "Nombre del archivo Excel: " EXCEL_FILE
    
    if [ -z "$EXCEL_FILE" ]; then
        EXCEL_FILE="excel_databases/quarto_metadata.xlsx"
    elif [[ ! "$EXCEL_FILE" =~ ^excel_databases/ ]]; then
        EXCEL_FILE="excel_databases/$EXCEL_FILE"
    fi
    
    if [ ! -f "$EXCEL_FILE" ]; then
        print_error "Archivo no encontrado: $EXCEL_FILE"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Simulando actualización..."
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --config metadata_config.yml \
            --dry-run
    else
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --dry-run
    fi
    
    echo ""
    print_success "Simulación completada"
    read -p "Presiona Enter para continuar..."
}

# Opción 4: Actualizar desde Excel
option_update() {
    print_header "✅ ACTUALIZAR DESDE EXCEL"
    echo ""
    
    print_warning "Esta acción modificará los archivos index.qmd"
    read -p "¿Continuar? (s/N): " CONFIRM
    
    if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
        print_info "Actualización cancelada"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    get_base_path || return
    
    echo ""
    echo "Archivos Excel disponibles:"
    ls -1 excel_databases/*.xlsx 2>/dev/null | nl || {
        print_error "No hay archivos Excel"
        read -p "Presiona Enter para continuar..."
        return
    }
    
    echo ""
    read -p "Nombre del archivo Excel: " EXCEL_FILE
    
    if [ -z "$EXCEL_FILE" ]; then
        EXCEL_FILE="excel_databases/quarto_metadata.xlsx"
    elif [[ ! "$EXCEL_FILE" =~ ^excel_databases/ ]]; then
        EXCEL_FILE="excel_databases/$EXCEL_FILE"
    fi
    
    if [ ! -f "$EXCEL_FILE" ]; then
        print_error "Archivo no encontrado: $EXCEL_FILE"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Actualizando desde Excel..."
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --config metadata_config.yml
    else
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE"
    fi
    
    echo ""
    print_success "Actualización completada"
    read -p "Presiona Enter para continuar..."
}

# Opción 5: Actualizar solo un blog
option_update_blog() {
    print_header "📁 ACTUALIZAR SOLO UN BLOG"
    echo ""
    
    get_base_path || return
    
    echo ""
    read -p "Nombre del blog: " BLOG_NAME
    
    if [ -z "$BLOG_NAME" ]; then
        print_error "Nombre de blog requerido"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    echo ""
    echo "Archivos Excel disponibles:"
    ls -1 excel_databases/*.xlsx 2>/dev/null | nl
    
    echo ""
    read -p "Nombre del archivo Excel: " EXCEL_FILE
    
    if [ -z "$EXCEL_FILE" ]; then
        EXCEL_FILE="excel_databases/quarto_metadata.xlsx"
    elif [[ ! "$EXCEL_FILE" =~ ^excel_databases/ ]]; then
        EXCEL_FILE="excel_databases/$EXCEL_FILE"
    fi
    
    if [ ! -f "$EXCEL_FILE" ]; then
        print_error "Archivo no encontrado"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Actualizando blog '$BLOG_NAME'..."
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --blog "$BLOG_NAME" \
            --config metadata_config.yml
    else
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --blog "$BLOG_NAME"
    fi
    
    echo ""
    print_success "Actualización completada"
    read -p "Presiona Enter para continuar..."
}

# Opción 6: Actualizar con filtro
option_update_filter() {
    print_header "🔍 ACTUALIZAR CON FILTRO DE RUTA"
    echo ""
    
    get_base_path || return
    
    echo ""
    read -p "Filtro de ruta (ej: 2025, posts, python): " PATH_FILTER
    
    if [ -z "$PATH_FILTER" ]; then
        print_error "Filtro requerido"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    echo ""
    echo "Archivos Excel disponibles:"
    ls -1 excel_databases/*.xlsx 2>/dev/null | nl
    
    echo ""
    read -p "Nombre del archivo Excel: " EXCEL_FILE
    
    if [ -z "$EXCEL_FILE" ]; then
        EXCEL_FILE="excel_databases/quarto_metadata.xlsx"
    elif [[ ! "$EXCEL_FILE" =~ ^excel_databases/ ]]; then
        EXCEL_FILE="excel_databases/$EXCEL_FILE"
    fi
    
    if [ ! -f "$EXCEL_FILE" ]; then
        print_error "Archivo no encontrado"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Actualizando con filtro '$PATH_FILTER'..."
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --filter-path "$PATH_FILTER" \
            --config metadata_config.yml
    else
        python3 quarto_metadata_manager.py update "$BASE_PATH" "$EXCEL_FILE" \
            --filter-path "$PATH_FILTER"
    fi
    
    echo ""
    print_success "Actualización completada"
    read -p "Presiona Enter para continuar..."
}

# Opción 7: Crear configuración
option_create_config() {
    print_header "⚙️  CREAR CONFIGURACIÓN"
    echo ""
    
    if [ -f "metadata_config.yml" ]; then
        print_warning "metadata_config.yml ya existe"
        read -p "¿Sobrescribir? (s/N): " OVERWRITE
        
        if [ "$OVERWRITE" != "s" ] && [ "$OVERWRITE" != "S" ]; then
            print_info "Operación cancelada"
            read -p "Presiona Enter para continuar..."
            return
        fi
    fi
    
    read -p "Ruta base de publicaciones: " BASE_PATH
    
    if [ -z "$BASE_PATH" ]; then
        print_error "Ruta requerida"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Creando configuración..."
    python3 quarto_metadata_manager.py create-config "$BASE_PATH"
    
    echo ""
    print_success "Configuración creada"
    print_info "Edita metadata_config.yml para personalizar"
    read -p "Presiona Enter para continuar..."
}

# Opción 8: Ayuda
option_help() {
    print_header "📖 AYUDA"
    echo ""
    echo -e "${CYAN}Documentación disponible:${NC}"
    echo ""
    echo "  📄 README completo:"
    echo "     cat README.md"
    echo ""
    echo "  📝 Ejemplos de configuración:"
    echo "     cat EJEMPLOS_CONFIGURACION.md"
    echo ""
    echo "  🔄 Historial de cambios:"
    echo "     cat CHANGELOG.md"
    echo ""
    echo -e "${CYAN}Comandos manuales:${NC}"
    echo ""
    echo "  Crear base general:"
    echo "     python quarto_metadata_manager.py create-template ~/Documents/publicaciones"
    echo ""
    echo "  Actualizar:"
    echo "     python quarto_metadata_manager.py update ~/Documents/publicaciones excel.xlsx"
    echo ""
    echo "  Ver todas las opciones:"
    echo "     python quarto_metadata_manager.py --help"
    echo ""
    echo -e "${CYAN}Soporte:${NC}"
    echo "  Email: achalmaedison@gmail.com"
    echo ""
    read -p "Presiona Enter para continuar..."
}

# Opción 9: Abrir Excel
option_open_excel() {
    print_header "📊 ABRIR EXCEL"
    echo ""
    
    echo "Archivos Excel disponibles:"
    ls -1 excel_databases/*.xlsx 2>/dev/null | nl || {
        print_error "No hay archivos Excel"
        read -p "Presiona Enter para continuar..."
        return
    }
    
    echo ""
    read -p "Número o nombre del archivo: " EXCEL_CHOICE
    
    if [[ "$EXCEL_CHOICE" =~ ^[0-9]+$ ]]; then
        EXCEL_FILE=$(ls -1 excel_databases/*.xlsx 2>/dev/null | sed -n "${EXCEL_CHOICE}p")
    else
        if [[ "$EXCEL_CHOICE" =~ ^excel_databases/ ]]; then
            EXCEL_FILE="$EXCEL_CHOICE"
        else
            EXCEL_FILE="excel_databases/$EXCEL_CHOICE"
        fi
    fi
    
    if [ -z "$EXCEL_FILE" ] || [ ! -f "$EXCEL_FILE" ]; then
        print_error "Archivo no encontrado"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    print_step "Abriendo $EXCEL_FILE..."
    
    if command -v libreoffice &> /dev/null; then
        libreoffice "$EXCEL_FILE" &
    elif command -v open &> /dev/null; then
        open "$EXCEL_FILE"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$EXCEL_FILE"
    else
        print_error "No se encontró programa para abrir Excel"
        print_info "Abre manualmente: $EXCEL_FILE"
    fi
    
    echo ""
    print_success "Excel abierto"
    read -p "Presiona Enter para continuar..."
}

# Main loop
main() {
    # Verificar dependencias
    check_conda
    
    if ! check_dependencies; then
        print_error "Dependencias faltantes"
        print_info "Ejecuta: ./install.sh"
        exit 1
    fi
    
    while true; do
        show_banner
        show_menu
        read -p "Selecciona una opción: " OPTION
        
        case $OPTION in
            1) option_create_all ;;
            2) option_create_blog ;;
            3) option_dry_run ;;
            4) option_update ;;
            5) option_update_blog ;;
            6) option_update_filter ;;
            7) option_create_config ;;
            8) option_help ;;
            9) option_open_excel ;;
            0)
                print_info "Saliendo..."
                exit 0
                ;;
            *)
                print_error "Opción inválida"
                sleep 1
                ;;
        esac
    done
}

# Ejecutar
main