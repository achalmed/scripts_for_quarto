# Sistema de Gestión de Metadatos Quarto — v2.2

Sistema integral de administración de publicaciones Quarto: metadatos,
tags, autores, categorías, keywords, taxonomía y sincronización, para todos
tus proyectos (`pub_*` + `website-achalma`), usando Excel como base de datos.
Un solo archivo Excel puede contener cientos de artículos; editas los campos
en la hoja y actualizas todos los `.qmd` con un comando.

> **v2.1** absorbe por completo el antiguo `script_tag_manager`: toda la
> gestión de tags (normalización, reemplazos, altas/bajas, estadísticas y
> auditoría) vive ahora aquí, con una única implementación de parsing y
> escritura YAML. Ver [§8 Gestión de tags](#8-gestión-de-tags-v21).
>
> **v2.2** absorbe además los scripts legacy de la raíz del repositorio
> (`1_sincronizar_fecha...` y `3_actualizar_enlace_pdf...`) como los
> comandos `sync-dates` y `sync-pdf-urls` (ver final de
> [§7 Comandos completos](#7-comandos-completos)).

**Autor:** Edison Achalma — UNSCH, Ayacucho, Perú  
**Email:** elmer.achalma.09@unsch.edu.pe  
**ORCID:** 0000-0001-6996-3364

---

## 📋 Índice

1. [Qué hace este sistema](#1-qué-hace-este-sistema)
2. [Qué cambió en v2.0](#2-qué-cambió-en-v20)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Instalación](#4-instalación)
5. [Configuración inicial](#5-configuración-inicial)
6. [Uso rápido](#6-uso-rápido)
7. [Comandos completos](#7-comandos-completos)
8. [Gestión de tags (v2.1)](#8-gestión-de-tags-v21)
9. [Formato de datos en Excel](#9-formato-de-datos-en-excel)
10. [Ejemplos de configuración de campos](#10-ejemplos-de-configuración-de-campos)
11. [Filtros avanzados](#11-filtros-avanzados)
12. [Casos de uso comunes](#12-casos-de-uso-comunes)
13. [Fórmulas de Excel útiles](#13-fórmulas-de-excel-útiles)
14. [Añadir funcionalidades nuevas](#14-añadir-funcionalidades-nuevas)
15. [Resolución de problemas](#15-resolución-de-problemas)

---

## 1. Qué hace este sistema

- Recorre todos tus blogs (`pub_*` + `website-achalma`) buscando artículos
  reales (carpetas con fecha `YYYY-MM-DD`).
- Extrae los metadatos YAML de cada `index.qmd` y los vuelca en un Excel.
- Te permite editar títulos, keywords, draft, autores, etc. en una sola hoja.
- Aplica los cambios del Excel de vuelta a los archivos `index.qmd`,
  solo donde hay diferencias reales.
- Soporta modo incremental (agrega solo artículos nuevos), modo simulación
  (`--dry-run`), filtros por blog y por ruta.

---

## 2. Qué cambió en v2.0

| Aspecto          | v1.x (monolítico)                                      | v2.0 (modular)                             |
| ---------------- | ------------------------------------------------------ | ------------------------------------------ |
| Organización     | 1 archivo `quarto_metadata_manager.py` de ~2460 líneas | `main.py` + 7 módulos en `lib/`            |
| Nombre de blogs  | Lista antigua sin prefijo                              | Formato actual `pub_*` + `website-achalma` |
| Punto de entrada | `python quarto_metadata_manager.py`                    | `python main.py`                           |
| Comandos         | Idénticos                                              | Todos preservados                          |
| Menú interactivo | `quick_start.sh` con 9 opciones                        | `quick_start.sh` con 13 opciones           |

Todos los comandos originales (`create-config`, `create-template`, `update`,
`detect-new-fields`, `add-columns`, `find-differences`, `sync-article`,
`sync-batch`) siguen funcionando exactamente igual.

---

## 3. Estructura del proyecto

```
metadata-manager/
├── main.py                    ⭐ Punto de entrada único
├── quick_start.sh             🚀 Menú interactivo Bash (13 opciones)
├── install.sh                 🔧 Instalador de dependencias
├── metadata_config.yml        ⚙️  Configuración (blogs, exclusiones, salida)
├── README.md                  📖 Este archivo
├── excel_databases/           💾 Excel generados aquí
│   └── quarto_metadata.xlsx
└── lib/
    ├── __init__.py            Exportaciones del paquete
    ├── config.py              Constantes: ALL_FIELDS, exclusiones, carga YAML
    ├── yaml_parser.py         Extracción y fusión de YAML (index.qmd + _metadata.yml)
    ├── collector.py           Búsqueda recursiva de artículos válidos
    ├── field_mapper.py        Conversión YAML ↔ Excel (extracción y aplicación)
    ├── excel_writer.py        Creación de plantilla, modo incremental, instrucciones
    ├── qmd_updater.py         Escritura de cambios en archivos .qmd
    ├── sync.py                Comparación, sync-article, sync-batch, detect-new-fields
    ├── tag_utils.py           Funciones puras de tags: normalización, dedup, similitud
    ├── tag_operations.py      Operaciones de tags sobre archivos y sobre Excel
    ├── tag_reports.py         Estadísticas (tag-stats) y auditoría (audit-tags)
    └── path_sync.py           sync-dates y sync-pdf-urls (metadatos derivados de la ruta)
```

**Cada módulo tiene una responsabilidad única**, lo que facilita extender el
sistema sin tocar código existente.

---

## 4. Instalación

### Opción 1: Script automático (recomendado)

```bash
bash install.sh
```

### Opción 2: Con Conda

```bash
conda create -n metadata_manager python=3.9 -y
conda activate metadata_manager
conda install pandas openpyxl pyyaml -y
```

### Opción 3: Con pip

```bash
pip install pandas openpyxl pyyaml --break-system-packages
```

### Verificar instalación

```bash
python3 -c "import pandas, openpyxl, yaml; print('✅ Dependencias OK')"
python3 main.py --help
```

---

## 5. Configuración inicial

### Paso 1: Crear `metadata_config.yml`

```bash
python3 main.py create-config ~/Documents
```

Esto genera un `metadata_config.yml` con tus blogs en formato `pub_*`. Edítalo:

```yaml
# Blogs que serán procesados (vacío = todos los encontrados)
allowed_blogs:
  - pub_axiomata
  - pub_epsilon-y-beta
  - pub_numerus-scriptum
  - website-achalma
  # Agrega o quita según tus proyectos reales

# Carpetas adicionales a ignorar
excluded_folders:
  - apa
  - borradores
  - propuesta bicentenario

# Dónde guardar los Excel generados
excel_output_dir: ~/Documents/scripts/scripts_for_quarto/script_metadata_manager/excel_databases
```

### Paso 2: Estructura esperada de tus blogs

```
~/Documents/
├── pub_axiomata/
│   ├── _metadata.yml           ← configuración compartida (opcional)
│   ├── index.qmd               ← NO se procesa (no es artículo)
│   └── posts/
│       └── 2025-06-01-mi-articulo/
│           └── index.qmd       ← SÍ se procesa (tiene fecha)
├── pub_numerus-scriptum/
│   └── python/
│       └── 2024-03-15-pandas/
│           └── index.qmd
└── website-achalma/
    ├── blog/
    │   ├── index.qmd           ← NO se procesa
    │   └── posts/
    │       └── 2025-01-10-post/
    │           └── index.qmd   ← SÍ se procesa
    └── talk/
        └── 2024-09-20-charla/
            └── index.qmd       ← SÍ se procesa
```

El criterio para considerar un `index.qmd` como artículo: su **carpeta padre
debe comenzar con fecha** (`YYYY-MM-DD`). Los `index.qmd` dentro de `blog/`,
`posts/`, `about/`, etc. se ignoran automáticamente.

---

## 6. Uso rápido

### Con el menú interactivo (recomendado)

```bash
./quick_start.sh
```

### Flujo completo desde CLI

```bash
# 1. Generar Excel con todos los artículos
python3 main.py create-template ~/Documents --config metadata_config.yml

# 2. Abrir y editar
libreoffice excel_databases/quarto_metadata.xlsx

# 3. Simular cambios (verificar sin aplicar)
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx \
    --config metadata_config.yml --dry-run

# 4. Aplicar cambios
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx \
    --config metadata_config.yml

# 5. Renderizar blogs en Quarto
cd ~/Documents/pub_axiomata && quarto render
```

---

## 7. Comandos completos

### `create-config` — Crear configuración

```bash
python3 main.py create-config ~/Documents
python3 main.py create-config ~/Documents -o mi_config.yml
```

### `create-template` — Generar plantilla Excel

```bash
# Todos los blogs
python3 main.py create-template ~/Documents --config metadata_config.yml

# Solo un blog
python3 main.py create-template ~/Documents --blog pub_axiomata \
    --config metadata_config.yml

# Modo incremental (agrega solo artículos nuevos, preserva fórmulas)
python3 main.py create-template ~/Documents --config metadata_config.yml \
    --incremental

# Con nombre personalizado
python3 main.py create-template ~/Documents -o mis_metadatos.xlsx
```

**Salida esperada:**

```
🔍 Recolectando archivos index.qmd...
   (Solo se incluirán artículos/publicaciones con fecha)

📂 Procesando blog: pub_axiomata
  ✅ Artículo: 2025-06-01-proporcionalidad/index.qmd
  ⏭️ Omitido (no es artículo): index.qmd
  📊 Blog 'pub_axiomata': 3 artículos, 1 omitido

📊 RESUMEN DE RECOLECCIÓN:
  📁 Total archivos encontrados: 4
  ✅ Artículos válidos: 3
  ⏭️ Omitidos: 1

✅ Plantilla Excel creada: excel_databases/quarto_metadata.xlsx
📁 Hojas: METADATOS (todos los artículos), INSTRUCCIONES
```

### `update` — Actualizar archivos desde Excel

```bash
# Actualización completa
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx

# Simulación (recomendado siempre primero)
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx \
    --dry-run

# Solo un blog
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx \
    --blog pub_axiomata

# Solo rutas con "2025"
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx \
    --filter-path "2025"

# Combinar filtros
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx \
    --blog pub_numerus-scriptum --filter-path "python" --dry-run
```

**Salida esperada:**

```
[1/15] ✅ Actualizando: proporcionalidad/index.qmd
   📝 Cambios detectados: 3
      1. title: 'Viejo Título' → 'Nuevo Título'
      2. draft: True → False
      3. keywords: actualizado (5 items)

[2/15] ⏭️  Sin cambios: economia/index.qmd

✅ RESUMEN DE ACTUALIZACION
✅ Actualizados:  8
⏭️  Sin cambios:  5
❌ Errores:       0
```

### `detect-new-fields` — Detectar campos YAML no declarados

```bash
python3 main.py detect-new-fields ~/Documents --config metadata_config.yml
```

Muestra qué campos YAML existen en tus artículos pero no tienen columna en
el Excel, con el comando exacto para agregarlos.

### `add-columns` — Agregar columnas al Excel

```bash
python3 main.py add-columns ~/Documents excel_databases/quarto_metadata.xlsx \
    campo-nuevo otro-campo

# Simulación
python3 main.py add-columns ~/Documents excel_databases/quarto_metadata.xlsx \
    campo-nuevo --dry-run
```

### `find-differences` — Ver artículos desincronizados

```bash
python3 main.py find-differences ~/Documents excel_databases/quarto_metadata.xlsx

# Con filtros
python3 main.py find-differences ~/Documents excel_databases/quarto_metadata.xlsx \
    --blog pub_axiomata --max-show 20
```

### `sync-article` — Sincronizar un artículo (interactivo)

```bash
python3 main.py sync-article ~/Documents excel_databases/quarto_metadata.xlsx \
    "pub_axiomata/posts/2025-06-01-mi-articulo/index.qmd"
```

Muestra las diferencias y pregunta la dirección (index→Excel o Excel→index).

### `sync-batch` — Sincronización masiva interactiva

```bash
python3 main.py sync-batch ~/Documents excel_databases/quarto_metadata.xlsx

# Con filtros y simulación
python3 main.py sync-batch ~/Documents excel_databases/quarto_metadata.xlsx \
    --blog pub_axiomata --dry-run
```

### `sync-dates` — Fecha desde el nombre de la carpeta (v2.2)

Sincroniza el campo `date` con la fecha de la carpeta del artículo
(`2023-05-12-titulo` → `date: 05/12/2023`, el formato canónico del
proyecto). Acepta el mismo doble destino que los comandos de tags:
un `.xlsx` (solo actualiza la columna `date`) o un directorio (edita
los `index.qmd` directamente).

```bash
# Sobre los archivos (simular primero)
python3 main.py sync-dates ~/Documents --config metadata_config.yml --dry-run
python3 main.py sync-dates ~/Documents --config metadata_config.yml

# Sobre el Excel (luego aplicar con update)
python3 main.py sync-dates excel_databases/quarto_metadata.xlsx --dry-run
```

### `sync-pdf-urls` — citation.pdf-url desde la ruta real (v2.2)

Reconstruye `citation.pdf-url` como `<URL base del blog>/<ruta>/index.pdf`.
Corrige errores de copy-paste (pdf-url apuntando a otro blog/artículo) y
enlaces rotos por carpetas renombradas.

```bash
python3 main.py sync-pdf-urls ~/Documents --config metadata_config.yml --dry-run
python3 main.py sync-pdf-urls excel_databases/quarto_metadata.xlsx --blog chaska
```

La URL base de cada blog se resuelve así:

1. `blog_base_urls` en `metadata_config.yml` (si el blog figura ahí), p.ej.:
   ```yaml
   blog_base_urls:
     pub_chaska: https://chaska-x.netlify.app # no derivable del nombre
     website-achalma: https://achalmaedison.netlify.app
   ```
2. Si no, **voto por mayoría** de los pdf-url ya existentes en ese blog
   (un pdf-url erróneo aislado no contamina la detección).

Notas:

- Solo actualiza artículos que **ya tienen** bloque `citation`; nunca lo crea.
- La parte del script legacy que reescribía enlaces a PDF en el cuerpo del
  documento no se migró: ningún artículo actual los usa.

---

## 8. Gestión de tags (v2.1)

Todos los comandos de tags aceptan **dos tipos de destino**:

| Destino                    | Efecto                                                                                                |
| -------------------------- | ----------------------------------------------------------------------------------------------------- |
| Archivo `.xlsx`            | Modifica **solo la columna `tags`** del Excel; los `.qmd` no se tocan hasta ejecutar `update`         |
| Directorio (`~/Documents`) | Modifica los `index.qmd` **directamente** (usa el mismo collector y filtros que el resto del sistema) |

Todos soportan `--dry-run`, `--blog` y `--filter-path`. En modo directorio
acepta además `--config` (mismo `metadata_config.yml` de siempre).

> **Regla heredada del Tag Manager:** toda operación normaliza la lista
> completa (minúsculas, sin tildes, snake_case) y elimina duplicados, y los
> artículos **sin** campo `tags` se omiten siempre (nunca se crean tags
> donde no existían).

### `normalize-tags` — Normalizar y deduplicar

```bash
# Sobre el Excel (recomendado: revisar primero con --dry-run)
python3 main.py normalize-tags excel_databases/quarto_metadata.xlsx --dry-run
python3 main.py normalize-tags excel_databases/quarto_metadata.xlsx

# Directamente sobre los archivos
python3 main.py normalize-tags ~/Documents --config metadata_config.yml --dry-run
```

`"Gestión Empresarial"` → `gestion_empresarial`;
`economia, Economía, ECONOMIA` → `economia` (un solo tag).

### `replace-tags` — Reemplazo masivo

```bash
# Uno o varios reemplazos "viejo:nuevo" a la vez
python3 main.py replace-tags excel.xlsx "gestion:administracion" \
    "economia:economia_aplicada" "python:data_science" --dry-run
```

La comparación es insensible a mayúsculas/tildes (`"Gestión"` también
matchea `gestion`).

### `remove-tags` — Eliminación masiva

```bash
python3 main.py remove-tags excel.xlsx tag_obsoleto otro_tag --dry-run
# (también disponible como remove-tag)
```

### `add-tags` — Agregar tags

```bash
python3 main.py add-tags ~/Documents nuevo_tag --blog pub_axiomata --dry-run
```

Evita duplicados automáticamente y respeta el orden existente. Solo agrega
a artículos que ya tienen tags.

### `tag-stats` — Estadísticas de la colección

```bash
python3 main.py tag-stats ~/Documents --top 30
python3 main.py tag-stats excel.xlsx --blog pub_chaska
```

Reporta: totales, tags únicos, promedio por artículo, top N con histograma,
tags huérfanos (usados una sola vez), distribución por blog y por año.

### `audit-tags` — Auditoría de taxonomía

```bash
python3 main.py audit-tags excel.xlsx
python3 main.py audit-tags ~/Documents --threshold 0.85
```

Detecta: variantes de escritura que colapsan al normalizar, problemas de
formato (mayúsculas, tildes, espacios, kebab-case, tags muy largos), pares
singular/plural y tags casi iguales por similitud de cadenas (typos como
`expotacion` ~ `exportacion`). Al final imprime los comandos
`normalize-tags` / `replace-tags` listos para ejecutar las correcciones.

### Flujo recomendado (Excel como fuente de verdad)

```bash
# 1. Auditar
python3 main.py audit-tags excel_databases/quarto_metadata.xlsx

# 2. Corregir el Excel (sin tocar archivos)
python3 main.py normalize-tags excel_databases/quarto_metadata.xlsx
python3 main.py replace-tags excel_databases/quarto_metadata.xlsx "expotacion:exportacion"

# 3. Revisar y aplicar a los .qmd
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx
```

---

## 9. Formato de datos en Excel

### Ordena la hoja antes de trabajar (RECOMENDADO)

1. Selecciona todos tus datos
2. Datos → Ordenar
3. Primer criterio: columna `journal` (Z) → Ascendente
4. Segundo criterio: columna `pub_date` (AZ) → Ascendente
5. Aceptar

### Columnas de solo lectura (NO modificar)

| Columna          | Descripción                                               |
| ---------------- | --------------------------------------------------------- |
| `ruta_archivo`   | Ruta relativa del index.qmd — identifica el artículo      |
| `blog_nombre`    | Nombre del blog (`pub_axiomata`, `website-achalma`, etc.) |
| `tipo_documento` | Tipo detectado (`jou`/`stu`/`man`/`doc`)                  |

Si modificas estas columnas, el script no encontrará el archivo.

### Columnas editables

#### Identificación y publicación

| Campo        | Formato           | Ejemplo                                |
| ------------ | ----------------- | -------------------------------------- |
| `title`      | Texto             | `Proporcionalidad de Magnitudes`       |
| `shorttitle` | Texto (<50 chars) | `Proporcionalidad`                     |
| `subtitle`   | Texto             | `Un análisis detallado`                |
| `date`       | `MM/DD/YYYY`      | `01/15/2025`                           |
| `draft`      | `TRUE` / `FALSE`  | `FALSE` = publicado, `TRUE` = borrador |

#### Contenido y clasificación

| Campo          | Formato                     | Ejemplo                        |
| -------------- | --------------------------- | ------------------------------ |
| `abstract`     | Texto libre (<250 palabras) | `Este estudio analiza...`      |
| `description`  | Texto (<160 chars)          | `Análisis de proporcionalidad` |
| `keywords`     | Separados por comas         | `economía, análisis, datos`    |
| `tags`         | Separados por comas         | `python, tutorial, datos`      |
| `categories`   | Separados por comas         | `Economía, Estadística`        |
| `image`        | Nombre de archivo           | `featured.png`                 |
| `eval`         | `TRUE` / `FALSE`            | `TRUE` = ejecutar código       |
| `bibliography` | Nombre de archivo           | `referencias.bib`              |

#### Citación

| Campo              | Formato      | Ejemplo                |
| ------------------ | ------------ | ---------------------- |
| `citation_type`    | Tipo CSL     | `article-journal`      |
| `citation_author`  | Texto        | `Edison Achalma`       |
| `citation_pdf_url` | URL completa | `https://...index.pdf` |

Tipos de citación válidos: `article-journal`, `book`, `chapter`,
`paper-conference`, `thesis`, `report`.

#### Links adicionales

```
links_enabled: TRUE
links_data: [{"icon": "github", "name": "Repositorio", "url": "https://github.com/achalmed/proyecto"}, {"icon": "file-pdf", "name": "Slides", "url": "https://ejemplo.com/slides.pdf"}]
```

#### Campos específicos por tipo

**STU** (estudiante):

| Campo       | Formato      | Ejemplo                   |
| ----------- | ------------ | ------------------------- |
| `course`    | Texto        | `Metodología (ECON 5101)` |
| `professor` | Texto        | `Dr. Edison Achalma`      |
| `duedate`   | `MM/DD/YYYY` | `12/25/2025`              |
| `note`      | Texto        | `Código: 2020123456`      |

**JOU** (revista):

| Campo             | Formato    | Ejemplo                         |
| ----------------- | ---------- | ------------------------------- |
| `journal`         | Texto      | `Revista Peruana de Economía`   |
| `volume`          | Texto      | `2025, Vol. 7, No. 1, 1--25`    |
| `copyrightnotice` | Año entero | `2025`                          |
| `copyrightext`    | Texto      | `Todos los derechos reservados` |

**MAN** (manuscrito):

| Campo            | Formato        | Ejemplo                          |
| ---------------- | -------------- | -------------------------------- |
| `floatsintext`   | `TRUE`/`FALSE` | `FALSE` (figuras al final)       |
| `numbered_lines` | `TRUE`/`FALSE` | `TRUE` (facilita revisión)       |
| `meta_analysis`  | `TRUE`/`FALSE` | `FALSE`                          |
| `mask`           | `TRUE`/`FALSE` | `FALSE` (revisión ciega: `TRUE`) |

**DOC** (documento): `floatsintext`, `numbered_lines`

#### Autores (hasta 3)

Para cada autor N (1, 2, 3):

| Campo                             | Formato                              |
| --------------------------------- | ------------------------------------ |
| `author_N_name`                   | Nombre completo                      |
| `author_N_corresponding`          | `TRUE` (solo uno) / `FALSE`          |
| `author_N_orcid`                  | `0000-0001-6996-3364`                |
| `author_N_email`                  | correo@universidad.edu               |
| `author_N_affiliation_name`       | Universidad Nacional...              |
| `author_N_affiliation_department` | Facultad de Ciencias...              |
| `author_N_affiliation_city`       | Ayacucho                             |
| `author_N_affiliation_region`     | AYA                                  |
| `author_N_affiliation_country`    | Perú                                 |
| `author_N_roles`                  | `conceptualization, writing` (comas) |

**Roles CRediT válidos:** `conceptualization`, `methodology`, `software`,
`validation`, `formal-analysis`, `investigation`, `resources`,
`data-curation`, `writing`, `visualization`, `supervision`,
`project-administration`, `funding-acquisition`.

### Reglas de formato

```
✅ Booleanos:   TRUE o FALSE  (MAYÚSCULAS)
✅ Listas:      economía, estadística, análisis  (comas, sin corchetes)
✅ Fechas:      MM/DD/YYYY  →  01/15/2025
✅ Guardar:     siempre como .xlsx (no .xls ni .csv)

❌ draft: true          → debe ser TRUE
❌ [economía, análisis] → sin corchetes
❌ economía; análisis   → sin punto y coma
❌ 19-12-2025           → usar MM/DD/YYYY
```

---

## 10. Ejemplos de configuración de campos

### Campos comunes

```
title:        Análisis Económico de la Región Ayacucho 2024
shorttitle:   Análisis Económico 2024
subtitle:     Un Estudio Comprehensivo del Desarrollo Regional
date:         12/19/2025
draft:        FALSE
abstract:     Este estudio analiza el comportamiento económico de la región
              Ayacucho durante el año 2024...
description:  Análisis económico comprehensivo de Ayacucho 2024.
keywords:     economía regional, Ayacucho, desarrollo económico, INEI
tags:         economía, análisis, Perú, Ayacucho
categories:   Economía Regional, Análisis Económico
image:        featured.png
eval:         FALSE
bibliography: referencias.bib
```

### Autor 1 (correspondiente)

```
author_1_name:                  Edison Achalma
author_1_corresponding:         TRUE
author_1_orcid:                 0000-0001-6996-3364
author_1_email:                 elmer.achalma.09@unsch.edu.pe
author_1_affiliation_name:      Universidad Nacional de San Cristóbal de Huamanga
author_1_affiliation_department: Facultad de Ciencias Económicas
author_1_affiliation_city:      Ayacucho
author_1_affiliation_region:    Ayacucho
author_1_affiliation_country:   Perú
author_1_roles:                 conceptualization, methodology, writing
```

### Autor 2 (coautor)

```
author_2_name:             María González Pérez
author_2_corresponding:    FALSE
author_2_orcid:            0000-0002-9876-5432
author_2_email:            mgonzalez@universidad.edu
author_2_affiliation_name: Universidad Nacional de San Cristóbal de Huamanga
author_2_roles:            investigation, data curation, writing
```

### Tipo STU (estudiante)

```
course:    Metodología de la Investigación Económica (ECON 5101)
professor: Dr. Edison Achalma Mendoza
duedate:   01/23/2025
note:      Código de estudiante: 2020123456. Sección A
```

### Tipo JOU (revista)

```
journal:         Revista Peruana de Economía
volume:          2025, Vol. 7, No. 1, 1--25
copyrightnotice: 2025
copyrightext:    Universidad Nacional de San Cristóbal de Huamanga.
                 Todos los derechos reservados.
```

### Tipo MAN — envío a revista

```
floatsintext:  FALSE
numbered_lines: TRUE
meta_analysis: FALSE
mask:          FALSE
```

### Tipo MAN — revisión ciega

```
floatsintext:  FALSE
numbered_lines: TRUE
meta_analysis: FALSE
mask:          TRUE
```

### Casos especiales

**Serie de artículos:**

```
# Artículo 1
title:      Series de Tiempo en Economía: Parte I - Fundamentos
categories: Series Temporales, Tutorial
tags:       series-de-tiempo, parte-1

# Artículo 2
title:      Series de Tiempo en Economía: Parte II - Modelos ARIMA
categories: Series Temporales, Tutorial
tags:       series-de-tiempo, parte-2, arima
```

**Artículo con múltiples archivos de bibliografía:**

```
bibliography: referencias.bib, extra.bib
```

---

## 11. Filtros avanzados

```bash
# Solo un blog
--blog pub_axiomata

# Solo rutas con "2025-06"
--filter-path "2025-06"

# Solo la carpeta python de un blog
--filter-path "python"

# Combinar (blog + período)
--blog pub_numerus-scriptum --filter-path "2025-06"

# Siempre probar primero
--dry-run
```

---

## 12. Casos de uso comunes

### Publicar artículos (draft: TRUE → FALSE)

```bash
# 1. Abrir Excel, filtrar draft=TRUE, cambiar a FALSE, guardar
libreoffice excel_databases/quarto_metadata.xlsx

# 2. Simular
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run

# 3. Aplicar
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx
```

### Actualizar keywords de forma masiva

```bash
# 1. Crear base de datos
python3 main.py create-template ~/Documents

# 2. En Excel, editar columna keywords:
#    Artículo 1: economía, análisis, datos
#    Artículo 2: programación, python, tutorial

# 3. Actualizar
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx
```

### Cambiar tipo de documento (JOU → STU)

```bash
# 1. En Excel, columna tipo_documento: cambiar jou → stu
# 2. Llenar campos STU: course, professor, duedate
# 3. Actualizar
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx
```

### Agregar artículos nuevos sin perder datos existentes

```bash
python3 main.py create-template ~/Documents --config metadata_config.yml \
    --incremental
```

### Detectar campos YAML sin columna en Excel

```bash
python3 main.py detect-new-fields ~/Documents
# Muestra los campos y el comando exacto para agregarlos
```

### Actualizar solo artículos de un período

```bash
# Solo junio 2025
python3 main.py update ~/Documents excel.xlsx --filter-path "2025-06"

# Solo artículos de Python en numerus-scriptum
python3 main.py update ~/Documents excel.xlsx \
    --blog pub_numerus-scriptum --filter-path "python"
```

### Agregar segundo autor a múltiples artículos

```bash
# 1. En Excel, llenar columnas author_2_*:
#    author_2_name: María García
#    author_2_orcid: 0000-0002-1234-5678
#    author_2_affiliation_name: UNSCH
#    author_2_roles: writing, analysis

# 2. Actualizar
python3 main.py update ~/Documents excel.xlsx
```

### Backup de metadatos

```bash
# Copiar el Excel
cp excel_databases/quarto_metadata.xlsx \
   excel_databases/backup_$(date +%Y%m%d).xlsx

# O usar Git
cd excel_databases
git add quarto_metadata.xlsx
git commit -m "Backup metadatos $(date +%Y-%m-%d)"
```

---

## 13. Fórmulas de Excel útiles

Esta sección recoge fórmulas prácticas para generar y transformar datos
directamente en el Excel de metadatos, sin necesidad de editar manualmente
cada celda.

### 12.1 Eliminar saltos de línea (Enter)

**Con fórmula (recomendado para poder deshacer):**

```excel
=SUBSTITUTE(A1,CHAR(10)," ")
```

Para Windows (que usa CR+LF):

```excel
=SUBSTITUTE(SUBSTITUTE(A1,CHAR(13)," "),CHAR(10)," ")
```

Eliminar sin dejar espacio:

```excel
=SUBSTITUTE(A1,CHAR(10),"")
```

Con limpieza de espacios dobles:

```excel
=TRIM(SUBSTITUTE(A1,CHAR(10)," "))
```

**Con Buscar y Reemplazar (rápido):**

1. Selecciona la columna
2. `Ctrl + H`
3. En **Buscar**: presiona `Ctrl + J`
4. En **Reemplazar**: escribe un espacio
5. Reemplazar todo

---

### 12.2 Generar títulos desde rutas

Convierte `aequilibria/posts/2022-01-17-09-crecimiento-economico/index.qmd`
en `Crecimiento economico`.

**Excel en español:**

```excel
=MAYUSC(IZQUIERDA(SUSTITUIR(TEXTO.ANTES(TEXTO.DESPUES(A1,"-",4),"/"),"-"," "),1))
 & MINUSC(EXTRAE(SUSTITUIR(TEXTO.ANTES(TEXTO.DESPUES(A1,"-",4),"/"),"-"," "),2,99))
```

**Excel en inglés:**

```excel
=UPPER(LEFT(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "),1))
 & LOWER(MID(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "),2,99))
```

Variantes:

```excel
=PROPER(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "))  ← Cada Palabra
=UPPER(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "))   ← TODO MAYÚSCULA
=LOWER(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "))   ← todo minúscula
```

---

### 12.3 Crear enlaces a PDFs

Genera la URL del PDF a partir de `ruta_archivo` (columna A) y `blog_nombre`
(columna B).

**Excel en inglés:**

```excel
="https://" &
IF(B2="website-achalma","achalmaedison",
   IF(B2="chaska","chaska-x",B2)
) &
".netlify.app/" &
SUBSTITUTE(TEXTAFTER(A2,B2&"/"),"index.qmd","index.pdf")
```

**Excel en español:**

```excel
="https://" &
SI(B2="website-achalma","achalmaedison",
   SI(B2="chaska","chaska-x",B2)
) &
".netlify.app/" &
SUSTITUIR(TEXTO.DESPUES(A2,B2&"/"),"index.qmd","index.pdf")
```

**Ejemplo:**

```
ruta_archivo: actus-mercator/inteligencia-comercial/2025-05-15-herramientas/index.qmd
blog_nombre:  actus-mercator
→ https://actus-mercator.netlify.app/inteligencia-comercial/2025-05-15-herramientas/index.pdf
```

---

### 12.4 Extraer fechas de rutas

Extrae la fecha de `posts/2022-01-17-titulo/index.qmd` en formato `MM/DD/YYYY`:

```excel
=TEXT(DATE(LEFT(TEXTAFTER(A2,"/",2),4),MID(TEXTAFTER(A2,"/",2),6,2),MID(TEXTAFTER(A2,"/",2),9,2)),"mm/dd/yyyy")
```

Formatos alternativos:

```excel
=TEXT(DATE(...),"dd/mm/yyyy")     ← DD/MM/YYYY
=TEXT(DATE(...),"yyyy-mm-dd")     ← YYYY-MM-DD
=LEFT(TEXTAFTER(A2,"/",2),4)      ← Solo año (útil para copyrightnotice)
```

**`duedate` condicional (solo para STU):**

```excel
=IF(C2="stu",TEXT(DATE(LEFT(TEXTAFTER(A2,"/",2),4),MID(TEXTAFTER(A2,"/",2),6,2),MID(TEXTAFTER(A2,"/",2),9,2)),"mm/dd/yyyy"),"")
```

---

### 12.5 Gestión de tags

**Agregar tags sin reemplazar los existentes (LibreOffice Calc):**

En una columna auxiliar temporal:

```excel
=IFERROR(
 IF(
  VLOOKUP(A2,Sheet3.$A:$E,5,0)="",
  L2,
  IF(
   L2="",
   VLOOKUP(A2,Sheet3.$A:$E,5,0),
   L2 & ", " & VLOOKUP(A2,Sheet3.$A:$E,5,0)
  )
 ),
 L2
)
```

> **Método seguro:** escribe la fórmula en columna M auxiliar, cópiala hacia
> abajo, luego pega como **Solo valores** sobre la columna L y elimina M.

**Normalizar a minúsculas:**

```excel
=LOWER(TRIM(SUBSTITUTE(L2,","," , ")))
```

---

### 12.6 Extraer información de rutas

**Nombre del blog:**

```excel
=LEFT(A2,FIND("/",A2)-1)
```

**Carpeta del artículo:**

```excel
=TEXTAFTER(TEXTBEFORE(A2,"/index.qmd"),"/"-1)
```

**Detectar tipo de carpeta:**

```excel
=IF(ISNUMBER(SEARCH("posts",A2)),"posts",
 IF(ISNUMBER(SEARCH("talk",A2)),"talk",
 IF(ISNUMBER(SEARCH("publication",A2)),"publication","otros")))
```

**Contar niveles de carpetas:**

```excel
=LEN(A2)-LEN(SUBSTITUTE(A2,"/",""))
```

---

### 12.7 Generar campos automáticos

#### Campo `journal` desde nombre de blog

Solo para artículos JOU:

```excel
=IF($C2<>"jou","",
  IF(OR(LOWER(B2)="dialectica-y-mercado",LOWER(B2)="epsilon-y-beta"),
    PROPER(LEFT(B2,FIND("-y-",B2)-1)),
    PROPER(SUBSTITUTE(B2,"-"," "))
  )
)
```

Resultados: `dialectica-y-mercado → Dialectica`, `epsilon-y-beta → Epsilon`,
`actus-mercator → Actus Mercator`, `aequilibria → Aequilibria`.

#### Campo `volume` (requiere ordenar la hoja primero)

**Paso 1 — Ordenar** por `journal` ascendente, luego por `pub_date` ascendente.

**Paso 2 — Columna auxiliar `vol_number` (ej. columna BC):**

```excel
=IF($C2<>"jou","";1)                                           ← BC2 (primera fila)
=IF($C3<>"jou","";IF(Z3<>Z2;1;IF(BA3<>BA2;BC2+1;BC2)))        ← BC3 (y arrastrar)
```

**Paso 3 — Columna auxiliar `issue_number` (ej. columna BD):**

```excel
=IF($C2<>"jou","";1)                                                     ← BD2
=IF($C3<>"jou","";IF(OR(Z3<>Z2;BA3<>BA2);1;BD2+1))                      ← BD3
```

**Paso 4 — Fórmula final `volume`:**

```excel
=IF($C2<>"jou","";BA2&", Vol. "&BC2&", No. "&BD2&", 10--60")
```

Resultado: `2025, Vol. 2, No. 1, 10--60`

#### Campo `copyrightnotice`

```excel
=IF($C2="jou",LEFT(MID(A2,FIND("/",A2,FIND("/",A2)+1)+1,10),4),"")
```

#### Campo `copyrightext`

```excel
=IF($C2<>"jou","","All rights reserved")
```

Con símbolo ©:

```excel
=IF($C2="jou","© "&LEFT(MID(A2,FIND("/",A2,FIND("/",A2)+1)+1,10),4)&" All rights reserved","")
```

#### Campo `note` (solo STU)

```excel
=IF(AND($C2="stu",$V2<>"",$W2<>""),"Student ID: 09170105","")
```

Opción simple:

```excel
=IF(LOWER($C2)="stu","Student ID: 09170105","")
```

---

### 12.8 Limpieza y normalización

```excel
=TRIM(A1)                          ← Eliminar espacios extras
=SUBSTITUTE(A1," ","")             ← Eliminar todos los espacios
=LOWER(SUBSTITUTE(TRIM(A1)," ","_"))  ← Convertir a snake_case
=LOWER(SUBSTITUTE(TRIM(A1)," ","-"))  ← Convertir a kebab-case
```

---

### 12.9 Fórmulas de validación

**Validar ruta:**

```excel
=IF(AND(ISNUMBER(FIND("/",A2)),ISNUMBER(FIND("index.qmd",A2))),"Válido","❌ Inválido")
```

**Detectar artículos con fecha:**

```excel
=IF(ISNUMBER(VALUE(MID(TEXTAFTER(A2,"/",-2),1,4))),"Con fecha","⏭️ Sin fecha")
```

**Generar shorttitle automático (máx. 50 chars):**

```excel
=IF(LEN(B2)>50,LEFT(B2,47)&"...",B2)
```

**Generar keywords desde título:**

```excel
=LOWER(SUBSTITUTE(SUBSTITUTE(D2," ",", "),"  "," "))
```

**Validar email:**

```excel
=IF(AND(ISNUMBER(FIND("@",A1)),ISNUMBER(FIND(".",A1)),LEN(A1)>5),"✅","❌")
```

**Validar ORCID (`0000-0001-2345-6789`):**

```excel
=IF(AND(LEN(A1)=19,ISNUMBER(FIND("0000-",A1))),"Válido","❌ Inválido")
```

**Concatenar múltiples columnas con separador:**

```excel
=TEXTJOIN(", ",TRUE,A1,B1,C1,D1,E1)
```

---

### 12.10 Macros VBA útiles

**Eliminar saltos de línea en rango seleccionado:**

```vba
Sub EliminarEnter()
    Dim celda As Range
    For Each celda In Selection
        celda.Value = Replace(celda.Value, vbLf, " ")
        celda.Value = Replace(celda.Value, vbCr, " ")
    Next celda
End Sub
```

**Normalizar tags:**

```vba
Sub NormalizarTags()
    Dim celda As Range
    For Each celda In Selection
        celda.Value = LCase(celda.Value)
        celda.Value = Replace(celda.Value, " ", "_")
        celda.Value = Replace(celda.Value, "á", "a")
        celda.Value = Replace(celda.Value, "é", "e")
        celda.Value = Replace(celda.Value, "í", "i")
        celda.Value = Replace(celda.Value, "ó", "o")
        celda.Value = Replace(celda.Value, "ú", "u")
    Next celda
End Sub
```

---

### 12.11 Atajos de teclado

#### Excel (Windows)

| Atajo              | Acción                       |
| ------------------ | ---------------------------- |
| `Ctrl + H`         | Buscar y reemplazar          |
| `Ctrl + J`         | (en Buscar) Captura el Enter |
| `Ctrl + 1`         | Formato de celdas            |
| `Ctrl + Shift + L` | Activar/desactivar filtros   |
| `Alt + Enter`      | Insertar Enter en celda      |
| `Ctrl + Enter`     | Llenar selección con fórmula |
| `Ctrl + D`         | Rellenar hacia abajo         |
| `Ctrl + R`         | Rellenar hacia la derecha    |

#### LibreOffice Calc

| Atajo              | Acción                       |
| ------------------ | ---------------------------- |
| `Ctrl + H`         | Buscar y reemplazar          |
| `Ctrl + J`         | (en Buscar) Captura el Enter |
| `Ctrl + Shift + F` | Insertar función             |
| `Ctrl + ;`         | Insertar fecha actual        |
| `Ctrl + Shift + ;` | Insertar hora actual         |

---

### 12.12 Errores comunes en fórmulas

| Error               | Causa                          | Solución                                                 |
| ------------------- | ------------------------------ | -------------------------------------------------------- |
| `#VALUE!`           | Dato no válido para la función | Usa `IFERROR(formula,"")`                                |
| `#REF!`             | Referencia a celda eliminada   | Revisa referencias                                       |
| `#NAME?`            | Nombre de función incorrecto   | Verifica idioma (es/en)                                  |
| Fórmula no calcula  | Modo de cálculo manual         | Fórmulas → Cálculo automático                            |
| Enter no se elimina | Puede ser `CHAR(13)`           | Usa `SUBSTITUTE(SUBSTITUTE(A1,CHAR(13),""),CHAR(10),"")` |

---

## 14. Añadir funcionalidades nuevas

La arquitectura modular facilita extender el sistema. Cada módulo tiene una
responsabilidad clara:

| Módulo                | Qué cambias aquí                                     |
| --------------------- | ---------------------------------------------------- |
| `lib/config.py`       | Nuevos campos en `ALL_FIELDS`, exclusiones, defaults |
| `lib/yaml_parser.py`  | Cómo se lee y parsea el YAML                         |
| `lib/collector.py`    | Qué archivos se recolectan                           |
| `lib/field_mapper.py` | Nuevos campos Excel↔YAML, nuevas conversiones        |
| `lib/excel_writer.py` | Formato o estructura del Excel                       |
| `lib/qmd_updater.py`  | Cómo se escribe el YAML al archivo                   |
| `lib/sync.py`         | Nuevos comandos de sincronización                    |
| `main.py`             | Solo el `argparse` y el handler del nuevo comando    |

### Ejemplo: agregar campo `foo_bar`

1. Añadir `"foo_bar"` a `ALL_FIELDS` en `lib/config.py`.
2. Añadir extracción en `extract_value()` en `lib/field_mapper.py`.
3. Añadir escritura en `apply_row_to_yaml()` en `lib/field_mapper.py`.
4. El campo aparece automáticamente en el Excel y se actualiza con `update`.

### Ejemplo: agregar comando `export-json`

1. Crear la función en el módulo temático (ej. `lib/sync.py`).
2. Importarla en `lib/__init__.py`.
3. Añadir el subparser en `build_parser()` en `main.py`.
4. Añadir el handler y registrarlo en `COMMAND_MAP`.

---

## 15. Resolución de problemas

### "La ruta base no existe"

```bash
ls ~/Documents
python3 main.py create-template /ruta/absoluta/completa
```

### "No se encontraron artículos válidos"

Solo se procesan `index.qmd` cuya **carpeta padre** empieza con `YYYY-MM-DD`:

```
✅ posts/2025-06-01-mi-articulo/index.qmd
❌ posts/mi-articulo/index.qmd              ← sin fecha
❌ index.qmd                                ← configuración
```

### "Blog no encontrado"

Si configuraste `allowed_blogs`, el nombre debe coincidir exactamente con la
carpeta (`pub_axiomata`, no `axiomata`).

### El YAML actualizado tiene formato distinto

El módulo `qmd_updater.py` usa `yaml.dump()` con `sort_keys=False`, `indent=2`.
El orden de claves sigue `YAML_FIELD_ORDER` en `lib/config.py`. Para cambiarlo,
edita esa lista.

### Cambios no se aplican

1. Verifica booleanos en mayúsculas (`TRUE`/`FALSE`)
2. Excel guardado como `.xlsx`
3. Sin celdas fusionadas
4. Columna `ruta_archivo` no modificada
5. Prueba primero con `--dry-run`

### Autores no se actualizan

1. `author_N_name` no debe estar vacío
2. Solo un autor puede tener `corresponding: TRUE`
3. ORCID: formato `0000-0000-0000-0000`

### Error "bool object has no attribute 'get'"

Causa: `citation: true` en el YAML (booleano en vez de dict). Corrección:

```yaml
# ❌ Incorrecto
citation: true

# ✅ Correcto
citation:
  type: article-journal
  author: Edison Achalma
```

### Problemas con LibreOffice

Advertencias "Error 509" son normales y no afectan la funcionalidad.
Los caracteres con acento en instrucciones pueden mostrarse como `?` en
versiones antiguas — actualiza LibreOffice o ignóralos.

---

## Mejores prácticas

1. **Hacer backup antes de actualizar:** `cp -r ~/Documents/publicaciones ~/Documents/publicaciones_backup`
2. **Siempre usar `--dry-run` primero** para ver los cambios sin aplicarlos.
3. **Mantener Git** en la carpeta de scripts para versionar `metadata_config.yml` y los Excel.
4. **Nombres descriptivos para Excel:** `metadata_axiomata_publicar_2025-06.xlsx` en vez de `metadata.xlsx`.
5. **Verificar después de actualizar:** renderizar un blog de prueba con `quarto render`.
6. **Para campos booleanos:** siempre `TRUE` o `FALSE` en mayúsculas.
7. **Para listas (keywords, tags, categories):** separar con comas, sin corchetes, sin punto y coma.
8. **Usar el menú interactivo** (`./quick_start.sh`) para operaciones frecuentes y el CLI para scripts.
