# 🚀 Guía de Instalación - Gestor de Publicaciones Quarto v2.0

Instalación rápida y sencilla en 5 minutos.

## 📋 Requisitos Previos

### Software Necesario

#### 1. Quarto (Requerido)
```bash
# Verificar si está instalado
quarto --version

# Si no está instalado, descargar de:
# https://quarto.org/docs/get-started/
```

**Versión mínima:** 1.3.0  
**Recomendada:** 1.4.0+

#### 2. Bash (Incluido en Linux/macOS)
```bash
# Verificar versión
bash --version
```

**Versión mínima:** 4.0+

#### 3. Git (Opcional, para funciones Git)
```bash
# Verificar instalación
git --version
```

### Estructura de Directorios Requerida

El script asume esta estructura:

```
/home/achalmaedison/Documents/
├── publicaciones/          # Tus blogs
│   ├── numerus-scriptum/
│   ├── epsilon-y-beta/
│   └── [otros blogs]
└── scripts/
    └── scripts_for_quarto/  # Aquí va build.sh
```

Si tu estructura es diferente, necesitarás editar las rutas en `build.sh` (ver [Personalización](#personalización)).

## ⚡ Instalación Rápida

### Opción 1: Instalación Estándar (Recomendada)

```bash
# 1. Crear directorio de scripts
mkdir -p /home/achalmaedison/Documents/scripts/scripts_for_quarto

# 2. Copiar el archivo
cp build.sh /home/achalmaedison/Documents/scripts/scripts_for_quarto/

# 3. Dar permisos de ejecución
chmod +x /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh

# 4. Probar instalación
/home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh version
```

Si muestra la versión de Quarto, ¡instalación exitosa! ✓

### Opción 2: Con Alias (Más Conveniente)

```bash
# Después de la instalación estándar, añade alias
echo 'alias qbuild="/home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh"' >> ~/.bashrc

# Recargar configuración
source ~/.bashrc

# Ahora puedes usar simplemente:
qbuild list
qbuild new-post numerus-scriptum
```

### Opción 3: En PATH (Acceso Global)

```bash
# Añadir al PATH
echo 'export PATH="$PATH:/home/achalmaedison/Documents/scripts/scripts_for_quarto"' >> ~/.bashrc

# Recargar
source ~/.bashrc

# Ahora ejecuta desde cualquier lugar:
build.sh list
```

## 🎯 Primer Uso

### 1. Verificar Instalación

```bash
# Ver versión de Quarto
build.sh version

# Listar blogs disponibles
build.sh list
```

**Salida esperada:**
```
═══════════════════════════════════════════════════════════════
  🚀 Blogs Disponibles
═══════════════════════════════════════════════════════════════

1. 📖 actus-mercator
   Blog de Comercio Internacional
   📄 15 posts
   🔧 Git inicializado

[... más blogs ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 12 blogs
```

### 2. Crear Tu Primer Post

```bash
# Modo interactivo (recomendado para primera vez)
build.sh new-post numerus-scriptum
```

Sigue el formulario interactivo paso a paso.

### 3. Preview y Renderizar

```bash
# Ver preview en navegador
build.sh preview numerus-scriptum

# Renderizar versión final
build.sh render numerus-scriptum
```

## 🔧 Configuración Avanzada

### Personalización de Rutas

Si tus directorios son diferentes, edita `build.sh` (líneas 10-11):

```bash
# Abrir para editar
nano /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh

# Cambiar estas líneas:
PUBLICACIONES_DIR="/tu/ruta/personalizada/publicaciones"
SCRIPT_DIR="/tu/ruta/personalizada/scripts"
```

### Configurar Blogs Excluidos

Por defecto, estos blogs se excluyen automáticamente:
- apa
- borradores
- notas
- practicas preprofesionales
- propuesta bicentenario
- taller unsch como elaborar tesis de pregrado

Para cambiar, edita `build.sh` (líneas 13-21):

```bash
EXCLUDED_BLOGS=(
    "apa"
    "borradores"
    "tu-blog-a-excluir"
    # Añade más aquí
)
```

### Configurar Editor por Defecto

```bash
# Bash/Zsh
echo 'export EDITOR="code"' >> ~/.bashrc  # VS Code
echo 'export EDITOR="nano"' >> ~/.bashrc  # Nano
echo 'export EDITOR="vim"' >> ~/.bashrc   # Vim

source ~/.bashrc
```

### Aliases Adicionales Útiles

```bash
# Añadir a ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# Quarto Blog Management
alias qlist="build.sh list"
alias qnew="build.sh new-post"
alias qrender="build.sh render"
alias qpreview="build.sh preview"
alias qclean="build.sh clean"
alias qpublish="build.sh publish"
alias qall="build.sh render-all"

EOF

source ~/.bashrc
```

Ahora puedes usar:
```bash
qlist                           # Listar blogs
qnew numerus-scriptum           # Crear post
qrender epsilon-y-beta          # Renderizar
qpreview website-achalma 4300   # Preview en puerto 4300
```

## ✅ Verificación Post-Instalación

### Checklist Completa

Ejecuta estos comandos para verificar:

```bash
# 1. Quarto instalado
quarto --version
# ✓ Debe mostrar versión (ej: 1.4.551)

# 2. Script ejecutable
ls -l /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh
# ✓ Debe mostrar: -rwxr-xr-x (permisos de ejecución)

# 3. Script funciona
build.sh version
# ✓ Debe mostrar versión de Quarto

# 4. Detecta blogs
build.sh list
# ✓ Debe mostrar lista de blogs

# 5. Modo interactivo
build.sh
# ✓ Debe mostrar menú interactivo

# 6. Crear post de prueba
build.sh new-post numerus-scriptum
# ✓ Debe iniciar formulario interactivo
```

### Problemas Comunes y Soluciones

#### ❌ "comando no encontrado"

**Problema:** El sistema no encuentra `build.sh`

**Solución:**
```bash
# Opción 1: Usar ruta completa
/home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh list

# Opción 2: Añadir al PATH (ver arriba)

# Opción 3: Crear alias (ver arriba)
```

#### ❌ "Permission denied"

**Problema:** No tiene permisos de ejecución

**Solución:**
```bash
chmod +x /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh
```

#### ❌ "Quarto no está instalado"

**Problema:** Quarto no está en el sistema

**Solución:**
```bash
# Descargar e instalar desde:
# https://quarto.org/docs/get-started/

# Para verificar instalación:
which quarto
quarto --version
```

#### ❌ "No se encontraron blogs"

**Problema:** La ruta de publicaciones es incorrecta

**Solución:**
```bash
# Verificar que existe
ls -la /home/achalmaedison/Documents/publicaciones

# Si la ruta es diferente, editar build.sh
nano /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh
# Cambiar PUBLICACIONES_DIR
```

#### ❌ "inspect muestra mucho código"

**Esto ya fue solucionado en v2.0** - Ahora solo muestra información relevante.

Si aún ves mucho código:
```bash
# Verificar que tienes v2.0
head -5 build.sh
# Debe decir: # Versión: 2.0
```

## 📚 Siguientes Pasos

### 1. Leer Documentación
```bash
# Ver ayuda completa
build.sh help

# Leer README
less README.md
```

### 2. Explorar Funcionalidades

```bash
# Modo interactivo
build.sh

# Probar cada opción del menú
```

### 3. Crear Contenido

```bash
# Crear un post real
build.sh new-post [tu-blog]

# Escribir contenido
# [Editar index.qmd]

# Preview mientras escribes
build.sh preview [tu-blog]

# Renderizar final
build.sh render [tu-blog]
```

### 4. Configurar Publicación

```bash
# GitHub Pages
build.sh publish [tu-blog] gh-pages

# Netlify
build.sh publish [tu-blog] netlify
```

## 🎓 Tutoriales Adicionales

### Tutorial 1: Flujo Básico

```bash
# 1. Crear post
build.sh new-post numerus-scriptum
# Seleccionar: python
# Título: "Mi Primer Post"
# Tipo: jou

# 2. Editar contenido
nano /path/to/post/index.qmd

# 3. Preview
build.sh preview numerus-scriptum

# 4. Renderizar
build.sh render numerus-scriptum
```

### Tutorial 2: Mantenimiento Semanal

```bash
# Limpiar archivos temporales
build.sh clean-all

# Renderizar todos los blogs
build.sh render-all

# Verificar estructura
check-structure.sh  # Si instalaste scripts auxiliares
```

### Tutorial 3: Personalización

```bash
# 1. Crear plantilla personalizada de post
nano ~/.config/quarto/post-template.qmd

# 2. Configurar editor preferido
export EDITOR="code"

# 3. Configurar aliases personalizados
# [Ver sección de aliases]
```

## 🔒 Seguridad y Respaldos

### Crear Respaldo Inicial

```bash
# Usar script de backup (si lo instalaste)
backup-blogs.sh

# O manualmente
tar -czf ~/publicaciones-backup-$(date +%Y%m%d).tar.gz \
    --exclude='_site' \
    --exclude='_freeze' \
    --exclude='.quarto' \
    /home/achalmaedison/Documents/publicaciones/
```

### Configurar Git (Recomendado)

```bash
# Para cada blog
cd /home/achalmaedison/Documents/publicaciones/[blog]
git init
git add .
git commit -m "Initial commit"
git remote add origin [tu-repo]
git push -u origin main
```

## 📞 Soporte

### Documentación
- README.md - Guía completa
- CHANGELOG.md - Historial de cambios
- Este archivo - Guía de instalación

### Recursos Online
- [Quarto Docs](https://quarto.org/docs/)
- [APAQuarto](https://wjschne.github.io/apaquarto/)

### Contacto
- **Email:** achalmaedison@gmail.com
- **GitHub:** @achalmed

---

## 📝 Notas Finales

### Compatibilidad
- ✅ Linux (todas las distribuciones)
- ✅ macOS
- ⚠️ Windows (requiere Git Bash o WSL)

### Actualizaciones

Para actualizar a versiones futuras:

```bash
# Respaldar configuración actual
cp build.sh build.sh.backup

# Reemplazar con nueva versión
cp build-new.sh build.sh

# Restaurar personalizaciones si es necesario
# (Comparar con backup)
```

### Desinstalación

Si deseas desinstalar:

```bash
# Eliminar script
rm /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh

# Eliminar aliases (editar ~/.bashrc manualmente)

# Los blogs y contenido NO se eliminan
```

---

**Versión:** 2.0  
**Última actualización:** 28 de enero de 2025  
**Autor:** Edison Achalma

¡Disfruta creando contenido con Quarto! 🚀