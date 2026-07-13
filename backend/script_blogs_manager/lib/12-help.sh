#!/usr/bin/env bash
# =============================================================================
# 12-help.sh
# -----------------------------------------------------------------------------
# Texto de ayuda mostrado con "help", "-h" o "--help".
# =============================================================================

if [[ -n "${QBLOG_HELP_LOADED:-}" ]]; then
    return 0
fi
QBLOG_HELP_LOADED=1

# $1 = ruta absoluta de Documents (para mostrarla en la ayuda)
# $2 = ruta absoluta del directorio de backups
show_help() {
    local docs_dir="$1"
    local backup_dir="$2"

    cat << EOF
${QBLOG_CYAN}═══════════════════════════════════════════════════════════════${QBLOG_NC}
  🚀 Gestor de Publicaciones Quarto - Ayuda
${QBLOG_CYAN}═══════════════════════════════════════════════════════════════${QBLOG_NC}

${QBLOG_YELLOW}USO:${QBLOG_NC}
    main.sh [COMANDO] [OPCIONES]

${QBLOG_YELLOW}COMANDOS PRINCIPALES:${QBLOG_NC}

  ${QBLOG_GREEN}Gestión de Blogs:${QBLOG_NC}
    list                    Lista todos los blogs disponibles
    render BLOG             Renderiza un blog completo
    preview BLOG [PORT]     Inicia preview del blog (puerto opcional)
    preview-browser BLOG    Preview con apertura automática del navegador
    clean BLOG              Limpia archivos generados (_site, _freeze, etc.)
    publish BLOG [TARGET]   Publica el blog (gh-pages, netlify, etc.)
    check BLOG              Verifica la configuración del blog
    inspect BLOG            Inspecciona la estructura del blog

  ${QBLOG_GREEN}Gestión de Posts:${QBLOG_NC}
    list-posts BLOG         Lista todos los posts de un blog
    render-post POST_PATH   Renderiza un post específico
    new-post BLOG           Crea un nuevo post (asistente interactivo)

  ${QBLOG_GREEN}Operaciones Múltiples:${QBLOG_NC}
    render-all              Renderiza todos los blogs
    clean-all                Limpia todos los blogs (pide confirmación)

  ${QBLOG_GREEN}Git:${QBLOG_NC}
    git-init BLOG           Inicializa repositorio Git
    git-status BLOG         Muestra estado de Git
    git-commit BLOG [MSG]   Commit y push de cambios

  ${QBLOG_GREEN}Utilidades:${QBLOG_NC}
    convert FILE [FORMAT]   Convierte documento a otro formato
    init-blog NOMBRE [TITULO]   Crea un blog nuevo (carpeta pub_NOMBRE)
    check-structure         Verifica la integridad de todos los blogs
    backup                  Sistema de backups interactivo
    interactive, -i         Modo interactivo (menú)
    help, -h, --help        Muestra esta ayuda
    version, -v             Muestra versión de Quarto

${QBLOG_YELLOW}EJEMPLOS:${QBLOG_NC}

  # Listar todos los blogs
  main.sh list

  # Renderizar un blog específico
  main.sh render website-achalma

  # Preview de un blog en puerto específico
  main.sh preview pub_epsilon-y-beta 4300

  # Crear nuevo post (asistente interactivo completo)
  main.sh new-post pub_numerus-scriptum

  # Renderizar post específico
  main.sh render-post /path/to/blog/posts/2025-12-28-mi-post/index.qmd

  # Limpiar y renderizar
  main.sh clean pub_axiomata && main.sh render pub_axiomata

  # Commit y push
  main.sh git-commit website-achalma "Actualización de contenido"

  # Crear un blog nuevo
  main.sh init-blog mi-nuevo-blog "Mi Nuevo Blog"

  # Modo interactivo
  main.sh -i

${QBLOG_YELLOW}NOTAS SOBRE NOMBRES DE BLOG:${QBLOG_NC}
  Puedes usar el nombre exacto de la carpeta (ej: "pub_axiomata",
  "website-achalma") o el nombre corto sin el prefijo "pub_" (ej:
  "axiomata" se resuelve automáticamente a "pub_axiomata" si existe).

${QBLOG_YELLOW}UBICACIONES:${QBLOG_NC}
  Documents (autodetectado): ${docs_dir}
  Backups:                   ${backup_dir}

${QBLOG_YELLOW}NOTAS:${QBLOG_NC}
  - Los blogs deben tener un archivo index.qmd o _quarto.yml
  - El preview se ejecuta en puerto $QBLOG_DEFAULT_PREVIEW_PORT por defecto
  - La limpieza elimina: _site, _freeze, .quarto
  - Se gestionan todas las carpetas pub_* + website-achalma dentro de
    Documents (ver QBLOG_EXCLUDED_PROJECTS en lib/00-config.sh para excluir
    alguna puntualmente)

Para más información sobre Quarto: https://quarto.org/docs/

EOF
}
