#!/bin/bash
# ============================================================================
# Script de Instalación - Sistema de Gestión de Metadatos Quarto
# Autor: Edison Achalma
# Fecha: Diciembre 2024
# ============================================================================

set -e  # Salir si hay error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   INSTALACIÓN DE METADATA MANAGER         ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verificar Python
echo -e "${YELLOW}[1/4] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
    echo -e "${YELLOW}Por favor instale Python 3.6 o superior${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION encontrado${NC}"

# Verificar pip
echo ""
echo -e "${YELLOW}[2/4] Verificando pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ Error: pip no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip encontrado${NC}"

# Instalar dependencias
echo ""
echo -e "${YELLOW}[3/4] Instalando dependencias...${NC}"
echo -e "${BLUE}Instalando: pandas, openpyxl, pyyaml${NC}"

pip3 install pandas openpyxl pyyaml --break-system-packages --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}❌ Error instalando dependencias${NC}"
    exit 1
fi

# Dar permisos de ejecución
echo ""
echo -e "${YELLOW}[4/4] Configurando permisos...${NC}"
chmod +x quarto_metadata_manager.py quick_start.sh 2>/dev/null || true
echo -e "${GREEN}✅ Permisos configurados${NC}"

# Verificar instalación
echo ""
echo -e "${YELLOW}Verificando instalación...${NC}"
if python3 -c "import pandas, openpyxl, yaml" 2>/dev/null; then
    echo -e "${GREEN}✅ Todas las librerías funcionan correctamente${NC}"
else
    echo -e "${RED}❌ Error: Algunas librerías no se instalaron correctamente${NC}"
    exit 1
fi

# Resumen
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   ✅ INSTALACIÓN COMPLETADA               ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo ""
echo "1. Crear plantilla Excel:"
echo -e "   ${YELLOW}python3 quarto_metadata_manager.py create-template /ruta/publicaciones${NC}"
echo ""
echo "2. O usar el inicio rápido interactivo:"
echo -e "   ${YELLOW}./quick_start.sh${NC}"
echo ""
echo "3. Para ayuda detallada:"
echo -e "   ${YELLOW}python3 quarto_metadata_manager.py --help${NC}"
echo ""
echo -e "${BLUE}Documentación:${NC}"
echo "   • README_METADATA_MANAGER.md - Guía completa"
echo "   • EJEMPLOS_CONFIGURACION.md - Ejemplos prácticos"
echo "   • CHANGELOG.md - Historial de versiones"
echo ""
echo -e "${GREEN}¡Listo para usar! 🚀${NC}"
