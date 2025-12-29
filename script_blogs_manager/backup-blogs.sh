#!/bin/bash

################################################################################
# backup-blogs.sh - Crear backup de todos los blogs
# Crea backups comprimidos excluyendo archivos generados
################################################################################

set -e

PUBLICACIONES_DIR="/home/achalmaedison/Documents/publicaciones"
BACKUP_DIR="/home/achalmaedison/Documents/backups/publicaciones"
DATE=$(date +%Y%m%d_%H%M%S)

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

print_header "Backup de Publicaciones"
echo ""
print_info "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
print_info "Origen: $PUBLICACIONES_DIR"
print_info "Destino: $BACKUP_DIR"
echo ""

# Determinar tipo de backup
echo "Opciones de backup:"
echo "  1) Backup individual (un archivo por blog)"
echo "  2) Backup completo (un solo archivo con todo)"
echo "  3) Backup incremental (solo cambios desde último backup)"
echo ""
read -p "Selecciona opción (1-3): " option

case $option in
    1)
        # Backup individual
        print_info "Creando backups individuales..."
        
        for blog in "$PUBLICACIONES_DIR"/*/; do
            if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
                blog_name=$(basename "$blog")
                backup_file="$BACKUP_DIR/${blog_name}_${DATE}.tar.gz"
                
                print_info "Respaldando: $blog_name"
                
                tar -czf "$backup_file" \
                    --exclude='_site' \
                    --exclude='_freeze' \
                    --exclude='.quarto' \
                    --exclude='.git' \
                    --exclude='*.log' \
                    -C "$PUBLICACIONES_DIR" \
                    "$blog_name"
                
                size=$(du -h "$backup_file" | cut -f1)
                print_success "Creado: $backup_file ($size)"
            fi
        done
        ;;
        
    2)
        # Backup completo
        backup_file="$BACKUP_DIR/all-blogs_${DATE}.tar.gz"
        
        print_info "Creando backup completo..."
        
        tar -czf "$backup_file" \
            --exclude='_site' \
            --exclude='_freeze' \
            --exclude='.quarto' \
            --exclude='.git' \
            --exclude='*.log' \
            -C "$(dirname "$PUBLICACIONES_DIR")" \
            "$(basename "$PUBLICACIONES_DIR")"
        
        size=$(du -h "$backup_file" | cut -f1)
        print_success "Backup completo creado: $backup_file ($size)"
        ;;
        
    3)
        # Backup incremental (usando rsync)
        print_info "Creando backup incremental..."
        
        incremental_dir="$BACKUP_DIR/incremental"
        mkdir -p "$incremental_dir"
        
        rsync -av --delete \
            --exclude='_site/' \
            --exclude='_freeze/' \
            --exclude='.quarto/' \
            --exclude='.git/' \
            --exclude='*.log' \
            "$PUBLICACIONES_DIR/" \
            "$incremental_dir/"
        
        print_success "Backup incremental actualizado en: $incremental_dir"
        
        # Crear snapshot comprimido
        snapshot_file="$BACKUP_DIR/snapshot_${DATE}.tar.gz"
        tar -czf "$snapshot_file" -C "$BACKUP_DIR" "incremental"
        
        size=$(du -h "$snapshot_file" | cut -f1)
        print_success "Snapshot creado: $snapshot_file ($size)"
        ;;
        
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac

echo ""
print_header "Backups Existentes"
echo ""

# Listar backups existentes
ls -lh "$BACKUP_DIR" | grep -E ".tar.gz$|^d" | awk '{
    if ($9 != "") {
        printf "  %s  %s  %s\n", $5, $6" "$7, $9
    }
}'

echo ""

# Calcular espacio total usado por backups
total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
print_info "Espacio total usado: $total_size"

# Sugerir limpieza si hay muchos backups
backup_count=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
if [ $backup_count -gt 10 ]; then
    echo ""
    print_info "Tienes $backup_count backups"
    read -p "¿Deseas limpiar backups antiguos (mantener últimos 5)? (s/n): " clean
    
    if [ "$clean" = "s" ] || [ "$clean" = "S" ]; then
        cd "$BACKUP_DIR"
        ls -t *.tar.gz | tail -n +6 | xargs rm -f
        print_success "Backups antiguos eliminados"
    fi
fi

echo ""
print_success "Backup completado exitosamente"
