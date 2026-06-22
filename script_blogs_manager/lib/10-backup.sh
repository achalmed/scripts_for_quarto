#!/usr/bin/env bash
# =============================================================================
# 10-backup.sh
# -----------------------------------------------------------------------------
# Sistema de backups de los blogs gestionables: individual (un .tar.gz por
# blog), completo (un solo archivo con todos), o incremental con rsync.
# Equivalente al antiguo backup-blogs.sh.
# =============================================================================

if [[ -n "${QBLOG_BACKUP_LOADED:-}" ]]; then
    return 0
fi
QBLOG_BACKUP_LOADED=1

# Lista los backups existentes y muestra el espacio total usado, ofreciendo
# limpiar los antiguos si hay más de 10.
# $1 = ruta absoluta del directorio de backups
_backup_list_and_maybe_clean() {
    local backup_dir="$1"

    echo ""
    print_header "Backups Existentes"
    echo ""

    ls -lh "$backup_dir" 2>/dev/null | grep -E ".tar.gz$|^d" | awk '{
        if ($9 != "") {
            printf "  %s  %s  %s\n", $5, $6" "$7, $9
        }
    }'

    echo ""

    local total_size
    total_size=$(du -sh "$backup_dir" 2>/dev/null | cut -f1)
    print_info "Espacio total usado: $total_size"

    local backup_count
    backup_count=$(find "$backup_dir" -maxdepth 1 -name "*.tar.gz" 2>/dev/null | wc -l)
    if [[ $backup_count -gt 10 ]]; then
        echo ""
        print_info "Tienes $backup_count backups"
        read -r -p "¿Deseas limpiar backups antiguos (mantener últimos 5)? (s/n): " clean
        if [[ "$clean" =~ ^[Ss]$ ]]; then
            cd "$backup_dir" || return 1
            ls -t ./*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f
            print_success "Backups antiguos eliminados"
        fi
    fi
}

# Ejecuta el sistema de backups interactivo: pregunta el tipo y lo ejecuta.
# $1 = ruta absoluta de Documents
# $2 = ruta absoluta del directorio donde guardar los backups
backup_blogs_interactive() {
    local docs_dir="$1"
    local backup_dir="$2"
    local date_str
    date_str=$(date +%Y%m%d_%H%M%S)

    mkdir -p "$backup_dir"

    print_header "Backup de Publicaciones"
    echo ""
    print_info "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
    print_info "Origen: $docs_dir"
    print_info "Destino: $backup_dir"
    echo ""

    echo "Opciones de backup:"
    echo "  1) Backup individual (un archivo por blog)"
    echo "  2) Backup completo (un solo archivo con todo)"
    echo "  3) Backup incremental (solo cambios desde último backup)"
    echo ""
    read -r -p "Selecciona opción (1-3): " option

    case $option in
        1)
            print_info "Creando backups individuales..."
            local blog blog_name backup_file size
            while IFS= read -r blog; do
                [[ -z "$blog" ]] && continue
                blog_name="$(basename "$blog")"
                backup_file="$backup_dir/${blog_name}_${date_str}.tar.gz"

                print_info "Respaldando: $blog_name"

                tar -czf "$backup_file" \
                    --exclude='_site' \
                    --exclude='_freeze' \
                    --exclude='.quarto' \
                    --exclude='.git' \
                    --exclude='*.log' \
                    -C "$docs_dir" \
                    "$blog_name"

                size=$(du -h "$backup_file" | cut -f1)
                print_success "Creado: $backup_file ($size)"
            done < <(utils_list_projects "$docs_dir")
            ;;

        2)
            local backup_file="$backup_dir/all-blogs_${date_str}.tar.gz"
            print_info "Creando backup completo..."

            local includes=()
            local blog
            while IFS= read -r blog; do
                [[ -z "$blog" ]] && continue
                includes+=("$(basename "$blog")")
            done < <(utils_list_projects "$docs_dir")

            tar -czf "$backup_file" \
                --exclude='_site' \
                --exclude='_freeze' \
                --exclude='.quarto' \
                --exclude='.git' \
                --exclude='*.log' \
                -C "$docs_dir" \
                "${includes[@]}"

            local size
            size=$(du -h "$backup_file" | cut -f1)
            print_success "Backup completo creado: $backup_file ($size)"
            ;;

        3)
            print_info "Creando backup incremental..."
            local incremental_dir="$backup_dir/incremental"
            mkdir -p "$incremental_dir"

            local includes=()
            local blog
            while IFS= read -r blog; do
                [[ -z "$blog" ]] && continue
                includes+=("$blog")
            done < <(utils_list_projects "$docs_dir")

            # rsync cada proyecto individualmente al directorio incremental
            local proj proj_name
            for proj in "${includes[@]}"; do
                proj_name="$(basename "$proj")"
                rsync -av --delete \
                    --exclude='_site/' \
                    --exclude='_freeze/' \
                    --exclude='.quarto/' \
                    --exclude='.git/' \
                    --exclude='*.log' \
                    "$proj/" \
                    "$incremental_dir/$proj_name/"
            done

            print_success "Backup incremental actualizado en: $incremental_dir"

            local snapshot_file="$backup_dir/snapshot_${date_str}.tar.gz"
            tar -czf "$snapshot_file" -C "$backup_dir" "incremental"

            local size
            size=$(du -h "$snapshot_file" | cut -f1)
            print_success "Snapshot creado: $snapshot_file ($size)"
            ;;

        *)
            print_error "Opción inválida"
            return 1
            ;;
    esac

    _backup_list_and_maybe_clean "$backup_dir"

    echo ""
    print_success "Backup completado exitosamente"
}
