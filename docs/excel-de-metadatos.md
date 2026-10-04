---
tipo: doc
titulo: 'Referencia del Excel de metadatos: columnas, formatos y fórmulas'
estado: activo
---
# Referencia del Excel de metadatos

Para quien edita `backend/script_metadata_manager/excel_databases/quarto_metadata.xlsx`. Describe la
hoja; los comandos que la generan y la aplican están en el
[README del metadata manager](../backend/script_metadata_manager/README.md). La lista de columnas sale de
`ALL_FIELDS` en `backend/script_metadata_manager/lib/config.py`: si este documento y ese archivo
discrepan, manda el código.

## Hojas

| hoja | qué contiene |
|---|---|
| `INSTRUCCIONES` | guía breve que escribe `create-template` |
| `METADATOS` | una fila por artículo (`index.qmd` dentro de una carpeta `AAAA-MM-DD-…`) |

## Columnas de identificación (no se editan)

| col. | columna | qué es |
|---|---|---|
| A | `ruta_archivo` | ruta del `index.qmd` relativa a la ruta base (`~/Documents`); identifica la fila |
| B | `blog_nombre` | blog del artículo (`pub_axiomata`, o la ruta de la sección del hub) |
| C | `tipo_documento` | `jou`, `stu`, `man` o `doc` (modo de apaquarto), detectado del YAML |

Si se cambia `ruta_archivo`, `update` no encuentra el archivo y salta la fila.

## Columnas editables

Una celda vacía **elimina** el campo del `.qmd` al aplicar `update`.

| col. | columna | formato | ejemplo |
|---|---|---|---|
| D | `title` | texto | `Proporcionalidad de magnitudes` |
| E | `shorttitle` | texto corto (encabezado de página) | `Proporcionalidad` |
| F | `subtitle` | texto | |
| G | `date` | `AAAA-MM-DD`, celda de **texto** | `2025-01-15` |
| H | `draft` | `TRUE` / `FALSE` | `FALSE` = publicado |
| I | `abstract` | texto libre | |
| J | `description` | texto breve (metadatos del sitio) | |
| K | `keywords` | lista separada por comas | `economía, análisis, datos` |
| L | `tags` | lista separada por comas | `python, tutorial` |
| M | `categories` | lista separada por comas | `Economía, Estadística` |
| N | `image` | nombre de archivo | `featured.png` |
| O | `eval` | `TRUE` / `FALSE` | |
| P | `bibliography` | archivo, o varios separados por comas | `references.bib` |
| Q | `citation_type` | tipo CSL: `article-journal`, `book`, `chapter`, `paper-conference`, `thesis`, `report` | |
| R | `citation_author` | texto | |
| S | `citation_pdf_url` | URL completa; la mantiene `sync-pdf-urls` | |
| T | `links_enabled` | `TRUE` / `FALSE` | |
| U | `links_data` | lista JSON de `{"icon", "name", "url"}` | `[{"icon": "github", "name": "Repositorio", "url": "https://…"}]` |

Campos por tipo de documento:

| col. | columna | tipo | formato |
|---|---|---|---|
| V | `course` | `stu` | texto (`Metodología (ECON 5101)`) |
| W | `professor` | `stu` | texto |
| X | `duedate` | `stu` | texto; apaquarto lo imprime tal cual y `fechas-iso` no lo toca |
| Y | `note` | `stu` | texto |
| Z | `journal` | `jou` | texto |
| AA | `volume` | `jou` | texto (`2025, Vol. 7, No. 1, 1--25`) |
| AB | `copyrightnotice` | `jou` | año |
| AC | `copyrightext` | `jou` | texto |
| AD | `floatsintext` | `man`, `doc` | `TRUE` / `FALSE` (figuras en el texto o al final) |
| AE | `numbered_lines` | `man`, `doc` | `TRUE` / `FALSE` |
| AF | `meta_analysis` | `man` | `TRUE` / `FALSE` |
| AG | `mask` | `man` | `TRUE` para revisión ciega |

Autores (solo se actualizan los que ya existen en el `index.qmd`; `update` no crea autores):

| col. | columnas | formato |
|---|---|---|
| AH–AQ | `author_1_name`, `_corresponding`, `_orcid`, `_email`, `_affiliation_name`, `_affiliation_department`, `_affiliation_city`, `_affiliation_region`, `_affiliation_country`, `_roles` | `corresponding` en `TRUE` para un solo autor; ORCID `0000-0000-0000-0000`; roles separados por comas |
| AR–AU | `author_2_name`, `_orcid`, `_affiliation_name`, `_roles` | ídem |
| AV–AY | `author_3_name`, `_orcid`, `_affiliation_name`, `_roles` | ídem |

