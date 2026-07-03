#!/usr/bin/env bash
# =============================================================================
# 05-linker.sh
# -----------------------------------------------------------------------------
# Transformación de carpetas de publicación en enlaces Markdown: formateo
# del título, construcción de la URL según la estructura y composición de
# la línea final con icono de PDF.
# =============================================================================

if [[ -n "${GENIDX_LINKER_LOADED:-}" ]]; then
    return 0
fi
GENIDX_LINKER_LOADED=1

# format_post_title()
# Convierte "YYYY-MM-DD-mi-titulo" en "Mi Titulo": quita el prefijo de
# fecha, cambia guiones por espacios y capitaliza cada palabra.
# Nota: '\u' en sed es una extensión GNU (este repo asume Linux).
# Arguments:
#   $1 - Nombre de la carpeta de la publicación
# Outputs:
#   Título formateado por stdout
format_post_title() {
    printf '%s\n' "$1" |
        sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//' |
        tr '-' ' ' |
        sed 's/\b\(.\)/\u\1/g'
}

# build_post_url()
# Construye la URL pública de una publicación según la estructura.
#   website → base/<seccion>/<subblog>/<post>   (incluye la carpeta raíz)
#   blog    → base/<subblog>/<post>             (la raíz ES el sitio)
# Arguments:
#   $1 - Tipo de estructura ("website" o "blog")
#   $2 - Nombre del subblog (carpeta padre de la publicación)
#   $3 - Nombre de la carpeta de la publicación
# Outputs:
#   URL completa por stdout
build_post_url() {
    local blog_type="$1"
    local subblog_name="$2"
    local post_folder_name="$3"

    if [[ "$blog_type" == "website" ]]; then
        echo "$GENIDX_BASE_URL/$(basename "$GENIDX_BLOG_DIR")/$subblog_name/$post_folder_name"
    else
        echo "$GENIDX_BASE_URL/$subblog_name/$post_folder_name"
    fi
}

# convert_folder_to_link()
# Genera la línea Markdown de una publicación: icono con enlace al PDF
# seguido del título con enlace al artículo.
# Arguments:
#   $1 - Ruta absoluta a la carpeta de la publicación
# Outputs:
#   Línea Markdown por stdout
convert_folder_to_link() {
    local post_dir="$1"
    local post_folder_name subblog_name post_title post_url

    post_folder_name="$(basename "$post_dir")"
    # basename "$(dirname ...)" y no "dirname | xargs basename": xargs
    # divide por espacios y rompía con rutas como "01 notes"
    subblog_name="$(basename "$(dirname "$post_dir")")"
    post_title="$(format_post_title "$post_folder_name")"
    post_url="$(build_post_url "$GENIDX_BLOG_TYPE" "$subblog_name" "$post_folder_name")"

    printf '[%s](%s/index.pdf) [%s](%s)\n' \
        "$GENIDX_PDF_ICON" "$post_url" "$post_title" "$post_url"
}
