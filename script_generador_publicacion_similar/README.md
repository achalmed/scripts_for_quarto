# Generador de Índices de Contenido para Blogs Quarto
#readme

## 📋 Descripción

Script Bash que genera automáticamente archivos de índice (.qmd) para blogs Quarto. **Soporta dos estructuras diferentes**:

1. **Página web completa** (con nivel blog/)
2. **Blog independiente** (sin nivel blog/)

## 🎯 Estructuras Soportadas

### Estructura 1: Página Web Completa
```
mi-sitio/
├── blog/                          # ← Nivel extra
│   ├── posts/
│   │   ├── 2023-05-12-titulo/
│   │   │   └── index.qmd
│   │   └── _contenido_posts.qmd  # ← Generado
│   ├── index.qmd
│   └── sidebar.jpg
└── ...
```

**URL generada:** `https://dominio.com/blog/posts/2023-05-12-titulo/`

### Estructura 2: Blog Independiente
```
actus-mercator/
├── posts/                         # ← Directo, sin blog/
│   ├── 2022-01-23-titulo/
│   │   └── index.qmd
│   └── _contenido_posts.qmd      # ← Generado
├── inteligencia-comercial/
│   ├── 2025-05-15-titulo/
│   │   └── index.qmd
│   └── _contenido_inteligencia-comercial.qmd  # ← Generado
└── index.qmd
```

**URL generada:** `https://dominio.com/posts/2022-01-23-titulo/`

## 🚀 Instalación y Configuración

### 1. Descargar el Script
```bash
# Crear directorio para scripts
mkdir -p ~/scripts

# Descargar o crear el script
cd ~/scripts
nano generar_indices.sh
# [Pegar el contenido del script]

# Dar permisos de ejecución
chmod +x generar_indices.sh
```

### 2. Configurar Variables

Editar las siguientes líneas según tu proyecto:
```bash
# CONFIGURACIÓN PARA PÁGINA WEB
main_blog="/home/usuario/proyectos/mi-sitio/blog"
base_url="https://achalmaedison.netlify.app"
blog_type="auto"  # Detecta automáticamente

# CONFIGURACIÓN PARA BLOG INDEPENDIENTE
main_blog="/home/usuario/proyectos/actus-mercator"
base_url="https://actus-mercator.netlify.app"
blog_type="auto"  # Detecta automáticamente
```

**Opciones para `blog_type`:**
- `"auto"` - Detecta automáticamente (recomendado)
- `"website"` - Fuerza estructura de página web (blog/posts/)
- `"blog"` - Fuerza estructura de blog independiente (posts/)

### 3. Crear Alias (Opcional)

Para ejecutar desde cualquier directorio:
```bash
# Agregar al .bashrc o .zshrc
echo 'alias generar-indices="~/scripts/generar_indices.sh"' >> ~/.bashrc
source ~/.bashrc
```

## 💻 Uso

### Uso Básico
```bash
# Ejecutar directamente
cd ~/scripts
./generar_indices.sh
```

### Uso con Alias
```bash
# Desde cualquier directorio
generar-indices
```

### Procesar Múltiples Blogs

**Opción 1: Cambiar configuración**
```bash
# Editar el script antes de ejecutar
nano ~/scripts/generar_indices.sh
# Cambiar main_blog y base_url
# Guardar y ejecutar
./generar_indices.sh
```

**Opción 2: Crear scripts específicos**
```bash
cd ~/scripts

# Para página web
cp generar_indices.sh generar_indices_web.sh
nano generar_indices_web.sh
# Configurar: main_blog="/ruta/a/sitio/blog"
#            base_url="https://achalmaedison.netlify.app"

# Para blog independiente
cp generar_indices.sh generar_indices_actus.sh
nano generar_indices_actus.sh
# Configurar: main_blog="/ruta/a/actus-mercator"
#            base_url="https://actus-mercator.netlify.app"

# Crear alias
echo 'alias indices-web="~/scripts/generar_indices_web.sh"' >> ~/.bashrc
echo 'alias indices-actus="~/scripts/generar_indices_actus.sh"' >> ~/.bashrc
source ~/.bashrc
```

## 📖 Ejemplos de Salida

### Para Página Web (`blog/posts/`)

