#!/bin/bash

# QMD Tag Manager - Script de ayuda
# Proporciona atajos para operaciones comunes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QMD_MANAGER="$SCRIPT_DIR/qmd_tag_manager.py"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que existe el script principal
if [ ! -f "$QMD_MANAGER" ]; then
    print_error "No se encuentra qmd_tag_manager.py en $SCRIPT_DIR"
    exit 1
fi

# Función de ayuda
show_help() {
    print_header "QMD Tag Manager - Comandos Rápidos"
    echo ""
    echo "Uso: $0 [comando] [opciones]"
    echo ""
    echo "Comandos disponibles:"
    echo ""
    echo "  normalize [directorio]"
    echo "    Normaliza todos los tags en el directorio especificado"
    echo "    Ejemplo: $0 normalize ./posts"
    echo ""
    echo "  normalize-dry [directorio]"
    echo "    Simula la normalización sin modificar archivos"
    echo "    Ejemplo: $0 normalize-dry ./posts"
    echo ""
    echo "  replace [directorio] 'viejo:nuevo' ['viejo2:nuevo2' ...]"
    echo "    Reemplaza tags específicos"
    echo "    Ejemplo: $0 replace ./posts 'Gestión:gestion' 'Economía:economia'"
    echo ""
    echo "  clean [directorio] tag1 [tag2 ...]"
    echo "    Elimina tags específicos"
    echo "    Ejemplo: $0 clean ./posts draft borrador temp"
    echo ""
    echo "  add [directorio] tag1 [tag2 ...]"
    echo "    Agrega nuevos tags a todos los archivos"
    echo "    Ejemplo: $0 add ./posts blog 2025"
    echo ""
    echo "  full [directorio]"
    echo "    Operación completa: normaliza, limpia duplicados"
    echo "    Ejemplo: $0 full ./posts"
    echo ""
    echo "  stats [directorio]"
    echo "    Muestra estadísticas de los tags en el directorio"
    echo "    Ejemplo: $0 stats ./posts"
    echo ""
    echo "  backup [directorio]"
    echo "    Crea un backup de los archivos .qmd antes de procesarlos"
    echo "    Ejemplo: $0 backup ./posts"
    echo ""
    echo "Opciones globales:"
    echo "  -h, --help     Muestra esta ayuda"
    echo "  -v, --version  Muestra la versión"
    echo ""
}

# Función para normalizar
normalize() {
    local dir="${1:-.}"
    local dry_run="${2:-false}"
    
    print_header "Normalizando tags en: $dir"
    
    if [ "$dry_run" = "true" ]; then
        print_warning "Modo DRY RUN - No se modificarán archivos"
        python3 "$QMD_MANAGER" --directory "$dir" --normalize --recursive --dry-run
    else
        python3 "$QMD_MANAGER" --directory "$dir" --normalize --recursive
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Operación completada"
    else
        print_error "Error durante la operación"
        exit 1
    fi
}

