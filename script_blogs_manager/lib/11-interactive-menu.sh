#!/usr/bin/env bash
# =============================================================================
# 11-interactive-menu.sh
# -----------------------------------------------------------------------------
# Menú interactivo de la aplicación: mismo flujo numerado del script
# original (1-16), con la opción 10 (limpiar todos) ahora apuntando a la
# función clean_all_blogs ya corregida.
# =============================================================================

if [[ -n "${QBLOG_INTERACTIVE_MENU_LOADED:-}" ]]; then
    return 0
fi
QBLOG_INTERACTIVE_MENU_LOADED=1

# Resuelve un nombre de blog ingresado en el menú. Si no existe, imprime un
# error claro y devuelve 1 (sin abortar el menú, ya que aquí estamos en un
# loop interactivo). El llamador debe comprobar el código de salida antes
# de usar la ruta resuelta.
_menu_resolve() {
    local docs_dir="$1"
    local blog_name="$2"
    if ! QBLOG_RESOLVED_PATH="$(utils_resolve_project_path "$docs_dir" "$blog_name")"; then
        print_error "Blog no encontrado: $blog_name"
        print_info "Usa la opción 1 para ver los blogs disponibles"
        return 1
    fi
    return 0
}

show_menu() {
    local docs_dir="$1"
    clear
    print_header "Gestor de Publicaciones Quarto v3.0"
    echo ""
    echo -e "${QBLOG_CYAN}Directorio:${QBLOG_NC} $docs_dir"
    echo ""

    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}Gestión de Blogs:${QBLOG_NC}"
    echo -e "  ${QBLOG_WHITE}1)${QBLOG_NC} $QBLOG_E_BOOK Listar todos los blogs"
    echo -e "  ${QBLOG_WHITE}2)${QBLOG_NC} $QBLOG_E_GEAR Renderizar blog"
    echo -e "  ${QBLOG_WHITE}3)${QBLOG_NC} $QBLOG_E_PREVIEW Preview de blog"
    echo -e "  ${QBLOG_WHITE}4)${QBLOG_NC} $QBLOG_E_CLEAN Limpiar archivos"
    echo -e "  ${QBLOG_WHITE}5)${QBLOG_NC} $QBLOG_E_PUBLISH Publicar blog"
    echo ""

    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}Gestión de Posts:${QBLOG_NC}"
    echo -e "  ${QBLOG_WHITE}6)${QBLOG_NC} $QBLOG_E_FILE Crear nuevo post"
    echo -e "  ${QBLOG_WHITE}7)${QBLOG_NC} $QBLOG_E_GEAR Renderizar post específico"
    echo -e "  ${QBLOG_WHITE}8)${QBLOG_NC} $QBLOG_E_FILE Listar posts"
    echo ""

    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}Operaciones Múltiples:${QBLOG_NC}"
    echo -e "  ${QBLOG_WHITE}9)${QBLOG_NC} $QBLOG_E_GEAR Renderizar todos los blogs"
    echo -e "  ${QBLOG_WHITE}10)${QBLOG_NC} $QBLOG_E_CLEAN Limpiar todos los blogs"
    echo ""

    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}Git:${QBLOG_NC}"
    echo -e "  ${QBLOG_WHITE}11)${QBLOG_NC} $QBLOG_E_GIT Git status de blog"
    echo -e "  ${QBLOG_WHITE}12)${QBLOG_NC} $QBLOG_E_GIT Git commit & push"
    echo -e "  ${QBLOG_WHITE}13)${QBLOG_NC} $QBLOG_E_GIT Inicializar Git en blog"
    echo ""

    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}Utilidades:${QBLOG_NC}"
    echo -e "  ${QBLOG_WHITE}14)${QBLOG_NC} $QBLOG_E_INFO Verificar blog (quarto check)"
    echo -e "  ${QBLOG_WHITE}15)${QBLOG_NC} $QBLOG_E_INFO Inspeccionar blog"
    echo -e "  ${QBLOG_WHITE}16)${QBLOG_NC} $QBLOG_E_INFO Convertir documento"
    echo ""

    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}Otras herramientas:${QBLOG_NC}"
    echo -e "  ${QBLOG_WHITE}17)${QBLOG_NC} $QBLOG_E_ROCKET Crear nuevo blog (init-blog)"
    echo -e "  ${QBLOG_WHITE}18)${QBLOG_NC} $QBLOG_E_INFO Verificar estructura de todos los blogs"
    echo -e "  ${QBLOG_WHITE}19)${QBLOG_NC} 💾 Crear backup"
    echo ""

    echo -e "  ${QBLOG_WHITE}0)${QBLOG_NC} ${QBLOG_RED}Salir${QBLOG_NC}"
    echo ""
}

