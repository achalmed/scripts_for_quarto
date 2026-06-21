# 🎉 ¡Nueva Versión 2.0 Disponible!

## 📦 Resumen de Actualización

Has recibido la versión **2.0** completamente renovada del Gestor de Publicaciones Quarto.

### 🚀 Lo Más Destacado

#### 1. Creación de Posts con APAQuarto (¡NUEVA!)

**Antes (v1.0):**

```bash
./build.sh new-post mi-blog "Título"
# Creaba solo un archivo básico
```

**Ahora (v2.0):**

```bash
./build.sh new-post mi-blog
# Formulario interactivo completo:
# - Detecta carpetas automáticamente (python, r, matlab, etc.)
# - Soporta 4 tipos de documentos (doc/jou/man/stu)
# - Integra con _metadata.yml
# - Configuración de autor flexible
# - Genera estructura completa APA
```

#### 2. Interfaz Visual Renovada

**Antes:** Texto plano sin colores

**Ahora:** Interfaz moderna con:

- ✅ Emojis contextuales (🚀📖📄🔧)
- ✅ Colores para mejor legibilidad
- ✅ Cajas y separadores visuales
- ✅ Indicadores de estado claros

#### 3. Gestión Inteligente de Blogs

**Nuevo:** Excluye automáticamente blogs innecesarios:

- borradores
- notas
- apa
- practicas preprofesionales
- propuesta bicentenario
- taller unsch como elaborar tesis de pregrado

**Nuevo:** Listado mejorado muestra:

- Título del blog
- Cantidad de posts
- Estado de Git

#### 4. Inspección Optimizada

**Antes:** Mostraba 200+ líneas de código Lua

**Ahora:** Solo información relevante:

- Type, Engine, Formats, Output
- Máximo 50 líneas
- Sin código innecesario

## 📋 Archivos Incluidos

### Scripts

- ✅ **build.sh** (v2.0) - Script principal con todas las mejoras

### Documentación

- ✅ **README.md** - Guía completa actualizada
- ✅ **INSTALL.md** - Instalación paso a paso
- ✅ **CHANGELOG.md** - Historial detallado de cambios
- ✅ **ACTUALIZACION.md** - Este archivo

### Scripts Auxiliares (de v1.0 - aún funcionales)

- ✅ **init-blog.sh** - Crear nuevos blogs
- ✅ **check-structure.sh** - Verificar estructura
- ✅ **backup-blogs.sh** - Sistema de backups
- ✅ **config.sh** - Configuración centralizada

## 🔄 Cómo Actualizar

### Si Ya Tienes v1.0 Instalada

```bash
# 1. Respaldar versión actual (por si acaso)
cp /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh \
   /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh.v1.backup

# 2. Reemplazar con v2.0
cp build.sh /home/achalmaedison/Documents/scripts/scripts_for_quarto/

# 3. Dar permisos
chmod +x /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh

# 4. Verificar versión
build.sh version
```

### Si Es Tu Primera Instalación

```bash
# Seguir guía completa en INSTALL.md
cat INSTALL.md
```

## ✨ Nuevas Características en Detalle

### 1. Tipos de Documento APAQuarto

| Tipo    | Descripción             | Ideal Para                  |
| ------- | ----------------------- | --------------------------- |
| **doc** | Documento flexible      | Ensayos, reportes generales |
| **jou** | Formato revista (2 col) | Artículos publicados        |
| **man** | Manuscrito formal       | Envío a revistas            |
| **stu** | Trabajo estudiantil     | Tareas, tesis               |

### 2. Detección Automática de Carpetas

El script detecta automáticamente carpetas como:

- python, r, matlab, stata
- eviews, latex, ofimatica
- Cualquier carpeta con estructura de posts

### 3. Integración con \_metadata.yml

**Inteligente:** No duplica información

- **En \_metadata.yml:** Configuración compartida (autor, formatos, ejecución)
- **En index.qmd:** Específico del post (título, tags, fecha)

### 4. Formulario Guiado

El script te guía paso a paso:

1. ✅ Seleccionar carpeta de posts
2. ✅ Ingresar información básica
3. ✅ Elegir tipo de documento
4. ✅ Añadir metadatos
5. ✅ Configurar autor
6. ✅ Info específica del tipo

## 📊 Comparativa de Versiones

| Característica         | v1.0 | v2.0 |
| ---------------------- | ---- | ---- |
| Crear posts básicos    | ✅   | ✅   |
| APAQuarto              | ❌   | ✅   |
| Formulario interactivo | ❌   | ✅   |
| Detección de carpetas  | ❌   | ✅   |
| \_metadata.yml         | ❌   | ✅   |
| Interfaz con colores   | ❌   | ✅   |
| Excluir blogs          | ❌   | ✅   |
| Inspección optimizada  | ❌   | ✅   |
| Listado mejorado       | ❌   | ✅   |

## 🎯 Casos de Uso Principales

### Caso 1: Crear Post de Econometría

```bash
$ build.sh new-post epsilon-y-beta

# Seleccionar carpeta: "econometria-aplicada"
# Título: "Modelos ARIMA en R"
# Tipo: jou (formato revista)
# Tags: econometría, r, series temporales
# Categorías: análisis, tutorial

✓ Post creado con estructura APA completa
```

### Caso 2: Post de Programación

```bash
$ build.sh new-post numerus-scriptum

# Carpeta: python
# Título: "Análisis de Datos con Pandas"
# Tipo: doc (flexible)
# [Completar formulario]

✓ Listo para escribir código Python
```

