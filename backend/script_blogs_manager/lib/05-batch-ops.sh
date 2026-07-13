#!/usr/bin/env bash
# =============================================================================
# 05-batch-ops.sh
# -----------------------------------------------------------------------------
# Operaciones que se aplican a TODOS los blogs gestionables a la vez.
#
# NOTA DE MIGRACIÓN: el script original (build.sh v2.0) invocaba
# "clean_all_blogs" desde el menú interactivo y desde main(), pero esa
# función nunca llegó a definirse — el comando "clean-all" rompía con
# "command not found". Aquí se agrega clean_all_blogs siguiendo el mismo
# patrón que render_all_blogs, corrigiendo ese bug.
# =============================================================================

if [[ -n "${QBLOG_BATCH_OPS_LOADED:-}" ]]; then
    return 0
fi
QBLOG_BATCH_OPS_LOADED=1

# Renderiza todos los blogs gestionables (no excluidos).
# $1 = ruta absoluta de Documents
render_all_blogs() {
    local docs_dir="$1"
    print_header "Renderizando TODOS los blogs"

    local success_count=0
    local fail_count=0
    local blog

    while IFS= read -r blog; do
        [[ -z "$blog" ]] && continue
        local blog_name
        blog_name="$(basename "$blog")"

        echo ""
        print_step "Procesando: $blog_name"

        if render_blog "$blog" 2>&1 | tail -5; then
            success_count=$((success_count + 1))
        else
            fail_count=$((fail_count + 1))
        fi
    done < <(utils_list_projects "$docs_dir")

    echo ""
    print_box "Resumen de Renderizado"
    echo ""
    echo -e "  ${QBLOG_GREEN}$QBLOG_E_SUCCESS Exitosos:${QBLOG_NC} $success_count"
    echo -e "  ${QBLOG_RED}$QBLOG_E_ERROR Fallidos:${QBLOG_NC} $fail_count"
    echo ""
}

# Limpia archivos generados (_site, _freeze, .quarto) de todos los blogs
# gestionables (no excluidos). Pide confirmación antes de proceder, ya que
# es una operación que borra archivos en todos los proyectos a la vez.
# $1 = ruta absoluta de Documents
# $2 = "1" para omitir confirmación (uso no interactivo), "0" por defecto
clean_all_blogs() {
    local docs_dir="$1"
    local skip_confirm="${2:-0}"

    print_header "$QBLOG_E_CLEAN Limpiando TODOS los blogs"

    if [[ "$skip_confirm" != "1" ]]; then
        read -r -p "¿Estás seguro? Esto eliminará _site, _freeze y .quarto de todos los blogs (s/n): " confirm
        if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
            print_info "Operación cancelada"
            return 0
        fi
    fi

    local cleaned_blogs=0
    local blog

    while IFS= read -r blog; do
        [[ -z "$blog" ]] && continue
        clean_blog "$blog"
        cleaned_blogs=$((cleaned_blogs + 1))
        echo ""
    done < <(utils_list_projects "$docs_dir")

    print_box "Resumen de Limpieza"
    echo ""
    echo -e "  ${QBLOG_GREEN}$QBLOG_E_SUCCESS Blogs procesados:${QBLOG_NC} $cleaned_blogs"
    echo ""
}
