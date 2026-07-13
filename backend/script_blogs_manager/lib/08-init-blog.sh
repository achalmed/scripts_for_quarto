#!/usr/bin/env bash
# =============================================================================
# 08-init-blog.sh
# -----------------------------------------------------------------------------
# Inicializa un nuevo blog Quarto con la estructura completa: _quarto.yml,
# index.qmd, about.qmd, styles.css, .gitignore y README.md. Equivalente al
# antiguo init-blog.sh, adaptado para crear el proyecto directamente dentro
# de Documents con el prefijo pub_ (en vez de dentro de una carpeta
# "publicaciones/" separada).
# =============================================================================

if [[ -n "${QBLOG_INIT_BLOG_LOADED:-}" ]]; then
    return 0
fi
QBLOG_INIT_BLOG_LOADED=1

# Crea un nuevo blog con estructura completa.
# $1 = ruta absoluta de Documents
# $2 = nombre del blog SIN el prefijo pub_ (ej: "mi-nuevo-blog" crea
#      "pub_mi-nuevo-blog"). Si ya viene con el prefijo, se respeta tal cual.
# $3 = título del blog (opcional, default = nombre)
init_blog() {
    local docs_dir="$1"
    local raw_name="$2"
    local blog_title="${3:-$raw_name}"

    if [[ -z "$raw_name" ]]; then
        print_warning "Uso: init-blog NOMBRE \"Título del Blog\""
        return 1
    fi

    local blog_name="$raw_name"
    if [[ "$blog_name" != "${QBLOG_PROJECT_PREFIX}"* ]] && [[ "$blog_name" != "$QBLOG_WEBSITE_PROJECT" ]]; then
        blog_name="${QBLOG_PROJECT_PREFIX}${raw_name}"
    fi

    local blog_path="$docs_dir/$blog_name"

    if [[ -d "$blog_path" ]]; then
        print_warning "El blog '$blog_name' ya existe"
        return 1
    fi

    print_header "$QBLOG_E_ROCKET Creando nuevo blog: $blog_name"

    mkdir -p "$blog_path"/{posts,assets/{img,fonts},_extensions,_partials}

    cat > "$blog_path/_quarto.yml" << EOF
project:
  type: website
  output-dir: _site

website:
  title: "$blog_title"
  description: ""
  navbar:
    left:
      - href: index.qmd
        text: Inicio
      - href: about.qmd
        text: Acerca de
  page-footer:
    left: "© $(date +%Y) $QBLOG_DEFAULT_AUTHOR"
    right:
      - icon: github
        href: https://github.com/achalmed
      - icon: twitter
        href: https://twitter.com/achalmaedison

format:
  html:
    theme: cosmo
    css: styles.css
    toc: true
    toc-depth: 3
    smooth-scroll: true
    link-external-newwindow: true

execute:
  freeze: auto
EOF

    cat > "$blog_path/index.qmd" << EOF
---
title: "$blog_title"
listing:
  contents: posts
  sort: "date desc"
  type: default
  categories: true
  sort-ui: false
  filter-ui: false
page-layout: full
title-block-banner: true
---

## Bienvenido

Descripción de tu blog...
EOF

    cat > "$blog_path/about.qmd" << EOF
---
title: "Acerca de"
---

## Sobre este blog

Información sobre el blog y el autor...

### Autor

**$QBLOG_DEFAULT_AUTHOR**
Economista | Data Scientist

- 🌐 [achalmaedison.com]($QBLOG_DEFAULT_AUTHOR_URL)
- 📧 $QBLOG_DEFAULT_AUTHOR_EMAIL
- 🐦 [@achalmaedison](https://twitter.com/achalmaedison)
EOF

    cat > "$blog_path/styles.css" << 'EOF'
/* Estilos personalizados */

:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
}

.quarto-title-banner {
    background-color: var(--primary-color);
}

h1, h2, h3 {
    color: var(--primary-color);
}

a {
    color: var(--secondary-color);
}
EOF

    cat > "$blog_path/.gitignore" << 'EOF'
/.quarto/
/_site/
/_freeze/
/.Rproj.user/
.Rhistory
.RData
.DS_Store
EOF

    cat > "$blog_path/README.md" << EOF
# $blog_title

Blog personal sobre [tema]

## Desarrollo

\`\`\`bash
# Preview local
quarto preview

# Renderizar
quarto render

# Publicar
quarto publish gh-pages
\`\`\`

## Autor

$QBLOG_DEFAULT_AUTHOR
EOF

    print_success "Blog creado exitosamente en: $blog_path"
    echo ""
    echo "Próximos pasos:"
    echo "  1. cd $blog_path"
    echo "  2. Editar index.qmd y about.qmd"
    echo "  3. quarto preview"
    echo "  4. Crear tu primer post con: main.sh new-post $blog_name \"Título del Post\""
}
