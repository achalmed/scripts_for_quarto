#!/bin/bash

################################################################################
# Script: Generador de Índices de Contenido para Blogs Quarto
# Autor: Edison Achalma
# Descripción: Genera automáticamente archivos de índice (.qmd) con enlaces
#              a publicaciones organizadas por fecha en blogs de Quarto
# Versión: 2.0
# Última actualización: 2025-01-19
################################################################################

#===============================================================================
# CONFIGURACIÓN PRINCIPAL
#===============================================================================

# Ruta al blog principal que deseas procesar
# Ejemplos de uso:
#   - "../gestion-empresarial" para el blog de gestión
#   - "../finanzas" para el blog de finanzas
#   - "../macroeconomia" para el blog de macroeconomía
main_blog="/home/achalmaedison/Downloads/actus-mercator"

# URL base del sitio web (sin barra final)
base_url="https://actus-mercator.netlify.app"

#===============================================================================
# FUNCIONES
#===============================================================================

################################################################################
# Función: convert_to_link
# Propósito: Convierte una ruta de carpeta en un enlace Markdown formateado
# Parámetros:
#   $1 - Ruta completa de la carpeta con fecha (ej: ../blog/tema/2024-01-15-mi-post)
# Salida: Línea con enlaces al post y PDF en formato Markdown
################################################################################
convert_to_link() {
    local path="$1"
    
    # Extraer el nombre de la carpeta (última parte de la ruta)
    local folder_name=$(basename "$path")
    
    # Procesar el título:
    # 1. Eliminar el prefijo de fecha (YYYY-MM-DD-)
    # 2. Reemplazar guiones con espacios
    # 3. Capitalizar la primera letra de cada palabra
    local title=$(echo "$folder_name" | \
                  sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//' | \
                  tr '-' ' ' | \
                  sed 's/\b\(.\)/\u\1/g')
    
    # Obtener el nombre del subblog (carpeta padre)
    local subblog=$(dirname "$path" | xargs basename)
    
    # Obtener el nombre de la carpeta principal del blog
    local main_folder=$(basename "$main_blog")
    
    # Construir las URLs completas
    local url="$base_url/$main_folder/$subblog/$folder_name"
    local pdf_url="$url/index.pdf"
    
    # Retornar la línea formateada con icono de PDF y enlaces
    # Formato: [📄](url-pdf) [Título](url-post)
    echo -e "[{{< fa regular file-pdf >}}]($pdf_url) [$title]($url)"
}

################################################################################
# Función: log_message
# Propósito: Registrar mensajes con formato en la consola
# Parámetros:
#   $1 - Tipo de mensaje (INFO, SUCCESS, ERROR)
#   $2 - Mensaje a mostrar
################################################################################
log_message() {
    local type="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$type" in
        "INFO")    echo "[$timestamp] ℹ️  $message" ;;
        "SUCCESS") echo "[$timestamp] ✅ $message" ;;
        "ERROR")   echo "[$timestamp] ❌ $message" ;;
        *)         echo "[$timestamp] $message" ;;
    esac
}

#===============================================================================
# VALIDACIONES INICIALES
#===============================================================================

# Verificar que el directorio principal existe
if [ ! -d "$main_blog" ]; then
    log_message "ERROR" "El directorio '$main_blog' no existe."
    log_message "INFO" "Por favor, verifica la variable 'main_blog' en la configuración."
    exit 1
fi

log_message "INFO" "Iniciando procesamiento del blog: $main_blog"
log_message "INFO" "URL base configurada: $base_url"

#===============================================================================
# PROCESAMIENTO PRINCIPAL
#===============================================================================

# Contador de archivos generados
total_files=0

# Iterar sobre cada subblog (subcarpeta) dentro del blog principal
for subblog in "$main_blog"/*; do
    # Verificar que es un directorio
    if [ -d "$subblog" ]; then
        subblog_name=$(basename "$subblog")
        log_message "INFO" "Procesando subblog: $subblog_name"
        
        # Definir el nombre del archivo de salida
        # Formato: _contenido_nombre-del-subblog.qmd
        output_file="$subblog/_contenido_${subblog_name}.qmd"
        
        # Crear o limpiar el archivo de salida
        > "$output_file"
        
        # Agregar encabezado YAML al archivo (opcional pero recomendado)
        cat > "$output_file" << EOF
---
title: "Índice de Contenidos - $subblog_name"
date: "$(date '+%Y-%m-%d')"
format: html
---

# Publicaciones

EOF
        
        # Contador de publicaciones en este subblog
        count=1
        posts_found=0
        
        # Procesar cada carpeta con formato de fecha dentro del subblog
        for dated_folder in "$subblog"/*; do
            if [ -d "$dated_folder" ]; then
                # Verificar que la carpeta sigue el formato YYYY-MM-DD-*
                folder_name=$(basename "$dated_folder")
                if [[ $folder_name =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}- ]]; then
                    echo -e "$count. $(convert_to_link "$dated_folder")" >> "$output_file"
                    ((count++))
                    ((posts_found++))
                fi
            fi
        done
        
        if [ $posts_found -gt 0 ]; then
            log_message "SUCCESS" "Generado: $output_file ($posts_found publicaciones)"
            ((total_files++))
        else
            log_message "INFO" "No se encontraron publicaciones en: $subblog_name"
            rm "$output_file"  # Eliminar archivo vacío
        fi
    fi
done

#===============================================================================
# RESUMEN FINAL
#===============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════"
log_message "SUCCESS" "Proceso completado exitosamente"
log_message "INFO" "Total de archivos de índice generados: $total_files"
echo "════════════════════════════════════════════════════════════════"