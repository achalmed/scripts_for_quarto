# 📦 Paquete Completo de Scripts para Quarto

## Archivos Incluidos

### 1. **build.sh** (Script Principal) ⭐
   - **Tamaño:** 25 KB
   - **Descripción:** Script principal con todas las funcionalidades
   - **Características:**
     - Modo interactivo con menú completo
     - Gestión de blogs (render, preview, publish, clean)
     - Gestión de posts (crear, listar, renderizar)
     - Operaciones múltiples (render-all, clean-all)
     - Integración con Git (init, status, commit)
     - Utilidades avanzadas
   - **Comandos:** 16+ comandos diferentes

### 2. **README.md** (Documentación Completa)
   - **Tamaño:** 20 KB
   - **Contenido:**
     - Guía completa de uso
     - Todos los comandos explicados con ejemplos
     - Casos de uso prácticos
     - Solución de problemas
     - Personalización
     - Referencias y recursos

### 3. **INSTALL.md** (Guía de Instalación)
   - **Tamaño:** 3.4 KB
   - **Contenido:**
     - Pasos de instalación paso a paso
     - Configuración de aliases
     - Verificación de instalación
     - Solución rápida de problemas

### 4. **init-blog.sh** (Inicializador de Blogs)
   - **Tamaño:** 3.2 KB
   - **Función:** Crear nuevos blogs con estructura completa
   - **Crea:**
     - Estructura de directorios
     - _quarto.yml configurado
     - index.qmd y about.qmd
     - styles.css
     - .gitignore
     - README.md

### 5. **check-structure.sh** (Verificador)
   - **Tamaño:** 4.9 KB
   - **Función:** Verificar integridad de todos los blogs
   - **Verifica:**
     - Archivos esenciales
     - Estructura de directorios
     - Configuración Git
     - Sintaxis YAML
   - **Genera:** Reporte detallado con estadísticas

### 6. **backup-blogs.sh** (Sistema de Backups)
   - **Tamaño:** 5.0 KB
   - **Funciones:**
     - Backup individual por blog
     - Backup completo de todas las publicaciones
     - Backup incremental con rsync
     - Gestión automática de backups antiguos
   - **Características:**
     - Excluye archivos generados
     - Compresión automática
     - Reportes de tamaño

### 7. **config.sh** (Configuración)
   - **Tamaño:** 2.4 KB
   - **Contiene:**
     - Variables de configuración centralizadas
     - Aliases útiles
     - Funciones de acceso rápido
     - Configuración de Git

## Instalación Rápida

```bash
# 1. Copiar archivos
cp *.sh *.md /home/achalmaedison/Documents/scripts/scripts_for_quarto/

# 2. Dar permisos
cd /home/achalmaedison/Documents/scripts/scripts_for_quarto
chmod +x *.sh

# 3. Añadir al PATH (opcional)
echo 'export PATH="$PATH:/home/achalmaedison/Documents/scripts/scripts_for_quarto"' >> ~/.bashrc
source ~/.bashrc

# 4. Crear aliases (opcional)
cat >> ~/.bashrc << 'EOF'
alias qbuild="build.sh"
alias qlist="build.sh list"
alias qcheck="check-structure.sh"
alias qbackup="backup-blogs.sh"
EOF
source ~/.bashrc

# 5. ¡Listo! Probar
qbuild list
```

## Uso Rápido

### Comandos Más Usados

```bash
# Modo interactivo (recomendado para empezar)
build.sh

# Listar blogs
build.sh list

# Renderizar blog
build.sh render nombre-blog

# Preview
build.sh preview nombre-blog

# Crear post
build.sh new-post nombre-blog "Título del Post"

# Verificar estructura
check-structure.sh

# Backup
backup-blogs.sh
```

## Características Destacadas

### ✅ Gestión Completa
- Todos los comandos de Quarto integrados
- Modo interactivo amigable
- Modo CLI para automatización

### ✅ Organización
- Gestión de múltiples blogs simultáneamente
- Operaciones batch eficientes
- Estructura de directorios clara

### ✅ Git Integration
- Inicialización automática de repositorios
- Commit y push simplificados
- Verificación de estado

### ✅ Utilidades
- Sistema de backups completo
- Verificación de integridad
- Creación rápida de nuevos blogs

### ✅ Interfaz
- Colores y formato legible
- Mensajes claros de éxito/error
- Ayuda contextual

## Estructura de Tu Proyecto

