# 🚀 Gestor de Publicaciones Quarto

Script completo para gestionar múltiples blogs y sitios web creados con Quarto. Diseñado específicamente para gestionar la estructura de publicaciones de Edison Achalma.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
  - [Modo Interactivo](#modo-interactivo)
  - [Línea de Comandos](#línea-de-comandos)
- [Comandos Disponibles](#comandos-disponibles)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Estructura de Directorios](#estructura-de-directorios)
- [Solución de Problemas](#solución-de-problemas)

## ✨ Características

### Gestión de Blogs
- ✅ Listar todos los blogs disponibles
- ✅ Renderizar blogs completos o individuales
- ✅ Preview local con servidor integrado
- ✅ Publicación a múltiples plataformas (GitHub Pages, Netlify, Quarto Pub)
- ✅ Limpieza de archivos generados
- ✅ Verificación e inspección de proyectos

### Gestión de Posts
- ✅ Crear nuevos posts con plantilla automática
- ✅ Listar posts de cualquier blog
- ✅ Renderizar posts individuales
- ✅ Estructura de nombres automática basada en fecha

### Operaciones Múltiples
- ✅ Renderizar todos los blogs en batch
- ✅ Limpiar todos los proyectos simultáneamente
- ✅ Operaciones en paralelo para mayor eficiencia

### Integración Git
- ✅ Inicialización de repositorios
- ✅ Commit y push automatizado
- ✅ Verificación de estado
- ✅ Creación automática de .gitignore

### Interfaz
- ✅ Modo interactivo con menú intuitivo
- ✅ Modo línea de comandos para automatización
- ✅ Colores y formato para mejor visualización
- ✅ Mensajes claros de éxito/error

## 📦 Requisitos

### Software Necesario

1. **Quarto** (versión 1.3 o superior)
   ```bash
   # Verificar instalación
   quarto --version
   ```
   Descargar desde: https://quarto.org/docs/get-started/

2. **Bash** (incluido en Linux/macOS)
   ```bash
   bash --version
   ```

3. **Git** (opcional, para funciones de Git)
   ```bash
   git --version
   ```

### Estructura de Directorios Requerida

```
/home/achalmaedison/Documents/
├── publicaciones/          # Directorio principal de blogs
│   ├── actus-mercator/
│   │   ├── index.qmd
│   │   ├── _quarto.yml
│   │   └── posts/
│   ├── aequilibria/
│   ├── axiomata/
│   └── ...
└── scripts/
    └── scripts_for_quarto/
        ├── build.sh        # Este script
        └── README.md
```

## 🔧 Instalación

### 1. Descargar el Script

```bash
# Crear directorio de scripts si no existe
mkdir -p /home/achalmaedison/Documents/scripts/scripts_for_quarto

# Navegar al directorio
cd /home/achalmaedison/Documents/scripts/scripts_for_quarto

# Descargar o copiar el script build.sh aquí
```

### 2. Dar Permisos de Ejecución

```bash
chmod +x build.sh
```

### 3. (Opcional) Añadir al PATH

Para ejecutar el script desde cualquier ubicación:

```bash
# Añadir al ~/.bashrc o ~/.zshrc
echo 'export PATH="$PATH:/home/achalmaedison/Documents/scripts/scripts_for_quarto"' >> ~/.bashrc

# Recargar configuración
source ~/.bashrc

# Ahora puedes ejecutar simplemente:
build.sh
```

### 4. (Opcional) Crear Alias

```bash
# Añadir al ~/.bashrc o ~/.zshrc
echo 'alias qbuild="/home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh"' >> ~/.bashrc

# Recargar
source ~/.bashrc

# Usar alias
qbuild list
```

## 🎯 Uso

### Modo Interactivo

La forma más sencilla de usar el script es en modo interactivo:

```bash
./build.sh
# o simplemente
./build.sh -i
# o
./build.sh interactive
```

Esto mostrará un menú con todas las opciones disponibles:

```
═══════════════════════════════════════════════════════════════
  🚀 Gestor de Publicaciones Quarto
═══════════════════════════════════════════════════════════════

Directorio: /home/achalmaedison/Documents/publicaciones

Opciones principales:
  1) Listar todos los blogs
  2) Renderizar blog específico
  3) Preview de blog
  4) Limpiar archivos generados
  5) Publicar blog
  ...
```

### Línea de Comandos

Para automatización o uso rápido:

```bash
./build.sh [COMANDO] [OPCIONES]
```

## 📖 Comandos Disponibles

### Gestión de Blogs

#### `list`
Lista todos los blogs disponibles con sus títulos.

```bash
./build.sh list
```

**Salida:**
```
═══════════════════════════════════════════════════════════════
  Blogs Disponibles
═══════════════════════════════════════════════════════════════

1. actus-mercator
   📖 Blog de Comercio Internacional

2. aequilibria
   📖 Economía y Equilibrio
...
```

#### `render BLOG`
Renderiza un blog completo.

```bash
./build.sh render website-achalma
./build.sh render epsilon-y-beta
```

**Proceso:**
1. Navega al directorio del blog
2. Ejecuta `quarto render`
3. Genera el sitio en `_site/`

#### `preview BLOG [PUERTO]`
Inicia servidor de preview local.

```bash
# Puerto por defecto (4200)
./build.sh preview axiomata

# Puerto personalizado
./build.sh preview numerus-scriptum 4300
```

**Características:**
- Servidor local con recarga automática
- No abre navegador automáticamente
- Ctrl+C para detener

#### `preview-browser BLOG [PUERTO]`
Preview con apertura automática del navegador.

```bash
./build.sh preview-browser chaska 4500
```

#### `clean BLOG`
Elimina archivos generados.

```bash
./build.sh clean actus-mercator
```

**Elimina:**
- `_site/` - Sitio generado
- `_freeze/` - Cache de ejecución
- `.quarto/` - Archivos temporales de Quarto

#### `publish BLOG [TARGET]`
Publica el blog en plataforma seleccionada.

```bash
# GitHub Pages (por defecto)
./build.sh publish website-achalma

# Netlify
./build.sh publish website-achalma netlify

# Quarto Pub
./build.sh publish epsilon-y-beta quarto-pub

# Confluence
./build.sh publish methodica confluence
```

**Targets disponibles:**
- `gh-pages` - GitHub Pages
- `netlify` - Netlify
- `quarto-pub` - Quarto Pub
- `confluence` - Confluence

#### `check BLOG`
Verifica configuración del blog.

```bash
./build.sh check aequilibria
```

**Verifica:**
- Instalación de Quarto
- Dependencias de R/Python
- Configuración YAML
- Extensiones

#### `inspect BLOG`
Inspecciona estructura del proyecto.

```bash
./build.sh inspect optimums
```

**Muestra:**
- Archivos del proyecto
- Configuración detectada
- Outputs esperados

### Gestión de Posts

#### `list-posts BLOG`
Lista todos los posts de un blog.

```bash
./build.sh list-posts epsilon-y-beta
```

**Salida:**
```
═══════════════════════════════════════════════════════════════
  Posts en epsilon-y-beta
═══════════════════════════════════════════════════════════════

1. 2021-03-01-01-modelo-clasico-de-regresion-lineal
   📄 Modelo Clásico de Regresión Lineal
   📂 /home/.../epsilon-y-beta/posts/2021-03-01-01-modelo-clasico...

2. 2021-03-08-02-el-estimador-de-minimos-cuadrados-ordinarios-mco
   📄 El Estimador de Mínimos Cuadrados Ordinarios
...
```

#### `render-post RUTA_POST`
Renderiza un post específico.

```bash
./build.sh render-post /home/achalmaedison/Documents/publicaciones/numerus-scriptum/python/2021-04-17-01-introducion-a-la-programacion-con-python/index.qmd
```

#### `new-post BLOG [TITULO]`
Crea un nuevo post con plantilla.

```bash
# Con título en comando
./build.sh new-post axiomata "Tutorial de Álgebra Lineal"

# Sin título (pedirá interactivamente)
./build.sh new-post chaska
```

**Crea:**
```
posts/2025-12-28-tutorial-de-algebra-lineal/
└── index.qmd
```

**Plantilla generada:**
```yaml
---
title: "Tutorial de Álgebra Lineal"
author: "Edison Achalma"
date: "2025-12-28"
categories: []
description: ""
draft: true
---

## Introducción

Tu contenido aquí...
```

### Operaciones Múltiples

#### `render-all`
Renderiza todos los blogs.

```bash
./build.sh render-all
```

**Proceso:**
- Recorre todos los directorios en `/publicaciones/`
- Renderiza cada blog encontrado
- Muestra resumen al final

**Salida:**
```
═══════════════════════════════════════════════════════════════
  Renderizando TODOS los blogs
═══════════════════════════════════════════════════════════════

ℹ Procesando: actus-mercator
✓ Blog renderizado exitosamente

ℹ Procesando: aequilibria
✓ Blog renderizado exitosamente
...

═══════════════════════════════════════════════════════════════
  Resumen
═══════════════════════════════════════════════════════════════
✓ Exitosos: 15
```

#### `clean-all`
Limpia todos los blogs (con confirmación).

```bash
./build.sh clean-all
```

**Solicita confirmación:**
```
¿Estás seguro? Esta acción eliminará todos los archivos generados (s/n):
```

### Integración Git

#### `git-init BLOG`
Inicializa repositorio Git.

```bash
./build.sh git-init pecunia-fluxus
```

**Crea:**
- Repositorio Git
- `.gitignore` con exclusiones apropiadas

**`.gitignore` generado:**
```
/.quarto/
/_site/
/_freeze/
/.Rproj.user/
.Rhistory
.RData
.DS_Store
```

#### `git-status BLOG`
Muestra estado de Git.

```bash
./build.sh git-status dialectica-y-mercado
```

#### `git-commit BLOG [MENSAJE]`
Commit y push de cambios.

```bash
# Con mensaje personalizado
./build.sh git-commit res-publica "Actualización de posts sobre administración pública"

# Mensaje por defecto
./build.sh git-commit methodica
```

**Proceso:**
1. `git add .`
2. `git commit -m "MENSAJE"`
3. `git push`

### Utilidades

#### `convert ARCHIVO [FORMATO]`
Convierte documento a otro formato.

```bash
# HTML (por defecto)
./build.sh convert documento.qmd

# PDF
./build.sh convert documento.qmd pdf

# Word
./build.sh convert documento.qmd docx
```

**Formatos soportados:**
- `html`
- `pdf`
- `docx`
- `revealjs` (presentaciones)
- `beamer` (presentaciones PDF)

#### `help`, `-h`, `--help`
Muestra ayuda completa.

```bash
./build.sh help
```

#### `version`, `-v`
Muestra versión de Quarto.

```bash
./build.sh version
```

## 💡 Ejemplos Prácticos

### Flujo de Trabajo Típico

#### 1. Crear y Desarrollar Nuevo Post

```bash
# Crear nuevo post
./build.sh new-post epsilon-y-beta "Análisis de Series Temporales"

# El script abre el editor y comienzas a escribir...

# Preview mientras escribes
./build.sh preview epsilon-y-beta

# Renderizar cuando termines
./build.sh render epsilon-y-beta
```

#### 2. Actualizar Blog Existente

```bash
# Ver estado actual
./build.sh git-status website-achalma

# Limpiar archivos antiguos
./build.sh clean website-achalma

# Renderizar versión fresca
./build.sh render website-achalma

# Commit y publicar
./build.sh git-commit website-achalma "Actualización de diciembre"
./build.sh publish website-achalma
```

#### 3. Mantenimiento General

```bash
# Listar todos los blogs
./build.sh list

# Verificar configuración de un blog específico
./build.sh check axiomata

# Renderizar todos los blogs (útil para verificación)
./build.sh render-all

# Limpiar todo antes de backup
./build.sh clean-all
```

#### 4. Trabajo en Post Específico

```bash
# Listar posts de un blog
./build.sh list-posts numerus-scriptum

# Renderizar solo ese post
./build.sh render-post /home/achalmaedison/Documents/publicaciones/numerus-scriptum/python/2021-04-17-01-introducion-a-la-programacion-con-python/index.qmd
```

### Casos de Uso Avanzados

#### Publicación Multi-Plataforma

```bash
# Publicar en GitHub Pages
./build.sh publish website-achalma gh-pages

# Publicar en Netlify para staging
./build.sh publish website-achalma netlify

# Publicar versión final en Quarto Pub
./build.sh publish website-achalma quarto-pub
```

#### Automatización con Cron

```bash
# Editar crontab
crontab -e

# Renderizar todos los blogs diariamente a las 2 AM
0 2 * * * /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh render-all >> /tmp/quarto-render.log 2>&1

# Limpiar archivos temporales semanalmente
0 3 * * 0 /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh clean-all
```

#### Scripts de Integración Continua

```bash
#!/bin/bash
# deploy.sh - Script de despliegue

SCRIPT="/home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh"

# Limpiar y renderizar
$SCRIPT clean website-achalma
$SCRIPT render website-achalma

# Verificar que no hay errores
if [ $? -eq 0 ]; then
    # Commit y publicar
    $SCRIPT git-commit website-achalma "Deploy automático $(date)"
    $SCRIPT publish website-achalma gh-pages
else
    echo "Error en renderizado, abortando deploy"
    exit 1
fi
```

## 📁 Estructura de Directorios

### Estructura Esperada de un Blog

```
blog-name/
├── index.qmd                    # Página principal
├── _quarto.yml                  # Configuración del blog
├── _metadata.yml               # (Opcional) Metadatos globales
├── about.qmd                   # (Opcional) Página sobre
├── assets/                     # Recursos estáticos
│   ├── fonts/
│   └── img/
├── _extensions/                # Extensiones de Quarto
│   └── quarto-ext/
├── posts/                      # Directorio de posts
│   ├── YYYY-MM-DD-titulo-post-1/
│   │   ├── index.qmd
│   │   └── images/
│   └── YYYY-MM-DD-titulo-post-2/
│       └── index.qmd
├── _site/                      # Sitio generado (ignorar)
├── _freeze/                    # Cache (ignorar)
├── .quarto/                    # Temporal (ignorar)
└── .gitignore
```

### Archivos Clave

#### `_quarto.yml`
```yaml
project:
  type: website
  output-dir: _site

website:
  title: "Mi Blog"
  navbar:
    left:
      - href: index.qmd
        text: Inicio
      - about.qmd

format:
  html:
    theme: cosmo
    css: styles.css
```

#### `index.qmd`
```yaml
---
title: "Mi Blog"
listing:
  contents: posts
  sort: "date desc"
  type: default
  categories: true
---
```

## 🔍 Solución de Problemas

### Problema: Script no ejecuta

**Síntomas:**
```bash
$ ./build.sh
bash: ./build.sh: Permission denied
```

**Solución:**
```bash
chmod +x build.sh
```

### Problema: Quarto no encontrado

**Síntomas:**
```
✗ Quarto no está instalado
```

**Solución:**
```bash
# Verificar instalación
which quarto

# Si no está instalado, descargar de:
# https://quarto.org/docs/get-started/

# Verificar que está en PATH
echo $PATH

# Añadir al PATH si es necesario
export PATH="$PATH:/opt/quarto/bin"
```

### Problema: Blog no encontrado

**Síntomas:**
```
✗ Blog no encontrado: mi-blog
```

**Solución:**
```bash
# Verificar nombre exacto
./build.sh list

# Usar el nombre exacto del directorio
./build.sh render nombre-exacto-del-blog
```

### Problema: Error al renderizar

**Síntomas:**
```
✗ Error al renderizar el blog
```

**Verificaciones:**

1. **Verificar sintaxis YAML:**
```bash
./build.sh check nombre-blog
```

2. **Verificar estructura:**
```bash
./build.sh inspect nombre-blog
```

3. **Revisar logs:**
```bash
cd /home/achalmaedison/Documents/publicaciones/nombre-blog
quarto render --verbose
```

4. **Limpiar cache:**
```bash
./build.sh clean nombre-blog
./build.sh render nombre-blog
```

### Problema: Git push falla

**Síntomas:**
```
⚠ No se pudo hacer push. ¿Necesitas configurar el remote?
```

**Solución:**
```bash
cd /home/achalmaedison/Documents/publicaciones/nombre-blog

# Verificar remote
git remote -v

# Si no hay remote, añadir
git remote add origin https://github.com/usuario/repo.git

# Configurar upstream
git push -u origin main
```

### Problema: Puerto en uso

**Síntomas:**
```
Error: Port 4200 already in use
```

**Solución:**
```bash
# Usar puerto diferente
./build.sh preview nombre-blog 4300

# O matar proceso en puerto 4200
lsof -ti:4200 | xargs kill -9
```

## 🎨 Personalización

### Cambiar Directorios por Defecto

Editar variables al inicio del script:

```bash
# En build.sh, líneas 15-16
PUBLICACIONES_DIR="/ruta/personalizada/publicaciones"
SCRIPT_DIR="/ruta/personalizada/scripts"
```

### Añadir Nuevos Comandos

1. Crear función en sección de funciones:

```bash
# Nueva función
mi_comando() {
    local blog_path="$1"
    print_header "Mi Comando Personalizado"
    
    # Tu código aquí
    cd "$blog_path"
    # ...
    
    print_success "Comando ejecutado"
}
```

2. Añadir caso en la función `main`:

```bash
case "$1" in
    # ... casos existentes ...
    
    mi-comando)
        if [ -z "$2" ]; then
            print_error "Especifica el nombre del blog"
            exit 1
        fi
        mi_comando "$PUBLICACIONES_DIR/$2"
        ;;
```

3. Actualizar ayuda y menú interactivo.

### Cambiar Plantilla de Posts

Modificar la función `create_post`:

```bash
# Línea ~450 en build.sh
cat > "$post_dir/index.qmd" << EOF
---
title: "$post_title"
author: "Tu Nombre"
date: "$date"
categories: [tutorial, programación]
description: "Descripción automática"
image: "thumbnail.jpg"
draft: false
---

## Resumen

Resumen del post...

## Contenido Principal

Tu contenido aquí...

## Conclusiones

Conclusiones del post...

## Referencias
EOF
```

## 📚 Referencias

- [Documentación Quarto](https://quarto.org/docs/guide/)
- [Quarto Publishing](https://quarto.org/docs/publishing/)
- [Quarto CLI Reference](https://quarto.org/docs/reference/)
- [GitHub Pages con Quarto](https://quarto.org/docs/publishing/github-pages.html)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)

## 📝 Notas Adicionales

### Compatibilidad

- **Linux:** Totalmente compatible
- **macOS:** Totalmente compatible
- **Windows:** Requiere Git Bash o WSL

### Rendimiento

- Renderizado individual: ~5-30 segundos por blog
- Renderizado completo: Varía según cantidad de posts
- Preview: Inicio instantáneo

### Seguridad

- No ejecuta comandos remotos
- No modifica archivos fuera de directorios configurados
- Pide confirmación en operaciones destructivas

### Actualizaciones

Para actualizar el script:

```bash
cd /home/achalmaedison/Documents/scripts/scripts_for_quarto
# Descargar nueva versión
# Verificar cambios
./build.sh version
```

## 🤝 Contribuciones

Este script es de uso personal pero puede ser adaptado según necesidades.

### Sugerencias de Mejora

- Añadir soporte para más formatos de exportación
- Integración con más plataformas de publicación
- Generación automática de thumbnails
- Análisis de métricas del sitio
- Optimización de imágenes automática

---

**Versión:** 1.0.0  
**Fecha:** Diciembre 2025  
**Autor:** Edison Achalma  
**Licencia:** Uso personal

Para reportar problemas o sugerencias, crear un issue en el repositorio correspondiente.
