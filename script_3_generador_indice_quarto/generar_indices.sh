#!/bin/bash

################################################################################
# Script: Generador de Índices de Contenido para Blogs Quarto
# Autor: Edison Achalma
# Descripción: Genera automáticamente archivos de índice (.qmd) con enlaces
#              a publicaciones organizadas por fecha en blogs de Quarto.
#              Soporta dos estructuras:
#              - Página web: blog/posts/YYYY-MM-DD-titulo/
#              - Blog independiente: posts/YYYY-MM-DD-titulo/
# Versión: 3.0
# Última actualización: 2025-01-19
################################################################################

#===============================================================================
# CONFIGURACIÓN PRINCIPAL
#===============================================================================

# RUTA ABSOLUTA al directorio del blog que deseas procesar
# Ejemplos:
#   - Para página web: "/home/usuario/proyectos/mi-sitio/blog"
#   - Para blog independiente: "/home/usuario/proyectos/actus-mercator"
main_blog="/ruta/absoluta/a/tu/blog"

# URL base del sitio web (sin barra final)
# Para página web: "https://achalmaedison.netlify.app"
# Para blog independiente: "https://actus-mercator.netlify.app"
base_url="https://achalmaedison.netlify.app"

# Tipo de estructura del blog
# Valores posibles:
#   - "website" : Para estructura blog/posts/ (página web completa)
#   - "blog"    : Para estructura posts/ (blog independiente)
#   - "auto"    : Detecta automáticamente la estructura
blog_type="auto"

#===============================================================================
# FUNCIONES
#===============================================================================

