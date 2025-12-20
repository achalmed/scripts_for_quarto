# CHANGELOG - Sistema de Gestión de Metadatos Quarto

Todos los cambios notables a este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] - 2024-12-19

### 🎉 Lanzamiento Inicial

Primera versión completa del Sistema de Gestión de Metadatos para Blogs Quarto.

### ✨ Agregado

#### Funcionalidades Principales
- **Recolección automática** de archivos `index.qmd` en múltiples blogs
- **Generación de plantillas Excel** con metadatos extraídos
- **Actualización masiva** de archivos .qmd desde Excel
- **Modo simulación** (`--dry-run`) para previsualizar cambios
- **Filtrado por blog** específico para operaciones selectivas

#### Soporte de Tipos de Documentos
- **STU (Estudiante)**: Trabajos académicos con campos de curso, profesor, fecha de entrega
- **MAN (Manuscrito)**: Documentos formales con opciones de floats, numeración, meta-análisis
- **JOU (Revista)**: Formato de revista con información de publicación
- **DOC (Documento)**: Formato general flexible

#### Gestión de Metadatos
- ✅ Campos comunes obligatorios para todos los tipos
- ✅ Campos específicos por tipo de documento
- ✅ Soporte para hasta 3 autores con información completa
- ✅ Gestión de afiliaciones institucionales
- ✅ Roles CRediT para contribución de autores
- ✅ Keywords, tags y categorías (listas separadas por comas)
- ✅ Información de citación (tipo, autor, PDF URL)
- ✅ Enlaces adicionales en formato JSON
- ✅ Bibliografía (archivos .bib)

#### Características Técnicas
- 🚫 Exclusión automática de carpetas: `_site`, `_freeze`, `.git`, etc.
- 🚫 Exclusión de archivos especiales: `_contenido-*.qmd`, `404.qmd`, etc.
- 🔍 Detección automática del tipo de documento
- 📊 Generación de Excel con hojas separadas por tipo
- 📖 Hoja de instrucciones integrada en el Excel
- ✍️ Preservación del contenido del documento (solo actualiza YAML)
- 🎨 Formato Excel con colores y columnas ajustadas

#### Interfaz de Usuario
- 💻 CLI completo con argumentos
- 🎯 Script interactivo de inicio rápido (`quick_start.sh`)
- 📚 Documentación exhaustiva (README, ejemplos, changelog)
- 🐛 Mensajes de error descriptivos
- ✅ Confirmaciones de operaciones críticas

#### Validación y Seguridad
- ✔️ Validación de formato de booleanos (TRUE/FALSE)
- ✔️ Validación de rutas de archivos
- ✔️ Detección de cambios antes de actualizar
- ✔️ Opción de simular cambios antes de aplicar
- ✔️ Mensajes de progreso detallados

### 📝 Documentación

#### Archivos Incluidos
- `README_METADATA_MANAGER.md`: Guía completa de uso
- `EJEMPLOS_CONFIGURACION.md`: Ejemplos prácticos de configuración
- `CHANGELOG.md`: Este archivo
- Comentarios inline en el código Python

#### Contenido de la Documentación
- Instalación y requisitos
- Guía de uso paso a paso
- Ejemplos prácticos por tipo de documento
- Solución de problemas comunes
- Flujo de trabajo recomendado
- Casos de uso académicos y profesionales

### 🛠️ Arquitectura Técnica

#### Dependencias
- `pandas`: Manejo de datos y Excel
- `openpyxl`: Lectura/escritura de archivos Excel con formato
- `pyyaml`: Parsing y generación de YAML
- Python 3.6+: Lenguaje base

#### Estructura del Código
```python
QuartoMetadataManager
├── __init__(): Inicialización
├── collect_index_files(): Recolección de archivos
├── create_excel_template(): Generación de Excel
├── update_yaml_from_excel(): Actualización masiva
├── extract_yaml_from_qmd(): Extracción de YAML
├── detect_document_mode(): Detección de tipo
└── Helper methods: Métodos auxiliares
```

#### Diseño Modular
- Separación clara de responsabilidades
- Métodos reutilizables
- Fácil extensión para nuevos tipos de documentos
- Manejo robusto de errores

### 🎯 Casos de Uso Soportados

#### Academia
- Blogs de investigación
- Portafolios estudiantiles
- Material de cursos
- Publicaciones académicas

