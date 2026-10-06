---
tipo: guia_ia
estado: activo
---
# CLAUDE.md — scripts-quarto (repo `scripts_for_quarto`)

Guía para el asistente. En español, como todo el ecosistema. `AGENTS.md` es un enlace a este archivo.
Léase antes: `estado.md` (dónde está; §Por hacer), `README.md` (qué es, contrato con el hub, uso),
`docs/README.md`, el `suite.yml` y el README de la herramienta que se toque y, si el cambio toca lo que
lanza la GUI, el repo `gui-suites` (`gui-suites/quarto/README.md`).

## Reglas que no se negocian

- **Dónde va cada cosa nueva.** En la raíz solo `README.md`, `CLAUDE.md`, `AGENTS.md`, `estado.md`,
  `LICENSE` y `CHANGELOG.md` como documentos; cualquier otro `.md` ahí está fuera de lugar
  (`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.11).

  | lo que apareció | va a | nunca a |
  |---|---|---|
  | cómo se usa una herramienta, una opción nueva | el README de su carpeta (`backend/script_*/`) | un `GUIA_*.md` |
  | qué escribe una herramienta en el hub o los pubs | `README.md` §«Contrato con el hub» | una copia en `04 index` |
  | una columna, un formato o una fórmula del Excel | `docs/excel-de-metadatos.md` | el README del metadata manager |
  | por qué se decidió algo | `docs/decisiones.md` (fecha en cada entrada) | un `DECISION_<fecha>.md` |
  | una versión nueva de una herramienta | su constante en el código y `CHANGELOG.md` | el README |
  | un pendiente | `estado.md` §Por hacer, con fecha y dueño | un `TODO.md` |
  | un bloque generado desactualizado | `core/suites.py generar --aplicar` o `core/docs.py indice --aplicar` | la edición a mano |

  Lo que hiciste en esta sesión va al mensaje de commit, no a un archivo. Si nada encaja, pregunta antes
  de crear un documento.

- **Cinco herramientas independientes; su GUI vive en el repo `gui-suites`.** Cada `backend/script_*/` es
  autónomo (`main.*` + config + `lib/`, `suite.yml`, README). Quarto Studio (`gui-suites/quarto/`, ola 4, fase B)
  nunca importa su código: construye un `Command` y lo ejecuta con `QProcess`, y encuentra cada entrada por
  `SCRIPTS_QUARTO` de `core/env.py` (`gui-suites/comun/rutas.py`, `BACKENDS`). Si un script se mueve o cambia de
  nombre, se toca allí.
- **Los blogs viven en el hub.** Hub `04 index` (repo `website-achalma`) y 11 `pub_*` como submódulos
  en `04 index/_pubs/` (el guion bajo evita que Quarto los renderice como parte del
  hub). Cada herramienta los localiza por una sola variable (`QBLOG_PUBS_SUBDIR`, `PUBINDEX_PUBS_SUBDIR`,
  `PUBS_SUBDIR`), por defecto `<hub>/_pubs`; `website-achalma` sigue aceptado como alias del hub
  (`QBLOG_WEBSITE_DIR`, `HUB_ALIASES`). Un blog se nombra por carpeta (`pub_axiomata`) o en corto
  (`axiomata`). Un post es `<blog>/posts/AAAA-MM-DD-titulo/index.qmd`: lo que no empieza por fecha no
  es un post. Las herramientas toman la raíz (`DOCS_ROOT`) y la carpeta del hub (`INDEX_DIR`) de
  `core/env.sh` y `core/env.py`; la raíz se fuerza exportando `DOCS_ROOT` (sin alias propios de la raíz desde
  la ola 0).
- **La verdad de un post es su `index.qmd`; el Excel es la mesa de trabajo.** `update` escribe solo
  donde hay diferencias y una celda vacía borra el campo; antes de un cambio masivo, `--dry-run`
  siempre: en la terminal solo `publish` y `git-commit` de `blogs_manager` simulan por defecto (actúan
  con `--aplicar`, nunca `git add .` y siempre tras la puerta R6 del hub, `$INDEX_DIR/scripts/puerta-r6.sh`).
- **UN escritor de YAML y UN reordenador:** `qmd_updater.write_yaml_to_qmd` y `field_mapper.reorder_yaml`
  en `backend/script_metadata_manager/lib/`. No se introducen implementaciones paralelas; toda operación
  de tags pasa por el mismo `collector` + `write_yaml_to_qmd` que `update`.
- **Toda operación de tags normaliza la lista completa** (minúsculas, sin tildes, espacios → `_`:
  `Gestión Empresarial` → `gestion_empresarial`; sin duplicados) **y omite los artículos sin campo
  `tags`**: nunca se crean tags donde no existían.
- **`sync-pdf-urls` nunca crea un bloque `citation`**: solo actualiza `citation.pdf-url` donde ya existe.
- **Fechas ISO `AAAA-MM-DD` en `date`** (`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §3): `sync-dates`
  escribe ISO; `fechas-iso` solo cambia el formato. Cuando solo cambia `date`, se sustituye esa única
  línea del frontmatter y el resto del archivo queda byte-idéntico (comentarios y comillas incluidos);
  el escritor completo es el recurso de reserva.
