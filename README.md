---
tipo: readme
estado: activo
---
# scripts_quarto_studio/ — herramientas de la familia de blogs Quarto (repo scripts_for_quarto); su GUI vive en studios

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

Cinco herramientas de línea de comandos (tres en Bash, dos en Python) para mantener la familia de blogs Quarto del autor: el hub
`04 index` (repo `website-achalma`) y sus satélites `pub_*`, submódulos git del hub en `04 index/_pubs/`
(la lista, en `04 index/_pubs/pubs.yml`). Resuelven lo que Quarto no hace por sí solo: editar el frontmatter de cientos de posts
a la vez desde un Excel, normalizar etiquetas y fechas, reparar bloques YAML, generar índices de contenido,
mantener un índice por año en el vault y renderizar o publicar los doce sitios desde un solo menú.

Dos nombres para una sola cosa: la carpeta es `scripts_quarto_studio` y el remoto en GitHub se llama
`scripts_for_quarto`. La aplicación de escritorio que las envuelve, **Quarto Studio** (suite `quarto_studio`), vive
desde la ola 4 en el repo `studios` (`studios/quarto/`) y encuentra estas herramientas por `SCRIPTS_QUARTO` de
`core/env.py`.

**No es** un tema, un sitio ni una plantilla de Quarto: el tema de los doce sitios vive en el hub y se
propaga con `04 index/scripts/sync-theme-pubs.sh`; el contenido de cada post vive en su pub. Tampoco es
una biblioteca: cada herramienta es autónoma, con su `suite.yml`, su README y su `lib/`, y Quarto Studio las
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
| `blogs_manager` | `_site/`, `_freeze/`, posts nuevos, commits, respaldos | hub y pubs; `06 archives/backups-publicaciones/`; el remoto git (Netlify) o `quarto publish <destino>` | `publish` y `git-commit` simulan salvo `--aplicar`, empujan solo tras la puerta R6 y no hacen `git add .`; `clean-all` pide confirmación |
| Quarto Studio (repo `studios`) | nada propio: lanza las cinco anteriores | — | una operación a la vez; «Dry-run» marcado por defecto en metadatos e índices |

Cómo están montados los pubs y por qué se confirma dentro del pub antes que en el hub:
`04 index/docs/pubs-submodulos.md`.

## Uso

```bash
pip install -r requirements.txt                       # pyyaml, pandas, openpyxl (un entorno conda es opcional)
python3 ../studios/quarto/main.py                     # Quarto Studio, la GUI (repo studios)
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
```

Regla de oro: `--dry-run` antes de cualquier cambio masivo. En la terminal ninguna herramienta simula
por defecto, salvo `publish` y `git-commit` de `blogs_manager`, que simulan sin `--aplicar`. La GUI
marca la simulación por defecto en metadatos e índices, y publica y confirma solo tras mostrar la simulación.

## Estructura

| carpeta | qué es | dueño / generador |
|---|---|---|
| `backend/script_blogs_manager/` | Bash, `main.sh` + `lib/`: listar, render, preview, publicar, posts APA, git, respaldos | a mano |
| `backend/script_metadata_manager/` | Python, `main.py` + `lib/`: metadatos, tags, fechas y `pdf-url` desde el Excel de `excel_databases/`; `metadata_config.yml`; `install.sh`, `quick_start.sh` | a mano; el Excel lo escribe `create-template`; `respaldos/` ignorado |
| `backend/script_pub_index_symlink/` | Bash, `main.sh` + `lib/`: enlaces por año en `04 index/_indice/`; `logs/` ignorado | a mano |
| `backend/script_format_yaml/` | Python, `main.py` + `config.py` + `lib/`; `fix_qmd_files.py` es un alias | a mano |
| `backend/script_generador_publicacion_similar/` | Bash, `main.sh` + `lib/`: índices `_contenido_*.qmd` | a mano |
| `suite.yml` (uno por backend) | manifiesto de cada suite (`core/suite.schema.yml`) | a mano; los bloques de README los genera `core/suites.py generar --aplicar` |
| `requirements.txt` | dependencias Python de los backends | a mano |
| `tests/` | pytest: cada suite en simulación no escribe nada; el flujo de `publish`/`git-commit` con un remoto bare local | a mano |
| `docs/` | referencia del Excel de metadatos y registro de decisiones; índice generado | a mano; `docs/README.md` por `core/docs.py indice` |
| `CHANGELOG.md` · `LICENSE` | versiones de cada herramienta con fecha ISO; MIT | a mano |

Variante `suite` de `meta/workspace.yml`: cada herramienta se documenta en su carpeta; `docs/` guarda
solo lo que no cabe en una puerta.

## Documentación

| documento | para qué leerlo |
|---|---|
| `CLAUDE.md` | reglas para el asistente: invariantes de diseño, cómo verificar, trampas |
| `studios/quarto/README.md` | la GUI (repo `studios`): arquitectura, regla de dependencias, cómo añadir una herramienta |
| `backend/script_blogs_manager/README.md` | manual del gestor de blogs v3.0 |
| `backend/script_metadata_manager/README.md` | manual del gestor de metadatos y tags (Excel, filtros, fórmulas, columnas) |
| `backend/script_pub_index_symlink/README.md` | qué cuenta como publicación, conflictos, logs |
| `backend/script_format_yaml/README.md` | el formateador YAML y cómo reparar `---` pegados |
| `backend/script_generador_publicacion_similar/README.md` | estructuras `website` y `blog`, URL base |
| `docs/excel-de-metadatos.md` | columnas, formatos y fórmulas del Excel de metadatos |
| `docs/decisiones.md` | por qué el repo es como es |
| `estado.md` | dónde está el repo y lo pendiente (§Por hacer) |
| `CHANGELOG.md` | qué versión de cada herramienta hay y desde cuándo |
| `04 index/docs/pubs-submodulos.md` | el hub y sus submódulos (frontera con `04 index`) |
| `meta/INDICE_SCRIPTS.md` | estas suites entre las del espacio de trabajo (generado) |

## Límite honesto

- **Pruebas sí; lint y build, no**: `tests/` comprueba que cada suite en simulación no escribe nada
  (`test_simulacion.py`) y el flujo de `publish`/`git-commit` con un remoto bare local; corren con
  `python3 -m pytest -q tests -p no:cacheprovider --basetemp ~/.cache/pytest/quarto-ola4`. Lo demás es
  `bash -n`, `py_compile` y mirar el resultado de `--dry-run` en un pub.
- **Los backends no son seguros en paralelo**: mutan los mismos árboles; Quarto Studio ejecuta una operación a la
  vez y en terminal hay que hacer lo mismo.
- **`blogs_manager` simula solo lo que publica**: `publish` y `git-commit` piden `--aplicar`; `clean`,
  `clean-all` y `render` escriben de verdad; solo `clean-all` pide confirmación (en la GUI, también las
  operaciones sobre todos los blogs).
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