Roles CRediT admitidos: `conceptualization`, `methodology`, `software`, `validation`, `formal-analysis`,
`investigation`, `resources`, `data-curation`, `writing`, `visualization`, `supervision`,
`project-administration`, `funding-acquisition`.

Desde la columna AZ la hoja del autor lleva columnas auxiliares (`pub_date`, `year_pub`, `vol_number`,
`issue`…) que sirven a las fórmulas de abajo. No están en `ALL_FIELDS`: `update` no las lee ni las escribe.

## Reglas de formato

```text
Booleanos   TRUE o FALSE, en mayúsculas          (no: true)
Listas      economía, estadística, análisis       (no: [economía, análisis] ni economía; análisis)
Fechas      2025-01-15, como texto                 (no: 12/19/2025; fechas-iso lo convierte)
Fórmulas    pegar como valores antes de update     (openpyxl no calcula: una fórmula sin valor guardado llega vacía y borra el campo)
Archivo     .xlsx                                  (no .xls ni .csv)
```

El YAML resultante sigue el orden de `YAML_FIELD_ORDER` (`backend/script_metadata_manager/lib/config.py`); salvo que solo cambie
`date`, `update` reescribe el bloque entero con comillas normalizadas.

## Fórmulas para rellenar columnas

Las que se pueden hacer con un comando, mejor con el comando: `sync-dates` (fecha desde la carpeta),
`sync-pdf-urls` (URL del PDF), `normalize-tags`, `add-tags`, `replace-tags`. Estas otras no tienen
comando. Fórmulas en Excel en inglés; en LibreOffice, `;` como separador de argumentos.

**Título desde la ruta** (`…/2022-01-17-09-crecimiento-economico/index.qmd` → `Crecimiento economico`):

```text
=UPPER(LEFT(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A2,"-",4),"/"),"-"," "),1)) & LOWER(MID(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A2,"-",4),"/"),"-"," "),2,99))
```

**`journal` desde el blog**, solo en filas `jou` (`dialectica-y-mercado` → `Dialectica`, `actus-mercator` → `Actus Mercator`):

```text
=IF($C2<>"jou","",IF(OR(LOWER(B2)="dialectica-y-mercado",LOWER(B2)="epsilon-y-beta"),PROPER(LEFT(B2,FIND("-y-",B2)-1)),PROPER(SUBSTITUTE(B2,"-"," "))))
```

**`volume`**, solo en filas `jou`. Ordenar antes la hoja por `journal` (Z) y `pub_date` (AZ); `year_pub`
en BA; columnas auxiliares de volumen (BC) y número (BD):

```text
BC2  =IF($C2<>"jou","",1)
BC3  =IF($C3<>"jou","",IF(Z3<>Z2,1,IF(BA3<>BA2,BC2+1,BC2)))      (y arrastrar)
BD2  =IF($C2<>"jou","",1)
BD3  =IF($C3<>"jou","",IF(OR(Z3<>Z2,BA3<>BA2),1,BD2+1))          (y arrastrar)
AA2  =IF($C2<>"jou","",BA2&", Vol. "&BC2&", No. "&BD2&", 10--60")
```

**`copyrightnotice`** (el año de la carpeta del artículo) y **`copyrightext`**:

```text
AB2  =IF($C2="jou",LEFT(MID(A2,FIND("/",A2,FIND("/",A2)+1)+1,10),4),"")
AC2  =IF($C2<>"jou","","All rights reserved")
```

**`note`** en filas `stu` (sustituir `<código>`):

```text
Y2   =IF(LOWER($C2)="stu","Student ID: <código>","")
```

## Errores frecuentes

| síntoma | causa |
|---|---|
| un cambio no se aplica | booleano en minúsculas, celdas combinadas, `ruta_archivo` editada o archivo guardado en otro formato |
| un campo desaparece del `.qmd` | la celda quedó vacía, o tenía una fórmula sin valor guardado |
| un autor no se actualiza | `author_N_name` vacío, o el autor no existe en el `index.qmd` |
| `'bool' object has no attribute 'get'` | el `.qmd` tiene `citation: true`; `citation` debe ser un bloque con `type` y `author` |
