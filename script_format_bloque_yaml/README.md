# Guía de Uso - fix_qmd_files_v2.py

## 🎯 Qué hace este script

Corrige automáticamente el formato del bloque YAML en archivos `.qmd`, asegurando que:

1. **NO hay línea en blanco** después del primer `---`
2. **Hay EXACTAMENTE una línea en blanco** después del segundo `---` y antes del contenido
3. **Es idempotente**: puedes ejecutarlo múltiples veces y siempre producirá el mismo resultado

### Formato correcto:

```yaml
---
title: Mi título
date: "05/15/2025"
draft: false
---

## Mi contenido empieza aquí
```
## Uso de entorno conda (opcional)

### 1. Creamos el entorno para el script
```bash
conda create --name script_tag_manager python=3.14 pyyaml 
```

### 2. Activamos el entorno
```bash
conda activate script_tag_manager
```


## 🚀 Uso Rápido

### Para archivos con el problema del `---` pegado:

```bash
# Ver qué se cambiaría (sin modificar)
python fix_qmd_files.py --directory /home/achalmaedison/Documents/publicaciones --recursive --dry-run

# Aplicar la corrección
python fix_qmd_files.py --directory /home/achalmaedison/Documents/publicaciones --recursive
```

### Para procesar recursivamente todos los subdirectorios:

```bash
python fix_qmd_files.py --directory /home/achalmaedison/Documents/publicaciones --recursive
```

### Para un archivo específico:

```bash
python fix_qmd_files.py --file mi_archivo.qmd
```

## 📋 Ejemplos

### Ejemplo 1: Archivo con `---` pegado

**Antes:**
```yaml
---
title: Mi título
draft: false---
## Contenido
```

**Después de ejecutar el script:**
```yaml
---
title: Mi título
draft: false
---

## Contenido
```

### Ejemplo 2: Archivo con múltiples líneas en blanco

**Antes:**
```yaml
---

title: Mi título
draft: false


---


## Contenido
```

**Después:**
```yaml
---
title: Mi título
draft: false


---

## Contenido
```

**Nota:** Las líneas en blanco DENTRO del contenido YAML se mantienen (son parte del YAML). Solo se normaliza el espacio DESPUÉS del `---` de cierre.

## ✅ Características clave

### 1. Idempotente
Puedes ejecutarlo 1, 2, 3, 10 veces y siempre produce el mismo resultado:

```bash
# Primera ejecución
python fix_qmd_files.py --file archivo.qmd
# ✅ Archivo corregido

# Segunda ejecución
python fix_qmd_files.py --file archivo.qmd
# ✓ OK (formato correcto)

# Tercera ejecución
python fix_qmd_files.py --file archivo.qmd
# ✓ OK (formato correcto)
```

### 2. Seguro con --dry-run
Siempre puedes verificar qué cambiará antes de aplicarlo:

```bash
python fix_qmd_files.py --directory ./posts --recursive --dry-run
```

### 3. Verbose para más detalles
```bash
python fix_qmd_files.py --directory ./posts --verbose
```

## 🔄 Flujo de trabajo recomendado

```bash
# 1. Backup (siempre primero!)
cp -r ./posts ./posts_backup_$(date +%Y%m%d)

# 2. Ver qué se cambiaría
python fix_qmd_files.py --directory ./posts --recursive --dry-run

# 3. Aplicar cambios
python fix_qmd_files.py --directory ./posts --recursive

# 4. Verificar algunos archivos manualmente
head -20 ./posts/mi_archivo.qmd

# 5. Si todo está bien, hacer commit
git add .
git commit -m "Corregir formato YAML en archivos .qmd"
```

## 🆘 Solución de problemas

### El script dice "No se encontró bloque YAML válido"

**Posibles causas:**
1. El archivo no empieza con `---`
2. El archivo no tiene un segundo `---`
3. El formato está muy corrupto

**Solución:** Revisa manualmente el archivo.

### El script no hace cambios pero mi archivo se ve mal

Si tu archivo tiene este formato:
```yaml
---
title: Test
---
## Contenido
```

El script NO lo modificará porque ya tiene el formato correcto (hay una línea en blanco implícita después de `---`).

Para verificar, usa:
```bash
cat -A mi_archivo.qmd | head -10
```

Esto muestra todos los caracteres invisibles.

## 📊 Opciones del script

```
Opciones:
  -d, --directory DIR    Directorio con archivos .qmd (por defecto: .)
  -f, --file FILE        Reparar un archivo específico
  --dry-run              Simular cambios sin modificar archivos
  --recursive            Procesar subdirectorios recursivamente
  -v, --verbose          Mostrar información detallada
  -h, --help             Mostrar ayuda
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

## 💡 Tips

1. **Siempre usa `--dry-run` primero** para ver qué cambiará
2. **Haz backup antes de operaciones masivas**
3. **El script es seguro de ejecutar múltiples veces** (idempotente)
4. **Verifica manualmente algunos archivos** después de procesar

## ✨ Diferencia con fix_qmd_files.py (versión anterior)

| Característica | v1 (fix_qmd_files.py) | v2 (fix_qmd_files_v2.py) |
|----------------|----------------------|--------------------------|
| Idempotente | ❌ No (agrega líneas cada vez) | ✅ Sí |
| Línea después de primer `---` | ❌ Agregaba línea | ✅ No agrega línea |
| Línea antes de segundo `---` | ❌ Agregaba múltiples | ✅ Solo normaliza después |
| Simplicidad | Complejo | Simple y claro |

---

**Versión:** 2.0  
**Fecha:** 17 de Diciembre 2025