# 🔧 Guía de Reparación - Archivos QMD Afectados

## Problemas Identificados

### 1. Separador YAML pegado al contenido
**Síntoma:** El contenido del documento aparece pegado a la última línea `---` del YAML

**Antes (incorrecto):**
```yaml
date: "05/15/2025"
draft: false---
## Plataformas de Inteligencia Comercial
```

**Después (correcto):**
```yaml
date: "05/15/2025"
draft: false
---

## Plataformas de Inteligencia Comercial
```

### 2. Tags agregados a archivos que no deberían tenerlos
**Síntoma:** Archivos sin tags originalmente ahora tienen tags agregados

---

## ✅ Solución Rápida

### Paso 1: Reparar separadores YAML

```bash
# Ver qué archivos se repararían (dry-run)
python fix_qmd_files.py --fix-separator --recursive --dry-run

# Aplicar reparación
python fix_qmd_files.py --fix-separator --recursive
```

### Paso 2: Eliminar tags de archivos que no los tenían

```bash
# El script preguntará por cada archivo
python fix_qmd_files.py --remove-unwanted-tags --recursive
```

### Paso 3: Hacer ambas reparaciones de una vez

```bash
python fix_qmd_files.py --fix-separator --remove-unwanted-tags --recursive
```

---

## 📋 Instrucciones Detalladas

### Si tus archivos ya fueron modificados:

#### Opción A: Usar Git para revertir (RECOMENDADO)

Si tienes control de versiones con Git:

```bash
# Ver qué cambios se hicieron
git status

# Ver los cambios en un archivo específico
git diff archivo.qmd

# Revertir TODOS los cambios
git restore .

# O revertir un archivo específico
git restore archivo.qmd

# Luego usar el script corregido
python qmd_tag_manager.py --normalize --recursive
```

#### Opción B: Usar el script de reparación

Si no tienes Git o ya hiciste commit:

```bash
# 1. Primero hacer backup
cp -r ./posts ./posts_backup_$(date +%Y%m%d)

# 2. Reparar separadores
python fix_qmd_files.py --fix-separator --recursive

# 3. Revisar manualmente algunos archivos
# Verifica que el separador --- tiene salto de línea después

# 4. Si algunos archivos tienen tags que no deberían
python fix_qmd_files.py --remove-unwanted-tags --recursive
```

#### Opción C: Reparación manual (para pocos archivos)

1. Abrir el archivo en un editor de texto
2. Buscar `draft: false---` o similar
3. Agregar salto de línea después de `---`:

**Antes:**
```yaml
draft: false---
## Contenido
```

**Después:**
```yaml
draft: false
---

## Contenido
```

---

## 🔍 Verificar la Reparación

### Comando para verificar separadores:

```bash
# Buscar archivos con el problema
grep -l "draft: false---" *.qmd

# Si no devuelve nada, está correcto
```

### Verificar manualmente:

1. Abrir algunos archivos .qmd
2. Verificar que después de `---` hay un salto de línea
3. Verificar que el contenido empieza en una nueva línea

---

## 🚀 Usar el Script Corregido

### El script ahora tiene estas mejoras:

1. **Separa correctamente el YAML del contenido**
   - Siempre agrega salto de línea después de `---`

2. **No agrega tags a archivos sin tags**
   - Solo procesa archivos que ya tienen tags
   - Omite archivos sin tags cuando usas `--add`

### Ejemplos de uso correcto:

```bash
# Normalizar (solo archivos con tags)
python qmd_tag_manager.py --normalize --recursive

# Agregar tags (solo a archivos que YA tienen tags)
python qmd_tag_manager.py --add "nuevo_tag" --recursive

# Reemplazar tags
python qmd_tag_manager.py --replace "viejo:nuevo" --recursive
```

---

## ⚠️ Prevención para el Futuro

### Antes de ejecutar operaciones masivas:

1. **SIEMPRE hacer backup:**
   ```bash
   ./qmd_helper.sh backup ./posts
   ```

2. **SIEMPRE usar dry-run primero:**
   ```bash
   python qmd_tag_manager.py --normalize --recursive --dry-run
   ```

3. **Revisar manualmente algunos archivos:**
   - Después del dry-run, revisa 2-3 archivos
   - Verifica que los cambios son los esperados

4. **Usar Git:**
   ```bash
   git add .
   git commit -m "Estado antes de normalizar tags"
   ```

5. **Procesar por etapas:**
   - Primero un archivo de prueba
   - Luego un directorio pequeño
   - Finalmente todo el sitio

---

## 🆘 Casos de Emergencia

### Si algo salió muy mal:

#### Si tienes Git:
```bash
# Ver el último commit
git log --oneline -5

# Revertir al commit anterior
git reset --hard HEAD~1

# O revertir a un commit específico
git reset --hard [hash_del_commit]
```

#### Si tienes backup:
```bash
# Restaurar desde backup
rm -rf ./posts
cp -r ./posts_backup_20251217 ./posts
```

#### Si no tienes nada:
1. Usar el script de reparación `fix_qmd_files.py`
2. Reparar manualmente los archivos más importantes
3. Para el resto, considerar recrear el YAML header

---

## 📊 Script de Verificación

Usa este comando para verificar todos tus archivos:

```bash
# Verificar separadores en todos los archivos
find ./posts -name "*.qmd" -exec sh -c '
  file="$1"
  if grep -q "draft: false---" "$file" || grep -q "date:.*---" "$file"; then
    echo "❌ PROBLEMA: $file"
  else
    echo "✅ OK: $file"
  fi
' sh {} \;
```

---

## ✨ Resultado Final Esperado

Después de la reparación, tus archivos deben verse así:

```yaml
---
title: Mi título
date: "05/15/2025"
draft: false
tags:
  - economia_internacional
  - gestion_empresarial
---

## Mi contenido empieza aquí

Con el salto de línea correcto después de ---
```

---

## 🤝 Soporte

Si encuentras más problemas:

1. Revisa el README.md para ejemplos adicionales
2. Usa `python qmd_tag_manager.py --help`
3. Prueba primero con `--dry-run`
4. Reporta el problema con un ejemplo del archivo afectado

---

**Versión del Script:** 1.1.0 (Corregido)  
**Fecha:** 17 de Diciembre 2025
