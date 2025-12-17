# QMD Tag Manager - Gestor de Tags para Archivos Quarto

Un script completo en Python para gestionar tags en archivos `.qmd` de Quarto con capacidades de normalización, reemplazo, eliminación y adición de tags.

## 📝 Changelog

### v1.1.0 (17 Diciembre 2025)
- ✅ **CORREGIDO**: Separador YAML `---` ahora tiene salto de línea correcto antes del contenido
- ✅ **CORREGIDO**: `--add` ya no agrega tags a archivos que no tienen tags
- ✅ **NUEVO**: Script de reparación `fix_qmd_files.py` para archivos afectados
- ℹ️ Ahora solo procesa archivos que YA tienen tags cuando se usa `--add`

### v1.0.0 (17 Diciembre 2025)
- Lanzamiento inicial

## 🔧 Si Actualizaste desde v1.0.0

Si ya usaste la versión anterior del script, puede que algunos archivos tengan:
1. El separador `---` pegado al contenido
2. Tags agregados a archivos que no deberían tenerlos

**Solución rápida:**
```bash
# Reparar separadores
python fix_qmd_files.py --fix-separator --recursive

# Ver guía completa
cat REPARACION.md
```

## 📋 Características

- ✅ **Normalización automática**: Convierte tags a minúsculas, elimina tildes y caracteres especiales
- 🔄 **Reemplazo de tags**: Cambia tags específicos por otros
- 🗑️ **Eliminación de tags**: Remueve tags no deseados
- ➕ **Adición de tags**: Agrega nuevos tags
- 🔍 **Detección de duplicados**: Evita tags duplicados automáticamente
- 📁 **Procesamiento por lotes**: Procesa múltiples archivos o directorios completos
- 🧪 **Modo Dry-Run**: Simula cambios sin modificar archivos
- 🔁 **Recursivo**: Procesa subdirectorios

## 🚀 Instalación

### 1. Creamos el entorno para el script
```bash
conda create --name script_tag_manager python=3.14 pyyaml 
```

### 2. Activamos el entorno
```bash
conda activate script_tag_manager
```

### Descargar el script

Guarda el script como `qmd_tag_manager.py` y dale permisos de ejecución:

```bash
chmod +x qmd_tag_manager.py
```

## 📖 Uso

### Sintaxis básica

```bash
python qmd_tag_manager.py [OPCIONES]
```

### Opciones disponibles

| Opción | Descripción |
|--------|-------------|
| `-d, --directory DIR` | Directorio donde se encuentran los archivos .qmd |
| `-n, --normalize` | Normalizar todos los tags |
| `-r, --replace OLD:NEW` | Reemplazar tags (formato: "viejo:nuevo") |
| `--remove TAG` | Eliminar tags específicos |
| `-a, --add TAG` | Agregar nuevos tags |
| `--dry-run` | Simular cambios sin guardar |
| `--recursive` | Procesar subdirectorios recursivamente |
| `-f, --file FILE` | Procesar un archivo específico |

## 💡 Ejemplos de uso

### 1. Normalizar tags en el directorio actual

```bash
python qmd_tag_manager.py --normalize
```

**Qué hace:**
- Convierte "Gestión Empresarial" → "gestion_empresarial"
- Convierte "Economía Internacional" → "economia_internacional"
- Convierte "Cadena de suministros" → "cadena_de_suministros"

### 2. Reemplazar tags específicos

```bash
python qmd_tag_manager.py --replace "Gestión Empresarial:gestion_empresarial" "Cadena de suministros:cadena_de_suministros"
```

**Qué hace:**
- Busca el tag normalizado de "Gestión Empresarial" y lo reemplaza por "gestion_empresarial"
- Si encuentra variaciones como "gestión empresarial", "GESTIÓN EMPRESARIAL", etc., las detecta y reemplaza

### 3. Reemplazar múltiples tags

```bash
python qmd_tag_manager.py --replace \
  "Gestión Empresarial:gestion_empresarial" \
  "Cadena de suministros:logistica_empresarial" \
  "Economía Internacional:comercio_internacional"
```

### 4. Eliminar tags obsoletos

```bash
python qmd_tag_manager.py --remove "tag_obsoleto" "otro_tag_viejo"
```

### 5. Agregar nuevos tags

```bash
python qmd_tag_manager.py --add "supply_chain" "logistics" "business_management"
```

**⚠️ IMPORTANTE**: El comando `--add` solo agrega tags a archivos que **YA tienen** una sección de tags. Los archivos sin tags serán omitidos automáticamente. Esto previene agregar tags a archivos que no deberían tenerlos.

### 6. Combinación de operaciones

```bash
python qmd_tag_manager.py \
  --normalize \
  --replace "old_tag:new_tag" \
  --remove "obsolete_tag" \
  --add "new_tag"
```

### 7. Procesar un directorio específico

```bash
python qmd_tag_manager.py --directory "/ruta/a/tus/posts" --normalize
```

### 8. Modo dry-run (simular sin guardar)

```bash
python qmd_tag_manager.py --normalize --dry-run
```

**Útil para:**
- Ver qué cambios se realizarían antes de aplicarlos
- Verificar que las operaciones son correctas

### 9. Procesar recursivamente

```bash
python qmd_tag_manager.py --directory "/ruta/base" --normalize --recursive
```