```
/home/achalmaedison/Documents/
├── publicaciones/                    # Tus blogs
│   ├── website-achalma/
│   ├── epsilon-y-beta/
│   ├── numerus-scriptum/
│   └── [15+ blogs más]
│
├── scripts/
│   └── scripts_for_quarto/          # Scripts instalados aquí
│       ├── build.sh                  ⭐ Principal
│       ├── init-blog.sh              🆕 Crear blogs
│       ├── check-structure.sh        ✓ Verificar
│       ├── backup-blogs.sh           💾 Backups
│       ├── config.sh                 ⚙️ Config
│       ├── README.md                 📖 Docs
│       └── INSTALL.md                🚀 Guía
│
└── backups/                          # Creado por backup-blogs.sh
    └── publicaciones/
        ├── website-achalma_20251228.tar.gz
        └── ...
```

## Workflows Recomendados

### Desarrollo de Post
```bash
# 1. Crear post
build.sh new-post epsilon-y-beta "Análisis Econométrico"

# 2. Preview mientras escribes
build.sh preview epsilon-y-beta

# 3. Renderizar final
build.sh render epsilon-y-beta

# 4. Publicar
build.sh git-commit epsilon-y-beta "Nuevo post sobre econometría"
build.sh publish epsilon-y-beta
```

### Mantenimiento Semanal
```bash
# 1. Verificar estructura
check-structure.sh

# 2. Renderizar todos
build.sh render-all

# 3. Backup
backup-blogs.sh

# 4. Limpiar temporales
build.sh clean-all
```

### Inicio de Nuevo Blog
```bash
# 1. Crear estructura
init-blog.sh mi-nuevo-blog "Mi Nuevo Blog"

# 2. Inicializar Git
build.sh git-init mi-nuevo-blog

# 3. Crear primer post
build.sh new-post mi-nuevo-blog "Primer Post"

# 4. Preview
build.sh preview mi-nuevo-blog
```

## Comandos Completos Disponibles

### build.sh (Principal)
1. `list` - Listar blogs
2. `render BLOG` - Renderizar blog
3. `preview BLOG [PORT]` - Preview
4. `preview-browser BLOG` - Preview con browser
5. `clean BLOG` - Limpiar archivos
6. `publish BLOG [TARGET]` - Publicar
7. `check BLOG` - Verificar configuración
8. `inspect BLOG` - Inspeccionar estructura
9. `list-posts BLOG` - Listar posts
10. `render-post PATH` - Renderizar post
11. `new-post BLOG [TITLE]` - Crear post
12. `render-all` - Renderizar todos
13. `clean-all` - Limpiar todos
14. `git-init BLOG` - Inicializar Git
15. `git-status BLOG` - Estado Git
16. `git-commit BLOG [MSG]` - Commit y push
17. `convert FILE [FORMAT]` - Convertir documento
18. `interactive, -i` - Modo interactivo
19. `help, -h` - Ayuda
20. `version, -v` - Versión

### Otros Scripts
- `init-blog.sh NOMBRE "TITULO"` - Crear blog nuevo
- `check-structure.sh` - Verificar todos los blogs
- `backup-blogs.sh` - Sistema de backups interactivo

## Personalización

### Cambiar Directorios
Editar en `build.sh` (líneas 15-16):
```bash
PUBLICACIONES_DIR="/tu/ruta/personalizada"
SCRIPT_DIR="/tu/ruta/scripts"
```

### Cambiar Plantilla de Posts
Editar función `create_post` en `build.sh` (línea ~450)

### Añadir Comandos
1. Crear función en `build.sh`
2. Añadir caso en función `main`
3. Actualizar ayuda y menú

## Soporte y Ayuda

### Documentación
- `README.md` - Guía completa y detallada
- `INSTALL.md` - Guía de instalación
- `build.sh help` - Ayuda en línea

### Resolución de Problemas
Consulta la sección "Solución de Problemas" en `README.md`

### Verificación
```bash
# Verificar instalación
quarto --version

# Probar scripts
build.sh version
check-structure.sh
```

## Notas Importantes

1. **Quarto Requerido:** Asegúrate de tener Quarto instalado
2. **Permisos:** Los scripts necesitan permisos de ejecución
3. **Backups:** Recomendado hacer backup antes de operaciones masivas
4. **Git:** Algunas funciones requieren Git instalado

## Contacto

**Autor:** Edison Achalma  
**Email:** achalmaedison@gmail.com  
**GitHub:** @achalmed  
**Ubicación:** Ayacucho, Perú

---

## 🎉 ¡Listo para Usar!

Todos los scripts están listos y documentados. Lee el `INSTALL.md` para comenzar.

**Siguiente paso:** `cat INSTALL.md`