- **Patrón Bash modular** (`blogs_manager`, `pub_index_symlink`, `generador_publicacion_similar`): un
  `main.sh` delgado carga los `lib/NN-*.sh` en orden numérico; solo `00-config.sh` fija rutas, colores
  y valores por defecto; globales con prefijo (`QBLOG_`, `PUBINDEX_`, `GENIDX_`) y guarda `*_LOADED`.
- **`main.py` del metadata manager es solo argparse y despacho**; la lógica vive en su `lib/`.
- **Raíz y logger de `core/`**: ninguna suite escribe `$HOME/Documents` ni define su logger; carga
  `core/env.sh` o `core/env.py` y envuelve `core/shell-lib` o `core/py-common` (FS2). Ninguna ruta de
  máquina (`$HOME/...`) en código ni en documentos.
- **Lo generado no se edita**: los bloques `<!-- suite:inicio -->` y `<!-- suites:inicio -->` de los
  README salen de los `suite.yml` con `core/suites.py generar --aplicar`; `_site/` y `_freeze/`
  los regenera su herramienta.
- **Español con tildes** en código, mensajes, comentarios y docs; nada del despacho en este repo.
- **Un solo camino de instalación documentado**: `pip install -r requirements.txt`; `install.sh` (conda)
  del metadata manager es alternativa.

## Cómo se verifica un cambio

Desde `~/Documents`:

```bash
python3 core/archivos.py validar scripts_quarto_studio          # A01–A14 y D01–D12
python3 core/docs.py verificar scripts_quarto_studio            # índice de docs/ al día
python3 core/suites.py validar                                   # los suite.yml contra el esquema
python3 core/suites.py generar                                   # ¿bloques de README desfasados? (simula)
meta/doctor/main.sh --breve
```

Desde la raíz del repo:

```bash
bash -n backend/script_blogs_manager/main.sh                     # sintaxis; un archivo por invocación
python3 -m py_compile backend/*/main.py                        # sintaxis Python
cd backend/script_metadata_manager                              # el gestor de metadatos, desde su carpeta
python3 main.py find-differences ~/Documents excel_databases/quarto_metadata.xlsx  # Excel vs .qmd
python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run  # simular antes de aplicar
cd ../..
backend/script_pub_index_symlink/main.sh --dry-run               # y --check-broken
backend/script_generador_publicacion_similar/main.sh "../04 index/_pubs/pub_axiomata" --dry-run
python3 backend/script_format_yaml/main.py --directory "../04 index/_pubs/pub_axiomata" --recursive --dry-run
```

Pruebas: `python3 -m pytest -q tests -p no:cacheprovider --basetemp ~/.cache/pytest/quarto-ola4` (nunca
`/tmp`; fixtures y remoto bare en temporal, jamás el hub ni los pubs: Netlify despliega con cada push).
Lo aplicado de verdad se confirma dentro del pub y luego el puntero del submódulo en el hub.

## Detalles que cuesta redescubrir

