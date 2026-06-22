#!/usr/bin/env bash
################################################################################
# quick_start.sh — Inicio rápido del Sistema de Metadatos Quarto v2.0
# Autor: Edison Achalma  |  Ayacucho, Perú
################################################################################

set -euo pipefail

# Colores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; PURPLE='\033[0;35m'; CYAN='\033[0;36m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PY="$SCRIPT_DIR/main.py"
CONFIG_FILE="$SCRIPT_DIR/metadata_config.yml"

print_header()  { echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error()   { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info()    { echo -e "${PURPLE}ℹ️  $1${NC}"; }
print_step()    { echo -e "${CYAN}▶ $1${NC}"; }

# ---------------------------------------------------------------------------
# Verificar entorno conda y dependencias
# ---------------------------------------------------------------------------

check_conda() {
    command -v conda &>/dev/null || return 1
    if [ "${CONDA_DEFAULT_ENV:-}" != "metadata_manager" ]; then
        print_info "Activando entorno conda metadata_manager..."
        eval "$(conda shell.bash hook)"
        conda activate metadata_manager || true
    fi
    return 0
}

check_dependencies() {
    command -v python3 &>/dev/null || { print_error "Python 3 no encontrado"; return 1; }
    python3 -c "import pandas, openpyxl, yaml" 2>/dev/null || {
        print_error "Dependencias faltantes (pandas, openpyxl, pyyaml)"
        print_info  "Ejecuta: bash install.sh"
        return 1
    }
    return 0
}

# ---------------------------------------------------------------------------
# Ruta base de los blogs
# ---------------------------------------------------------------------------

get_base_path() {
    # Intentar leer desde el config
    if [ -f "$CONFIG_FILE" ]; then
        BASE_PATH=$(python3 -c "
import yaml, os
with open('$CONFIG_FILE') as f:
    c = yaml.safe_load(f)
out = c.get('excel_output_dir','').replace('excel_databases','').replace('~',os.environ['HOME']).rstrip('/')
print(out or os.environ['HOME'] + '/Documents')
" 2>/dev/null || echo "$HOME/Documents")
    else
        BASE_PATH="$HOME/Documents"
    fi

    print_info "Ruta detectada: $BASE_PATH"
    read -rp "¿Usar esta ruta? (S/n): " USE_DEFAULT
    if [[ "${USE_DEFAULT:-}" =~ ^[Nn]$ ]]; then
        read -rp "Ingresa la ruta: " CUSTOM
        [ -n "$CUSTOM" ] && BASE_PATH="${CUSTOM/#\~/$HOME}"
    fi

    if [ ! -d "$BASE_PATH" ]; then
        print_warning "La ruta no existe: $BASE_PATH"
        read -rp "¿Crear directorio? (s/N): " CREATE
        if [[ "${CREATE:-}" =~ ^[Ss]$ ]]; then
            mkdir -p "$BASE_PATH"
            print_success "Directorio creado"
        else
            return 1
        fi
    fi
    return 0
}

# ---------------------------------------------------------------------------
# Selección del Excel
# ---------------------------------------------------------------------------

get_excel_file() {
    local out_dir="$SCRIPT_DIR/excel_databases"
    echo ""
    echo "Archivos Excel disponibles:"
    if ls "$out_dir"/*.xlsx 2>/dev/null | nl; then
        :
    else
        print_error "No hay archivos Excel en $out_dir"
        read -rp "Presiona Enter para continuar..."
        return 1
    fi
    echo ""
    read -rp "Nombre del archivo Excel (Enter = quarto_metadata.xlsx): " EXCEL_FILE
    EXCEL_FILE="${EXCEL_FILE:-quarto_metadata.xlsx}"
    [[ "$EXCEL_FILE" != "$out_dir/"* ]] && EXCEL_FILE="$out_dir/$EXCEL_FILE"
    [ -f "$EXCEL_FILE" ] || { print_error "Archivo no encontrado: $EXCEL_FILE"; read -rp "Presiona Enter..."; return 1; }
    return 0
}

config_arg() {
    [ -f "$CONFIG_FILE" ] && echo "--config $CONFIG_FILE" || echo ""
}

# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

option_create_all() {
    print_header "📊 CREAR BASE GENERAL (todos los blogs)"
    get_base_path || return
    print_step "Ejecutando create-template..."
    python3 "$MAIN_PY" create-template "$BASE_PATH" $(config_arg)
    print_success "Base de datos creada"
    read -rp "Presiona Enter para continuar..."
}

option_create_blog() {
    print_header "📁 CREAR BASE DE BLOG ESPECÍFICO"
    get_base_path || return
    echo ""
    read -rp "Nombre del blog (ej: pub_axiomata o website-achalma): " BLOG_NAME
    [ -z "$BLOG_NAME" ] && { print_error "Nombre requerido"; read -rp "Presiona Enter..."; return; }
    python3 "$MAIN_PY" create-template "$BASE_PATH" --blog "$BLOG_NAME" $(config_arg)
    print_success "Base de datos creada"
    read -rp "Presiona Enter para continuar..."
}

option_incremental() {
    print_header "🔄 AGREGAR SOLO ARTÍCULOS NUEVOS (modo incremental)"
    get_base_path || return
    python3 "$MAIN_PY" create-template "$BASE_PATH" --incremental $(config_arg)
    print_success "Modo incremental completado"
    read -rp "Presiona Enter para continuar..."
}

option_dry_run() {
    print_header "🔍 SIMULAR ACTUALIZACIÓN (dry-run)"
    get_base_path || return
    get_excel_file || return
    python3 "$MAIN_PY" update "$BASE_PATH" "$EXCEL_FILE" --dry-run $(config_arg)
    print_success "Simulación completada"
    read -rp "Presiona Enter para continuar..."
}

option_update() {
    print_header "✅ ACTUALIZAR DESDE EXCEL"
    print_warning "Esta acción modificará los archivos index.qmd"
    read -rp "¿Continuar? (s/N): " CONFIRM
    [[ "${CONFIRM:-}" =~ ^[Ss]$ ]] || { print_info "Cancelado"; read -rp "Presiona Enter..."; return; }
    get_base_path || return
    get_excel_file || return
    python3 "$MAIN_PY" update "$BASE_PATH" "$EXCEL_FILE" $(config_arg)
    print_success "Actualización completada"
    read -rp "Presiona Enter para continuar..."
}

option_update_blog() {
    print_header "📁 ACTUALIZAR SOLO UN BLOG"
    get_base_path || return
    read -rp "Nombre del blog: " BLOG_NAME
    [ -z "$BLOG_NAME" ] && { print_error "Nombre requerido"; read -rp "Presiona Enter..."; return; }
    get_excel_file || return
    python3 "$MAIN_PY" update "$BASE_PATH" "$EXCEL_FILE" --blog "$BLOG_NAME" $(config_arg)
    print_success "Actualización completada"
    read -rp "Presiona Enter para continuar..."
}

option_update_filter() {
    print_header "🔍 ACTUALIZAR CON FILTRO DE RUTA"
    get_base_path || return
    read -rp "Filtro de ruta (ej: 2025, posts, python): " PATH_FILTER
    [ -z "$PATH_FILTER" ] && { print_error "Filtro requerido"; read -rp "Presiona Enter..."; return; }
    get_excel_file || return
    python3 "$MAIN_PY" update "$BASE_PATH" "$EXCEL_FILE" --filter-path "$PATH_FILTER" $(config_arg)
    print_success "Actualización completada"
    read -rp "Presiona Enter para continuar..."
}

option_find_diff() {
    print_header "🔍 ENCONTRAR DIFERENCIAS"
    get_base_path || return
    get_excel_file || return
    read -rp "Filtrar por blog (Enter para todos): " BLOG_F
    BLOG_ARG="${BLOG_F:+--blog $BLOG_F}"
    python3 "$MAIN_PY" find-differences "$BASE_PATH" "$EXCEL_FILE" $BLOG_ARG $(config_arg)
    read -rp "Presiona Enter para continuar..."
}

option_sync_batch() {
    print_header "🔄 SINCRONIZACIÓN MASIVA INTERACTIVA"
    get_base_path || return
    get_excel_file || return
    python3 "$MAIN_PY" sync-batch "$BASE_PATH" "$EXCEL_FILE" $(config_arg)
    print_success "Sincronización completada"
    read -rp "Presiona Enter para continuar..."
}

option_detect_fields() {
    print_header "🔎 DETECTAR CAMPOS NUEVOS"
    get_base_path || return
    python3 "$MAIN_PY" detect-new-fields "$BASE_PATH" $(config_arg)
    read -rp "Presiona Enter para continuar..."
}

option_create_config() {
    print_header "⚙️  CREAR CONFIGURACIÓN"
    [ -f "$CONFIG_FILE" ] && {
        print_warning "metadata_config.yml ya existe"
        read -rp "¿Sobrescribir? (s/N): " OW
        [[ "${OW:-}" =~ ^[Ss]$ ]] || { print_info "Cancelado"; read -rp "Presiona Enter..."; return; }
    }
    read -rp "Ruta base de los blogs: " BP
    [ -z "$BP" ] && { print_error "Ruta requerida"; read -rp "Presiona Enter..."; return; }
    python3 "$MAIN_PY" create-config "${BP/#\~/$HOME}" -o "$CONFIG_FILE"
    print_success "Configuración creada: $CONFIG_FILE"
    print_info "Edita allowed_blogs y excluded_folders según tu entorno"
    read -rp "Presiona Enter para continuar..."
}

option_help() {
    print_header "📖 AYUDA"
    echo ""
    echo -e "${CYAN}Ver ayuda completa:${NC}"
    echo "   python3 main.py --help"
    echo ""
    echo -e "${CYAN}Documentación:${NC}"
    echo "   cat README.md"
    echo ""
    echo -e "${CYAN}Ejemplos de campos Excel:${NC}"
    echo "   cat Guia_de_Configuracion_para_Excel.md"
    echo ""
    echo -e "${CYAN}Comandos disponibles:${NC}"
    echo "   create-config      Crear metadata_config.yml"
    echo "   create-template    Generar plantilla Excel"
    echo "   update             Aplicar Excel → archivos .qmd"
    echo "   detect-new-fields  Detectar campos YAML nuevos"
    echo "   add-columns        Agregar columnas al Excel"
    echo "   find-differences   Ver diferencias"
    echo "   sync-article       Sincronizar un artículo"
    echo "   sync-batch         Sincronización masiva"
    echo ""
    read -rp "Presiona Enter para continuar..."
}

option_open_excel() {
    print_header "📊 ABRIR EXCEL"
    local out_dir="$SCRIPT_DIR/excel_databases"
    echo "Archivos disponibles:"
    ls -1 "$out_dir"/*.xlsx 2>/dev/null | nl || {
        print_error "No hay archivos Excel en $out_dir"
        read -rp "Presiona Enter..."; return
    }
    echo ""
    read -rp "Número o nombre: " CHOICE
    if [[ "$CHOICE" =~ ^[0-9]+$ ]]; then
        EXCEL_FILE=$(ls -1 "$out_dir"/*.xlsx 2>/dev/null | sed -n "${CHOICE}p")
    else
        EXCEL_FILE="$out_dir/$CHOICE"
    fi
    [ -f "$EXCEL_FILE" ] || { print_error "Archivo no encontrado"; read -rp "Presiona Enter..."; return; }
    if command -v libreoffice &>/dev/null; then
        libreoffice "$EXCEL_FILE" &
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$EXCEL_FILE"
    elif command -v open &>/dev/null; then
        open "$EXCEL_FILE"
    else
        print_info "Abre manualmente: $EXCEL_FILE"
    fi
    print_success "Excel abierto"
    read -rp "Presiona Enter para continuar..."
}

# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------

show_menu() {
    print_header "📋 MENÚ PRINCIPAL — Gestión de Metadatos Quarto v2.0"
    echo ""
    echo -e "${GREEN}CREAR BASES DE DATOS${NC}"
    echo -e "  ${CYAN}1)${NC} Crear base general (todos los blogs)"
    echo -e "  ${CYAN}2)${NC} Crear base de un blog específico"
    echo -e "  ${CYAN}3)${NC} Modo incremental (solo artículos nuevos)"
    echo ""
    echo -e "${YELLOW}ACTUALIZAR METADATOS${NC}"
    echo -e "  ${CYAN}4)${NC} Simular actualización (--dry-run)"
    echo -e "  ${CYAN}5)${NC} Actualizar desde Excel (todos)"
    echo -e "  ${CYAN}6)${NC} Actualizar solo un blog"
    echo -e "  ${CYAN}7)${NC} Actualizar con filtro de ruta"
    echo ""
    echo -e "${PURPLE}SINCRONIZACIÓN${NC}"
    echo -e "  ${CYAN}8)${NC} Encontrar diferencias"
    echo -e "  ${CYAN}9)${NC} Sincronización masiva interactiva"
    echo -e "  ${CYAN}10)${NC} Detectar campos YAML nuevos"
    echo ""
    echo -e "${BLUE}UTILIDADES${NC}"
    echo -e "  ${CYAN}11)${NC} Crear configuración (metadata_config.yml)"
    echo -e "  ${CYAN}12)${NC} Abrir Excel generado"
    echo -e "  ${CYAN}13)${NC} Ver ayuda"
    echo ""
    echo -e "  ${RED}0)${NC} Salir"
    echo ""
}

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

main() {
    check_conda || true
    check_dependencies || exit 1

    while true; do
        clear
        show_menu
        read -rp "Selecciona una opción: " OPT

        case "${OPT:-}" in
            1)  option_create_all ;;
            2)  option_create_blog ;;
            3)  option_incremental ;;
            4)  option_dry_run ;;
            5)  option_update ;;
            6)  option_update_blog ;;
            7)  option_update_filter ;;
            8)  option_find_diff ;;
            9)  option_sync_batch ;;
            10) option_detect_fields ;;
            11) option_create_config ;;
            12) option_open_excel ;;
            13) option_help ;;
            0)  print_info "Saliendo..."; exit 0 ;;
            *)  print_error "Opción inválida"; sleep 1 ;;
        esac
    done
}

main
