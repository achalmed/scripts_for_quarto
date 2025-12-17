#!/usr/bin/env python3
"""
Configuración de ejemplo para operaciones comunes de tags
Puedes modificar este archivo según tus necesidades
"""

# =============================================================================
# CONFIGURACIÓN DE REEMPLAZOS COMUNES
# =============================================================================

# Define aquí los reemplazos que usas frecuentemente
COMMON_REPLACEMENTS = {
    # Formato: "tag_original": "tag_nuevo"
    
    # Ejemplos de gestión empresarial
    "Gestión Empresarial": "gestion_empresarial",
    "Gestión de Negocios": "gestion_negocios",
    "Management": "gestion",
    
    # Ejemplos de economía
    "Economía Internacional": "economia_internacional",
    "International Economics": "economia_internacional",
    "Economía Global": "economia_global",
    
    # Ejemplos de logística y cadena de suministro
    "Cadena de suministros": "cadena_de_suministros",
    "Supply Chain": "cadena_de_suministros",
    "Logística": "logistica",
    "Logistics": "logistica",
    
    # Ejemplos de análisis de datos
    "Análisis de Datos": "analisis_datos",
    "Data Analysis": "analisis_datos",
    "Ciencia de Datos": "ciencia_datos",
    "Data Science": "ciencia_datos",
    
    # Ejemplos de estadística
    "Estadística": "estadistica",
    "Statistics": "estadistica",
    "Análisis Estadístico": "analisis_estadistico",
    
    # Ejemplos de investigación
    "Metodología de Investigación": "metodologia_investigacion",
    "Research Methods": "metodologia_investigacion",
    
    # Posts y artículos
    "Posts": "articulos",
    "Blog Posts": "articulos",
    "Artículos": "articulos",
}

# =============================================================================
# TAGS PARA ELIMINAR
# =============================================================================

# Tags obsoletos o no deseados
TAGS_TO_REMOVE = [
    "draft",
    "borrador",
    "temp",
    "temporal",
    "test",
    "prueba",
    # Agrega aquí tags que quieras eliminar globalmente
]

# =============================================================================
# TAGS PARA AGREGAR GLOBALMENTE
# =============================================================================

# Tags que quieres agregar a todos los archivos
GLOBAL_TAGS = [
    # "blog",
    # "2025",
    # "achalmaedison",
    # Descomenta y agrega tags que quieras en todos los archivos
]

# =============================================================================
# CONFIGURACIÓN DE DIRECTORIOS
# =============================================================================

# Directorios comunes donde están tus archivos .qmd
DIRECTORIES = {
    "posts": "./posts",
    "blog": "./blog",
    "articulos": "./articulos",
    "documentos": "./documentos",
}

# =============================================================================
# MAPEO DE CATEGORÍAS A TAGS
# =============================================================================

# Mapeo para convertir categorías en tags específicos
CATEGORY_TO_TAGS = {
    "Economía internacional": ["economia_internacional", "comercio_global"],
    "Gestión empresarial": ["gestion_empresarial", "administracion"],
    "Análisis de datos": ["analisis_datos", "estadistica"],
    "Investigación": ["metodologia_investigacion", "analisis"],
}

# =============================================================================
# REGLAS DE VALIDACIÓN
# =============================================================================

# Tags que siempre deben mantenerse juntos
REQUIRED_TAG_GROUPS = [
    # Ejemplo: Si existe "analisis_datos", debería existir "estadistica"
    # ["analisis_datos", "estadistica"],
]

# Longitud máxima recomendada para tags
MAX_TAG_LENGTH = 30

# Número máximo de tags por archivo
MAX_TAGS_PER_FILE = 10

# =============================================================================
# FUNCIONES DE AYUDA
# =============================================================================

def get_replacement_args():
    """Convierte COMMON_REPLACEMENTS en argumentos para el script"""
    return [f"{old}:{new}" for old, new in COMMON_REPLACEMENTS.items()]

def get_command_for_directory(directory_name, dry_run=True):
    """
    Genera el comando completo para procesar un directorio
    
    Args:
        directory_name: Nombre del directorio (debe estar en DIRECTORIES)
        dry_run: Si True, agrega --dry-run al comando
    
    Returns:
        String con el comando completo
    """
    if directory_name not in DIRECTORIES:
        raise ValueError(f"Directorio '{directory_name}' no encontrado en configuración")
    
    directory = DIRECTORIES[directory_name]
    cmd_parts = [
        "python qmd_tag_manager.py",
        f"--directory '{directory}'",
        "--normalize",
        "--recursive"
    ]
    
    if COMMON_REPLACEMENTS:
        replacements = " ".join([f'"{old}:{new}"' for old, new in COMMON_REPLACEMENTS.items()])
        cmd_parts.append(f"--replace {replacements}")
    
    if TAGS_TO_REMOVE:
        removes = " ".join([f'"{tag}"' for tag in TAGS_TO_REMOVE])
        cmd_parts.append(f"--remove {removes}")
    
    if GLOBAL_TAGS:
        adds = " ".join([f'"{tag}"' for tag in GLOBAL_TAGS])
        cmd_parts.append(f"--add {adds}")
    
    if dry_run:
        cmd_parts.append("--dry-run")
    
    return " \\\n  ".join(cmd_parts)

def print_example_commands():
    """Imprime comandos de ejemplo basados en la configuración"""
    print("=" * 70)
    print("COMANDOS DE EJEMPLO BASADOS EN TU CONFIGURACIÓN")
    print("=" * 70)
    print()
    
    print("1. Procesar directorio de posts (dry-run):")
    print("-" * 70)
    try:
        print(get_command_for_directory("posts", dry_run=True))
    except ValueError as e:
        print(f"   ⚠️  {e}")
    print()
    
    print("2. Aplicar cambios a directorio de posts:")
    print("-" * 70)
    try:
        print(get_command_for_directory("posts", dry_run=False))
    except ValueError as e:
        print(f"   ⚠️  {e}")
    print()
    
    print("3. Solo normalizar tags:")
    print("-" * 70)
    print("python qmd_tag_manager.py --normalize --recursive")
    print()
    
    print("4. Solo reemplazar tags comunes:")
    print("-" * 70)
    if COMMON_REPLACEMENTS:
        replacements = " ".join([f'"{old}:{new}"' for old, new in list(COMMON_REPLACEMENTS.items())[:3]])
        print(f"python qmd_tag_manager.py --replace {replacements}")
    else:
        print("   ℹ️  No hay reemplazos configurados en COMMON_REPLACEMENTS")
    print()

if __name__ == "__main__":
    print_example_commands()
    
    print("=" * 70)
    print("CONFIGURACIÓN ACTUAL")
    print("=" * 70)
    print(f"Reemplazos configurados: {len(COMMON_REPLACEMENTS)}")
    print(f"Tags para eliminar: {len(TAGS_TO_REMOVE)}")
    print(f"Tags globales: {len(GLOBAL_TAGS)}")
    print(f"Directorios configurados: {len(DIRECTORIES)}")
    print()
    
    if COMMON_REPLACEMENTS:
        print("Reemplazos configurados:")
        for old, new in list(COMMON_REPLACEMENTS.items())[:5]:
            print(f"  • {old} → {new}")
        if len(COMMON_REPLACEMENTS) > 5:
            print(f"  ... y {len(COMMON_REPLACEMENTS) - 5} más")
