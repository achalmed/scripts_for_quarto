#!/bin/bash
# ============================================================================
# Script de Ejemplo de Uso - Sistema de Gestión de Metadatos Quarto
# Autor: Edison Achalma
# Fecha: Diciembre 2024
# ============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    echo -e "${2}${1}${NC}"
}

# Función para imprimir cabecera
print_header() {
    echo ""
    print_color "============================================" "$BLUE"
    print_color "$1" "$BLUE"
    print_color "============================================" "$BLUE"
    echo ""
}

# Verificar que el script de gestión existe
if [ ! -f "quarto_metadata_manager.py" ]; then
    print_color "❌ Error: No se encuentra quarto_metadata_manager.py" "$RED"
    print_color "Asegúrate de estar en el directorio correcto" "$YELLOW"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_color "❌ Error: Python 3 no está instalado" "$RED"
    exit 1
fi

print_header "SISTEMA DE GESTIÓN DE METADATOS PARA BLOGS QUARTO"

print_color "Autor: Edison Achalma" "$GREEN"
print_color "Versión: 1.0.0" "$GREEN"
echo ""

# Menú principal
print_color "Seleccione una opción:" "$YELLOW"
echo "1) Crear plantilla Excel para TODOS los blogs"
echo "2) Crear plantilla Excel para UN blog específico"
echo "3) Actualizar metadatos desde Excel (SIMULACIÓN)"
echo "4) Actualizar metadatos desde Excel (REAL)"
echo "5) Actualizar UN blog específico"
echo "6) Mostrar ayuda"
echo "0) Salir"
echo ""

read -p "Opción: " option

case $option in
    1)
        print_header "CREAR PLANTILLA PARA TODOS LOS BLOGS"
        read -p "Ruta base de publicaciones (ej: ~/Documents/publicaciones): " base_path
        read -p "Nombre del archivo Excel (default: quarto_metadata.xlsx): " output_file
        output_file=${output_file:-quarto_metadata.xlsx}
        
        print_color "🔍 Recolectando archivos index.qmd..." "$BLUE"
        python3 quarto_metadata_manager.py create-template "$base_path" -o "$output_file"
        
        if [ $? -eq 0 ]; then
            print_color "✅ Plantilla creada exitosamente: $output_file" "$GREEN"
            print_color "💡 Próximo paso: Editar el Excel y ejecutar opción 3 (simulación)" "$YELLOW"
        else
            print_color "❌ Error creando plantilla" "$RED"
        fi
        ;;
        
    2)
        print_header "CREAR PLANTILLA PARA UN BLOG ESPECÍFICO"
        read -p "Ruta base de publicaciones: " base_path
        read -p "Nombre del blog (ej: axiomata): " blog_name
        output_file="quarto_metadata_${blog_name}.xlsx"
        
        print_color "🔍 Recolectando archivos del blog '$blog_name'..." "$BLUE"
        python3 quarto_metadata_manager.py create-template "$base_path" --blog "$blog_name" -o "$output_file"
        
        if [ $? -eq 0 ]; then
            print_color "✅ Plantilla creada: $output_file" "$GREEN"
        else
            print_color "❌ Error creando plantilla" "$RED"
        fi
        ;;
        
    3)
        print_header "ACTUALIZAR METADATOS (SIMULACIÓN - DRY RUN)"
        read -p "Ruta base de publicaciones: " base_path
        read -p "Archivo Excel: " excel_file
        
        if [ ! -f "$excel_file" ]; then
            print_color "❌ Error: Archivo Excel no encontrado: $excel_file" "$RED"
            exit 1
        fi
        
        print_color "🔍 Simulando actualización..." "$BLUE"
        print_color "⚠️  ESTO NO APLICARÁ CAMBIOS REALES" "$YELLOW"
        python3 quarto_metadata_manager.py update "$base_path" "$excel_file" --dry-run
        
        echo ""
        print_color "💡 Si los cambios se ven bien, ejecute la opción 4" "$YELLOW"
        ;;
        
    4)
        print_header "ACTUALIZAR METADATOS (APLICAR CAMBIOS REALES)"
        read -p "Ruta base de publicaciones: " base_path
        read -p "Archivo Excel: " excel_file
        
        if [ ! -f "$excel_file" ]; then
            print_color "❌ Error: Archivo Excel no encontrado: $excel_file" "$RED"
            exit 1
        fi
        
        print_color "⚠️  ¡ATENCIÓN! Esto aplicará cambios reales" "$RED"
        read -p "¿Continuar? (s/N): " confirm
        
        if [[ $confirm =~ ^[Ss]$ ]]; then
            print_color "📝 Aplicando cambios..." "$BLUE"
            python3 quarto_metadata_manager.py update "$base_path" "$excel_file"
            
            if [ $? -eq 0 ]; then
                print_color "✅ Actualización completada" "$GREEN"
            else
                print_color "❌ Error durante actualización" "$RED"
            fi
        else
            print_color "❌ Operación cancelada" "$YELLOW"
        fi
        ;;
        
    5)
        print_header "ACTUALIZAR UN BLOG ESPECÍFICO"
        read -p "Ruta base de publicaciones: " base_path
        read -p "Archivo Excel: " excel_file
        read -p "Nombre del blog: " blog_name
        read -p "¿Simulación primero? (S/n): " sim
        
        if [[ $sim =~ ^[Nn]$ ]]; then
            print_color "⚠️  Aplicando cambios REALES al blog '$blog_name'" "$RED"
            python3 quarto_metadata_manager.py update "$base_path" "$excel_file" --blog "$blog_name"
        else
            print_color "🔍 Simulando cambios para '$blog_name'" "$BLUE"
            python3 quarto_metadata_manager.py update "$base_path" "$excel_file" --blog "$blog_name" --dry-run
        fi
        ;;
        
    6)
        print_header "AYUDA"
        python3 quarto_metadata_manager.py --help
        echo ""
        print_color "📖 Para más información, consulte: README_METADATA_MANAGER.md" "$GREEN"
        ;;
        
    0)
        print_color "👋 ¡Hasta luego!" "$GREEN"
        exit 0
        ;;
        
    *)
        print_color "❌ Opción inválida" "$RED"
        exit 1
        ;;
esac

echo ""
print_color "✅ Operación completada" "$GREEN"
