#!/bin/bash

################################################################################
# check-structure.sh - Verificar y reportar estructura de blogs
# Verifica que todos los blogs tengan la estructura correcta
################################################################################

set -e

PUBLICACIONES_DIR="/home/achalmaedison/Documents/publicaciones"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

check_blog() {
    local blog_path="$1"
    local blog_name=$(basename "$blog_path")
    local issues=0
    
    echo ""
    echo -e "${BLUE}📁 $blog_name${NC}"
    
    # Verificar archivos esenciales
    if [ -f "$blog_path/_quarto.yml" ]; then
        print_success "_quarto.yml existe"
    else
        print_error "_quarto.yml NO encontrado"
        ((issues++))
    fi
    
    if [ -f "$blog_path/index.qmd" ]; then
        print_success "index.qmd existe"
    else
        print_error "index.qmd NO encontrado"
        ((issues++))
    fi
    
    # Verificar directorios comunes
    if [ -d "$blog_path/posts" ]; then
        local post_count=$(find "$blog_path/posts" -name "index.qmd" | wc -l)
        print_success "Directorio posts/ existe ($post_count posts encontrados)"
    else
        print_warning "Directorio posts/ no existe"
    fi
    
    if [ -d "$blog_path/assets" ]; then
        print_success "Directorio assets/ existe"
    else
        print_warning "Directorio assets/ no existe"
    fi
    
    # Verificar .gitignore
    if [ -f "$blog_path/.gitignore" ]; then
        print_success ".gitignore existe"
    else
        print_warning ".gitignore no existe"
    fi
    
    # Verificar si es repositorio Git
    if [ -d "$blog_path/.git" ]; then
        print_success "Es un repositorio Git"
        
        # Verificar remote
        cd "$blog_path"
        if git remote -v | grep -q "origin"; then
            local remote=$(git remote get-url origin)
            print_success "Remote configurado: $remote"
        else
            print_warning "No hay remote configurado"
        fi
    else
        print_warning "No es un repositorio Git"
    fi
    
    # Verificar archivos generados
    if [ -d "$blog_path/_site" ]; then
        local size=$(du -sh "$blog_path/_site" | cut -f1)
        print_info "Sitio generado existe ($size)"
    fi
    
    # Verificar sintaxis YAML (requiere yq o python-yaml)
    if command -v yq &> /dev/null; then
        if yq eval "$blog_path/_quarto.yml" > /dev/null 2>&1; then
            print_success "YAML válido"
        else
            print_error "YAML tiene errores de sintaxis"
            ((issues++))
        fi
    fi
    
    # Resumen
    if [ $issues -eq 0 ]; then
        echo -e "  ${GREEN}Estado: OK${NC}"
    elif [ $issues -le 2 ]; then
        echo -e "  ${YELLOW}Estado: Revisar${NC}"
    else
        echo -e "  ${RED}Estado: Requiere atención${NC}"
    fi
    
    return $issues
}

# Main
print_header "Verificación de Estructura de Blogs"

total_blogs=0
total_issues=0
blogs_ok=0
blogs_warning=0
blogs_error=0

for blog in "$PUBLICACIONES_DIR"/*/; do
    if [ -f "$blog/index.qmd" ] || [ -f "$blog/_quarto.yml" ]; then
        check_blog "$blog"
        issues=$?
        
        total_blogs=$((total_blogs + 1))
        total_issues=$((total_issues + issues))
        
        if [ $issues -eq 0 ]; then
            blogs_ok=$((blogs_ok + 1))
        elif [ $issues -le 2 ]; then
            blogs_warning=$((blogs_warning + 1))
        else
            blogs_error=$((blogs_error + 1))
        fi
    fi
done

# Resumen final
echo ""
print_header "Resumen General"
echo ""
echo -e "Total de blogs: ${CYAN}$total_blogs${NC}"
echo -e "${GREEN}✓ OK:${NC} $blogs_ok"
echo -e "${YELLOW}⚠ Revisar:${NC} $blogs_warning"
echo -e "${RED}✗ Problemas:${NC} $blogs_error"
echo ""
echo -e "Total de issues encontrados: $total_issues"
echo ""

# Recomendaciones
if [ $blogs_warning -gt 0 ] || [ $blogs_error -gt 0 ]; then
    echo -e "${YELLOW}Recomendaciones:${NC}"
    echo "  • Para crear archivos faltantes, usa: init-blog.sh"
    echo "  • Para inicializar Git: build.sh git-init BLOG"
    echo "  • Para verificar sintaxis: build.sh check BLOG"
fi
