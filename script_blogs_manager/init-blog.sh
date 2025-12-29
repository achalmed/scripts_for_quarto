#!/bin/bash

################################################################################
# init-blog.sh - Script para inicializar un nuevo blog de Quarto
# Uso: ./init-blog.sh nombre-del-blog "Título del Blog"
################################################################################

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PUBLICACIONES_DIR="/home/achalmaedison/Documents/publicaciones"

if [ -z "$1" ]; then
    echo -e "${YELLOW}Uso: $0 nombre-del-blog \"Título del Blog\"${NC}"
    exit 1
fi

BLOG_NAME="$1"
BLOG_TITLE="${2:-$BLOG_NAME}"
BLOG_PATH="$PUBLICACIONES_DIR/$BLOG_NAME"

if [ -d "$BLOG_PATH" ]; then
    echo -e "${YELLOW}⚠ El blog '$BLOG_NAME' ya existe${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Creando nuevo blog: $BLOG_NAME${NC}"

# Crear estructura de directorios
mkdir -p "$BLOG_PATH"/{posts,assets/{img,fonts},_extensions,_partials}

# Crear _quarto.yml
cat > "$BLOG_PATH/_quarto.yml" << EOF
project:
  type: website
  output-dir: _site

website:
  title: "$BLOG_TITLE"
  description: ""
  navbar:
    left:
      - href: index.qmd
        text: Inicio
      - href: about.qmd
        text: Acerca de
  page-footer:
    left: "© $(date +%Y) Edison Achalma"
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

# Crear index.qmd
cat > "$BLOG_PATH/index.qmd" << EOF
---
title: "$BLOG_TITLE"
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

# Crear about.qmd
cat > "$BLOG_PATH/about.qmd" << EOF
---
title: "Acerca de"
---

## Sobre este blog

Información sobre el blog y el autor...

### Autor

**Edison Achalma**  
Economista | Data Scientist

- 🌐 [achalmaedison.com](https://achalmaedison.com)
- 📧 achalmaedison@gmail.com
- 🐦 [@achalmaedison](https://twitter.com/achalmaedison)
EOF

# Crear styles.css básico
cat > "$BLOG_PATH/styles.css" << EOF
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

# Crear .gitignore
cat > "$BLOG_PATH/.gitignore" << EOF
/.quarto/
/_site/
/_freeze/
/.Rproj.user/
.Rhistory
.RData
.DS_Store
EOF

# Crear README
cat > "$BLOG_PATH/README.md" << EOF
# $BLOG_TITLE

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

Edison Achalma
EOF

echo -e "${GREEN}✓ Blog creado exitosamente en: $BLOG_PATH${NC}"
echo ""
echo "Próximos pasos:"
echo "  1. cd $BLOG_PATH"
echo "  2. Editar index.qmd y about.qmd"
echo "  3. quarto preview"
echo "  4. Crear tu primer post con: build.sh new-post $BLOG_NAME \"Título del Post\""