### Caso 3: Trabajo Estudiantil

```bash
$ build.sh new-post [blog]

# Tipo: stu
# Curso: "Econometría II"
# Profesor: "Dr. Juan Pérez"
# Fecha entrega: "15/12/2024"

✓ Formato estudiantil con información del curso
```

## 🛠️ Compatibilidad

### Blogs Soportados

**Activos (12):**

- actus-mercator
- aequilibria
- axiomata
- chaska
- dialectica-y-mercado
- epsilon-y-beta
- methodica
- numerus-scriptum
- optimums
- pecunia-fluxus
- res-publica
- website-achalma

**Excluidos (6):**

- apa, borradores, notas
- practicas preprofesionales
- propuesta bicentenario
- taller unsch...

### Configuración Existente

✅ **Totalmente compatible** con:

- Blogs creados en v1.0
- Scripts auxiliares (init-blog, check-structure, backup)
- Aliases configurados
- PATH personalizado

## 📚 Documentación Actualizada

### README.md

- ✅ Reescrito completamente
- ✅ Sección nueva: APAQuarto
- ✅ Ejemplos visuales
- ✅ Tabla comparativa de tipos
- ✅ Interfaz documentada

### INSTALL.md

- ✅ Guía paso a paso actualizada
- ✅ Troubleshooting ampliado
- ✅ Configuración avanzada
- ✅ Tutoriales incluidos

### CHANGELOG.md

- ✅ Historial completo de cambios
- ✅ Detalles técnicos
- ✅ Comparativas de comportamiento
- ✅ Roadmap de futuras versiones

## 🐛 Bugs Resueltos

- ✅ Inspección ya no muestra código innecesario
- ✅ Listado de posts agrupa correctamente
- ✅ Detección de blogs más precisa
- ✅ Metadata no se duplica

## 🎓 Primeros Pasos con v2.0

### 1. Instalar/Actualizar

```bash
# Ver INSTALL.md para detalles
cp build.sh /home/achalmaedison/Documents/scripts/scripts_for_quarto/
chmod +x /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh
```

### 2. Explorar Interfaz

```bash
# Modo interactivo
build.sh

# Listar blogs (nota la nueva presentación)
build.sh list
```

### 3. Crear Tu Primer Post APAQuarto

```bash
# Iniciar creación interactiva
build.sh new-post [tu-blog]

# Seguir el formulario guiado
# ¡Disfruta la nueva experiencia!
```

### 4. Leer Documentación

```bash
# Ver ayuda completa
build.sh help

# Leer README completo
less README.md

# Ver ejemplos
grep -A 20 "Ejemplo" README.md
```

## 💡 Tips y Trucos

### Tip 1: Usar Alias

```bash
# Crear alias cortos
alias qnew="build.sh new-post"
alias qlist="build.sh list"

# Usar
qnew numerus-scriptum
qlist
```

### Tip 2: Tipo de Documento por Defecto

Si siempre usas `jou`, simplemente presiona Enter cuando pregunte el tipo.

### Tip 3: Autor Predeterminado

Si usas el mismo autor, responde "s" cuando pregunte por autor predeterminado.

### Tip 4: Ver Posts por Carpeta

```bash
build.sh list-posts [blog]
# Ahora agrupa por carpeta (python, r, matlab, etc.)
```

## 🔮 Próximamente (v2.1+)

- [ ] Editar posts existentes
- [ ] Plantillas personalizadas
- [ ] Búsqueda de posts
- [ ] Estadísticas de blogs
- [ ] Integración con editores
- [ ] Exportación batch

## ❓ Preguntas Frecuentes

**P: ¿Puedo seguir usando comandos de v1.0?**  
R: Sí, todos los comandos anteriores siguen funcionando.

**P: ¿Necesito reconfigurar algo?**  
R: No, es compatible con tu configuración actual.

**P: ¿Qué pasa con mis blogs existentes?**  
R: Nada, siguen funcionando perfectamente.

**P: ¿Debo usar APAQuarto obligatoriamente?**  
R: No, puedes seguir creando posts simples.

**P: ¿Cómo vuelvo a v1.0 si tengo problemas?**  
R: Restaura el backup: `mv build.sh.v1.backup build.sh`

## 📞 Soporte

### Si Encuentras Problemas

1. **Consulta:** INSTALL.md (sección Troubleshooting)
2. **Revisa:** CHANGELOG.md (bugs conocidos)
3. **Contacta:** achalmaedison@gmail.com

### Reportar Bugs

Envía email con:

- Versión de Quarto (`quarto --version`)
- Comando ejecutado
- Error recibido
- Sistema operativo

## 🎉 ¡Gracias por Actualizar!

La versión 2.0 representa una mejora significativa en:

- **Usabilidad** - Interfaz más amigable
- **Funcionalidad** - APAQuarto completo
- **Eficiencia** - Procesos optimizados
- **Documentación** - Guías completas

**¡Disfruta creando contenido académico de calidad con Quarto!** 🚀

---

**Versión:** 2.0  
**Fecha de lanzamiento:** 28 de enero de 2025  
**Desarrollador:** Edison Achalma  
**Contacto:** achalmaedison@gmail.com

---

## 🔗 Enlaces Rápidos

- 📖 [README.md](README.md) - Guía completa
- 🚀 [INSTALL.md](INSTALL.md) - Instalación
- 📝 [CHANGELOG.md](CHANGELOG.md) - Cambios detallados

**Siguiente paso:** Leer [INSTALL.md](INSTALL.md) para comenzar 👈
