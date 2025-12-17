# 🚀 Guía de Inicio Rápido - QMD Tag Manager

## Instalación en 3 pasos

### 1️⃣ Instalar dependencias
```bash
pip install pyyaml
```

### 2️⃣ Verificar instalación
```bash
python qmd_tag_manager.py --help
```

### 3️⃣ ¡Listo para usar!

---

## 📝 Tu primera operación (5 minutos)

### Paso 1: Hacer una prueba sin modificar archivos

```bash
# Ir al directorio donde están tus archivos .qmd
cd /ruta/a/tus/posts

# Ejecutar en modo dry-run para ver qué cambiaría
python qmd_tag_manager.py --normalize --dry-run
```

**¿Qué hace esto?**
- Escanea todos los archivos .qmd en el directorio actual
- Muestra qué tags se normalizarían
- NO modifica ningún archivo (porque usamos `--dry-run`)

### Paso 2: Si todo se ve bien, aplicar los cambios

```bash
python qmd_tag_manager.py --normalize
```

**¿Qué hace esto?**
- Normaliza todos los tags (minúsculas, sin tildes, con guiones bajos)
- Elimina duplicados automáticamente
- Guarda los cambios en los archivos

---

## 🎯 Casos de uso más comunes

### Caso 1: "Quiero estandarizar todos mis tags"

```bash
# Ver primero qué cambiaría
python qmd_tag_manager.py --normalize --recursive --dry-run

# Aplicar cambios
python qmd_tag_manager.py --normalize --recursive
```

### Caso 2: "Quiero reemplazar un tag específico"

Por ejemplo, cambiar "Gestión Empresarial" por "gestion_empresarial":

```bash
python qmd_tag_manager.py --replace "Gestión Empresarial:gestion_empresarial"
```

El script es inteligente: encontrará todas las variaciones:
- "Gestión Empresarial"
- "gestión empresarial"
- "GESTIÓN EMPRESARIAL"
- "gestion empresarial"

Y las convertirá todas a: `gestion_empresarial`

### Caso 3: "Quiero reemplazar varios tags a la vez"

```bash
python qmd_tag_manager.py --replace \
  "Gestión Empresarial:gestion_empresarial" \
  "Cadena de suministros:cadena_de_suministros" \
  "Economía Internacional:economia_internacional"
```

### Caso 4: "Quiero eliminar tags obsoletos"

```bash
python qmd_tag_manager.py --remove "draft" "borrador" "temp"
```

### Caso 5: "Quiero agregar un tag a todos mis posts"

```bash
python qmd_tag_manager.py --add "blog" "2025"
```

---

## 🔧 Configuración personalizada

### Opción 1: Usar el script tal cual

```bash
python qmd_tag_manager.py [opciones]
```

### Opción 2: Personalizar configuración (recomendado)

1. Edita `tag_config.py`:
```python
COMMON_REPLACEMENTS = {
    "Gestión Empresarial": "gestion_empresarial",
    "Tu Tag Viejo": "tu_tag_nuevo",
    # Agrega más aquí
}
```

2. Genera comandos automáticamente:
```bash
python tag_config.py
```

3. Copia y ejecuta el comando generado

---

## ✅ Checklist antes de procesar muchos archivos

- [ ] Tengo una copia de seguridad (Git commit o respaldo)
- [ ] Probé con `--dry-run` primero
- [ ] Revisé la salida del dry-run y se ve correcta
- [ ] Entiendo qué cambios se van a hacer
- [ ] Estoy en el directorio correcto

---

## 🆘 Problemas comunes

### "No se encontraron archivos .qmd"

**Solución**: Verifica que estás en el directorio correcto o usa:
```bash
python qmd_tag_manager.py --directory "/ruta/completa/a/tus/posts"
```

### "ModuleNotFoundError: No module named 'yaml'"

**Solución**: Instala PyYAML:
```bash
pip install pyyaml
```

### Los cambios no se aplican

**Solución**: Asegúrate de NO usar `--dry-run` si quieres aplicar cambios

---

## 📚 Comandos útiles para copiar y pegar

### Normalizar todo en el directorio actual
```bash
python qmd_tag_manager.py --normalize
```

### Normalizar todo recursivamente
```bash
python qmd_tag_manager.py --normalize --recursive
```

### Ver ayuda completa
```bash
python qmd_tag_manager.py --help
```

### Procesar un archivo específico
```bash
python qmd_tag_manager.py --file "mi_archivo.qmd" --normalize
```

### Operación completa (normalizar + reemplazar + limpiar)
```bash
python qmd_tag_manager.py \
  --normalize \
  --replace "Old Tag:new_tag" \
  --remove "obsolete" \
  --add "new_tag" \
  --recursive
```

---

## 🎓 Flujo de trabajo recomendado

### Primera vez usando el script:

1. **Backup primero**
   ```bash
   git add .
   git commit -m "Backup antes de normalizar tags"
   ```

2. **Probar en un archivo**
   ```bash
   python qmd_tag_manager.py --file "test.qmd" --normalize --dry-run
   ```

3. **Si se ve bien, aplicar al archivo**
   ```bash
   python qmd_tag_manager.py --file "test.qmd" --normalize
   ```

4. **Verificar el resultado**
   - Abre el archivo y revisa los tags
   - Verifica que todo se ve correcto

5. **Aplicar a todos los archivos**
   ```bash
   python qmd_tag_manager.py --normalize --recursive --dry-run
   python qmd_tag_manager.py --normalize --recursive
   ```

6. **Commit final**
   ```bash
   git add .
   git commit -m "Normalizar todos los tags"
   ```

---

## 📊 Entendiendo la salida

```
📄 Procesando: /ruta/al/archivo.qmd
   Tags actuales: ['Gestión Empresarial', 'Cadena de suministros']
   🔄 Reemplazado: 'gestion_empresarial' → 'logistica'
   🗑️  Eliminados: 1 tag(s)
   ➕ Agregado: 'nuevo_tag'
   🔍 Duplicados eliminados: 2
   Tags finales: ['logistica', 'nuevo_tag', 'economia']
   ✅ Archivo actualizado exitosamente
```

**Leyenda:**
- 📄 = Archivo siendo procesado
- 🔄 = Tag reemplazado
- 🗑️ = Tags eliminados
- ➕ = Tags agregados
- 🔍 = Duplicados encontrados y eliminados
- ✅ = Operación exitosa

---

## 💡 Tips y trucos

1. **Siempre usa dry-run primero** 🔍
   - Te ahorra dolores de cabeza
   - Te muestra exactamente qué va a cambiar

2. **Procesa por etapas** 📝
   - Primero normaliza
   - Luego reemplaza tags específicos
   - Finalmente limpia tags obsoletos

3. **Usa Git** 🎯
   - Commit antes de cambios grandes
   - Puedes revertir si algo sale mal

4. **Revisa algunos archivos manualmente** 👀
   - Después de procesar, abre algunos archivos
   - Verifica que los tags se ven correctos

5. **Personaliza tag_config.py** ⚙️
   - Define tus reemplazos comunes una vez
   - Reutiliza en múltiples operaciones

---

## 🤔 ¿Necesitas más ayuda?

- Revisa el README.md completo para documentación detallada
- Ejecuta `python qmd_tag_manager.py --help`
- Mira los ejemplos en `tag_config.py`
- Prueba con el archivo `test_example.qmd`

---

**¡Listo! Ya puedes empezar a gestionar tus tags de manera eficiente** 🎉
