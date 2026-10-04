---
tipo: readme
estado: activo
---
# scripts_quarto_studio/ — herramientas y GUI de la familia de blogs Quarto (repo scripts_for_quarto, suite quarto_studio)

<!-- suite:inicio -->
**Suite `quarto_studio`** · objetivo *publicacion* · estado *activo* · python · interfaz gui

Interfaz de escritorio (PySide6) sobre los backends de la familia de blogs Quarto: render, publicación, metadatos, índices.

- Escribe en: web, vault · simula por defecto: sí
- Depende de: PySide6, blogs_manager, metadata_manager, pub_index_symlink

Comandos:

```bash
main.py
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-10-04); no se edita a mano.</sub>
<!-- suite:fin -->

<!-- suites:inicio -->
Suites de esta carpeta (6); índice global en `meta/INDICE_SCRIPTS.md`. Patrón: M main · C config · L lib.

| Suite | Carpeta | Objetivo | Escribe en | Simula | Timer | Estado | Patrón |
|---|---|---|---|---|---|---|---|
| `blogs_manager` | [scripts_quarto_studio/backend/script_blogs_manager](backend/script_blogs_manager/) | publicacion | web, git, archivos | no |  | activo | `MCL` |
| `format_yaml` | [scripts_quarto_studio/backend/script_format_yaml](backend/script_format_yaml/) | publicacion | web | no |  | activo | `MCL` |
| `generador_publicacion_similar` | [scripts_quarto_studio/backend/script_generador_publicacion_similar](backend/script_generador_publicacion_similar/) | publicacion | web | no |  | activo | `MCL` |
| `metadata_manager` | [scripts_quarto_studio/backend/script_metadata_manager](backend/script_metadata_manager/) | publicacion | web | no |  | activo | `MCL` |
| `pub_index_symlink` | [scripts_quarto_studio/backend/script_pub_index_symlink](backend/script_pub_index_symlink/) | publicacion | vault | no |  | activo | `MCL` |
| `quarto_studio` | [scripts_quarto_studio](./) | publicacion | web, vault | sí |  | activo | `MCL` |

<sub>Bloque generado desde los `suite.yml` por `core/suites.py generar` (2026-10-04); no se edita a mano.</sub>
<!-- suites:fin -->

## Qué es

Cinco herramientas de línea de comandos (tres en Bash, dos en Python) y una aplicación de escritorio
(Quarto Studio, PySide6) que las envuelve, para mantener la familia de blogs Quarto del autor: el hub
`04 index` (repo `website-achalma`) y sus satélites `pub_*`, submódulos git del hub en `04 index/_pubs/`
(la lista, en `04 index/_pubs/pubs.yml`). Resuelven lo que Quarto no hace por sí solo: editar el frontmatter de cientos de posts
a la vez desde un Excel, normalizar etiquetas y fechas, reparar bloques YAML, generar índices de contenido,
mantener un índice por año en el vault y renderizar o publicar los doce sitios desde un solo menú.

Cuatro nombres para una sola cosa: la carpeta es `scripts_quarto_studio`; el remoto en GitHub se llama
`scripts_for_quarto`; la suite raíz se llama `quarto_studio` y la GUI, «Quarto Studio».

**No es** un tema, un sitio ni una plantilla de Quarto: el tema de los doce sitios vive en el hub y se
propaga con `04 index/scripts/sync-theme-pubs.sh`; el contenido de cada post vive en su pub. Tampoco es
una biblioteca: cada herramienta es autónoma, con su `suite.yml`, su README y su `lib/`, y la GUI las
invoca como procesos, nunca importa su código. Depende de `core/` (raíz y logger) y de `04 index`
(`meta/workspace.yml`). Su único dato propio es el Excel de metadatos,
`backend/script_metadata_manager/excel_databases/quarto_metadata.xlsx`, versionado a propósito como mesa
de trabajo: la verdad de cada post sigue siendo su `index.qmd`.

## Contrato con el hub

Lo que cada herramienta escribe fuera de este repo. Este repo es el proveedor: `04 index` enlaza aquí
desde su `CLAUDE.md` y su `docs/`. La verdad de un post es siempre su `index.qmd`; el
Excel es la mesa de trabajo, y lo que se edite a mano en un `.qmd` prevalece hasta el siguiente
`create-template --incremental` o `find-differences`.

| herramienta | escribe | dónde | cómo se protege |
|---|---|---|---|
| `metadata_manager` | el frontmatter YAML de los `index.qmd` | `04 index/blog/posts/` y los `posts/` de cada pub | `--dry-run` (la terminal aplica sin él); solo cambia lo que difiere; un solo escritor de YAML; nunca crea `citation` |
| `format_yaml` | el bloque YAML de cada `.qmd` (delimitadores y líneas en blanco) | la carpeta que se le pase | idempotente; `--dry-run` |
| `generador_publicacion_similar` | `_contenido_<subblog>.qmd`, fragmentos con `tipo: fragmento` para `{{< include >}}` | la carpeta de cada subblog del blog que se le pase | `--dry-run`; si un subblog queda sin posts, borra su índice |
| `pub_index_symlink` | enlaces simbólicos por año, nunca copias | `04 index/_indice/` (ignorado en git; del vault) | omite lo que ya apunta bien; no toca archivos reales; `--dry-run` |
| `blogs_manager` | `_site/`, `_freeze/`, posts nuevos, commits, respaldos | hub y pubs; `06 archives/backups-publicaciones/`; `quarto publish` | `clean-all` pide confirmación; no tiene `--dry-run` |
| `app/` (Quarto Studio) | nada propio: lanza las cinco anteriores | — | una operación a la vez; «Dry-run» marcado por defecto en metadatos e índices |

Cómo están montados los pubs y por qué se confirma dentro del pub antes que en el hub:
`04 index/docs/pubs-submodulos.md`.

## Uso

```bash
pip install -r requirements.txt                       # PySide6, pyyaml, pandas, openpyxl (un entorno conda es opcional)
python3 main.py                                       # Quarto Studio, la GUI
backend/script_blogs_manager/main.sh                  # menú interactivo; `main.sh help` lista los comandos
backend/script_blogs_manager/main.sh list             # los sitios que ve el gestor
backend/script_blogs_manager/main.sh render axiomata  # nombre corto o pub_axiomata; también preview, publish, clean, git-*
cd backend/script_metadata_manager                    # el gestor de metadatos se ejecuta desde su carpeta
python3 main.py create-template ~/Documents --config metadata_config.yml --incremental   # Excel al día
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run        # simular; sin --dry-run aplica
python3 main.py normalize-tags ~/Documents --config metadata_config.yml --dry-run        # igual: sync-dates, fechas-iso, sync-pdf-urls
cd ../..
python3 backend/script_format_yaml/main.py --directory "../04 index/_pubs/pub_axiomata" --recursive --dry-run
backend/script_generador_publicacion_similar/main.sh "../04 index/_pubs/pub_axiomata" --dry-run
backend/script_pub_index_symlink/main.sh --dry-run    # sin --dry-run escribe 04 index/_indice/; --check-broken, --clean-broken
./build_resources.sh                                  # opcional: compila resources.qrc (la GUI funciona sin este paso)
```

Regla de oro: `--dry-run` antes de cualquier cambio masivo. En la terminal ninguna herramienta simula
por defecto; `blogs_manager` es la única sin `--dry-run`. La GUI marca la simulación por defecto en
metadatos e índices.

## Estructura

| carpeta | qué es | dueño / generador |
|---|---|---|
| `main.py` | entrada de la GUI: `QApplication` + `MainWindow`, nada más | a mano |
| `app/` | Quarto Studio: `application.py`, `settings.py`, `models/`, `services/`, `workers/`, `controllers/`, `ui/`, `widgets/`, `dialogs/`, `utils/`, `resources/` | a mano; `app/README.md` |
| `backend/script_blogs_manager/` | Bash, `main.sh` + `lib/`: listar, render, preview, publicar, posts APA, git, respaldos | a mano |
| `backend/script_metadata_manager/` | Python, `main.py` + `lib/`: metadatos, tags, fechas y `pdf-url` desde el Excel de `excel_databases/`; `metadata_config.yml`; `install.sh`, `quick_start.sh` | a mano; el Excel lo escribe `create-template`; `respaldos/` ignorado |
| `backend/script_pub_index_symlink/` | Bash, `main.sh` + `lib/`: enlaces por año en `04 index/_indice/`; `logs/` ignorado | a mano |
| `backend/script_format_yaml/` | Python, `main.py` + `config.py` + `lib/`; `fix_qmd_files.py` es un alias | a mano |
| `backend/script_generador_publicacion_similar/` | Bash, `main.sh` + `lib/`: índices `_contenido_*.qmd` | a mano |
| `suite.yml` (raíz y uno por backend) | manifiesto de cada suite (`core/suite.schema.yml`) | a mano; los bloques de README los genera `core/suites.py generar --aplicar` |
| `requirements.txt` · `build_resources.sh` | dependencias Python; compilación opcional de los recursos Qt | a mano |
| `docs/` | referencia del Excel de metadatos y registro de decisiones; índice generado | a mano; `docs/README.md` por `core/docs.py indice` |
| `CHANGELOG.md` · `LICENSE` | versiones de cada herramienta con fecha ISO; MIT | a mano |

Variante `suite` de `meta/workspace.yml`: cada herramienta se documenta en su carpeta; `docs/` guarda
solo lo que no cabe en una puerta.

## Documentación

| documento | para qué leerlo |
|---|---|
| `CLAUDE.md` | reglas para el asistente: invariantes de diseño, cómo verificar, trampas |
| `app/README.md` | la GUI: arquitectura, regla de dependencias, cómo añadir una herramienta |
| `backend/script_blogs_manager/README.md` | manual del gestor de blogs v3.0 |
| `backend/script_metadata_manager/README.md` | manual del gestor de metadatos y tags (Excel, filtros, fórmulas, columnas) |
| `backend/script_pub_index_symlink/README.md` | qué cuenta como publicación, conflictos, logs |
| `backend/script_format_yaml/README.md` | el formateador YAML y cómo reparar `---` pegados |
| `backend/script_generador_publicacion_similar/README.md` | estructuras `website` y `blog`, URL base |
| `docs/excel-de-metadatos.md` | columnas, formatos y fórmulas del Excel de metadatos |
| `docs/decisiones.md` | por qué el repo es como es, y los pendientes |
| `CHANGELOG.md` | qué versión de cada herramienta hay y desde cuándo |
| `04 index/docs/pubs-submodulos.md` | el hub y sus submódulos (frontera con `04 index`) |
| `meta/INDICE_SCRIPTS.md` | estas suites entre las del espacio de trabajo (generado) |

## Límite honesto

- **No hay pruebas automáticas, lint ni build**: la comprobación es `--dry-run`, `bash -n`, `py_compile` y
  mirar el resultado en un pub.
- **Los backends no son seguros en paralelo**: mutan los mismos árboles; la GUI ejecuta una operación a la
  vez y en terminal hay que hacer lo mismo.
- **`blogs_manager` no simula**: `clean`, `clean-all`, `publish` y `git-commit` escriben de verdad; solo
  `clean-all` pide confirmación (en la GUI, también las operaciones sobre todos los blogs).
- **El Excel no es la verdad**: si se edita un `.qmd` a mano, el Excel queda atrás hasta regenerarlo;
  `update` solo escribe donde hay diferencias, pero una celda vacía borra el campo del `.qmd`.
- **Solo `date` se sustituye línea a línea**; cualquier otro cambio reescribe el bloque YAML completo
  (comillas y orden normalizados por `field_mapper.reorder_yaml`).
- **`pub_chaska` publica en `chaska-x.netlify.app`**: la URL base no se deriva del nombre de carpeta; por eso
  la detección vota entre los `pdf-url` existentes y `blog_base_urls` de `metadata_config.yml` manda.
- **El asistente de posts es interactivo** (`07-post-creator.sh`, unas 50 preguntas): no se automatiza; la
  GUI lo sustituye con `post_service.py`, que genera el mismo `index.qmd`.
- **Un solo camino de instalación documentado**: `pip install -r requirements.txt`;
  `backend/script_metadata_manager/install.sh` (con conda) es una alternativa, no un requisito.
- Licencia MIT (`LICENSE`); el contenido de los blogs es del autor y vive en sus repos.