# Función para reemplazar tags
replace_tags() {
    local dir="$1"
    shift
    local replacements=("$@")
    
    if [ ${#replacements[@]} -eq 0 ]; then
        print_error "Debe especificar al menos un reemplazo"
        echo "Formato: 'viejo:nuevo'"
        exit 1
    fi
    
    print_header "Reemplazando tags en: $dir"
    echo "Reemplazos a realizar:"
    for replacement in "${replacements[@]}"; do
        echo "  • $replacement"
    done
    echo ""
    
    python3 "$QMD_MANAGER" --directory "$dir" --replace "${replacements[@]}" --recursive
    
    if [ $? -eq 0 ]; then
        print_success "Reemplazos completados"
    else
        print_error "Error durante los reemplazos"
        exit 1
    fi
}

# Función para limpiar tags
clean_tags() {
    local dir="$1"
    shift
    local tags_to_remove=("$@")
    
    if [ ${#tags_to_remove[@]} -eq 0 ]; then
        print_error "Debe especificar al menos un tag para eliminar"
        exit 1
    fi
    
    print_header "Eliminando tags en: $dir"
    echo "Tags a eliminar:"
    for tag in "${tags_to_remove[@]}"; do
        echo "  • $tag"
    done
    echo ""
    
    python3 "$QMD_MANAGER" --directory "$dir" --remove "${tags_to_remove[@]}" --recursive
    
    if [ $? -eq 0 ]; then
        print_success "Tags eliminados"
    else
        print_error "Error durante la eliminación"
        exit 1
    fi
}

# Función para agregar tags
add_tags() {
    local dir="$1"
    shift
    local tags_to_add=("$@")
    
    if [ ${#tags_to_add[@]} -eq 0 ]; then
        print_error "Debe especificar al menos un tag para agregar"
        exit 1
    fi
    
    print_header "Agregando tags en: $dir"
    echo "Tags a agregar:"
    for tag in "${tags_to_add[@]}"; do
        echo "  • $tag"
    done
    echo ""
    
    python3 "$QMD_MANAGER" --directory "$dir" --add "${tags_to_add[@]}" --recursive
    
    if [ $? -eq 0 ]; then
        print_success "Tags agregados"
    else
        print_error "Error durante la adición"
        exit 1
    fi
}

# Función para operación completa
full_operation() {
    local dir="${1:-.}"
    
    print_header "Operación completa en: $dir"
    print_warning "Esta operación normalizará todos los tags"
    echo ""
    read -p "¿Continuar? (s/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_warning "Operación cancelada"
        exit 0
    fi
    
    # Primero hacer dry-run
    print_header "Paso 1: Verificación (dry-run)"
    python3 "$QMD_MANAGER" --directory "$dir" --normalize --recursive --dry-run
    echo ""
    
    read -p "¿Aplicar cambios? (s/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_warning "Operación cancelada"
        exit 0
    fi
    
    # Aplicar cambios
    print_header "Paso 2: Aplicando cambios"
    python3 "$QMD_MANAGER" --directory "$dir" --normalize --recursive
    
    if [ $? -eq 0 ]; then
        print_success "Operación completa exitosa"
    else
        print_error "Error durante la operación"
        exit 1
    fi
}

# Función para estadísticas
show_stats() {
    local dir="${1:-.}"
    
    print_header "Estadísticas de tags en: $dir"
    
    # Contar archivos .qmd
    local total_files=$(find "$dir" -name "*.qmd" -type f | wc -l)
    print_success "Total de archivos .qmd: $total_files"
    echo ""
    
    # Extraer y contar tags únicos
    echo "Extrayendo tags..."
    
    # Usar un array asociativo para contar tags
    declare -A tag_count
    
    while IFS= read -r file; do
        # Extraer tags del archivo (simplificado)
        while IFS= read -r line; do
            if [[ $line =~ ^[[:space:]]*-[[:space:]](.+)$ ]]; then
                tag="${BASH_REMATCH[1]}"
                ((tag_count["$tag"]++))
            fi
        done < <(sed -n '/^tags:/,/^[a-zA-Z]/p' "$file" | grep -E "^[[:space:]]*-")
    done < <(find "$dir" -name "*.qmd" -type f)
    
    echo ""
    echo "Top 20 tags más usados:"
    echo "------------------------"
    
    # Ordenar y mostrar
    for tag in "${!tag_count[@]}"; do
        echo "${tag_count[$tag]} $tag"
    done | sort -rn | head -20 | while read count tag; do
        echo "  $count veces: $tag"
    done
    
    echo ""
    print_success "Total de tags únicos: ${#tag_count[@]}"
}

# Función para backup
create_backup() {
    local dir="${1:-.}"
    local backup_dir="${dir}_backup_$(date +%Y%m%d_%H%M%S)"
    
    print_header "Creando backup de: $dir"
    
    # Crear directorio de backup
    mkdir -p "$backup_dir"
    
    # Copiar archivos .qmd
    find "$dir" -name "*.qmd" -type f -exec cp --parents {} "$backup_dir" \;
    
    if [ $? -eq 0 ]; then
        print_success "Backup creado en: $backup_dir"
        
        # Contar archivos
        local file_count=$(find "$backup_dir" -name "*.qmd" -type f | wc -l)
        echo "  Total de archivos respaldados: $file_count"
    else
        print_error "Error al crear backup"
        exit 1
    fi
}

# Procesamiento de comandos
case "$1" in
    normalize)
        normalize "${2:-.}" false
        ;;
    normalize-dry)
        normalize "${2:-.}" true
        ;;
    replace)
        shift
        replace_tags "$@"
        ;;
    clean)
        shift
        clean_tags "$@"
        ;;
    add)
        shift
        add_tags "$@"
        ;;
    full)
        full_operation "${2:-.}"
        ;;
    stats)
        show_stats "${2:-.}"
        ;;
    backup)
        create_backup "${2:-.}"
        ;;
    -h|--help|help)
        show_help
        ;;
    -v|--version)
        echo "QMD Tag Manager Helper v1.0.0"
        ;;
    "")
        print_error "Debe especificar un comando"
        echo ""
        show_help
        exit 1
        ;;
    *)
        print_error "Comando desconocido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

exit 0
