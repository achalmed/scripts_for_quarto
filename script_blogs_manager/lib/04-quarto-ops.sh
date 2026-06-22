#!/usr/bin/env bash
# =============================================================================
# 04-quarto-ops.sh
# -----------------------------------------------------------------------------
# Operaciones individuales de Quarto sobre un blog/proyecto: renderizar,
# preview, limpiar, publicar, verificar, inspeccionar y convertir
# documentos. Misma lógica que el script original.
# =============================================================================

if [[ -n "${QBLOG_QUARTO_OPS_LOADED:-}" ]]; then
    return 0
fi
QBLOG_QUARTO_OPS_LOADED=1

# Renderiza un blog completo.
# $1 = ruta absoluta del blog
render_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "$QBLOG_E_GEAR Renderizando: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    if quarto render; then
        print_success "Blog renderizado exitosamente"
    else
        print_error "Error al renderizar el blog"
        return 1
    fi
}

# Preview del blog sin abrir navegador (servidor en segundo plano hasta Ctrl+C).
# $1 = ruta absoluta del blog
# $2 = puerto (opcional, default QBLOG_DEFAULT_PREVIEW_PORT)
preview_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"
    local port="${2:-$QBLOG_DEFAULT_PREVIEW_PORT}"

    print_header "Preview: $blog_name (Puerto: $port)"
    print_info "Presiona Ctrl+C para detener el servidor"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }
    quarto preview --port "$port" --no-browser
}

# Preview del blog abriendo el navegador automáticamente.
# $1 = ruta absoluta del blog
# $2 = puerto (opcional)
preview_blog_browser() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"
    local port="${2:-$QBLOG_DEFAULT_PREVIEW_PORT}"

    print_header "Preview: $blog_name (Puerto: $port)"
    print_info "Se abrirá en el navegador automáticamente"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }
    quarto preview --port "$port"
}

# Limpia archivos generados (_site, _freeze, .quarto) de un blog.
# $1 = ruta absoluta del blog
clean_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "$QBLOG_E_CLEAN Limpiando: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    local cleaned=0
    local dir
    for dir in _site _freeze .quarto; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
            print_success "Eliminado: $dir"
            cleaned=$((cleaned + 1))
        fi
    done

    if [[ $cleaned -eq 0 ]]; then
        print_info "No hay archivos para limpiar"
    else
        print_success "Limpieza completada ($cleaned directorios)"
    fi
}

# Publica un blog en el target indicado (gh-pages, netlify, quarto-pub,
# confluence).
# $1 = ruta absoluta del blog
# $2 = target (opcional, default QBLOG_DEFAULT_PUBLISH_TARGET)
publish_blog() {
    local blog_path="$1"
    local target="${2:-$QBLOG_DEFAULT_PUBLISH_TARGET}"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "$QBLOG_E_PUBLISH Publicando: $blog_name"
    print_info "Target: $target"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

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

# Renderiza un post específico (un solo index.qmd).
# $1 = ruta absoluta del index.qmd del post
render_post() {
    local post_path="$1"

    if [[ ! -f "$post_path" ]]; then
        print_error "Post no encontrado: $post_path"
        return 1
    fi

    local post_name
    post_name="$(basename "$(dirname "$post_path")")"
    print_header "Renderizando post: $post_name"

    cd "$(dirname "$post_path")" || { print_error "No se pudo acceder al post"; return 1; }

    if quarto render "$(basename "$post_path")"; then
        print_success "Post renderizado exitosamente"
    else
        print_error "Error al renderizar el post"
        return 1
    fi
}

# Verifica la instalación/configuración de Quarto para un blog (quarto check).
# $1 = ruta absoluta del blog
check_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Verificando: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }
    quarto check
}

# Inspecciona la estructura de un blog (quarto inspect), mostrando solo
# información relevante (Type, Engine, Formats, Output) en vez del JSON
# completo.
# $1 = ruta absoluta del blog
inspect_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "$QBLOG_E_INFO Inspeccionando: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    echo -e "${QBLOG_DIM}"
    quarto inspect | grep -E "(Type|Engine|Formats|Output)" || quarto inspect | head -50
    echo -e "${QBLOG_NC}"
}

# Convierte un documento a otro formato usando quarto convert.
# $1 = ruta del archivo de entrada
# $2 = formato de salida (opcional, default html)
convert_document() {
    local input_file="$1"
    local output_format="${2:-html}"

    if [[ ! -f "$input_file" ]]; then
        print_error "Archivo no encontrado: $input_file"
        return 1
    fi

    print_header "Convirtiendo documento"
    print_info "Entrada: $input_file"
    print_info "Formato: $output_format"

    quarto convert "$input_file" --output "$output_format"
    print_success "Documento convertido"
}
