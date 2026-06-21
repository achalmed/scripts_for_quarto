# Changelog - Gestor de Publicaciones Quarto

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [2.0.0] - 2025-01-28

### 🎉 Características Principales Añadidas

#### Creación de Posts con APAQuarto

- ✨ **Formulario interactivo completo** para crear posts paso a paso
- ✨ **Soporte para 4 tipos de documentos**: doc, jou, man, stu
- ✨ **Detección automática** de carpetas de posts (eviews, python, matlab, etc.)
- ✨ **Integración inteligente con \_metadata.yml** para evitar duplicación
- ✨ **Generación automática** de estructura de archivos (index.qmd, references.bib)
- ✨ **Configuración de autor** predeterminado o personalizado
- ✨ **Metadata específica** según tipo de documento (journal, course, etc.)

#### Interfaz Visual Mejorada

- 🎨 **Colores y emojis** para mejor legibilidad
- 🎨 **Cajas decorativas** para encabezados importantes
- 🎨 **Separadores visuales** entre secciones
- 🎨 **Indicadores de estado** claros (✓, ✗, ⚠, ℹ)
- 🎨 **Menú interactivo renovado** con mejor organización
- 🎨 **Mensajes informativos** con iconos contextuales

#### Gestión de Blogs Mejorada

- 📁 **Exclusión automática** de blogs específicos:
  - apa
  - borradores
  - notas
  - practicas preprofesionales
  - propuesta bicentenario
  - taller unsch como elaborar tesis de pregrado
- 📁 **Función is_excluded_blog()** para filtrado eficiente
- 📁 **Listado mejorado** con información adicional:
  - Título del blog
  - Cantidad de posts
  - Estado de Git
- 📁 **Detección inteligente** de carpetas de posts

#### Inspección Optimizada

- 🔍 **Salida filtrada** sin código innecesario
- 🔍 **Solo información relevante** (Type, Engine, Formats, Output)
- 🔍 **Límite de 50 líneas** en salida sin filtro
- 🔍 **Formato mejorado** con colores tenues

#### Funciones Nuevas

- 📝 `create_post_interactive()` - Creación completa de posts
- 📝 `detect_post_folders()` - Detecta carpetas automáticamente
- 📝 `create_metadata_file()` - Genera \_metadata.yml
- 📝 `is_excluded_blog()` - Verifica exclusión de blogs
- 📝 `print_box()` - Crea cajas decorativas
- 📝 `print_step()` - Indicador de pasos del proceso
- 📝 `print_subheader()` - Subencabezados visuales

### 🔧 Mejoras Técnicas

#### Estructura de Código

- ♻️ **Refactorización completa** del código base
- ♻️ **Mejor organización** de funciones por categoría
- ♻️ **Comentarios mejorados** y documentación inline
- ♻️ **Constantes centralizadas** para configuración

#### Manejo de Datos

- 💾 **Detección automática** de estructura de blogs
- 💾 **Parseo inteligente** de archivos YAML
- 💾 **Validación de datos** en formularios
- 💾 **Generación dinámica** de metadata

#### Rendimiento

- ⚡ **Filtrado eficiente** de blogs excluidos
- ⚡ **Caché de detección** de carpetas
- ⚡ **Optimización** de operaciones batch
- ⚡ **Menor uso de recursos** en inspección

### 📚 Documentación

#### README

- 📖 **Reescritura completa** del README
- 📖 **Sección nueva**: Crear Posts con APAQuarto
- 📖 **Tabla comparativa** de tipos de documento
- 📖 **Ejemplos prácticos** extendidos
- 📖 **Interfaz visual** documentada con screenshots ASCII
- 📖 **Guía de integración** con \_metadata.yml

#### Ejemplos

- 💡 **Ejemplo completo** de creación de post
- 💡 **Workflow de publicación** documentado
- 💡 **Casos de uso** específicos por tipo de blog
- 💡 **Solución de problemas** ampliada

### 🐛 Correcciones

#### Bugs Resueltos

- **Inspeccionar** ya no muestra código innecesario de extensiones
- **Listado de posts** ahora agrupa correctamente por carpetas
- **Detección de blogs** excluye correctamente carpetas del sistema
- **Metadata** no se duplica entre \_metadata.yml e index.qmd

