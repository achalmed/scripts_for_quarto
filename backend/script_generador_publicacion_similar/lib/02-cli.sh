#!/usr/bin/env bash
# =============================================================================
# 02-cli.sh
# -----------------------------------------------------------------------------
# Parsing de argumentos y ayuda. Reemplaza la configuración hardcodeada de la
# versión monolítica: el directorio del blog ahora es un argumento posicional
# obligatorio, lo que permite procesar cualquier blog sin editar el script.
# =============================================================================

if [[ -n "${GENIDX_CLI_LOADED:-}" ]]; then
    return 0
fi
GENIDX_CLI_LOADED=1

# show_help()
# Imprime la ayuda completa con ejemplos reales de este entorno.
show_help() {
    cat << EOF
Uso: $GENIDX_SCRIPT_NAME BLOG_DIR [OPCIONES]

Genera archivos de índice (${GENIDX_OUTPUT_PREFIX}<subblog>.qmd) con enlaces
a las publicaciones (carpetas YYYY-MM-DD-titulo/) de un blog Quarto.

Argumentos:
  BLOG_DIR              Directorio del blog a procesar (obligatorio)

Opciones:
  -u, --base-url URL    URL base del sitio, sin barra final
                        (por defecto: $GENIDX_DEFAULT_BASE_URL)
  -t, --type TIPO       Estructura del blog: auto | website | blog
                        (por defecto: $GENIDX_DEFAULT_BLOG_TYPE)
  -n, --dry-run         Simula la ejecución sin escribir ni borrar archivos
  -h, --help            Muestra esta ayuda
      --version         Muestra la versión

Tipos de estructura:
  blog     Proyecto Quarto independiente (pub_*): la URL no incluye el
           nombre de la carpeta raíz  →  base/<subblog>/<post>/
  website  Sección de una página web (website-achalma/blog, /teching):
           la URL incluye la sección  →  base/<seccion>/<subblog>/<post>/
  auto     Detecta según la ubicación del _quarto.yml (recomendado)

Ejemplos:
  # Blog independiente (URL base propia del blog)
  $GENIDX_SCRIPT_NAME ~/Documents/pub_actus-mercator \\
      --base-url https://actus-mercator.netlify.app

  # Sección de la página web (usa la URL base por defecto)
  $GENIDX_SCRIPT_NAME ~/Documents/website-achalma/teching

  # Simular sin modificar nada
  $GENIDX_SCRIPT_NAME ~/Documents/pub_axiomata --dry-run
EOF
}

# parse_arguments()
# Puebla las variables globales GENIDX_BLOG_DIR, GENIDX_BASE_URL,
# GENIDX_BLOG_TYPE y GENIDX_DRY_RUN a partir de los argumentos CLI.
# Sale con código 2 ante argumentos inválidos.
# Arguments:
#   $@ - Argumentos recibidos por main.sh
parse_arguments() {
    GENIDX_BLOG_DIR=""
    GENIDX_BASE_URL="$GENIDX_DEFAULT_BASE_URL"
    GENIDX_BLOG_TYPE="$GENIDX_DEFAULT_BLOG_TYPE"
    GENIDX_DRY_RUN=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--base-url)
                _require_option_value "$1" "${2:-}"
                GENIDX_BASE_URL="$2"
                shift 2
                ;;
            -t|--type)
                _require_option_value "$1" "${2:-}"
                GENIDX_BLOG_TYPE="$2"
                shift 2
                ;;
            -n|--dry-run)
                GENIDX_DRY_RUN=1
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                echo "$GENIDX_SCRIPT_NAME v$GENIDX_VERSION"
                exit 0
                ;;
            -*)
                log_error "Opción desconocida: $1"
                echo ""
                show_help
                exit 2
                ;;
            *)
                if [[ -n "$GENIDX_BLOG_DIR" ]]; then
                    log_error "Solo se admite un directorio de blog (recibido: '$GENIDX_BLOG_DIR' y '$1')"
                    exit 2
                fi
                GENIDX_BLOG_DIR="$1"
                shift
                ;;
        esac
    done
}

# _require_option_value()
# Verifica que una opción que espera valor lo haya recibido.
# Arguments:
#   $1 - Nombre de la opción (para el mensaje de error)
#   $2 - Valor recibido (posiblemente vacío)
_require_option_value() {
    if [[ -z "$2" ]]; then
        log_error "La opción '$1' requiere un valor"
        exit 2
    fi
}