################################################################################
# Función: detect_blog_structure
# Propósito: Detecta automáticamente si es un blog independiente o página web
# Parámetros:
#   $1 - Ruta al directorio principal del blog
# Retorna: "website" o "blog"
################################################################################
detect_blog_structure() {
    local path="$1"
    local blog_name=$(basename "$path")
    
    # Si el directorio se llama "blog" y tiene subdirectorios como "posts", es una página web
    if [[ "$blog_name" == "blog" ]] && [[ -d "$path/posts" ]]; then
        echo "website"
        return
    fi
    
    # Si tiene directamente carpetas "posts" o subcarpetas con fechas, es un blog independiente
    if [[ -d "$path/posts" ]] || ls -d "$path"/*/ 2>/dev/null | grep -q "[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-"; then
        echo "blog"
        return
    fi
    
    # Por defecto, asumimos blog independiente
    echo "blog"
}

################################################################################
# Función: build_url
# Propósito: Construye la URL correcta según la estructura del blog
# Parámetros:
#   $1 - Tipo de blog ("website" o "blog")
#   $2 - URL base
#   $3 - Nombre del blog principal (carpeta raíz)
#   $4 - Nombre del subblog
#   $5 - Nombre de la carpeta con fecha
# Retorna: URL completa del post
################################################################################
build_url() {
    local type="$1"
    local base="$2"
    local main_folder="$3"
    local subblog="$4"
    local folder_name="$5"
    
    if [[ "$type" == "website" ]]; then
        # Estructura: https://domain.com/blog/posts/YYYY-MM-DD-titulo/
        echo "$base/$main_folder/$subblog/$folder_name"
    else
        # Estructura: https://domain.com/posts/YYYY-MM-DD-titulo/
        echo "$base/$subblog/$folder_name"
    fi
}

################################################################################
# Función: convert_to_link
# Propósito: Convierte una ruta de carpeta en un enlace Markdown formateado
# Parámetros:
#   $1 - Ruta completa de la carpeta con fecha
#   $2 - Tipo de estructura del blog
# Salida: Línea con enlaces al post y PDF en formato Markdown
################################################################################
convert_to_link() {
    local path="$1"
    local type="$2"
    
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
    
    # Construir las URLs según la estructura
    local url=$(build_url "$type" "$base_url" "$main_folder" "$subblog" "$folder_name")
    local pdf_url="$url/index.pdf"
    
    # Retornar la línea formateada con icono de PDF y enlaces
    echo -e "[{{< fa regular file-pdf >}}]($pdf_url) [$title]($url)"
}

################################################################################
# Función: log_message
# Propósito: Registrar mensajes con formato en la consola
# Parámetros:
#   $1 - Tipo de mensaje (INFO, SUCCESS, ERROR, WARNING)
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
        "WARNING") echo "[$timestamp] ⚠️  $message" ;;
        *)         echo "[$timestamp] $message" ;;
    esac
}

#===============================================================================
# VALIDACIONES INICIALES
#===============================================================================

# Verificar que se proporcionó una ruta absoluta
if [[ ! "$main_blog" = /* ]]; then
    log_message "WARNING" "Se recomienda usar ruta absoluta. Ruta actual: $main_blog"
fi

# Verificar que el directorio principal existe
if [ ! -d "$main_blog" ]; then
    log_message "ERROR" "El directorio '$main_blog' no existe."
    log_message "INFO" "Por favor, verifica la variable 'main_blog' en la configuración."
    log_message "INFO" "Usa la ruta absoluta completa, ejemplo: /home/usuario/proyectos/blog"
    exit 1
fi

# Detectar o usar el tipo de blog especificado
if [[ "$blog_type" == "auto" ]]; then
    detected_type=$(detect_blog_structure "$main_blog")
    log_message "INFO" "Estructura detectada automáticamente: $detected_type"
    blog_type="$detected_type"
else
    log_message "INFO" "Usando estructura especificada: $blog_type"
fi

log_message "INFO" "Iniciando procesamiento del blog: $main_blog"
log_message "INFO" "URL base configurada: $base_url"
log_message "INFO" "Tipo de estructura: $blog_type"

#===============================================================================
# PROCESAMIENTO PRINCIPAL
#===============================================================================

# Contador de archivos generados
total_files=0
total_posts=0

# Iterar sobre cada subblog (subcarpeta) dentro del blog principal
for subblog in "$main_blog"/*; do
    # Verificar que es un directorio
    if [ -d "$subblog" ]; then
        subblog_name=$(basename "$subblog")
        
        # Saltar directorios que no son subblogs (como _site, .quarto, etc.)
        if [[ "$subblog_name" =~ ^[._] ]] || \
           [[ "$subblog_name" == "site_libs" ]] || \
           [[ "$subblog_name" == "beschikbaarheid" ]] || \
           [[ "$subblog_name" == "_partials" ]]; then
            continue
        fi
        
        log_message "INFO" "Procesando subblog: $subblog_name"
        
        # Definir el nombre del archivo de salida
        # Formato: _contenido_nombre-del-subblog.qmd
        output_file="$subblog/_contenido_${subblog_name}.qmd"
        
        # Limpiar el archivo de salida (sin encabezado YAML)
        > "$output_file"
        
        # Contador de publicaciones en este subblog
        count=1
        posts_found=0
        
        # Procesar cada carpeta con formato de fecha dentro del subblog
        for dated_folder in "$subblog"/*; do
            if [ -d "$dated_folder" ]; then
                # Verificar que la carpeta sigue el formato YYYY-MM-DD-*
                folder_name=$(basename "$dated_folder")
                if [[ $folder_name =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}- ]]; then
                    # Verificar que existe al menos index.qmd dentro
                    if [ -f "$dated_folder/index.qmd" ]; then
                        echo -e "$count. $(convert_to_link "$dated_folder" "$blog_type")" >> "$output_file"
                        ((count++))
                        ((posts_found++))
                    else
                        log_message "WARNING" "Carpeta sin index.qmd: $folder_name"
                    fi
                fi
            fi
        done
        
        if [ $posts_found -gt 0 ]; then
            log_message "SUCCESS" "Generado: $output_file ($posts_found publicaciones)"
            ((total_files++))
            ((total_posts+=posts_found))
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
if [ $total_files -gt 0 ]; then
    log_message "SUCCESS" "Proceso completado exitosamente"
    log_message "INFO" "Total de archivos de índice generados: $total_files"
    log_message "INFO" "Total de publicaciones procesadas: $total_posts"
    log_message "INFO" "Estructura utilizada: $blog_type"
else
    log_message "WARNING" "No se generaron archivos de índice"
    log_message "INFO" "Verifica la estructura de carpetas y las rutas configuradas"
fi
echo "════════════════════════════════════════════════════════════════"