#### Validaciones

- **Verificación de existencia** de posts antes de crear
- **Validación de nombres** de carpetas y archivos
- **Comprobación de formato** de datos ingresados
- **Manejo de errores** mejorado en todas las funciones

### 🔄 Cambios en Comportamiento

#### Listado de Blogs

**Antes:**

```
Blogs Disponibles

1. actus-mercator
2. apa
3. borradores
```

**Ahora:**

```
═══════════════════════════════════════════════════════════════
  🚀 Blogs Disponibles
═══════════════════════════════════════════════════════════════

1. 📖 actus-mercator
   Blog de Comercio Internacional
   📄 15 posts
   🔧 Git inicializado
```

#### Inspección

**Antes:** Muestra ~200 líneas de código Lua y configuración

**Ahora:** Muestra solo:

```
═══════════════════════════════════════════════════════════════
  ℹ Inspeccionando: optimums
═══════════════════════════════════════════════════════════════

Type: website
Engine: markdown
Formats: html, pdf, docx
Output: _site/
```

#### Creación de Posts

**Antes:** Solo plantilla básica sin interacción

**Ahora:** Formulario completo con:

- Selección de carpeta
- Tipo de documento APAQuarto
- Metadata completa
- Configuración de autor
- Información específica por tipo

### ⚙️ Configuración

#### Variables Nuevas

```bash
EXCLUDED_BLOGS=(...)  # Lista de blogs a excluir
EMOJI_*              # Conjunto de emojis para UI
```

#### Rutas

- Sin cambios en rutas principales
- Compatible con configuración v1.0

### 🔐 Seguridad

- Validación de inputs de usuario
- Escape de caracteres especiales
- Prevención de sobrescritura accidental
- Confirmación en operaciones destructivas

### 📊 Estadísticas

- **Líneas de código**: ~1000 (desde ~868 en v1.0)
- **Funciones nuevas**: 7
- **Funciones mejoradas**: 12
- **Blogs soportados**: 12 activos + 6 excluidos
- **Tipos de documento APAQuarto**: 4 (doc, jou, man, stu)

### 🎯 Próximas Características (Planificadas)

#### v2.1

- [ ] Editar posts existentes
- [ ] Plantillas personalizadas de posts
- [ ] Búsqueda de posts por tags/categorías
- [ ] Estadísticas de blogs

#### v2.2

- [ ] Integración con editores externos
- [ ] Generación automática de TOC
- [ ] Exportación batch a PDF/DOCX
- [ ] Respaldos automáticos

### 🙏 Agradecimientos

- **Quarto Team**: Por crear esta increíble herramienta
- **WJSchne**: Por la extensión APAQuarto
- **Comunidad**: Por feedback y sugerencias

---

## [1.0.0] - 2024-12-28

### 🎉 Lanzamiento Inicial

#### Características Base

- Gestión básica de blogs
- Comandos de Quarto (render, preview, clean, publish)
- Operaciones batch
- Integración con Git
- Modo interactivo básico
- Creación simple de posts
- Scripts auxiliares (init-blog, check-structure, backup)

#### Comandos Implementados

- `list` - Listar blogs
- `render` - Renderizar blog
- `preview` - Preview local
- `clean` - Limpiar archivos
- `publish` - Publicar blog
- `new-post` - Crear post básico
- `render-all` - Batch rendering
- `clean-all` - Batch cleaning

#### Documentación

- README básico
- INSTALL.md
- Plantillas de ejemplo

---

## Formato del Changelog

Este changelog sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

### Tipos de Cambios

- **Added** (Añadido) - para nuevas características
- **Changed** (Cambiado) - para cambios en funcionalidad existente
- **Deprecated** (Obsoleto) - para características que pronto serán removidas
- **Removed** (Removido) - para características removidas
- **Fixed** (Corregido) - para corrección de bugs
- **Security** (Seguridad) - en caso de vulnerabilidades

---

**Mantenedor:** Edison Achalma  
**Última actualización:** 28 de enero de 2025