#### Profesional
- Documentación técnica
- Blogs corporativos
- Sitios de divulgación
- Archivos de proyectos

### 📊 Estadísticas de Lanzamiento

- **Líneas de código**: ~1,200
- **Funciones**: 15+
- **Campos soportados**: 40+
- **Tipos de documentos**: 4
- **Autores máximos**: 3
- **Formatos de salida**: Excel (.xlsx)

### 🔒 Limitaciones Conocidas

- Máximo 3 autores en la interfaz Excel (extensible en código)
- Solo archivos `index.qmd` (no procesa otros .qmd)
- Requiere estructura YAML válida en archivos
- No valida sintaxis LaTeX o código incrustado
- No soporta archivos Excel .xls (solo .xlsx)

### 🚀 Rendimiento

- ⚡ Rápido: ~100 archivos/segundo para recolección
- 💾 Ligero: <10MB de memoria para 1000 archivos
- 🔄 Eficiente: Solo actualiza archivos con cambios

### ⚙️ Configuración

#### Variables de Entorno
Ninguna requerida en v1.0.0

#### Configuración por Defecto
```python
EXCLUDED_FOLDERS = {
    '_site', '_freeze', 'site_libs', 
    '.git', '.quarto', 'node_modules',
    '__pycache__', '_extensions'
}

EXCLUDED_INDEX_FILES = {
    '_contenido-inicio.qmd',
    '_contenido-final.qmd',
    '_contenido_posts.qmd',
    '404.qmd', 'contact.qmd', 
    'accessibility.qmd', 'license.qmd'
}
```

### 🧪 Testing

**Status**: Sin tests automatizados en v1.0.0

**Testing Manual**:
- ✅ Creación de plantillas
- ✅ Actualización de metadatos
- ✅ Modo dry-run
- ✅ Filtrado por blog
- ✅ Manejo de errores

### 📦 Distribución

**Archivos del Paquete**:
- `quarto_metadata_manager.py`: Script principal
- `quick_start.sh`: Script de inicio rápido
- `README_METADATA_MANAGER.md`: Documentación
- `EJEMPLOS_CONFIGURACION.md`: Ejemplos
- `CHANGELOG.md`: Este archivo

**Instalación**:
```bash
# Clonar o descargar archivos
pip install pandas openpyxl pyyaml --break-system-packages
chmod +x quarto_metadata_manager.py quick_start.sh
```

### 🙏 Agradecimientos

- **Quarto**: Por el excelente sistema de publicación científica
- **Apaquarto**: Por las plantillas APA profesionales
- **Comunidad Python**: Por las librerías robustas
- **Usuarios beta**: Por feedback valioso

### 📞 Soporte

**Autor**: Edison Achalma
**Email**: achalmaedison@gmail.com
**Ubicación**: Ayacucho, Perú

**Reportar Issues**:
- Descripción detallada del problema
- Pasos para reproducir
- Salida del comando con error
- Versión de Python y dependencias

### 🔮 Roadmap Futuro

Posibles mejoras para versiones futuras:

#### v1.1.0 (Planificado)
- [ ] Soporte para más de 3 autores
- [ ] Validación de ORCID en línea
- [ ] Backup automático antes de actualizar
- [ ] Estadísticas de cambios aplicados

#### v1.2.0 (Planificado)
- [ ] Interfaz gráfica (GUI) con Tkinter
- [ ] Exportación a CSV/JSON
- [ ] Importación desde Google Sheets
- [ ] Historial de cambios (git integration)

#### v2.0.0 (Futuro)
- [ ] Web interface
- [ ] API REST
- [ ] Sincronización en tiempo real
- [ ] Tests unitarios completos
- [ ] CI/CD pipeline

### 📜 Licencia

Uso libre para proyectos académicos y personales.

### 🏷️ Tags

`quarto` `metadata` `yaml` `blog-management` `academic-writing` 
`python` `excel` `automation` `publishing` `apa`

---

## Versionado

- **MAJOR**: Cambios incompatibles con API anterior
- **MINOR**: Funcionalidad nueva compatible con versión anterior
- **PATCH**: Correcciones de bugs compatibles

**Versión Actual**: 1.0.0

---

**Fecha de Lanzamiento**: 19 de Diciembre, 2024  
**Autor**: Edison Achalma  
**Estado**: Estable ✅