**Archivo generado:** `blog/posts/_contenido_posts.qmd`
```markdown
1. [{{< fa regular file-pdf >}}](https://achalmaedison.netlify.app/blog/posts/2023-05-12-la-economia-peruana-entre-1970-1990/index.pdf) [La Economia Peruana Entre 1970 1990](https://achalmaedison.netlify.app/blog/posts/2023-05-12-la-economia-peruana-entre-1970-1990)
2. [{{< fa regular file-pdf >}}](https://achalmaedison.netlify.app/blog/posts/2023-05-16-economia-regional/index.pdf) [Economia Regional](https://achalmaedison.netlify.app/blog/posts/2023-05-16-economia-regional)
```

### Para Blog Independiente (`posts/`)

**Archivo generado:** `posts/_contenido_posts.qmd`
```markdown
1. [{{< fa regular file-pdf >}}](https://actus-mercator.netlify.app/posts/2022-01-23-cadena-de-suministros/index.pdf) [Cadena De Suministros](https://actus-mercator.netlify.app/posts/2022-01-23-cadena-de-suministros)
2. [{{< fa regular file-pdf >}}](https://actus-mercator.netlify.app/posts/2021-07-13-plan-de-negocio-exportacion-de-tuna/index.pdf) [Plan De Negocio Exportacion De Tuna](https://actus-mercator.netlify.app/posts/2021-07-13-plan-de-negocio-exportacion-de-tuna)
```

## 📊 Log de Ejecución
```
[2025-01-19 15:30:00] ℹ️  Estructura detectada automáticamente: blog
[2025-01-19 15:30:00] ℹ️  Iniciando procesamiento del blog: /home/usuario/actus-mercator
[2025-01-19 15:30:00] ℹ️  URL base configurada: https://actus-mercator.netlify.app
[2025-01-19 15:30:00] ℹ️  Tipo de estructura: blog
[2025-01-19 15:30:00] ℹ️  Procesando subblog: posts
[2025-01-19 15:30:00] ✅ Generado: /home/usuario/actus-mercator/posts/_contenido_posts.qmd (15 publicaciones)
[2025-01-19 15:30:00] ℹ️  Procesando subblog: inteligencia-comercial
[2025-01-19 15:30:00] ✅ Generado: /home/usuario/actus-mercator/inteligencia-comercial/_contenido_inteligencia-comercial.qmd (8 publicaciones)

════════════════════════════════════════════════════════════════
[2025-01-19 15:30:00] ✅ Proceso completado exitosamente
[2025-01-19 15:30:00] ℹ️  Total de archivos de índice generados: 2
[2025-01-19 15:30:00] ℹ️  Total de publicaciones procesadas: 23
[2025-01-19 15:30:00] ℹ️  Estructura utilizada: blog
════════════════════════════════════════════════════════════════
```

## ❓ Solución de Problemas

### El script no detecta la estructura correctamente
```bash
# Forzar el tipo manualmente
blog_type="blog"      # Para blogs independientes
# o
blog_type="website"   # Para páginas web
```

### Las URLs no son correctas

1. Verificar que `base_url` NO tenga barra final
2. Confirmar el valor de `blog_type`
3. Revisar la estructura real de tu sitio

### Carpetas ignoradas

El script ignora automáticamente:
- Carpetas que empiezan con `_` o `.`
- `site_libs`, `_partials`, etc.

Para ajustar, edita la sección:
```bash
if [[ "$subblog_name" =~ ^[._] ]] || \
   [[ "$subblog_name" == "tu_carpeta_a_ignorar" ]]; then
    continue
fi
```

## 🔄 Integración con Quarto

### Incluir el índice en otro archivo
```markdown
---
title: "Mi Blog"
---

## Publicaciones Recientes

{{< include posts/_contenido_posts.qmd >}}
```

### Workflow automatizado
```bash
#!/bin/bash
# Script para regenerar índices y renderizar

# Generar índices
~/scripts/generar_indices.sh

# Renderizar el sitio
quarto render

echo "✅ Sitio actualizado con nuevos índices"
```

## 👤 Autor

**Edison Achalma**
- Website: [achalmaedison.netlify.app](https://achalmaedison.netlify.app)
- Blog: [actus-mercator.netlify.app](https://actus-mercator.netlify.app)
- GitHub: [@achalmed](https://github.com/achalmed)

---

⭐ **Tip**: Ejecuta este script cada vez que agregues nuevas publicaciones para mantener tus índices actualizados automáticamente.