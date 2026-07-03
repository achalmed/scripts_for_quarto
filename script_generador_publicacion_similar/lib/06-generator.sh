#!/usr/bin/env bash
# =============================================================================
# 06-generator.sh
# -----------------------------------------------------------------------------
# Lógica principal: recorre los subblogs, construye el contenido del índice
# en memoria y lo escribe de una sola vez. Escribir al final (y no truncar
# el archivo al inicio, como hacía la versión monolítica) evita dejar
# índices vacíos o a medias si el proceso se interrumpe, y hace trivial
# el modo --dry-run.
# =============================================================================

if [[ -n "${GENIDX_GENERATOR_LOADED:-}" ]]; then
    return 0
fi
GENIDX_GENERATOR_LOADED=1

# is_ignored_dir()
# Decide si una carpeta debe excluirse del procesamiento: las que empiezan
# con "." o "_" (artefactos de Quarto: _site, _freeze, .quarto...) y las
# listadas en GENIDX_IGNORE_DIRS.
# Arguments:
#   $1 - Nombre de la carpeta (sin ruta)
# Returns:
#   0 si debe ignorarse, 1 si es un subblog válido
is_ignored_dir() {
    local dir_name="$1"
    local ignored

    if [[ "$dir_name" =~ ^[._] ]]; then
        return 0
    fi
    for ignored in "${GENIDX_IGNORE_DIRS[@]}"; do
        if [[ "$dir_name" == "$ignored" ]]; then
            return 0
        fi
    done
    return 1
}

# collect_subblog_entries()
# Recorre las carpetas con fecha de un subblog y acumula las líneas del
# índice en GENIDX_COLLECTED_CONTENT / GENIDX_LAST_POSTS_FOUND. El glob
# ordena alfabéticamente, que con prefijo YYYY-MM-DD equivale a orden
# cronológico (comportamiento original preservado).
# Arguments:
#   $1 - Ruta absoluta al subblog
collect_subblog_entries() {
    local subblog_dir="$1"
    local post_dir post_folder_name entry_number=1

    GENIDX_COLLECTED_CONTENT=""
    GENIDX_LAST_POSTS_FOUND=0

    for post_dir in "$subblog_dir"/*/; do
        [[ -d "$post_dir" ]] || continue
        post_dir="${post_dir%/}"
        post_folder_name="$(basename "$post_dir")"

        [[ "$post_folder_name" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}- ]] || continue

        if [[ ! -f "$post_dir/index.qmd" ]]; then
            log_warn "Carpeta sin index.qmd: $(basename "$subblog_dir")/$post_folder_name"
            continue
        fi

        GENIDX_COLLECTED_CONTENT+="${entry_number}. $(convert_folder_to_link "$post_dir")"$'\n'
        entry_number=$((entry_number + 1))
        GENIDX_LAST_POSTS_FOUND=$((GENIDX_LAST_POSTS_FOUND + 1))
    done
}

# write_subblog_index()
# Escribe (o simula escribir) el índice de un subblog. Si el subblog quedó
# sin publicaciones, elimina el índice obsoleto de una ejecución anterior
# (comportamiento original preservado).
# Arguments:
#   $1 - Ruta absoluta al subblog
# Returns:
#   0 en éxito o simulación, 1 si la escritura falló
write_subblog_index() {
    local subblog_dir="$1"
    local subblog_name output_file
    subblog_name="$(basename "$subblog_dir")"
    output_file="$subblog_dir/${GENIDX_OUTPUT_PREFIX}${subblog_name}.qmd"

    if [[ "$GENIDX_LAST_POSTS_FOUND" -eq 0 ]]; then
        log_info "No se encontraron publicaciones en: $subblog_name"
        if [[ -f "$output_file" ]]; then
            if [[ "$GENIDX_DRY_RUN" -eq 1 ]]; then
                log_info "[dry-run] Se eliminaría el índice obsoleto: $output_file"
            else
                rm -f "$output_file"
                log_info "Índice obsoleto eliminado: $output_file"
            fi
        fi
        return 0
    fi

    if [[ "$GENIDX_DRY_RUN" -eq 1 ]]; then
        log_success "[dry-run] Se generaría: $output_file ($GENIDX_LAST_POSTS_FOUND publicaciones)"
        return 0
    fi

    if ! printf '%s' "$GENIDX_COLLECTED_CONTENT" > "$output_file"; then
        log_error "No se pudo escribir: $output_file"
        return 1
    fi
    log_success "Generado: $output_file ($GENIDX_LAST_POSTS_FOUND publicaciones)"
}

# generate_all_indices()
# Orquesta el procesamiento de todos los subblogs y acumula los totales
# en GENIDX_TOTAL_FILES / GENIDX_TOTAL_POSTS para el resumen final.
generate_all_indices() {
    local subblog_dir subblog_name

    GENIDX_TOTAL_FILES=0
    GENIDX_TOTAL_POSTS=0

    for subblog_dir in "$GENIDX_BLOG_DIR"/*/; do
        [[ -d "$subblog_dir" ]] || continue
        subblog_dir="${subblog_dir%/}"
        subblog_name="$(basename "$subblog_dir")"

        if is_ignored_dir "$subblog_name"; then
            continue
        fi

        log_info "Procesando subblog: $subblog_name"
        collect_subblog_entries "$subblog_dir"
        write_subblog_index "$subblog_dir" || continue

        if [[ "$GENIDX_LAST_POSTS_FOUND" -gt 0 ]]; then
            GENIDX_TOTAL_FILES=$((GENIDX_TOTAL_FILES + 1))
            GENIDX_TOTAL_POSTS=$((GENIDX_TOTAL_POSTS + GENIDX_LAST_POSTS_FOUND))
        fi
    done
}

# print_summary()
# Muestra el resumen final con los totales de la ejecución.
print_summary() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    if [[ "$GENIDX_TOTAL_FILES" -gt 0 ]]; then
        log_success "Proceso completado exitosamente"
        log_info "Total de archivos de índice generados: $GENIDX_TOTAL_FILES"
        log_info "Total de publicaciones procesadas: $GENIDX_TOTAL_POSTS"
        log_info "Estructura utilizada: $GENIDX_BLOG_TYPE"
        if [[ "$GENIDX_DRY_RUN" -eq 1 ]]; then
            log_info "Modo dry-run: NO se modificó ningún archivo"
        fi
    else
        log_warn "No se generaron archivos de índice"
        log_info "Verifica la estructura de carpetas y las rutas configuradas"
    fi
    echo "════════════════════════════════════════════════════════════════"
}
