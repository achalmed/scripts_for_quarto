#!/bin/bash

################################################################################
# config.sh - Archivo de configuración para scripts de Quarto
# Fuente: source config.sh
################################################################################

# Directorios principales
export PUBLICACIONES_DIR="/home/achalmaedison/Documents/publicaciones"
export SCRIPTS_DIR="/home/achalmaedison/Documents/scripts/scripts_for_quarto"
export BACKUP_DIR="/home/achalmaedison/Documents/backups/publicaciones"

# Configuración de Git
export GIT_USER_NAME="Edison Achalma"
export GIT_USER_EMAIL="achalmaedison@gmail.com"

# Configuración de publicación
export DEFAULT_PUBLISH_TARGET="gh-pages"
export DEFAULT_PREVIEW_PORT=4200

# Configuración de editor
export EDITOR=${EDITOR:-"nano"}

# Configuración de plantillas
export DEFAULT_AUTHOR="Edison Achalma"
export DEFAULT_CATEGORIES='["tutorial"]'

# Blogs principales (para operaciones rápidas)
export BLOG_WEBSITE="website-achalma"
export BLOG_ECONOMIA="epsilon-y-beta"
export BLOG_PROGRAMACION="numerus-scriptum"
export BLOG_FILOSOFIA="dialectica-y-mercado"
export BLOG_LINUX="chaska"

# Funciones de ayuda
quick_preview() {
    local blog_var="BLOG_${1^^}"
    local blog_name="${!blog_var}"
    
    if [ -z "$blog_name" ]; then
        echo "Blog no encontrado. Opciones: website, economia, programacion, filosofia, linux"
        return 1
    fi
    
    $SCRIPTS_DIR/build.sh preview "$blog_name"
}

quick_render() {
    local blog_var="BLOG_${1^^}"
    local blog_name="${!blog_var}"
    
    if [ -z "$blog_name" ]; then
        echo "Blog no encontrado. Opciones: website, economia, programacion, filosofia, linux"
        return 1
    fi
    
    $SCRIPTS_DIR/build.sh render "$blog_name"
}

# Aliases útiles
alias qlist="$SCRIPTS_DIR/build.sh list"
alias qcheck="$SCRIPTS_DIR/check-structure.sh"
alias qbackup="$SCRIPTS_DIR/backup-blogs.sh"
alias qbuild="$SCRIPTS_DIR/build.sh"

echo "✓ Configuración de Quarto cargada"
echo "  Directorios:"
echo "    - Publicaciones: $PUBLICACIONES_DIR"
echo "    - Scripts: $SCRIPTS_DIR"
echo "    - Backups: $BACKUP_DIR"
echo ""
echo "  Comandos disponibles:"
echo "    - qlist: Listar blogs"
echo "    - qcheck: Verificar estructura"
echo "    - qbackup: Crear backup"
echo "    - qbuild: Script principal"
echo "    - quick_preview [blog]: Preview rápido"
echo "    - quick_render [blog]: Render rápido"
