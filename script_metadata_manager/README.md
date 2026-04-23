# Sistema de Gestión de Metadatos para Blogs Quarto

## Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características Principales](#-características-principales)
3. [Novedades v1.2](#-novedades-v12)
4. [Requisitos del Sistema](#-requisitos-del-sistema)
5. [Instalación](#-instalación)
6. [Configuración Inicial](#-configuración-inicial)
7. [Estructura del Proyecto](#-estructura-del-proyecto)
8. [Uso Básico](#-uso-básico)
9. [Comandos Disponibles](#-comandos-disponibles)
10. [Casos de Uso Comunes](#-casos-de-uso-comunes)
11. [Formato de Datos en Excel](#-formato-de-datos-en-excel)
12. [Filtros Avanzados](#-filtros-avanzados)
13. [Solución de Problemas](#-solución-de-problemas)
14. [Preguntas Frecuentes](#-preguntas-frecuentes)
15. [Mejores Prácticas](#-mejores-prácticas)
16. [Ejemplos Prácticos](#-ejemplos-prácticos)
17. [Contribuir](#-contribuir)
18. [Licencia](#-licencia)

---

## Descripción General

El **Sistema de Gestión de Metadatos para Blogs Quarto** es una herramienta que permite administrar de forma centralizada los metadatos YAML de múltiples blogs Quarto usando hojas de cálculo Excel.

### ¿Para qué sirve?

- Gestionar metadatos de **cientos de artículos** desde un solo archivo Excel
- Actualizar títulos, keywords, tags, autores, etc. de forma masiva
- Cambiar el estado de publicación (`draft: TRUE/FALSE`) fácilmente
- Mantener consistencia en metadatos entre múltiples blogs
- Exportar e importar metadatos para backup y análisis

### ¿Por qué usar este sistema?

**Antes:**

- Editar manualmente cada archivo `index.qmd`
- Buscar y reemplazar en múltiples archivos
- Riesgo de errores de sintaxis YAML
- Difícil mantener consistencia

**Ahora:**

- Editar todos los metadatos en Excel
- Actualización masiva con un comando
- Validación automática de formatos
- Filtros para actualización selectiva

---

## Características Principales

### **Recolección Inteligente**

- Solo procesa artículos/publicaciones (con fecha en carpeta)
- Excluye automáticamente archivos de configuración
- Respeta `_metadata.yml` para herencia de configuración
- Prioriza valores específicos de `index.qmd`

### **Excel Unificado**

- Una sola hoja `METADATOS` con todos los artículos
- Hoja `INSTRUCCIONES` con guía completa
- Compatible con Excel y LibreOffice Calc

### **Actualización Eficiente**

- Solo actualiza cuando hay diferencias
- Preserva formato e indentación YAML
- Reportes detallados de cambios aplicados
- Modo simulación para pruebas seguras

### **Filtros Avanzados**

- Actualizar solo un blog específico
- Filtrar por rutas parciales
- Combinar múltiples filtros
- Usar base de datos general sin generar archivos separados

### **Soporte Completo de Tipos**

- **STU (Estudiante):** Trabajos académicos
- **MAN (Manuscrito):** Envíos a revistas
- **JOU (Revista):** Artículos publicados
- **DOC (Documento):** Informes y ensayos

### **Gestión de Autores**

- Hasta 3 autores por artículo
- Información completa: nombre, ORCID, email
- Afiliaciones institucionales
- Roles CRediT

---

## Novedades v1.2

### Mejoras Principales

#### 1. **Filtro de Artículos Mejorado**

- Solo procesa `index.qmd` con fecha en carpeta
- Omite `blog/index.qmd`, `about/index.qmd`, etc.
- Reportes detallados de artículos vs configuraciones

**Ejemplo:**

```
✅ Procesa: axiomata/posts/2025-06-01-proporcionalidad/index.qmd
⏭️ Omite:  axiomata/index.qmd (no es artículo)
⏭️ Omite:  website-achalma/blog/index.qmd (configuración)
```

#### 2. **Una Sola Hoja de Metadatos**

- Todos los artículos en hoja `METADATOS`
- Fácil filtrado y búsqueda
- Gestión unificada

**Antes:**

```
📁 Hojas: STU, MAN, JOU, DOC (separadas)
```

**Ahora:**

```
📁 Hojas: METADATOS (todos juntos), INSTRUCCIONES
```

#### 3. **Prioridad Clara: index.qmd > \_metadata.yml**

- Respeta configuraciones específicas de cada artículo
- Hereda valores por defecto de `_metadata.yml`
- Fusión inteligente de datos

**Ejemplo:**

```yaml
# _metadata.yml (predeterminado)
documentmode: jou
author: Edison Achalma

# index.qmd (específico)
documentmode: stu
# (no tiene author)

# Resultado fusionado:
documentmode: stu  ← Prioridad a index.qmd
author: Edison Achalma  ← Heredado de _metadata.yml
```

#### 4. **Solo Actualiza Diferencias**

- Compara valores antes de actualizar
- Omite archivos sin cambios
- Reportes precisos de modificaciones

**Ejemplo:**

```
[1/15] ✅ Actualizando: proporcionalidad/index.qmd
   📝 Cambios detectados: 2
      1. draft: True → False
      2. keywords: actualizado (5 items)

[2/15] ⏭️ Sin cambios: economia/index.qmd
```

#### 5. **Filtros Avanzados**

```bash
# Solo un blog
--blog axiomata

# Solo rutas con "2025"
--filter-path "2025"

# Combinar
--blog axiomata --filter-path "posts/2025-06"
```

#### 6. **Instrucciones con Emojis**

- Guías intuitivas
- Compatible con LibreOffice
- Sin caracteres especiales problemáticos

#### 7. **Procesamiento Detallado**

- Progreso en tiempo real
- Resúmenes completos
- Mensajes informativos

---

## Requisitos del Sistema

### Software Necesario

- **Python:** 3.8 o superior
- **Sistema Operativo:** Linux, macOS, Windows
- **Gestor de entornos:** Conda (recomendado) o pip

### Paquetes Python Requeridos

```
pandas >= 1.3.0
openpyxl >= 3.0.0
pyyaml >= 5.4.0
```

### Herramientas Opcionales

- **Excel:** Microsoft Excel 2016+ o LibreOffice Calc 7.0+
- **Git:** Para control de versiones
- **Quarto:** Para renderizar los blogs

---

## Instalación

### Opción 1: Usando Conda (Recomendado)

```bash
# 1. Crear entorno virtual
conda create -n metadata_manager python=3.9
conda activate metadata_manager

# 2. Instalar dependencias
conda install pandas openpyxl pyyaml

# 3. Verificar instalación
python --version
python -c "import pandas, openpyxl, yaml; print('OK')"
```

### Opción 2: Usando pip

```bash
# 1. Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 2. Instalar dependencias
pip install pandas openpyxl pyyaml --break-system-packages

# 3. Verificar instalación
python --version
python -c "import pandas, openpyxl, yaml; print('OK')"
```

### Opción 3: Script de Instalación Automática

```bash
# Descargar e instalar automáticamente
bash install.sh
```

---

## Configuración Inicial

### Paso 1: Crear Archivo de Configuración

```bash
python quarto_metadata_manager.py create-config ~/Documents/publicaciones
```

Esto crea `metadata_config.yml` con:

```yaml
# Blogs permitidos (vacío = todos)
allowed_blogs:
  - axiomata
  - aequilibria
  - numerus-scriptum
  - actus-mercator
  - website-achalma
  # Agregar tus blogs aquí

# Carpetas adicionales a excluir
excluded_folders:
  - apa
  - notas
  - borradores
  - propuesta bicentenario
  - taller unsch como elaborar tesis de pregrado
  - practicas preprofesionales
  # Agregar carpetas a ignorar

# Directorio de salida para Excel
excel_output_dir: ~/Documents/scripts/scripts_for_quarto/script_metadata_manager/excel_databases
```

### Paso 2: Personalizar Configuración

Edita `metadata_config.yml`:

```bash
nano metadata_config.yml
# o
code metadata_config.yml
```

**Campos importantes:**

- **`allowed_blogs`**: Lista de blogs a procesar
  - Si está vacía `[]`, procesa todos los blogs encontrados
  - Si tiene elementos, solo procesa los listados
- **`excluded_folders`**: Carpetas adicionales a ignorar
  - Solo nombres, no rutas completas
  - Las carpetas del sistema ya están excluidas por defecto
- **`excel_output_dir`**: Dónde guardar los archivos Excel
  - Usa `~` para referirse a tu home
  - Se crea automáticamente si no existe

### Paso 3: Estructura de Directorios

Tu estructura debe verse así:

```
~/Documents/
├── publicaciones/              # ← Base de tus blogs
│   ├── axiomata/
│   │   ├── posts/
│   │   │   └── 2025-06-01-articulo/
│   │   │       └── index.qmd
│   │   ├── _metadata.yml
│   │   └── index.qmd          # ← NO se procesa (config)
│   ├── aequilibria/
│   ├── numerus-scriptum/
│   └── website-achalma/
│       ├── blog/
│       │   ├── posts/
│       │   │   └── 2024-05-10-post/
│       │   │       └── index.qmd
│       │   └── index.qmd      # ← NO se procesa (config)
│       └── _metadata.yml
└── scripts/
    └── scripts_for_quarto/
        └── script_metadata_manager/
            ├── quarto_metadata_manager.py
            ├── metadata_config.yml
            └── excel_databases/    # ← Aquí se guardan Excel
                ├── quarto_metadata.xlsx
                ├── quarto_metadata_axiomata.xlsx
                └── quarto_metadata_numerus.xlsx
```

---

## Estructura del Proyecto

### Carpetas y Archivos Principales

```
script_metadata_manager/
├── quarto_metadata_manager.py     # Script principal
├── metadata_config.yml            # Configuración
├── README.md                      # Esta guía
├── EJEMPLOS_CONFIGURACION.md      # Ejemplos detallados
├── CHANGELOG.md                   # Historial de cambios
├── install.sh                     # Script de instalación
├── quick_start.sh                 # Script de inicio rápido
└── excel_databases/               # Base de datos Excel
    ├── quarto_metadata.xlsx       # Base general
    └── quarto_metadata_*.xlsx     # Bases por blog
```

### Archivos de Configuración

#### `_metadata.yml` (en cada blog)

Archivo de configuración predeterminada de Quarto:

```yaml
# Valores por defecto para todos los artículos del blog
documentmode: jou
author:
  - name: Edison Achalma
    orcid: 0000-0001-6996-3364
draft: true
```

#### `metadata_config.yml` (script)

Configuración del sistema de gestión:

```yaml
allowed_blogs: [...] # Blogs a procesar
excluded_folders: [...] # Carpetas a ignorar
excel_output_dir: ... # Dónde guardar Excel
```

---

## Uso Básico

### Flujo de Trabajo Completo

```bash
# 1. Activar entorno conda
conda activate metadata_manager

# 2. Navegar al directorio del script
cd ~/Documents/scripts/scripts_for_quarto/script_metadata_manager

# 3. Crear base de datos Excel
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --config metadata_config.yml

# 4. Abrir Excel y editar metadatos
libreoffice excel_databases/quarto_metadata.xlsx
# o
open excel_databases/quarto_metadata.xlsx

# 5. Simular actualización (prueba)
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --config metadata_config.yml \
    --dry-run

# 6. Aplicar cambios
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --config metadata_config.yml

# 7. Renderizar blogs con Quarto
cd ~/Documents/publicaciones/axiomata
quarto render
```

---

## Comandos Disponibles

### 1. `create-config` - Crear Configuración

Genera archivo de configuración personalizado.

**Sintaxis:**

```bash
python quarto_metadata_manager.py create-config <ruta_base> [opciones]
```

**Opciones:**

- `-o, --output`: Nombre del archivo (default: `metadata_config.yml`)

**Ejemplos:**

```bash
# Crear con nombre por defecto
python quarto_metadata_manager.py create-config ~/Documents/publicaciones

# Crear con nombre personalizado
python quarto_metadata_manager.py create-config ~/Documents/publicaciones \
    -o mi_config.yml
```

---

### 2. `create-template` - Crear Base de Datos Excel

Recolecta metadatos y genera archivo Excel.

**Sintaxis:**

```bash
python quarto_metadata_manager.py create-template <ruta_base> [opciones]
```

**Opciones:**

- `-o, --output`: Nombre del Excel (default: `quarto_metadata.xlsx`)
- `-b, --blog`: Blog específico a procesar
- `-c, --config`: Archivo de configuración

**Ejemplos:**

```bash
# Base de datos general (todos los blogs) UNA SOLA VEZ
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --config metadata_config.yml
    
# Base de datos general (Agrega solo articulos nuevos (modo incremental))
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --config metadata_config.yml --incremental

# Blog específico
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --blog axiomata \
    --config metadata_config.yml

# Con nombre personalizado
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --blog numerus-scriptum \
    -o numerus_metadata.xlsx \
    --config metadata_config.yml

# Sin configuración (procesa todo)
python quarto_metadata_manager.py create-template ~/Documents/publicaciones
```

**Salida esperada:**

```
🔍 Recolectando archivos index.qmd...
   (Solo se incluirán artículos/publicaciones con fecha)

📂 Procesando blog: axiomata
  ✅ Artículo: 2025-06-01-proporcionalidad/index.qmd
  ⏭️ Omitido (no es artículo): index.qmd
  📊 Blog 'axiomata': 3 artículos, 1 omitido

======================================================================
📊 RESUMEN DE RECOLECCIÓN:
  📁 Total archivos encontrados: 4
  ✅ Artículos válidos: 3
  ⏭️ Omitidos: 1
======================================================================

📝 Extrayendo metadatos de cada artículo...
  ✅ Procesados: 3/3 artículos (100%)

✅ Plantilla Excel creada: excel_databases/quarto_metadata_axiomata.xlsx
📊 Total de artículos: 3
📁 Hojas: METADATOS (todos los artículos), INSTRUCCIONES
```


---

### 3. `update` - Actualizar desde Excel

Actualiza archivos `index.qmd` con datos del Excel.

**Sintaxis:**

```bash
python quarto_metadata_manager.py update <ruta_base> <archivo_excel> [opciones]
```

**Opciones:**

- `-b, --blog`: Filtrar por blog específico
- `-p, --filter-path`: Filtrar por substring en ruta
- `-c, --config`: Archivo de configuración
- `--dry-run`: Simular sin aplicar cambios

**Ejemplos:**

```bash
# Actualización completa
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --config metadata_config.yml

# Simulación (prueba sin aplicar)
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --config metadata_config.yml \
    --dry-run

# Solo un blog
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog axiomata \
    --config metadata_config.yml

# Solo rutas de 2025
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --filter-path "2025" \
    --config metadata_config.yml

# Combinar filtros
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog numerus-scriptum \
    --filter-path "python" \
    --config metadata_config.yml \
    --dry-run

# Combinar filtros para website
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog website-achalma \
    --filter-path "teching" \
    --config metadata_config.yml
```

**Salida esperada:**

```
📖 Leyendo Excel: excel_databases/quarto_metadata.xlsx

======================================================================
✅ ACTUALIZACION REAL
📊 Artículos a procesar: 15
======================================================================

[1/15] ✅ Actualizando: 2025-06-01-proporcionalidad/index.qmd
   📝 Cambios detectados: 3
      1. title: 'Viejo Título' → 'Nuevo Título'
      2. draft: True → False
      3. keywords: actualizado (5 items)

[2/15] ⏭️ Sin cambios: 2025-04-14-economia/index.qmd

[3/15] ✅ Actualizando: 2024-03-31-matematicas/index.qmd
   📝 Cambios detectados: 1
      1. draft: True → False

======================================================================
✅ RESUMEN DE ACTUALIZACION
======================================================================
✅ Actualizados: 8
⏭️ Sin cambios: 5
❌ Errores: 2
======================================================================
```

### 4. Más opciones

```bash
# 1. Detectar nuevos metadatos
python quarto_metadata_manager.py detect-new-fields ~/Documents/publicaciones

# 2. Agregar columnas detectadas
python quarto_metadata_manager.py add-columns ~/Documents/publicaciones \
  excel_databases/quarto_metadata.xlsx keywords-string author-note

# 3. Encontrar diferencias
python quarto_metadata_manager.py find-differences ~/Documents/publicaciones \
  excel_databases/quarto_metadata.xlsx --blog axiomata

# 4. Sincronizar UN artículo (interactivo)
python quarto_metadata_manager.py sync-article ~/Documents/publicaciones \
  excel_databases/quarto_metadata.xlsx \
  "axiomata/blog/2024-01-15-mi-articulo/index.qmd"

# 5. Sincronizar VARIOS artículos (interactivo)
python quarto_metadata_manager.py sync-batch ~/Documents/publicaciones \
  excel_databases/quarto_metadata.xlsx --blog axiomata

# 6. Simulación
python quarto_metadata_manager.py sync-batch ~/Documents/publicaciones \
  excel_databases/quarto_metadata.xlsx --dry-run
```



---

## Casos de Uso Comunes

### Caso 1: Publicar Artículos (cambiar draft a FALSE)

**Objetivo:** Cambiar múltiples artículos de borrador a publicado.

```bash
# 1. Abrir Excel
libreoffice excel_databases/quarto_metadata.xlsx

# 2. En la hoja METADATOS:
#    - Buscar artículos con draft = TRUE
#    - Cambiar a draft = FALSE
#    - Guardar archivo

# 3. Simular cambios
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --dry-run

# 4. Aplicar cambios
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx

# 5. Renderizar blogs
cd ~/Documents/publicaciones/axiomata
quarto render
```

---

### Caso 2: Actualizar Keywords de Forma Masiva

**Objetivo:** Agregar/modificar keywords en múltiples artículos.

```bash
# 1. Crear base de datos
python quarto_metadata_manager.py create-template ~/Documents/publicaciones

# 2. En Excel, columna 'keywords':
#    Artículo 1: economía, análisis, datos
#    Artículo 2: programación, python, tutorial
#    Artículo 3: estadística, inferencia, regresión

# 3. Actualizar
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx
```

---

### Caso 3: Cambiar Tipo de Documento

**Objetivo:** Cambiar artículos de tipo JOU a STU.

```bash
# 1. En Excel, columna 'tipo_documento':
#    Cambiar: jou → stu

# 2. Llenar campos específicos de STU:
#    - course: Metodología de Investigación
#    - professor: Dr. Edison Achalma
#    - duedate: 12/25/2025

# 3. Actualizar
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx
```

---

### Caso 4: Actualizar Solo un Blog

**Objetivo:** Modificar metadatos solo de `axiomata`.

```bash
# 1. Crear base general (todos los blogs)
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --config metadata_config.yml

# 2. Editar SOLO filas de axiomata en Excel

# 3. Actualizar SOLO axiomata
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog axiomata
```

---

### Caso 5: Actualizar Artículos de un Período

**Objetivo:** Modificar solo artículos de junio 2025.

```bash
# 1. Editar en Excel los artículos de 2025-06

# 2. Actualizar solo esos
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --filter-path "2025-06"
```

---

### Caso 6: Agregar Autores a Múltiples Artículos

**Objetivo:** Agregar segundo autor a varios artículos.

```bash
# 1. En Excel, columnas de autor_2:
#    - author_2_name: María García
#    - author_2_orcid: 0000-0002-1234-5678
#    - author_2_affiliation_name: UNSCH
#    - author_2_roles: writing, analysis

# 2. Actualizar
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx
```

---

## Formato de Datos en Excel

### Ordena la hoja (OBLIGATORIO)

1. Selecciona todos tus datos
2. Datos → Ordenar
3. Primer criterio: columna `pub_date` (AZ) → Ascendente
4. Segundo criterio: columna `journal` (Z) → Ascendente
5. Aceptar

### Hoja METADATOS

#### Columnas de Solo Lectura (NO MODIFICAR)

| Columna          | Descripción           | Ejemplo                                       |
| ---------------- | --------------------- | --------------------------------------------- |
| `ruta_archivo`   | Ubicación del archivo | `axiomata/posts/2025-06-01-prop.../index.qmd` |
| `blog_nombre`    | Nombre del blog       | `axiomata`                                    |
| `tipo_documento` | Tipo inicial          | `jou`                                         |

⚠️ **Importante:** Estas columnas identifican el archivo. Si las modificas, el script no encontrará el archivo.

#### Columnas Editables

##### **Identificación**

| Columna      | Formato           | Ejemplo                          | Obligatorio |
| ------------ | ----------------- | -------------------------------- | ----------- |
| `title`      | Texto             | `Proporcionalidad de Magnitudes` | ✅          |
| `shorttitle` | Texto (<50 chars) | `Proporcionalidad`               | ✅          |
| `subtitle`   | Texto             | `Aplicaciones en Comunicación`   | ❌          |

##### **Publicación**

| Columna | Formato          | Ejemplo      | Obligatorio |
| ------- | ---------------- | ------------ | ----------- |
| `date`  | `MM/DD/YYYY`     | `06/01/2025` | ✅          |
| `draft` | `TRUE` o `FALSE` | `FALSE`      | ✅          |

**Importante:**

- `draft = FALSE`: Artículo publicado (visible)
- `draft = TRUE`: Artículo borrador (oculto)

##### **Descripción**

| Columna       | Formato               | Ejemplo                        | Obligatorio |
| ------------- | --------------------- | ------------------------------ | ----------- |
| `abstract`    | Texto (<250 palabras) | `Este trabajo explora...`      | ✅          |
| `description` | Texto (<160 chars)    | `Análisis de proporcionalidad` | ✅          |

##### **Clasificación**

| Columna      | Formato                    | Ejemplo                      | Obligatorio |
| ------------ | -------------------------- | ---------------------------- | ----------- |
| `keywords`   | Lista (separada por comas) | `economía, análisis, datos`  | ✅          |
| `tags`       | Lista (separada por comas) | `python, tutorial, análisis` | ✅          |
| `categories` | Lista (separada por comas) | `Economía, Estadística`      | ✅          |

**Formato de listas:**

```
Correcto:   economía, estadística, análisis de datos
Incorrecto: economía; estadística; análisis de datos
Incorrecto: [economía, estadística, análisis de datos]
```

##### **Medios**

| Columna | Formato           | Ejemplo        | Obligatorio |
| ------- | ----------------- | -------------- | ----------- |
| `image` | Nombre de archivo | `featured.png` | ❌          |

##### **Código**

| Columna | Formato          | Ejemplo | Obligatorio |
| ------- | ---------------- | ------- | ----------- |
| `eval`  | `TRUE` o `FALSE` | `TRUE`  | ❌          |

**Importante:**

- `eval = TRUE`: Ejecuta bloques de código al renderizar
- `eval = FALSE`: No ejecuta código (solo muestra)

##### **Citación**

| Columna            | Formato | Ejemplo           | Obligatorio |
| ------------------ | ------- | ----------------- | ----------- |
| `citation_type`    | Tipo    | `article-journal` | ❌          |
| `citation_author`  | Texto   | `Edison Achalma`  | ❌          |
| `citation_pdf_url` | URL     | `https://...`     | ❌          |

##### **Bibliografía**

| Columna        | Formato           | Ejemplo           | Obligatorio |
| -------------- | ----------------- | ----------------- | ----------- |
| `bibliography` | Nombre de archivo | `referencias.bib` | ❌          |

##### **Campos Específicos por Tipo**

###### STU (Estudiante)

| Columna     | Formato      | Ejemplo                  |
| ----------- | ------------ | ------------------------ |
| `course`    | Texto        | `Metodología (ECON 101)` |
| `professor` | Texto        | `Dr. Edison Achalma`     |
| `duedate`   | `MM/DD/YYYY` | `12/25/2025`             |
| `note`      | Texto        | `Código: 2020123456`     |

###### JOU (Revista)

| Columna           | Formato | Ejemplo                         |
| ----------------- | ------- | ------------------------------- |
| `journal`         | Texto   | `Revista Peruana de Economía`   |
| `volume`          | Texto   | `2025, Vol. 7, No. 1, 1--25`    |
| `copyrightnotice` | Año     | `2025`                          |
| `copyrightext`    | Texto   | `Todos los derechos reservados` |

###### MAN (Manuscrito)

| Columna          | Formato        | Ejemplo |
| ---------------- | -------------- | ------- |
| `floatsintext`   | `TRUE`/`FALSE` | `FALSE` |
| `numbered_lines` | `TRUE`/`FALSE` | `TRUE`  |
| `meta_analysis`  | `TRUE`/`FALSE` | `FALSE` |
| `mask`           | `TRUE`/`FALSE` | `FALSE` |

###### DOC (Documento)

| Columna          | Formato        | Ejemplo |
| ---------------- | -------------- | ------- |
| `floatsintext`   | `TRUE`/`FALSE` | `TRUE`  |
| `numbered_lines` | `TRUE`/`FALSE` | `FALSE` |

##### **Autores (hasta 3)**

Para cada autor (N = 1, 2, 3):

| Columna                           | Formato                    | Ejemplo                      |
| --------------------------------- | -------------------------- | ---------------------------- |
| `author_N_name`                   | Texto                      | `Edison Achalma`             |
| `author_N_corresponding`          | `TRUE`/`FALSE`             | `TRUE` (solo uno)            |
| `author_N_orcid`                  | ORCID                      | `0000-0001-6996-3364`        |
| `author_N_email`                  | Email                      | `achalmaedison@gmail.com`    |
| `author_N_affiliation_name`       | Texto                      | `UNSCH`                      |
| `author_N_affiliation_department` | Texto                      | `Economía`                   |
| `author_N_affiliation_city`       | Texto                      | `Ayacucho`                   |
| `author_N_affiliation_region`     | Texto                      | `AYA`                        |
| `author_N_affiliation_country`    | Texto                      | `Perú`                       |
| `author_N_roles`                  | Lista (separada por comas) | `conceptualization, writing` |

**Roles CRediT válidos:**

- `conceptualization`, `methodology`, `software`, `validation`
- `formal-analysis`, `investigation`, `resources`, `data-curation`
- `writing`, `visualization`, `supervision`, `project-administration`
- `funding-acquisition`

---

## Filtros Avanzados

### Filtro por Blog

Actualizar solo artículos de un blog específico.

```bash
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog axiomata
```

**Uso:**

- Útil cuando editas solo artículos de un blog en el Excel general
- Ignora cambios en otros blogs

### Filtro por Ruta

Actualizar solo artículos cuya ruta contenga un substring.

```bash
# Solo artículos de 2025
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --filter-path "2025"

# Solo artículos de posts
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --filter-path "posts"

# Solo artículos de python
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --filter-path "python"
```

**Uso:**

- Útil para actualizar artículos por tema o período
- El filtro busca el substring en toda la ruta

### Combinar Filtros

Puedes combinar múltiples filtros:

```bash
# Blog axiomata, solo junio 2025
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog axiomata \
    --filter-path "2025-06"

# Blog numerus-scriptum, solo Python
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog numerus-scriptum \
    --filter-path "python"
```

### Modo Simulación

Siempre prueba primero con `--dry-run`:

```bash
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --blog axiomata \
    --dry-run
```

**Beneficios:**

- Ver cambios antes de aplicar
- Detectar errores
- Confirmar que los filtros funcionan correctamente

---

## Solución de Problemas

### Error: "La ruta base no existe"

**Mensaje:**

```
❌ La ruta base no existe: ~/Documents/publicaciones
```

**Solución:**

```bash
# Verificar que la ruta existe
ls ~/Documents/publicaciones

# Si no existe, crearla
mkdir -p ~/Documents/publicaciones

# Usar ruta absoluta si hay problemas
python quarto_metadata_manager.py create-template \
    /home/achalmaedison/Documents/publicaciones
```

### Error: "No se encontraron artículos válidos"

**Mensaje:**

```
⚠️ No se encontraron artículos válidos
```

**Causas y soluciones:**

1. **No hay artículos con fecha en carpeta**

   ```bash
   # Verificar estructura
   # ✅ Correcto: posts/2025-06-01-articulo/index.qmd
   # ❌ Incorrecto: posts/articulo/index.qmd
   ```

2. **Blogs no están en `allowed_blogs`**

   ```yaml
   # Editar metadata_config.yml
   allowed_blogs:
     - tu_blog_aqui
   ```

3. **Archivos excluidos por configuración**
   ```bash
   # Verificar que no estén en excluded_folders
   ```

### Error: "'bool' object has no attribute 'get'"

**Causa:** Campo `citation` definido como booleano en vez de diccionario.

**Solución:** Este error está corregido en v1.2. Si aparece:

```yaml
# ❌ Incorrecto en index.qmd
citation: true

# ✅ Correcto
citation:
  type: article-journal
  author: Edison Achalma
```

### Error: "Archivo no encontrado"

**Mensaje:**

```
❌ Archivo no encontrado: axiomata/posts/2025-06-01.../index.qmd
```

**Causas:**

1. **Archivo movido o eliminado**

   ```bash
   # Regenerar Excel
   python quarto_metadata_manager.py create-template ~/Documents/publicaciones
   ```

2. **Columna `ruta_archivo` modificada**
   ```
   ⚠️ NO MODIFICAR la columna ruta_archivo en Excel
   ```

### Problemas con LibreOffice

**Problema:** Caracteres raros en instrucciones

**Solución:** Actualizar a v1.2 que usa solo emojis y ASCII.

**Problema:** Error 509 en celdas

**Solución:** Ignorar, no afecta funcionalidad. Es un warning de LibreOffice.

### Problemas de Indentación YAML

**Síntoma:** Error al renderizar con Quarto

**Solución:**

```bash
# 1. Verificar sintaxis YAML
cat index.qmd | head -20

# 2. Usar validador online
# https://www.yamllint.com/

# 3. El script preserva indentación, pero si falla:
# Regenerar Excel y actualizar de nuevo
```

---

## Preguntas Frecuentes

### ¿Puedo usar este sistema con otros formatos además de APA?

Sí, el sistema funciona con cualquier blog Quarto, no solo APA. Los campos específicos de APA (como `documentmode`) son opcionales.

### ¿Qué pasa si edito el index.qmd directamente?

Puedes editarlo directamente. La próxima vez que ejecutes `create-template`, el Excel se actualizará con los nuevos valores.

### ¿Se pierden los comentarios en el YAML?

Sí, los comentarios en `index.qmd` se pierden al actualizar. Mantén comentarios importantes en `_metadata.yml`.

### ¿Puedo tener más de 3 autores?

En la plantilla Excel solo hay columnas para 3 autores. Para más autores, edita `AUTHOR_FIELDS` en el código.

### ¿El sistema funciona en Windows?

Sí, funciona en Windows, macOS y Linux. Solo ajusta las rutas:

```bash
# Windows
python quarto_metadata_manager.py create-template C:\Users\Usuario\Documents\publicaciones
```

### ¿Puedo usar Google Sheets?

No directamente. Debes exportar de Google Sheets a Excel (.xlsx) y luego usar el archivo exportado.

### ¿Qué pasa si ejecuto create-template dos veces?

El Excel se **sobrescribe**. Si quieres mantener el anterior, usa nombres diferentes:

```bash
# Primera vez
python ... create-template ... -o metadata_v1.xlsx

# Segunda vez
python ... create-template ... -o metadata_v2.xlsx
```

### ¿Cómo hago backup de mis metadatos?

```bash
# Opción 1: Copiar Excel
cp excel_databases/quarto_metadata.xlsx \
   excel_databases/backup_$(date +%Y%m%d).xlsx

# Opción 2: Git
git add excel_databases/quarto_metadata.xlsx
git commit -m "Backup metadatos"
```

---

## Mejores Prácticas

### 1. Hacer Backup Siempre

```bash
# Antes de actualizar
cp -r ~/Documents/publicaciones ~/Documents/publicaciones_backup

# O usar Git
cd ~/Documents/publicaciones
git add .
git commit -m "Backup antes de actualizar metadatos"
```

### 2. Usar Siempre --dry-run Primero

```bash
# 1. Probar cambios
python quarto_metadata_manager.py update ... --dry-run

# 2. Si todo OK, aplicar
python quarto_metadata_manager.py update ...
```

### 3. Mantener Configuración en Git

```bash
cd ~/Documents/scripts/scripts_for_quarto/script_metadata_manager
git init
git add metadata_config.yml
git commit -m "Configuración inicial"
```

### 4. Usar Nombres Descriptivos para Excel

```bash
# Mal
-o metadata.xlsx

# Bien
-o metadata_todos_blogs_2024-12-19.xlsx
-o metadata_axiomata_publicar.xlsx
```

### 5. Verificar Después de Actualizar

```bash
# Renderizar un blog de prueba
cd ~/Documents/publicaciones/axiomata
quarto render

# Si hay errores, revisar YAML
nano posts/2025-06-01-articulo/index.qmd
```

### 6. Documentar Cambios Importantes

```bash
# En Excel, agregar columna "notas" para cambios importantes
# O mantener log en archivo separado
echo "2024-12-19: Publicados 5 artículos de axiomata" >> cambios.log
```

### 7. Usar Entorno Conda Dedicado

```bash
# Crear entorno específico
conda create -n metadata_manager python=3.9
conda activate metadata_manager

# Siempre activar antes de usar
conda activate metadata_manager
```

---

## Ejemplos Prácticos

### Ejemplo 1: Publicación Masiva de Artículos

**Escenario:** Tienes 20 artículos en borrador que quieres publicar.

```bash
# 1. Crear Excel
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --blog axiomata

# 2. Abrir Excel
libreoffice excel_databases/quarto_metadata_axiomata.xlsx

# 3. En columna 'draft':
#    - Filtrar por TRUE
#    - Seleccionar 20 artículos
#    - Cambiar a FALSE
#    - Guardar

# 4. Simular
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata_axiomata.xlsx \
    --dry-run

# 5. Aplicar
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata_axiomata.xlsx

# 6. Renderizar
cd ~/Documents/publicaciones/axiomata
quarto render
```

### Ejemplo 2: Actualizar Keywords por Categoría

**Escenario:** Agregar keyword "economía" a todos los artículos de la categoría "Economía".

```bash
# 1. Crear Excel general
python quarto_metadata_manager.py create-template ~/Documents/publicaciones

# 2. En Excel:
#    - Filtrar columna 'categories' por "Economía"
#    - En columna 'keywords', agregar "economía" al inicio
#    - Ejemplo: "economía, análisis, datos"

# 3. Actualizar
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx
```

### Ejemplo 3: Cambiar Autor en Múltiples Artículos

**Escenario:** Corregir el ORCID del autor en todos sus artículos.

```bash
# 1. En Excel:
#    - Buscar todos los artículos del autor
#    - Columna 'author_1_orcid': Cambiar a nuevo ORCID
#    - Ejemplo: 0000-0001-6996-3364

# 2. Actualizar solo esos artículos
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx \
    --filter-path "autor-nombre"
```

### Ejemplo 4: Migrar Artículos de JOU a STU

**Escenario:** Cambiar tipo de documento de varios artículos.

```bash
# 1. En Excel:
#    - Columna 'tipo_documento': jou → stu
#    - Llenar campos STU:
#      * course: Metodología de Investigación
#      * professor: Dr. Edison Achalma
#      * duedate: 12/25/2025

# 2. Actualizar
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx
```

---

## Contribuir

### Reportar Problemas

Si encuentras un bug:

1. Verifica que estás usando la última versión
2. Ejecuta con `--dry-run` para diagnosticar
3. Contacta con detalles:
   - Comando ejecutado
   - Mensaje de error completo
   - Archivo `index.qmd` de ejemplo (si es relevante)

### Sugerir Mejoras

Envía sugerencias a: achalmaedison@gmail.com

---

## Licencia

Este proyecto está licenciado bajo CC BY-SA 4.0.

---

## Soporte

**Autor:** Edison Achalma  
**Email:** achalmaedison@gmail.com  
**Ubicación:** Ayacucho, Perú  
**Versión:** 1.2.0  
**Fecha:** Diciembre 2024

---

## Agradecimientos

Gracias a todos los que han contribuido con ideas y reportes de bugs para mejorar este sistema.

---

**Última actualización:** Enero 22, 2026
