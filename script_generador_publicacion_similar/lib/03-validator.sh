#!/usr/bin/env bash
# =============================================================================
# 03-validator.sh
# -----------------------------------------------------------------------------
# Validación de entradas ANTES de ejecutar cualquier lógica: directorio del
# blog, URL base y tipo de estructura. Normaliza valores (ruta absoluta,
# URL sin barra final) para que el resto de módulos no repita comprobaciones.
# =============================================================================

if [[ -n "${GENIDX_VALIDATOR_LOADED:-}" ]]; then
    return 0
fi
GENIDX_VALIDATOR_LOADED=1

# validate_environment()
# Ejecuta todas las validaciones en orden. Sale con el código apropiado
# (2 = uso incorrecto, 3 = directorio inexistente) ante el primer fallo.
validate_environment() {
    _validate_blog_dir
    _normalize_base_url
    _validate_blog_type
}

# _validate_blog_dir()
# Comprueba que se indicó un directorio, que existe, y lo convierte a ruta
# absoluta para que los mensajes y archivos generados sean inequívocos.
_validate_blog_dir() {
    if [[ -z "$GENIDX_BLOG_DIR" ]]; then
        log_error "Falta el directorio del blog a procesar"
        echo "" >&2
        show_help >&2
        exit 2
    fi

    if [[ ! -d "$GENIDX_BLOG_DIR" ]]; then
        log_error "El directorio '$GENIDX_BLOG_DIR' no existe"
        log_info "Ejemplos válidos: ~/Documents/pub_axiomata, ~/Documents/website-achalma/blog"
        exit 3
    fi

    # cd en subshell: resuelve rutas relativas y symlinks sin afectar al caller
    GENIDX_BLOG_DIR="$(cd "$GENIDX_BLOG_DIR" && pwd)"
}

# _normalize_base_url()
# Elimina la barra final si el usuario la incluyó (evita URLs con "//")
# y avisa si el esquema no parece una URL web.
_normalize_base_url() {
    GENIDX_BASE_URL="${GENIDX_BASE_URL%/}"

    if [[ ! "$GENIDX_BASE_URL" =~ ^https?:// ]]; then
        log_warn "La URL base no empieza con http(s):// — '$GENIDX_BASE_URL'"
    fi
}

# _validate_blog_type()
# Restringe el tipo a los tres valores soportados.
_validate_blog_type() {
    case "$GENIDX_BLOG_TYPE" in
        auto|website|blog)
            return 0
            ;;
        *)
            log_error "Tipo de estructura inválido: '$GENIDX_BLOG_TYPE' (use: auto, website o blog)"
            exit 2
            ;;
    esac
}
