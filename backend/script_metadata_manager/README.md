---
tipo: readme
estado: activo
---
# backend/script_metadata_manager/ — metadatos, tags, fechas y pdf-url de todos los .qmd de la familia de blogs desde una base Excel (v2.3)

<!-- suite:inicio -->
**Suite `metadata_manager`** · objetivo *publicacion* · estado *activo* · python · interfaz cli

Metadatos y etiquetas de todos los .qmd de la familia de blogs desde una base Excel: plantilla, aplicar, normalizar tags, fechas, URL de PDF.

- Escribe en: web · simula por defecto: sí
- Entrada: excel_databases/*.xlsx
- Depende de: python3, openpyxl

Comandos:

```bash
main.py create-template
main.py update [--dry-run]
main.py normalize-tags
main.py sync-dates
main.py audit-tags
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-09-20); no se edita a mano.</sub>
<!-- suite:fin -->

## Qué es

Edita en masa el frontmatter de los posts de la familia de blogs a través de un Excel: `create-template`
vuelca a una hoja los metadatos de cada `index.qmd` cuya carpeta empieza por `AAAA-MM-DD-`, se editan
allí, y `update` los devuelve a los archivos donde difieren. Además normaliza y audita tags, sincroniza
`date` con el nombre de la carpeta y `citation.pdf-url` con la ruta publicada. La verdad de un post es
su `index.qmd`; el Excel es la mesa de trabajo. Las columnas, sus formatos y las fórmulas de la hoja
están en [`docs/excel-de-metadatos.md`](../../docs/excel-de-metadatos.md).

## Uso

Se ejecuta desde su carpeta, con las dependencias de `requirements.txt` de la raíz del repo
(`pyyaml`, `pandas`, `openpyxl`). **`update` y los comandos que escriben aplican directamente: se simula
con `--dry-run`.** El menú `./quick_start.sh` ofrece los mismos flujos.

```bash
cd backend/script_metadata_manager
python3 main.py create-template ~/Documents --config metadata_config.yml --incremental   # añade al Excel los artículos nuevos
python3 main.py find-differences ~/Documents excel_databases/quarto_metadata.xlsx        # Excel frente a los .qmd
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --config metadata_config.yml --dry-run
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --config metadata_config.yml --blog pub_axiomata
```

Sin `--config metadata_config.yml`, `create-template` procesa todos los blogs y guarda el Excel en
una carpeta excel_databases **bajo la ruta base** (en la raíz de `~/Documents`), no en esta carpeta.

| comando | qué hace | escribe |
|---|---|---|
| `create-config RUTA` | escribe un `metadata_config.yml` por defecto (`-o` para otro nombre) | el archivo |
| `create-template RUTA [--incremental] [-b BLOG]` | genera el Excel; con `--incremental`, solo añade artículos nuevos y conserva las fórmulas | el Excel |
| `update RUTA EXCEL` | aplica el Excel a los `.qmd` | los `.qmd` |
| `find-differences RUTA EXCEL [--max-show N]` | lista los artículos desincronizados | nada |
| `detect-new-fields RUTA` | campos YAML sin columna en el Excel, con la orden para añadirlos | nada |
| `add-columns RUTA EXCEL CAMPO…` | añade columnas al Excel | el Excel |
| `sync-article RUTA EXCEL ARTÍCULO` · `sync-batch RUTA EXCEL` | sincronización interactiva, de uno o de varios | los `.qmd` |
| `normalize-tags DESTINO` | minúsculas, sin tildes, espacios a `_`, sin duplicados | destino |
| `replace-tags DESTINO VIEJO:NUEVO…` · `remove-tags DESTINO TAG…` · `add-tags DESTINO TAG…` | reemplazos, bajas y altas masivas (`remove-tag` es alias) | destino |
| `tag-stats DESTINO [--top N]` · `audit-tags DESTINO [--threshold X]` | estadísticas · variantes y erratas de la taxonomía | nada |
| `sync-dates DESTINO` | `date` desde la carpeta `AAAA-MM-DD-…`, en ISO | destino |
| `fechas-iso DESTINO` | `date` al formato `AAAA-MM-DD` sin cambiar la fecha | destino |
| `sync-pdf-urls DESTINO` | `citation.pdf-url` desde la ruta publicada | destino |

`RUTA` es la raíz del espacio de trabajo (`~/Documents`). `DESTINO` es un Excel (`.xlsx`: cambia solo la
hoja, para revisar y luego aplicar con `update`) o un directorio (cambia los `.qmd`). Filtros comunes:
`-b/--blog pub_axiomata`, `-p/--filter-path 2025-06` (subcadena de la ruta) y `-c/--config`. Todo
comando que escribe acepta `--dry-run`.

## Configuración

`metadata_config.yml`: `allowed_blogs` (vacío = todos), `excluded_folders` (nombres de carpeta, no
rutas), `excel_output_dir` y, opcional, `blog_base_urls` (URL base por blog para `sync-pdf-urls`; sin
ella, se vota entre los `pdf-url` existentes). Los blogs se localizan en `04 index/_pubs/`
(`PUBS_SUBDIR` en `lib/config.py`); `website-achalma` es alias del hub.

## Estructura

| carpeta | qué es | dueño |
|---|---|---|
| `main.py` | solo `argparse` y despacho (`build_parser`, `COMMAND_MAP`) | a mano |
| `lib/config.py` | versión (`VERSION`), campos del Excel (`ALL_FIELDS`), orden del YAML (`YAML_FIELD_ORDER`), exclusiones | a mano |
| `lib/collector.py` · `yaml_parser.py` | búsqueda de artículos; lectura del YAML con su `_metadata.yml` | a mano |
| `lib/field_mapper.py` · `qmd_updater.py` | YAML ⇄ fila del Excel; el único escritor del YAML | a mano |
| `lib/excel_writer.py` · `sync.py` | hojas `METADATOS` e `INSTRUCCIONES`; diferencias y sincronización | a mano |
| `lib/tag_utils.py` · `tag_operations.py` · `tag_reports.py` | tags: funciones puras, operaciones, informes | a mano |
| `lib/fechas.py` · `path_sync.py` | fechas ISO; `sync-dates`, `fechas-iso`, `sync-pdf-urls` | a mano |
| `excel_databases/quarto_metadata.xlsx` | el Excel de trabajo, versionado; `respaldos/` ignorado | `create-template` y el autor |
| `metadata_config.yml` · `quick_start.sh` · `install.sh` | configuración; menú; instalador alternativo con conda | a mano |
| `suite.yml` | manifiesto de la suite | a mano; el bloque de arriba lo genera `core/suites.py` |

Un campo nuevo: añadirlo a `ALL_FIELDS` en `lib/config.py` y su lectura y escritura en
`extract_value()` y `apply_row_to_yaml()` de `lib/field_mapper.py`. Un comando nuevo: su función en el
módulo temático, el subparser en `build_parser()` y su entrada en `COMMAND_MAP`.

## Límite honesto

- **No simula por defecto en la terminal**: `update`, los comandos de tags y los de fechas escriben salvo `--dry-run` (la GUI sí marca la simulación por defecto).
- **Una celda vacía borra el campo** del `.qmd`, y una fórmula sin valor guardado cuenta como vacía (openpyxl no calcula fórmulas).
- **Nunca crea un bloque `citation`**: `sync-pdf-urls` solo actualiza `citation.pdf-url` donde ya existe.
- **Toda operación de tags omite los artículos sin campo `tags`** (nunca los crea) y normaliza la lista completa, no solo el tag tocado.
- **Un solo escritor de YAML** (`qmd_updater.write_yaml_to_qmd`) **y un solo reordenador** (`field_mapper.reorder_yaml`): salvo cuando solo cambia `date`, el bloque se reescribe entero con comillas y orden normalizados.
- **Solo ve `index.qmd` dentro de carpetas `AAAA-MM-DD-…`**; un post fuera de esa convención no entra en el Excel.
- **El Excel queda atrás** si se edita un `.qmd` a mano, hasta `create-template --incremental` o `find-differences`; `update` solo escribe donde hay diferencias.
- **La URL base no se deduce del nombre de carpeta** (`pub_chaska` publica en `chaska-x.netlify.app`): sin `pdf-url` previos, hay que declararla en `blog_base_urls`.