**Qué hace:**
- Busca archivos .qmd en todos los subdirectorios
- Aplica las operaciones a todos los archivos encontrados

### 10. Procesar un archivo específico

```bash
python qmd_tag_manager.py --file "mi_post.qmd" --normalize
```

## 🎯 Casos de uso comunes

### Caso 1: Estandarizar todos los tags de tu blog

```bash
# Primero, simular para ver los cambios
python qmd_tag_manager.py --directory "./posts" --normalize --recursive --dry-run

# Si todo se ve bien, aplicar los cambios
python qmd_tag_manager.py --directory "./posts" --normalize --recursive
```

### Caso 2: Actualizar nomenclatura de tags

Supongamos que quieres cambiar la nomenclatura de varios tags:

```bash
python qmd_tag_manager.py \
  --replace \
    "Gestión Empresarial:gestion_empresarial" \
    "Cadena de suministros:cadena_de_suministros" \
    "Economía Internacional:economia_internacional" \
    "Posts:articulos" \
  --recursive
```

### Caso 3: Limpiar y reorganizar tags

```bash
# Paso 1: Normalizar todos los tags
python qmd_tag_manager.py --normalize --recursive

# Paso 2: Eliminar tags obsoletos
python qmd_tag_manager.py --remove "old_tag1" "old_tag2" --recursive

# Paso 3: Agregar tags nuevos a todos los archivos
python qmd_tag_manager.py --add "blog" "2025" --recursive
```

### Caso 4: Migración de taxonomía

Si estás migrando de un sistema de tags a otro:

```bash
python qmd_tag_manager.py \
  --replace \
    "Management:gestion" \
    "Supply Chain:cadena_suministros" \
    "International Economics:economia_internacional" \
  --remove "deprecated" "old_system" \
  --add "migrated" \
  --recursive
```

## 🔧 Reglas de normalización

El script aplica las siguientes reglas automáticamente:

1. **Minúsculas**: TODO → todo
2. **Sin tildes**: gestión → gestion
3. **Espacios**: "Gestión Empresarial" → "gestion_empresarial"
4. **Caracteres especiales**: Se eliminan o convierten a guión bajo
5. **Guiones múltiples**: Se reducen a uno solo
6. **Limpieza**: Se eliminan guiones al inicio y final

### Ejemplos de normalización:

| Original | Normalizado |
|----------|-------------|
| "Gestión Empresarial" | "gestion_empresarial" |
| "Economía & Finanzas" | "economia_finanzas" |
| "Supply-Chain  Management" | "supply_chain_management" |
| "CADENA DE SUMINISTROS" | "cadena_de_suministros" |
| "Análisis Estadístico" | "analisis_estadistico" |

## ⚠️ Detección de duplicados

El script es inteligente para detectar duplicados:

```yaml
# Antes
tags:
  - Gestión Empresarial
  - gestion_empresarial
  - GESTION EMPRESARIAL
  - gestión empresarial

# Después (con --normalize)
tags:
  - gestion_empresarial
```

## 📊 Salida del script

El script proporciona información detallada:

```
==============================================================
🏷️  QMD TAG MANAGER
==============================================================
📁 Directorio: /home/usuario/posts
==============================================================
🔍 Encontrados 15 archivo(s) .qmd

📄 Procesando: /home/usuario/posts/post1.qmd
   Tags actuales: ['Gestión Empresarial', 'Cadena de suministros']
   🔄 Reemplazado: 'gestion_empresarial' → 'gestion_empresarial'
   Tags finales: ['gestion_empresarial', 'cadena_de_suministros']
   ✅ Archivo actualizado exitosamente

...

==============================================================
✅ Procesados exitosamente: 15/15 archivos
```

## 🐛 Solución de problemas

### Error: "No se encontró encabezado YAML"

**Causa**: El archivo no tiene un encabezado YAML válido entre `---`

**Solución**: Verifica que tu archivo tenga esta estructura:

```yaml
---
title: Mi título
tags:
  - tag1
  - tag2
---

# Contenido del documento
```

### Error: "ModuleNotFoundError: No module named 'yaml'"

**Causa**: Falta la biblioteca PyYAML

**Solución**:
```bash
pip install pyyaml
```

### Los cambios no se aplican

**Causa**: Puede que estés usando `--dry-run`

**Solución**: Ejecuta sin la opción `--dry-run` para aplicar los cambios

## 🔒 Seguridad

- El script crea una copia de seguridad implícita al mantener el formato YAML original
- Usa `--dry-run` para simular cambios antes de aplicarlos
- Se recomienda usar control de versiones (Git) antes de ejecutar cambios masivos

## 📝 Recomendaciones

1. **Siempre usa dry-run primero**: Simula los cambios antes de aplicarlos
2. **Haz commit en Git**: Asegúrate de tener una copia de seguridad
3. **Procesa por etapas**: Normaliza primero, luego reemplaza, luego elimina/agrega
4. **Revisa los resultados**: Verifica algunos archivos manualmente después del procesamiento

## 🤝 Contribuciones

Este script fue creado por Edison Achalma para gestionar tags en blogs de Quarto.

## 📄 Licencia

Uso libre para propósitos educativos y personales.

## 📧 Contacto

- GitHub: [@achalmed](https://github.com/achalmed)
- LinkedIn: [achalmaedison](https://www.linkedin.com/in/achalmaedison)

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2025