# $1 = ruta absoluta de Documents
# $2 = ruta absoluta del directorio de backups
interactive_mode() {
    local docs_dir="$1"
    local backup_dir="$2"

    while true; do
        show_menu "$docs_dir"
        read -r -p "$(echo -e "${QBLOG_WHITE}${QBLOG_BOLD}→${QBLOG_NC}")  Selecciona una opción: " option

        case $option in
            1)
                list_blogs "$docs_dir"
                read -r -p "Presiona Enter para continuar..."
                ;;
            2)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    render_blog "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            3)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                read -r -p "Puerto (default: $QBLOG_DEFAULT_PREVIEW_PORT): " port
                port=${port:-$QBLOG_DEFAULT_PREVIEW_PORT}
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    preview_blog "$QBLOG_RESOLVED_PATH" "$port"
                fi
                ;;
            4)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    clean_blog "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            5)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                echo "Targets disponibles: gh-pages, netlify, quarto-pub, confluence"
                read -r -p "Target (default: $QBLOG_DEFAULT_PUBLISH_TARGET): " target
                target=${target:-$QBLOG_DEFAULT_PUBLISH_TARGET}
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    publish_blog "$QBLOG_RESOLVED_PATH" "$target"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            6)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    create_post_interactive "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            7)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    list_posts "$QBLOG_RESOLVED_PATH"
                    read -r -p "Ruta completa del index.qmd: " post_path
                    render_post "$post_path"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            8)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    list_posts "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            9)
                render_all_blogs "$docs_dir"
                read -r -p "Presiona Enter para continuar..."
                ;;
            10)
                clean_all_blogs "$docs_dir"
                read -r -p "Presiona Enter para continuar..."
                ;;
            11)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    git_status_blog "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            12)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                read -r -p "Mensaje del commit: " message
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    git_commit_push "$QBLOG_RESOLVED_PATH" "$message"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            13)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    git_init "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            14)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    check_blog "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            15)
                list_blogs "$docs_dir"
                read -r -p "Nombre del blog: " blog_name
                if _menu_resolve "$docs_dir" "$blog_name"; then
                    inspect_blog "$QBLOG_RESOLVED_PATH"
                fi
                read -r -p "Presiona Enter para continuar..."
                ;;
            16)
                read -r -p "Ruta del archivo: " input_file
                read -r -p "Formato de salida (html/pdf/docx): " format
                convert_document "$input_file" "$format"
                read -r -p "Presiona Enter para continuar..."
                ;;
            17)
                read -r -p "Nombre del nuevo blog (sin prefijo pub_): " new_name
                read -r -p "Título del blog: " new_title
                init_blog "$docs_dir" "$new_name" "$new_title"
                read -r -p "Presiona Enter para continuar..."
                ;;
            18)
                check_structure_all "$docs_dir"
                read -r -p "Presiona Enter para continuar..."
                ;;
            19)
                backup_blogs_interactive "$docs_dir" "$backup_dir"
                read -r -p "Presiona Enter para continuar..."
                ;;
            0)
                echo ""
                print_success "¡Hasta luego!"
                echo ""
                exit 0
                ;;
            *)
                print_error "Opción inválida"
                sleep 2
                ;;
        esac
    done
}