- **`pub_chaska` publica en `chaska-x.netlify.app`**, no derivable de la carpeta. Por eso la URL base de
  cada blog se resuelve por voto mayoritario entre los `pdf-url` existentes (una URL mal pegada no
  envenena la detección) y `blog_base_urls` de `metadata_config.yml` tiene prioridad
  (`backend/script_metadata_manager/lib/path_sync.py`).
- **Nombres que ya no existen:** `script_tag_manager/` y `qmd_tag_manager.py` (los comandos de tags
  viven en el metadata manager); `1_sincronizar_fecha_carpeta_en_index_qmd.py` y
  `3_actualizar_enlace_pdf_en_qmd.py` (hoy `sync-dates` y `sync-pdf-urls`); el prefijo `quarto_studio/`
  en una ruta nunca existió: las herramientas son `backend/` y la GUI, desde la ola 4, `gui-suites/quarto/`.
- **`fix_qmd_files.py` es un alias** de `backend/script_format_yaml/main.py`; la lógica
  está en `config.py` y `lib/` de esa carpeta. Quarto Studio todavía invoca el alias (`paths.yaml_formatter`, repo `gui-suites`).
- **El asistente de posts no se automatiza** (`backend/script_blogs_manager/lib/07-post-creator.sh`, unas
  50 preguntas encadenadas): es la única lógica portada a Python (`gui-suites/quarto/quarto_app/services/post_service.py`), que
  genera el mismo `index.qmd`. Las confirmaciones de los scripts (`--clean-broken`, respaldo) se
  responden por stdin después de que la GUI confirmó con el usuario.
- **El runner de Quarto Studio rechaza ejecuciones concurrentes**: los backends no son seguros en paralelo.
- **El Excel guarda `date` como texto**, no como fórmula: openpyxl no calcula y una fórmula sin valor
  guardado llega vacía y borra el campo. `backend/script_metadata_manager/excel_databases/quarto_metadata.xlsx` está versionado a
  propósito (`docs/decisiones.md`); `respaldos/` y `logs/` están ignorados.
- **`04 index/_indice/` es del vault**, ignorado en el hub: `pub_index_symlink` solo crea enlaces por
  año ahí; nunca se borra `04 index` para reindexar, solo el contenido de `_indice/`.
- **`generador_publicacion_similar` escribe un fragmento `tipo: fragmento` en la carpeta de cada subblog**
  para `{{< include >}}`; ordena por el glob (con prefijo de fecha equivale a cronológico) y
  **borra** el índice de un subblog que se queda sin posts; la capitalización usa `sed` GNU.
- **`excel_output_dir` relativo se resuelve contra la carpeta del metadata manager** (y sin la clave
  es su `excel_databases/`): desde la ola 4 ya no nace la carpeta fantasma en la raíz que el doctor vigila.

## Dónde está cada cosa

| pregunta | documento |
|---|---|
| qué escribe cada herramienta en el hub y los pubs | `README.md` §«Contrato con el hub» |
| la GUI: arquitectura, decisiones, cómo añadir una herramienta | `gui-suites/quarto/README.md` (repo `gui-suites`) |
| comandos y filtros del metadata manager | `backend/script_metadata_manager/README.md` |
| render, preview, publicar, posts APA, git, respaldos | `backend/script_blogs_manager/README.md` |
| qué es una publicación, conflictos, logs del índice | `backend/script_pub_index_symlink/README.md` |
| reparar bloques YAML y `---` pegados | `backend/script_format_yaml/README.md` |
| estructuras `website`/`blog`, URL base | `backend/script_generador_publicacion_similar/README.md` |
| columnas, formatos y fórmulas del Excel | `docs/excel-de-metadatos.md` |
| por qué se decidió algo; dónde está el repo y qué falta | `docs/decisiones.md`; `estado.md` |
| versiones y desde cuándo | `CHANGELOG.md` |
| el hub, los submódulos y el tema compartido | `04 index/docs/pubs-submodulos.md`, `04 index/CLAUDE.md` |
| el contrato de suite y los bloques generados | `core/suite.schema.yml`, `core/README.md` |
| normativa de archivos, fechas y cabeceras | `meta/docs/historial/NORMATIVA_ARCHIVOS.md` |
