# Ejemplos Específicos para tu Blog

## Escenario actual

Basándome en tu archivo .qmd de ejemplo, estos son los comandos específicos que necesitas:

## 1. Normalizar el archivo de ejemplo

```bash
# Ver qué cambiaría (dry-run)
python qmd_tag_manager.py --file test_example.qmd --normalize --dry-run

# Aplicar los cambios
python qmd_tag_manager.py --file test_example.qmd --normalize
```

**Resultado esperado:**
```yaml
tags:
  - gestion_empresarial
  - economia_internacional
  - cadena_de_suministros
```

## 2. Reemplazar tags específicos en tu blog

Según tu ejemplo, quieres hacer estos cambios:

```bash
python qmd_tag_manager.py \
  --directory ./posts \
  --replace \
    "Gestión Empresarial:gestion_empresarial" \
    "Economía Internacional:economia_internacional" \
    "Cadena de suministros:cadena_de_suministros" \
    "Posts:articulos" \
  --recursive
```

## 3. Limpiar todos los archivos de tu blog

Primero hacer una prueba:

```bash
# Paso 1: Ver qué cambiaría
python qmd_tag_manager.py \
  --directory ./posts \
  --normalize \
  --recursive \
  --dry-run

# Paso 2: Si se ve bien, aplicar
python qmd_tag_manager.py \
  --directory ./posts \
  --normalize \
  --recursive
```

## 4. Actualizar tags manteniendo tu nomenclatura

Si quieres actualizar "gestion_empresarial" a "gestiones_empresariales":

```bash
python qmd_tag_manager.py \
  --replace "gestion_empresarial:gestiones_empresariales" \
  --recursive
```

## 5. Operación completa para tu blog

```bash
# Paso 1: Backup (siempre primero!)
./qmd_helper.sh backup ./posts

# Paso 2: Normalizar y ver resultados
python qmd_tag_manager.py \
  --directory ./posts \
  --normalize \
  --recursive \
  --dry-run

# Paso 3: Aplicar normalización
python qmd_tag_manager.py \
  --directory ./posts \
  --normalize \
  --recursive

# Paso 4: Reemplazar tags específicos (si es necesario)
python qmd_tag_manager.py \
  --directory ./posts \
  --replace \
    "supply_chain:cadena_de_suministros" \
    "business_processes:procesos_empresariales" \
  --recursive

# Paso 5: Eliminar tags obsoletos
python qmd_tag_manager.py \
  --directory ./posts \
  --remove "draft" "borrador" "temp" \
  --recursive
```

## 6. Configurar tus reemplazos comunes

Edita `tag_config.py` con tus tags específicos:

```python
COMMON_REPLACEMENTS = {
    # Tags en español
    "Gestión Empresarial": "gestion_empresarial",
    "Economía Internacional": "economia_internacional",
    "Cadena de suministros": "cadena_de_suministros",
    "Análisis de Datos": "analisis_datos",
    "Ciencia de Datos": "ciencia_datos",
    
    # Tags en inglés que quieres en español
    "Supply Chain": "cadena_de_suministros",
    "Business Management": "gestion_empresarial",
    "Data Analysis": "analisis_datos",
    "Data Science": "ciencia_datos",
    
    # Tags de tu universidad
    "UNSCH": "universidad_huamanga",
    "Ayacucho": "ayacucho_peru",
}

TAGS_TO_REMOVE = [
    "draft",
    "borrador",
    "temp",
    "test",
    "prueba",
]

GLOBAL_TAGS = [
    "economia",  # Tag general para todos tus posts
    "blog",      # Identificar que es un post de blog
]
```

Luego ejecuta:

```bash
python tag_config.py  # Para ver los comandos generados
```

## 7. Casos específicos para tu archivo de ejemplo

Tu archivo actual tiene:
```yaml
tags:
  - gestion_empresarial
  - economia_internacional
  - cadena_de_suministros
```

### Caso A: Actualizar "cadena_de_suministros" a "logistica_empresarial"

```bash
python qmd_tag_manager.py \
  --file test_example.qmd \
  --replace "cadena_de_suministros:logistica_empresarial"
```

### Caso B: Agregar tags adicionales

```bash
python qmd_tag_manager.py \
  --file test_example.qmd \
  --add "supply_chain" "business_logistics" "operations_management"
```

### Caso C: Eliminar un tag específico

```bash
python qmd_tag_manager.py \
  --file test_example.qmd \
  --remove "gestion_empresarial"
```

## 8. Workflow recomendado para tu blog completo

```bash
# 1. Ir al directorio de tu blog
cd ~/tu-blog/posts

# 2. Crear backup
../qmd_helper.sh backup .

# 3. Ver estadísticas actuales
../qmd_helper.sh stats .

# 4. Normalizar todos los tags (dry-run)
python ../qmd_tag_manager.py --normalize --recursive --dry-run

# 5. Si se ve bien, aplicar
python ../qmd_tag_manager.py --normalize --recursive

# 6. Reemplazar tags según tu nomenclatura
python ../qmd_tag_manager.py \
  --replace \
    "Gestión Empresarial:gestion_empresarial" \
    "Economía Internacional:economia_internacional" \
    "Supply Chain:cadena_suministros" \
  --recursive

# 7. Limpiar tags obsoletos
python ../qmd_tag_manager.py \
  --remove "draft" "temp" "test" \
  --recursive

# 8. Ver nuevas estadísticas
../qmd_helper.sh stats .

# 9. Commit en Git
git add .
git commit -m "Normalizar y actualizar tags del blog"
```

## 9. Comandos rápidos usando el helper

```bash
# Normalizar con confirmación interactiva
./qmd_helper.sh full ./posts

# Ver estadísticas
./qmd_helper.sh stats ./posts

# Crear backup antes de cualquier operación
./qmd_helper.sh backup ./posts

# Normalizar rápido
./qmd_helper.sh normalize ./posts

# Normalizar en modo prueba
./qmd_helper.sh normalize-dry ./posts
```

## 10. Validar cambios después de procesar

```bash
# Ver los tags de un archivo específico
grep -A 10 "^tags:" tu_archivo.qmd

# Ver todos los tags únicos en tu blog
find ./posts -name "*.qmd" -exec grep -A 5 "^tags:" {} \; | grep "  -" | sort | uniq

# Contar cuántos posts tienen cada tag
find ./posts -name "*.qmd" -exec grep -A 10 "^tags:" {} \; | grep "  -" | sort | uniq -c | sort -rn
```

## Tips adicionales para tu caso

1. **Mantén consistencia lingüística**: Decide si prefieres tags en español o inglés
2. **Usa la configuración personalizada**: Define tus reemplazos en `tag_config.py`
3. **Siempre haz backup**: Especialmente importante si tienes muchos posts
4. **Verifica manualmente**: Después de procesar, revisa algunos archivos
5. **Documenta tus decisiones**: Mantén un registro de qué tags usas y por qué

---

¿Necesitas ayuda con algún caso específico? Prueba estos comandos y ajusta según tus necesidades.
