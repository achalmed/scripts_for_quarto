#!/usr/bin/env bash
# =============================================================================
# 07-post-creator.sh
# -----------------------------------------------------------------------------
# Asistente interactivo completo para crear posts APAQuarto: detecta/crea
# carpeta de destino, recorre 6 secciones del formulario (opciones
# generales, formato, autores, author-note, abstract/keywords, idioma), y
# genera el index.qmd resultante. Misma lógica exacta del script original;
# solo se separó en su propio archivo para facilitar mantenimiento.
# =============================================================================

if [[ -n "${QBLOG_POST_CREATOR_LOADED:-}" ]]; then
    return 0
fi
QBLOG_POST_CREATOR_LOADED=1

# Wizard interactivo completo de creación de post.
# $1 = ruta absoluta del blog
create_post_interactive() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "🚀 Asistente de Creación de Posts - $blog_name"

    echo -e "${QBLOG_CYAN}Este asistente te guiará paso a paso para crear un post APAQuarto completo.${QBLOG_NC}"
    echo -e "${QBLOG_DIM}Presiona Enter para usar valores por defecto | Escribe 'omitir' para saltar secciones opcionales${QBLOG_NC}"
    echo ""
    read -r -p "Presiona Enter para comenzar..."

    # =========================================================================
    # PASO 0: Selección de carpeta de destino
    # =========================================================================
    clear
    print_header "📁 Paso 0/6: Carpeta de Destino"

    print_step "Detectando carpetas de posts..."
    local post_folders=()
    while IFS= read -r f; do
        [[ -n "$f" ]] && post_folders+=("$f")
    done < <(utils_detect_post_folders "$blog_path")

    if [[ ${#post_folders[@]} -eq 0 ]]; then
        print_warning "No se detectaron carpetas de posts existentes"
        read -r -p "Nombre de la nueva carpeta de posts: " new_folder
        post_folders=("$new_folder")
    fi

    echo ""
    echo -e "${QBLOG_CYAN}Carpetas disponibles:${QBLOG_NC}"
    local i=1
    local folder
    for folder in "${post_folders[@]}"; do
        echo -e "  ${QBLOG_MAGENTA}$i)${QBLOG_NC} ${QBLOG_GREEN}$folder${QBLOG_NC}"
        i=$((i + 1))
    done
    echo -e "  ${QBLOG_MAGENTA}$i)${QBLOG_NC} ${QBLOG_BOLD}Crear nueva carpeta${QBLOG_NC}"
    echo ""

    read -r -p "Selecciona carpeta (1-$i): " folder_choice

    local target_folder
    if [[ "$folder_choice" -eq "$i" ]]; then
        read -r -p "Nombre de la nueva carpeta: " new_folder
        target_folder="$new_folder"
        mkdir -p "$blog_path/$target_folder"

        if [[ ! -f "$blog_path/$target_folder/_metadata.yml" ]]; then
            create_metadata_file "$blog_path/$target_folder"
        fi
    else
        target_folder="${post_folders[$((folder_choice - 1))]}"
    fi

    print_success "Carpeta seleccionada: $target_folder"
    sleep 1

    # =========================================================================
    # SECCIÓN 1: OPCIONES GENERALES
    # =========================================================================
    clear
    print_header "📝 Sección 1/6: Opciones Generales"

    print_subheader "1.1. Información del Título"

    read -r -p "Title (título principal): " post_title
    while [[ -z "$post_title" ]]; do
        print_warning "El título es obligatorio"
        read -r -p "Title: " post_title
    done

    echo -e "${QBLOG_DIM}Ejemplo: \"Análisis Econométrico Avanzado: Modelos ARIMA\"${QBLOG_NC}"
    read -r -p "Subtitle (opcional, Enter para omitir): " post_subtitle

    local short_title
    echo -e "${QBLOG_DIM}Ejemplo: \"Análisis Econométrico\" (máx. 50 caracteres)${QBLOG_NC}"
    read -r -p "Shorttitle (Enter para auto-generar desde title): " short_title
    [[ -z "$short_title" ]] && short_title=$(echo "$post_title" | cut -c1-50)

    print_subheader "1.2. Opciones del Documento"
    echo -e "${QBLOG_DIM}Configuración avanzada del documento (Enter para valores por defecto)${QBLOG_NC}"
    echo ""

    read -r -p "Floatsintext - Figuras/tablas en texto (s/n, default: n): " floatsintext
    floatsintext=${floatsintext:-n}

    read -r -p "Numbered-lines - Números de línea (s/n, default: n): " numbered_lines
    numbered_lines=${numbered_lines:-n}

    read -r -p "No-ampersand-parenthetical - Usar 'y' en lugar de '&' (s/n, default: n): " no_ampersand
    no_ampersand=${no_ampersand:-n}

    echo -e "${QBLOG_DIM}Ejemplo: \"referencias.bib\" o \"bib1.bib, bib2.bib\"${QBLOG_NC}"
    read -r -p "Bibliography file(s) (Enter para 'references.bib'): " bibliography
    bibliography=${bibliography:-references.bib}

    read -r -p "Mask - Revisión ciega (s/n, default: n): " mask
    mask=${mask:-n}

    echo -e "${QBLOG_DIM}Ejemplo: \"@estudio1, @estudio2\" (para meta-análisis)${QBLOG_NC}"
    read -r -p "Nocite - Referencias no citadas (Enter para omitir): " nocite

    read -r -p "Meta-analysis - Marcar estudios con asterisco (s/n, default: n): " meta_analysis
    meta_analysis=${meta_analysis:-n}

    echo -e "${QBLOG_DIM}Ejemplo: \"Este estudio impacta la práctica clínica...\"${QBLOG_NC}"
    read -r -p "Impact-statement (Enter para omitir): " impact_statement

    print_subheader "1.3. Suprimir Elementos (opcional)"
    echo -e "${QBLOG_YELLOW}¿Deseas configurar supresión de elementos? (s/n, default: n):${QBLOG_NC} "
    read -r suppress_config

    declare -A suppress_elements
    if [[ "$suppress_config" =~ ^[Ss]$ ]]; then
        echo ""
        echo -e "${QBLOG_DIM}Marca 's' para suprimir cada elemento:${QBLOG_NC}"

        local element
        for element in title-page title short-title author affiliation author-note orcid abstract keywords; do
            read -r -p "  Suppress-$element (s/n): " suppress_choice
            suppress_elements[$element]=$suppress_choice
        done
    fi

    print_success "Opciones generales configuradas"
    sleep 1

    # =========================================================================
    # SECCIÓN 2: OPCIONES DE FORMATO
    # =========================================================================
    clear
    print_header "🎨 Sección 2/6: Opciones de Formato"

    print_subheader "2.1. Tipo de Documento"
    echo ""
    echo -e "${QBLOG_MAGENTA}1)${QBLOG_NC} doc  - Documento general (flexible)"
    echo -e "${QBLOG_MAGENTA}2)${QBLOG_NC} jou  - Formato revista (2 columnas) ${QBLOG_YELLOW}[Recomendado]${QBLOG_NC}"
    echo -e "${QBLOG_MAGENTA}3)${QBLOG_NC} man  - Manuscrito formal"
    echo -e "${QBLOG_MAGENTA}4)${QBLOG_NC} stu  - Trabajo estudiantil"
    echo ""

    read -r -p "Selecciona tipo (1-4, Enter=jou): " doc_type_choice
    doc_type_choice=${doc_type_choice:-2}

    local doc_type
    case $doc_type_choice in
        1) doc_type="doc" ;;
        2) doc_type="jou" ;;
        3) doc_type="man" ;;
        4) doc_type="stu" ;;
        *) doc_type="jou" ;;
    esac

    print_subheader "2.2. Formatos de Salida"
    echo -e "${QBLOG_DIM}Selecciona formatos a generar (s/n para cada uno):${QBLOG_NC}"

    read -r -p "  apaquarto-docx (Word) (s/n, default: s): " format_docx
    format_docx=${format_docx:-s}

    read -r -p "  apaquarto-html (Web) (s/n, default: s): " format_html
    format_html=${format_html:-s}

    read -r -p "  apaquarto-pdf (PDF) (s/n, default: s): " format_pdf
    format_pdf=${format_pdf:-s}

    read -r -p "  apaquarto-typst (Typst) (s/n, default: n): " format_typst
    format_typst=${format_typst:-n}

    local fontsize blank_lines_title blank_lines_author a4paper

    if [[ "$format_pdf" =~ ^[Ss]$ ]] || [[ "$format_typst" =~ ^[Ss]$ ]]; then
        echo ""
        echo -e "${QBLOG_DIM}Ejemplo: \"12pt\" (opciones: 10pt, 11pt, 12pt)${QBLOG_NC}"
        read -r -p "  Fontsize (Enter=12pt): " fontsize
        fontsize=${fontsize:-12pt}

        echo -e "${QBLOG_DIM}Ejemplo: 2 (líneas en blanco sobre el título)${QBLOG_NC}"
        read -r -p "  Blank-lines-above-title (Enter=2): " blank_lines_title
        blank_lines_title=${blank_lines_title:-2}

        read -r -p "  Blank-lines-above-author-note (Enter=2): " blank_lines_author
        blank_lines_author=${blank_lines_author:-2}

        read -r -p "  A4paper (s/n, default: n): " a4paper
        a4paper=${a4paper:-n}
    fi

    local journal_name volume_info copyright_notice copyright_text
    local course_name professor_name due_date student_note

    if [[ "$doc_type" == "jou" ]]; then
        print_subheader "2.3. Información de Revista (modo journal)"
        echo -e "${QBLOG_DIM}Ejemplo: \"Journal of Economic Psychology\"${QBLOG_NC}"
        read -r -p "Nombre de la revista: " journal_name

        echo -e "${QBLOG_DIM}Ejemplo: \"2025, Vol. 7, No. 1, 1--25\"${QBLOG_NC}"
        read -r -p "Volumen y número: " volume_info

        echo -e "${QBLOG_DIM}Ejemplo: \"© 2025\"${QBLOG_NC}"
        read -r -p "Copyright notice (Enter para omitir): " copyright_notice

        echo -e "${QBLOG_DIM}Ejemplo: \"Todos los derechos reservados\"${QBLOG_NC}"
        read -r -p "Copyright text (Enter para omitir): " copyright_text

    elif [[ "$doc_type" == "stu" ]]; then
        print_subheader "2.3. Información del Curso (modo estudiantil)"
        echo -e "${QBLOG_DIM}Ejemplo: \"Econometría Aplicada (ECON 5201)\"${QBLOG_NC}"
        read -r -p "Nombre del curso: " course_name

        echo -e "${QBLOG_DIM}Ejemplo: \"Dr. Juan Pérez\"${QBLOG_NC}"
        read -r -p "Profesor: " professor_name

        echo -e "${QBLOG_DIM}Ejemplo: \"15/12/2025\"${QBLOG_NC}"
        read -r -p "Fecha de entrega: " due_date

        echo -e "${QBLOG_DIM}Ejemplo: \"Student ID: 2020123456\"${QBLOG_NC}"
        read -r -p "Nota adicional (Enter para omitir): " student_note
    fi

    print_success "Opciones de formato configuradas"
    sleep 1

    # =========================================================================
    # SECCIÓN 3: AUTORES Y AFILIACIONES
    # =========================================================================
    clear
    print_header "👤 Sección 3/6: Autores y Afiliaciones"

    echo -e "${QBLOG_YELLOW}¿Usar autor predeterminado de _metadata.yml? (s/n):${QBLOG_NC} "
    read -r use_default_author

    local author_name="" author_orcid="" author_email="" is_corresponding="" author_url=""
    local affiliation_id="" institution_name="" department="" address=""
    local city="" region="" country="" postal_code=""
    declare -A credit_roles

    if [[ ! "$use_default_author" =~ ^[Ss]$ ]]; then
        print_subheader "3.1. Información del Autor Principal"

        echo -e "${QBLOG_DIM}Ejemplo: \"María González Pérez\"${QBLOG_NC}"
        read -r -p "Nombre completo: " author_name

        echo -e "${QBLOG_DIM}Ejemplo: \"0000-0002-1234-5678\"${QBLOG_NC}"
        read -r -p "ORCID (Enter para omitir): " author_orcid

        echo -e "${QBLOG_DIM}Ejemplo: \"maria.gonzalez@universidad.edu\"${QBLOG_NC}"
        read -r -p "Email: " author_email

        read -r -p "¿Es autor correspondiente? (s/n, default: s): " is_corresponding
        is_corresponding=${is_corresponding:-s}

        echo -e "${QBLOG_DIM}Ejemplo: \"https://investigador.com/maria\"${QBLOG_NC}"
        read -r -p "URL (Enter para omitir): " author_url

        print_subheader "3.2. Roles CRediT del Autor"
        echo -e "${QBLOG_DIM}Opciones: No, Yes, Lead, Supporting, Equal (Enter para No)${QBLOG_NC}"
        echo ""

        local role role_display role_value
        for role in conceptualization "data-curation" "formal-analysis" "funding-acquisition" \
                    investigation methodology "project-administration" resources software \
                    supervision validation visualization writing editing; do
            role_display=$(echo "$role" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
            read -r -p "  $role_display (No/Yes/Lead/Supporting/Equal): " role_value
            if [[ -n "$role_value" ]] && [[ "$role_value" != "No" ]]; then
                credit_roles[$role]=$role_value
            fi
        done

        print_subheader "3.3. Afiliación Institucional"
        echo -e "${QBLOG_DIM}Ejemplo: \"unsch\"${QBLOG_NC}"
        read -r -p "ID de afiliación: " affiliation_id

        echo -e "${QBLOG_DIM}Ejemplo: \"Universidad Nacional de San Cristóbal de Huamanga\"${QBLOG_NC}"
        read -r -p "Nombre de la institución: " institution_name

        echo -e "${QBLOG_DIM}Ejemplo: \"Facultad de Ciencias Económicas\"${QBLOG_NC}"
        read -r -p "Departamento: " department

        echo -e "${QBLOG_DIM}Ejemplo: \"Av. Independencia 123\"${QBLOG_NC}"
        read -r -p "Dirección (Enter para omitir): " address

        echo -e "${QBLOG_DIM}Ejemplo: \"Ayacucho\"${QBLOG_NC}"
        read -r -p "Ciudad: " city

        echo -e "${QBLOG_DIM}Ejemplo: \"Ayacucho\"${QBLOG_NC}"
        read -r -p "Región/Estado: " region

        echo -e "${QBLOG_DIM}Ejemplo: \"Perú\"${QBLOG_NC}"
        read -r -p "País (Enter para omitir): " country

        echo -e "${QBLOG_DIM}Ejemplo: \"05001\"${QBLOG_NC}"
        read -r -p "Código postal (Enter para omitir): " postal_code
    fi

    print_success "Información de autores configurada"
    sleep 1

    # =========================================================================
    # SECCIÓN 4: AUTHOR NOTE
    # =========================================================================
    clear
    print_header "📋 Sección 4/6: Author Note"

    print_subheader "4.1. Cambios de Estado"
    echo -e "${QBLOG_DIM}Ejemplo: \"María González ahora está en Temple University.\"${QBLOG_NC}"
    read -r -p "Affiliation-change (Enter para omitir): " affiliation_change

    echo -e "${QBLOG_DIM}Ejemplo: \"Juan Pérez falleció el 15 de enero de 2024.\"${QBLOG_NC}"
    read -r -p "Deceased (Enter para omitir): " deceased

    print_subheader "4.2. Disclosures"
    echo -e "${QBLOG_DIM}Ejemplo: \"Los autores no tienen conflictos de interés que declarar.\"${QBLOG_NC}"
    read -r -p "Conflict-of-interest: " conflict_of_interest
    conflict_of_interest=${conflict_of_interest:-"Los autores no tienen conflictos de interés que declarar."}

    echo -e "${QBLOG_DIM}Ejemplo: \"Este estudio fue financiado por Grant XYZ-789...\"${QBLOG_NC}"
    read -r -p "Financial-support (Enter para omitir): " financial_support

    echo -e "${QBLOG_DIM}Ejemplo: \"Registrado en ClinicalTrials.gov (NCT123456).\"${QBLOG_NC}"
    read -r -p "Study-registration (Enter para omitir): " study_registration

    echo -e "${QBLOG_DIM}Ejemplo: \"Los datos están disponibles en https://osf.io/abc123.\"${QBLOG_NC}"
    read -r -p "Data-sharing (Enter para omitir): " data_sharing

    echo -e "${QBLOG_DIM}Ejemplo: \"Basado en la tesis doctoral de María González (2023).\"${QBLOG_NC}"
    read -r -p "Related-report (Enter para omitir): " related_report

    echo -e "${QBLOG_DIM}Ejemplo: \"Agradecemos a Dr. Pedro López por sus comentarios.\"${QBLOG_NC}"
    read -r -p "Gratitude (Enter para omitir): " gratitude

    echo -e "${QBLOG_DIM}Ejemplo: \"El orden de autoría refleja contribuciones iguales.\"${QBLOG_NC}"
    read -r -p "Authorship-agreements (Enter para omitir): " authorship_agreements

    print_success "Author Note configurada"
    sleep 1

    # =========================================================================
    # SECCIÓN 5: ABSTRACT Y KEYWORDS
    # =========================================================================
    clear
    print_header "📄 Sección 5/6: Abstract y Keywords"

    print_subheader "5.1. Abstract"
    echo -e "${QBLOG_DIM}Escribe el resumen (máximo 250 palabras). Presiona Enter dos veces para finalizar.${QBLOG_NC}"
    echo -e "${QBLOG_DIM}Ejemplo: \"Este estudio examina el impacto de X en Y utilizando datos de Z...\"${QBLOG_NC}"
    echo ""

    echo "Abstract:"
    local abstract=""
    local line
    while IFS= read -r line; do
        [[ -z "$line" ]] && break
        abstract="$abstract$line "
    done

    print_subheader "5.2. Keywords"
    echo -e "${QBLOG_DIM}Ejemplo: economía, política fiscal, crecimiento económico${QBLOG_NC}"
    read -r -p "Keywords (separadas por comas, 3-5 recomendadas): " keywords_input
    IFS=',' read -ra keywords <<< "$keywords_input"

    print_subheader "5.3. Impact Statement (opcional)"
    echo -e "${QBLOG_DIM}Ejemplo: \"Los hallazgos tienen implicaciones directas para el diseño de políticas fiscales...\"${QBLOG_NC}"
    read -r -p "Impact-statement (Enter para omitir): " impact_statement_sec5

    read -r -p "Word-count - Mostrar conteo de palabras (s/n, default: n): " word_count
    word_count=${word_count:-n}

    print_success "Abstract y keywords configurados"
    sleep 1

    # =========================================================================
    # SECCIÓN 6: OPCIONES DE IDIOMA
    # =========================================================================
    clear
    print_header "🌍 Sección 6/6: Opciones de Idioma"

    echo -e "${QBLOG_DIM}Códigos: en (inglés), es (español), fr (francés), de (alemán), pt (portugués)${QBLOG_NC}"
    read -r -p "Lang (Enter=es): " lang
    lang=${lang:-es}

    local citation_separator="" citation_masked="" citation_date="" author_note_title=""
    local correspondence_note="" role_intro="" impact_title="" word_count_title="" meta_ref=""

    if [[ "$lang" != "en" ]]; then
        print_subheader "6.1. Personalizaciones de Idioma"

        echo -e "${QBLOG_DIM}Para español: \"y\", para inglés: \"and\"${QBLOG_NC}"
        read -r -p "Citation-last-author-separator (Enter=\"y\"): " citation_separator
        citation_separator=${citation_separator:-y}

        echo -e "${QBLOG_DIM}Ejemplo: \"Cita Enmascarada\"${QBLOG_NC}"
        read -r -p "Citation-masked-author (Enter=Cita Enmascarada): " citation_masked
        citation_masked=${citation_masked:-"Cita Enmascarada"}

        echo -e "${QBLOG_DIM}Ejemplo: \"n.f.\" (no fecha)${QBLOG_NC}"
        read -r -p "Citation-masked-date (Enter=n.f.): " citation_date
        citation_date=${citation_date:-"n.f."}

        echo -e "${QBLOG_DIM}Ejemplo: \"Nota de Autores\"${QBLOG_NC}"
        read -r -p "Title-block-author-note (Enter=Nota de Autores): " author_note_title
        author_note_title=${author_note_title:-"Nota de Autores"}

        echo -e "${QBLOG_DIM}¿Configurar más opciones de idioma? (s/n, default: n):${QBLOG_NC} "
        read -r more_lang_config

        if [[ "$more_lang_config" =~ ^[Ss]$ ]]; then
            read -r -p "Title-block-correspondence-note: " correspondence_note
            read -r -p "Title-block-role-introduction: " role_intro
            read -r -p "Title-impact-statement: " impact_title
            read -r -p "Title-word-count: " word_count_title
            read -r -p "References-meta-analysis: " meta_ref
        fi
    fi

    print_success "Opciones de idioma configuradas"
    sleep 1

    # =========================================================================
    # INFORMACIÓN ADICIONAL
    # =========================================================================
    clear
    print_header "🏷️ Información Adicional"

    echo -e "${QBLOG_DIM}Ejemplo: análisis, econometría, tutorial${QBLOG_NC}"
    read -r -p "Tags (separados por comas): " tags_input

    echo -e "${QBLOG_DIM}Ejemplo: Análisis, Tutorial (máximo 2)${QBLOG_NC}"
    read -r -p "Categorías (separadas por comas, 1-2): " categories_input

    IFS=',' read -ra tags <<< "$tags_input"
    IFS=',' read -ra categories <<< "$categories_input"

    print_success "Información adicional configurada"
    sleep 1

    # =========================================================================
    # GENERACIÓN DEL ARCHIVO INDEX.QMD
    # =========================================================================
    clear
    print_header "⚙️ Generando index.qmd..."

    local post_date
    post_date=$(date +%Y-%m-%d)
    local post_slug
    post_slug=$(echo "$post_title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
    local post_dir="$blog_path/$target_folder/$post_date-$post_slug"

    if [[ -d "$post_dir" ]]; then
        print_error "Ya existe un post con ese nombre"
        return 1
    fi

    mkdir -p "$post_dir"

    cat > "$post_dir/index.qmd" << EOF
---
title: "$post_title"
EOF

    [[ -n "$post_subtitle" ]] && echo "subtitle: \"$post_subtitle\"" >> "$post_dir/index.qmd"
    echo "shorttitle: \"$short_title\"" >> "$post_dir/index.qmd"
    echo "date: \"$post_date\"" >> "$post_dir/index.qmd"
    echo "date-modified: \"today\"" >> "$post_dir/index.qmd"

    if [[ ${#tags[@]} -gt 0 ]]; then
        echo -n "tags: [" >> "$post_dir/index.qmd"
        local idx tag
        for idx in "${!tags[@]}"; do
            tag=$(echo "${tags[$idx]}" | xargs)
            [[ $idx -eq 0 ]] && echo -n "\"$tag\"" >> "$post_dir/index.qmd" || echo -n ", \"$tag\"" >> "$post_dir/index.qmd"
        done
        echo "]" >> "$post_dir/index.qmd"
    fi

    if [[ ${#categories[@]} -gt 0 ]]; then
        echo -n "categories: [" >> "$post_dir/index.qmd"
        local idx cat
        for idx in "${!categories[@]}"; do
            cat=$(echo "${categories[$idx]}" | xargs)
            [[ $idx -eq 0 ]] && echo -n "\"$cat\"" >> "$post_dir/index.qmd" || echo -n ", \"$cat\"" >> "$post_dir/index.qmd"
        done
        echo "]" >> "$post_dir/index.qmd"
    fi

    echo "image: ../featured.jpg" >> "$post_dir/index.qmd"
    echo "bibliography: $bibliography" >> "$post_dir/index.qmd"
    echo "jupyter: python3" >> "$post_dir/index.qmd"

    [[ "$floatsintext" =~ ^[Ss]$ ]] && echo "floatsintext: true" >> "$post_dir/index.qmd"
    [[ "$numbered_lines" =~ ^[Ss]$ ]] && echo "numbered-lines: true" >> "$post_dir/index.qmd"
    [[ "$no_ampersand" =~ ^[Ss]$ ]] && echo "no-ampersand-parenthetical: true" >> "$post_dir/index.qmd"
    [[ "$mask" =~ ^[Ss]$ ]] && echo "mask: true" >> "$post_dir/index.qmd"
    [[ -n "$nocite" ]] && echo "nocite: \"$nocite\"" >> "$post_dir/index.qmd"
    [[ "$meta_analysis" =~ ^[Ss]$ ]] && echo "meta-analysis: true" >> "$post_dir/index.qmd"
    [[ -n "$impact_statement" ]] && echo "impact-statement: \"$impact_statement\"" >> "$post_dir/index.qmd"

    local element
    for element in "${!suppress_elements[@]}"; do
        [[ "${suppress_elements[$element]}" =~ ^[Ss]$ ]] && echo "suppress-$element: true" >> "$post_dir/index.qmd"
    done

    if [[ "$doc_type" == "jou" ]]; then
        [[ -n "$journal_name" ]] && echo "journal: \"$journal_name\"" >> "$post_dir/index.qmd"
        [[ -n "$volume_info" ]] && echo "volume: \"$volume_info\"" >> "$post_dir/index.qmd"
        [[ -n "$copyright_notice" ]] && echo "copyrightnotice: \"$copyright_notice\"" >> "$post_dir/index.qmd"
        [[ -n "$copyright_text" ]] && echo "copyrightext: \"$copyright_text\"" >> "$post_dir/index.qmd"
    elif [[ "$doc_type" == "stu" ]]; then
        [[ -n "$course_name" ]] && echo "course: \"$course_name\"" >> "$post_dir/index.qmd"
        [[ -n "$professor_name" ]] && echo "professor: \"$professor_name\"" >> "$post_dir/index.qmd"
        [[ -n "$due_date" ]] && echo "duedate: \"$due_date\"" >> "$post_dir/index.qmd"
        [[ -n "$student_note" ]] && echo "note: \"$student_note\"" >> "$post_dir/index.qmd"
    fi

    if [[ ! "$use_default_author" =~ ^[Ss]$ ]]; then
        cat >> "$post_dir/index.qmd" << AUTHOR_EOF

author:
  - name: $author_name
AUTHOR_EOF
        [[ -n "$author_orcid" ]] && echo "    orcid: $author_orcid" >> "$post_dir/index.qmd"
        [[ -n "$author_email" ]] && echo "    email: $author_email" >> "$post_dir/index.qmd"
        [[ "$is_corresponding" =~ ^[Ss]$ ]] && echo "    corresponding: true" >> "$post_dir/index.qmd"
        [[ -n "$author_url" ]] && echo "    url: $author_url" >> "$post_dir/index.qmd"

        if [[ ${#credit_roles[@]} -gt 0 ]]; then
            echo "    role:" >> "$post_dir/index.qmd"
            local role
            for role in "${!credit_roles[@]}"; do
                echo "      - $role: ${credit_roles[$role]}" >> "$post_dir/index.qmd"
            done
        fi

        if [[ -n "$institution_name" ]]; then
            cat >> "$post_dir/index.qmd" << AFF_EOF
    affiliations:
      - id: $affiliation_id
        name: $institution_name
AFF_EOF
            [[ -n "$department" ]] && echo "        department: $department" >> "$post_dir/index.qmd"
            [[ -n "$address" ]] && echo "        address: $address" >> "$post_dir/index.qmd"
            [[ -n "$city" ]] && echo "        city: $city" >> "$post_dir/index.qmd"
            [[ -n "$region" ]] && echo "        region: $region" >> "$post_dir/index.qmd"
            [[ -n "$country" ]] && echo "        country: $country" >> "$post_dir/index.qmd"
            [[ -n "$postal_code" ]] && echo "        postal-code: $postal_code" >> "$post_dir/index.qmd"
        fi
    fi

    cat >> "$post_dir/index.qmd" << NOTE_EOF

author-note:
NOTE_EOF

    if [[ -n "$affiliation_change" ]] || [[ -n "$deceased" ]]; then
        echo "  status-changes:" >> "$post_dir/index.qmd"
        [[ -n "$affiliation_change" ]] && echo "    affiliation-change: \"$affiliation_change\"" >> "$post_dir/index.qmd"
        [[ -n "$deceased" ]] && echo "    deceased: \"$deceased\"" >> "$post_dir/index.qmd"
    fi

    cat >> "$post_dir/index.qmd" << DISC_EOF
  disclosures:
    conflict-of-interest: "$conflict_of_interest"
DISC_EOF

    [[ -n "$financial_support" ]] && echo "    financial-support: \"$financial_support\"" >> "$post_dir/index.qmd"
    [[ -n "$study_registration" ]] && echo "    study-registration: \"$study_registration\"" >> "$post_dir/index.qmd"
    [[ -n "$data_sharing" ]] && echo "    data-sharing: \"$data_sharing\"" >> "$post_dir/index.qmd"
    [[ -n "$related_report" ]] && echo "    related-report: \"$related_report\"" >> "$post_dir/index.qmd"
    [[ -n "$gratitude" ]] && echo "    gratitude: \"$gratitude\"" >> "$post_dir/index.qmd"
    [[ -n "$authorship_agreements" ]] && echo "    authorship-agreements: \"$authorship_agreements\"" >> "$post_dir/index.qmd"

    [[ -n "$abstract" ]] && echo "abstract: \"$abstract\"" >> "$post_dir/index.qmd"

    if [[ ${#keywords[@]} -gt 0 ]]; then
        echo -n "keywords: [" >> "$post_dir/index.qmd"
        local idx kw
        for idx in "${!keywords[@]}"; do
            kw=$(echo "${keywords[$idx]}" | xargs)
            [[ $idx -eq 0 ]] && echo -n "\"$kw\"" >> "$post_dir/index.qmd" || echo -n ", \"$kw\"" >> "$post_dir/index.qmd"
        done
        echo "]" >> "$post_dir/index.qmd"
    fi

    [[ -n "$impact_statement_sec5" ]] && echo "impact-statement: \"$impact_statement_sec5\"" >> "$post_dir/index.qmd"
    [[ "$word_count" =~ ^[Ss]$ ]] && echo "word-count: true" >> "$post_dir/index.qmd"

    echo "lang: $lang" >> "$post_dir/index.qmd"

    if [[ "$lang" != "en" ]]; then
        cat >> "$post_dir/index.qmd" << LANG_EOF
language:
  citation-last-author-separator: "$citation_separator"
  citation-masked-author: "$citation_masked"
  citation-masked-date: "$citation_date"
  title-block-author-note: "$author_note_title"
LANG_EOF
        [[ -n "$correspondence_note" ]] && echo "  title-block-correspondence-note: \"$correspondence_note\"" >> "$post_dir/index.qmd"
        [[ -n "$role_intro" ]] && echo "  title-block-role-introduction: \"$role_intro\"" >> "$post_dir/index.qmd"
        [[ -n "$impact_title" ]] && echo "  title-impact-statement: \"$impact_title\"" >> "$post_dir/index.qmd"
        [[ -n "$word_count_title" ]] && echo "  title-word-count: \"$word_count_title\"" >> "$post_dir/index.qmd"
        [[ -n "$meta_ref" ]] && echo "  references-meta-analysis: \"$meta_ref\"" >> "$post_dir/index.qmd"
    fi

    cat >> "$post_dir/index.qmd" << 'CONTENT_EOF'
---

## Introducción

Escribe aquí la introducción de tu post...

## Desarrollo

### Sección 1

Contenido...

### Sección 2

Contenido...

## Conclusiones

Escribe tus conclusiones aquí...

## Referencias

Las referencias se generarán automáticamente desde references.bib
CONTENT_EOF

    touch "$post_dir/references.bib"

    # --- Resumen final --------------------------------------------------------
    clear
    print_header "✅ Post Creado Exitosamente"

    echo ""
    print_info "Ubicación: $post_dir"
    print_info "Archivo: index.qmd"
    print_info "Tipo: APAQuarto $doc_type"
    print_info "Carpeta: $target_folder"
    echo ""

    echo -e "${QBLOG_CYAN}Resumen de configuración:${QBLOG_NC}"
    echo -e "  ${QBLOG_DIM}• Título: $post_title${QBLOG_NC}"
    [[ -n "$post_subtitle" ]] && echo -e "  ${QBLOG_DIM}• Subtítulo: $post_subtitle${QBLOG_NC}"
    echo -e "  ${QBLOG_DIM}• Tipo de documento: $doc_type${QBLOG_NC}"
    echo -e "  ${QBLOG_DIM}• Tags: ${#tags[@]}${QBLOG_NC}"
    echo -e "  ${QBLOG_DIM}• Categorías: ${#categories[@]}${QBLOG_NC}"
    [[ -n "$author_name" ]] && echo -e "  ${QBLOG_DIM}• Autor: $author_name${QBLOG_NC}"
    echo ""

    read -r -p "¿Deseas abrir el archivo para editar? (s/n): " open_file
    if [[ "$open_file" =~ ^[Ss]$ ]]; then
        "$QBLOG_EDITOR" "$post_dir/index.qmd"
    fi
}

# Genera el archivo _metadata.yml compartido para una carpeta de posts
# (configuración común: autor por defecto, formatos, ejecución, etc.).
# $1 = ruta absoluta de la carpeta de posts
create_metadata_file() {
    local folder_path="$1"
    local metadata_file="$folder_path/_metadata.yml"

    print_info "Creando _metadata.yml..."

    cat > "$metadata_file" << EOF
# =============================================================================
# CONFIGURACIÓN GENERAL DEL DOCUMENTO
# =============================================================================

# Metadatos del Documento
date-modified: "today"
license: "CC BY-SA"
lang: es
search: true
lightbox: true

# Configuración del Bloque de Título
title-block-banner: true
is-particlejs-enabled: true

# =============================================================================
# INFORMACIÓN DEL AUTOR
# =============================================================================

author:
  - name: $QBLOG_DEFAULT_AUTHOR
    url: $QBLOG_DEFAULT_AUTHOR_URL
    affiliation:
      - id: $QBLOG_DEFAULT_AFFILIATION_ID
        name: $QBLOG_DEFAULT_INSTITUTION
        department: $QBLOG_DEFAULT_DEPARTMENT
        city: $QBLOG_DEFAULT_CITY
        region: $QBLOG_DEFAULT_REGION
        country: $QBLOG_DEFAULT_COUNTRY
    affiliation-url: https://www.gob.pe/unsch
    orcid: $QBLOG_DEFAULT_AUTHOR_ORCID
    email: $QBLOG_DEFAULT_AUTHOR_EMAIL
    attributes:
      corresponding: true
      equal-contributor: true
      deceased: false
    roles:
      - conceptualización
      - redacción

# Nota del Autor
author-note:
  disclosures:
    conflict-of-interest: Los autores no tienen conflictos de intereses que revelar.

# =============================================================================
# CONFIGURACIÓN DE TABLA DE CONTENIDOS
# =============================================================================

toc: true
toc-title: " "
toc-location: left

# =============================================================================
# CONFIGURACIÓN DE REFERENCIAS Y CITAS
# =============================================================================

floatsintext: true
citation: true
google-scholar: true
link-citations: true
appendix-cite-as: display
citation-last-author-separator: "y"
citation-masked-author: "Cita Enmascarada"
citation-masked-title: "Título Enmascarado"
citation-masked-date: "n.f."

# Bloques de Títulos
title-block-author-note: "Nota de Autores"
title-block-correspondence-note: "La correspondencia relativa a este artículo debe dirigirse a"
title-block-role-introduction: "Los roles de autor se clasificaron utilizando la taxonomía de roles de colaborador (CRediT; https://credit.niso.org/) de la siguiente manera:"
references-meta-analysis: "Las referencias marcadas con un asterisco indican estudios incluidos en el metanálisis."

# =============================================================================
# CONFIGURACIÓN DE REFERENCIAS CRUZADAS
# =============================================================================

language:
  crossref-fig-title: Figura
  crossref-tbl-title: Tabla
  crossref-lst-title: "Listing"
  crossref-thm-title: "Teorema"
  crossref-lem-title: "Lema"
  crossref-cor-title: "Corolario"
  crossref-prp-title: "Proposición"
  crossref-cnj-title: "Conjetura"
  crossref-def-title: "Definición"
  crossref-exm-title: "Ejemplo"
  crossref-exr-title: "Ejercicio"
  crossref-ch-prefix: "Capítulo"
  crossref-apx-prefix: Anexo
  crossref-sec-prefix: "Sección"
  crossref-eq-prefix: Ecuación
  crossref-lof-title: "Lista de Figuras"
  crossref-lot-title: "Lista de Tablas"
  crossref-lol-title: "Lista de Listings"

# =============================================================================
# CONFIGURACIÓN DE VISIBILIDAD Y BORRADOR
# =============================================================================

mask: false
draft: true
draftfirst: false
draftall: false

# =============================================================================
# FORMATOS DE SALIDA
# =============================================================================

format:
  # ---------------------------------------------------------------------------
  # Formato HTML
  # ---------------------------------------------------------------------------
  html:
    toc-depth: 1
    toc-expand: 3
    smooth-scroll: true
    link-external-newwindow: true
    citations-hover: true
    footnotes-hover: true
    highlight-style: github
    code-copy: true
    code-fold: true
    code-summary: "Mostrar el código"
    code-overflow: scroll
    code-line-numbers: true
    code-tools:
      source: repo
      toggle: false
      caption: none
    mermaid:
      theme: neutral
    citation-location: document
    self-contained: true
    template-partials:
      - ../_partials/title-block-link-buttons/title-block.html
    theme: litera
    other-links:
      - text: Gravatar
        href: https://gravatar.com/achalmaedison
    format-links: true

  # ---------------------------------------------------------------------------
  # Formato PDF (APA Quarto)
  # ---------------------------------------------------------------------------
  apaquarto-pdf:
    documentmode: jou
    copyrightnotice: 2025
    copyrightext: Todos los derechos reservados
    toc: true
    list-of-figures: true
    list-of-tables: true
    keep-tex: true
    fontsize: 12pt
    a4paper: true
    numbered-lines: false
    number-sections: true
    colorlinks: true
    pdf-engine: xelatex
    keep-md: false

  # ---------------------------------------------------------------------------
  # Formato DOCX (APA Quarto)
  # ---------------------------------------------------------------------------
  apaquarto-docx:
    toc: true
    fontsize: 12pt
    a4paper: true
    numbered-lines: false
    number-sections: true
    keep-md: false

# =============================================================================
# CONFIGURACIÓN DEL ENTORNO DE EJECUCIÓN
# =============================================================================

jupyter: python3

# Editor
editor:
  # Modo preferido (source o visual)
  mode: source

  # Configuración de Markdown
  markdown:
    canonical: true      # Formato consistente. Usar formato Markdown canónico (mejor para control de versiones)
    wrap: 72            # 72 caracteres por línea
    references:
      location: section # Notas al pie por sección

    # Opciones de escritura
    auto-wrapping: true
    sentence-spacing: true

# =============================================================================
# CONFIGURACIÓN DE COMENTARIOS
# =============================================================================

comments:
  utterances:
    repo: achalmed/website-achalma
    issue-term: title
    theme: boxy-light
    label: "comments :crystal_ball:"

# =============================================================================
# CONFIGURACIÓN DE EJECUCIÓN
# =============================================================================

execute:
  freeze: true  # true: Nunca re-ejecutar durante el renderizado del proyecto. auto: Re-ejecutar solo cuando cambia el código fuente (funciona solo si .qmd que tienen Python/R)
  keep-md: true  # Mantener archivos .md generados
  keep-ipynb: true
  echo: true  # Mostrar comandos ejecutados
  output: true  # Mostrar resultados de la ejecución
  warning: false  # Ocultar advertencias
  error: false  # Ocultar errores
  enabled: false  # Deshabilita la ejecución de código por defecto. Habilitar la ejecución: quarto render notebook.ipynb --execute
  cache: true  # PARA RESULTADOS DE CALCULO: quarto render index.qmd --cache-refresh #singledoc quarto render --cache-refresh #entireproject
EOF

    print_success "Creado $metadata_file"
}
