#!/bin/bash

################################################################################
# Script de Instalación - Sistema de Gestión de Metadatos Quarto
# Versión: 1.2.0
# Autor: Edison Achalma
# Fecha: Diciembre 2024
################################################################################

set -e  # Salir si hay errores

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

# Banner
clear
print_header "🚀 INSTALADOR - SISTEMA DE GESTIÓN DE METADATOS QUARTO v1.2"
echo ""
echo -e "${CYAN}Autor:${NC} Edison Achalma"
echo -e "${CYAN}Email:${NC} achalmaedison@gmail.com"
echo -e "${CYAN}Ubicación:${NC} Ayacucho, Perú"
echo ""
print_header "📋 VERIFICACIÓN DE REQUISITOS"

################################################################################
# VERIFICAR PYTHON
################################################################################

print_step "Verificando Python..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python encontrado: $PYTHON_VERSION"
    
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Versión compatible (>= 3.8)"
    else
        print_error "Python 3.8+ requerido. Tienes: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 no encontrado"
    print_info "Instala Python 3.8+:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

################################################################################
# DETECTAR GESTOR DE PAQUETES
################################################################################

print_step "Detectando gestor de paquetes..."

CONDA_AVAILABLE=false
PIP_AVAILABLE=false

if command -v conda &> /dev/null; then
    CONDA_VERSION=$(conda --version | cut -d' ' -f2)
    print_success "Conda encontrado: $CONDA_VERSION"
    CONDA_AVAILABLE=true
fi

if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    PIP_CMD=$(command -v pip3 || command -v pip)
    PIP_VERSION=$($PIP_CMD --version | cut -d' ' -f2)
    print_success "pip encontrado: $PIP_VERSION"
    PIP_AVAILABLE=true
fi

if [ "$CONDA_AVAILABLE" = false ] && [ "$PIP_AVAILABLE" = false ]; then
    print_error "No se encontró conda ni pip"
    exit 1
fi

################################################################################
# SELECCIONAR MÉTODO
################################################################################

print_header "📦 MÉTODO DE INSTALACIÓN"
echo ""

OPTION_NUM=1

if [ "$CONDA_AVAILABLE" = true ]; then
    echo -e "${GREEN}${OPTION_NUM})${NC} Instalar con Conda (Recomendado)"
    echo -e "   ✅ Entorno aislado"
    echo -e "   ✅ Fácil de gestionar"
    echo ""
    CONDA_OPTION=$OPTION_NUM
    OPTION_NUM=$((OPTION_NUM + 1))
fi

if [ "$PIP_AVAILABLE" = true ]; then
    echo -e "${YELLOW}${OPTION_NUM})${NC} Instalar con pip"
    echo -e "   ⚠️  Sistema global"
    echo ""
    PIP_OPTION=$OPTION_NUM
    OPTION_NUM=$((OPTION_NUM + 1))
fi

echo -e "${BLUE}${OPTION_NUM})${NC} Salir"
echo ""

read -p "Selecciona: " INSTALL_METHOD

################################################################################
# INSTALAR
################################################################################

if [ "$CONDA_AVAILABLE" = true ] && [ "$INSTALL_METHOD" = "$CONDA_OPTION" ]; then
    print_header "🐍 INSTALACIÓN CON CONDA"
    
    if conda env list | grep -q "metadata_manager"; then
        print_warning "Entorno 'metadata_manager' existe"
        read -p "¿Recrear? (s/N): " RECREATE
        
        if [ "$RECREATE" = "s" ] || [ "$RECREATE" = "S" ]; then
            print_step "Eliminando entorno..."
            conda env remove -n metadata_manager -y
            print_success "Eliminado"
        fi
    fi
    
    if ! conda env list | grep -q "metadata_manager"; then
        print_step "Creando entorno..."
        conda create -n metadata_manager python=3.9 -y
        print_success "Entorno creado"
    fi
    
    print_step "Instalando dependencias..."
    eval "$(conda shell.bash hook)"
    conda activate metadata_manager
    conda install pandas openpyxl pyyaml -y
    
    print_success "Dependencias instaladas"
    
    python -c "import pandas, openpyxl, yaml; print('OK')" && \
        print_success "Verificación exitosa"
    
    INSTALL_SUCCESS=true
    USING_CONDA=true

elif [ "$PIP_AVAILABLE" = true ] && [ "$INSTALL_METHOD" = "$PIP_OPTION" ]; then
    print_header "📦 INSTALACIÓN CON PIP"
    
    print_step "Instalando dependencias..."
    
    if $PIP_CMD install pandas openpyxl pyyaml 2>/dev/null; then
        print_success "Instalado"
    else
        print_warning "Usando --break-system-packages..."
        $PIP_CMD install pandas openpyxl pyyaml --break-system-packages
        print_success "Instalado"
    fi
    
    python3 -c "import pandas, openpyxl, yaml; print('OK')" && \
        print_success "Verificación exitosa"
    
    INSTALL_SUCCESS=true
    USING_CONDA=false

else
    print_info "Instalación cancelada"
    exit 0
fi

################################################################################
# CONFIGURAR
################################################################################

print_header "🔐 PERMISOS"

print_step "Configurando permisos..."

[ -f "quarto_metadata_manager.py" ] && chmod +x quarto_metadata_manager.py && print_success "Script principal"
[ -f "quick_start.sh" ] && chmod +x quick_start.sh && print_success "Quick start"

print_header "📁 DIRECTORIOS"

mkdir -p excel_databases
print_success "Directorio 'excel_databases' creado"

print_header "⚙️  CONFIGURACIÓN"

if [ ! -f "metadata_config.yml" ]; then
    print_warning "No existe metadata_config.yml"
    read -p "¿Crear archivo de configuración? (S/n): " CREATE_CONFIG
    
    if [ "$CREATE_CONFIG" != "n" ] && [ "$CREATE_CONFIG" != "N" ]; then
        read -p "Ruta de publicaciones (ej: ~/Documents/publicaciones): " BASE_PATH
        
        if [ -n "$BASE_PATH" ]; then
            print_step "Creando configuración..."
            
            if [ "$USING_CONDA" = true ]; then
                conda activate metadata_manager
            fi
            
            python3 quarto_metadata_manager.py create-config "$BASE_PATH"
            print_success "metadata_config.yml creado"
        fi
    fi
else
    print_success "metadata_config.yml encontrado"
fi

################################################################################
# RESUMEN
################################################################################

print_header "🎉 INSTALACIÓN COMPLETADA"
echo ""
print_success "Sistema listo para usar"
echo ""

if [ "$USING_CONDA" = true ]; then
    print_info "ACTIVAR ENTORNO ANTES DE USAR:"
    echo ""
    echo -e "  ${GREEN}conda activate metadata_manager${NC}"
    echo ""
fi

print_header "📚 PRÓXIMOS PASOS"
echo ""
echo "1️⃣  Editar configuración:"
echo "   nano metadata_config.yml"
echo ""
echo "2️⃣  Crear base de datos:"
if [ "$USING_CONDA" = true ]; then
    echo "   conda activate metadata_manager"
fi
echo "   python quarto_metadata_manager.py create-template ~/Documents/publicaciones \\"
echo "       --config metadata_config.yml"
echo ""
echo "3️⃣  Usar interfaz rápida:"
echo "   ./quick_start.sh"
echo ""

print_header "📖 AYUDA"
echo ""
echo "README:   cat README.md"
echo "Soporte:  achalmaedison@gmail.com"
echo ""
print_success "¡Instalación exitosa!"
echo ""