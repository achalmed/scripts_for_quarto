#!/usr/bin/env bash
# =============================================================================
# 04-detector.sh
# -----------------------------------------------------------------------------
# Detección automática de la estructura del blog. La señal principal es la
# ubicación del _quarto.yml: si está en el propio directorio es un proyecto
# independiente ("blog"); si está en el padre, el directorio es una sección
# de una página web ("website"). Esto corrige el bug de la versión monolítica,
# que solo reconocía "website" cuando la carpeta se llamaba literalmente
# "blog" (fallaba con secciones como teching/ o talk/).
# =============================================================================

if [[ -n "${GENIDX_DETECTOR_LOADED:-}" ]]; then
    return 0
fi
GENIDX_DETECTOR_LOADED=1

# detect_blog_structure()
# Determina la estructura del blog para construir URLs correctas.
# Arguments:
#   $1 - Ruta absoluta al directorio del blog
# Outputs:
#   "website" o "blog" por stdout
detect_blog_structure() {
    local blog_dir="$1"
    local parent_dir
    parent_dir="$(dirname "$blog_dir")"

    # Señal principal: dónde vive el _quarto.yml (raíz del sitio Quarto)
    if [[ -f "$blog_dir/_quarto.yml" ]]; then
        echo "blog"
        return 0
    fi
    if [[ -f "$parent_dir/_quarto.yml" ]]; then
        echo "website"
        return 0
    fi

    # Compatibilidad con la heurística de la versión monolítica, por si el
    # blog aún no tiene _quarto.yml (proyecto en construcción)
    if [[ "$(basename "$blog_dir")" == "blog" && -d "$blog_dir/posts" ]]; then
        echo "website"
        return 0
    fi

    echo "blog"
}
