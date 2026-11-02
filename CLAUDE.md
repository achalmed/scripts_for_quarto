---
tipo: guia_ia
estado: activo
---
# CLAUDE.md — quarto-studio (repo `scripts_for_quarto`)

Guía para el asistente. En español, como todo el ecosistema. `AGENTS.md` es un enlace a este archivo.
Léase antes: `estado.md` (dónde está; §Por hacer), `README.md` (qué es, contrato con el hub, uso),
`docs/README.md`, el `suite.yml` y el README de la herramienta que se toque y, si el cambio toca lo que
lanza la GUI, `studio/README.md`.

## Reglas que no se negocian

- **Dónde va cada cosa nueva.** En la raíz solo `README.md`, `CLAUDE.md`, `AGENTS.md`, `estado.md`,
  `LICENSE` y `CHANGELOG.md` como documentos; cualquier otro `.md` ahí está fuera de lugar
  (`meta/docs/historial/NORMATIVA_ARCHIVOS.md` §15.11).

  | lo que apareció | va a | nunca a |
  |---|---|---|
  | cómo se usa una herramienta, una opción nueva | el README de su carpeta (`backend/script_*/`) | un `GUIA_*.md` |
  | qué escribe una herramienta en el hub o los pubs | `README.md` §«Contrato con el hub» | una copia en `web` |
  | una columna, un formato o una fórmula del Excel | `docs/excel-de-metadatos.md` | el README del metadata manager |
  | por qué se decidió algo | `docs/decisiones.md` (fecha en cada entrada) | un `DECISION_<fecha>.md` |
  | una versión nueva de una herramienta | su constante en el código y `CHANGELOG.md` | el README |
  | un pendiente | `estado.md` §Por hacer, con fecha y dueño | un `TODO.md` |
  | un bloque generado desactualizado | `core/suites.py generar --aplicar` o `core/docs.py indice --aplicar` | la edición a mano |

  Lo que hiciste en esta sesión va al mensaje de commit, no a un archivo.

- **Cinco herramientas independientes y su GUI en el mismo repo.** Cada `backend/script_*/` es autónomo
  (`main.*` + config + `lib/`, `suite.yml`, README). Quarto Studio (`studio/`, `VentanaBase` de `gui-comun` 3.0;
  `docs/reingenieria.md`) nunca importa su código: construye un `Command` y lo corre como proceso (`gui_comun.tareas`), y
  encuentra cada entrada en `backend/` (`studio/quarto_app/services/paths.py`, `BACKENDS`). Lo común de los studios es
  del repo `gui-comun`; aquí no se copia.
- **Python no construye interfaz y QML no ejecuta procesos**: los controladores (`studio/quarto_app/controladores/`)
  exponen modelos y `@Slot`; el QML pinta y pide. Cada operación existe una sola vez en `studio/quarto_app/aplicacion.py`
  y su catálogo es `studio/quarto_app/services/operaciones.py`: **F5 simula** (la CLI o el plan de la ventana) y
  **Ctrl+Intro aplica** tras confirmar; publicar nombra sitio y dominio y exige que el destino sea el del sitio. Sin colores.
- **Corre con `/usr/bin/python3`** y se relanza con el `.venv` del repo si existe (`--system-site-packages`: el PySide6
  del sistema más `openpyxl` y `pandas`; `requirements.txt`); nunca se instala PySide6 en él. Nada de QtWidgets.
- **Las pruebas y las capturas del studio usan la familia de muestra** (`studio/muestra.py`), nunca `web` ni los pubs, y
  **ninguna prueba publica** (`tests/run.sh`). Quarto omite los archivos de un proyecto bajo una carpeta oculta
  (`~/.cache/…`): el render real de las pruebas va a `/var/tmp`.
- **Los blogs viven en el hub.** Hub `web` (repo `website-achalma`) y 11 `pub_*` como submódulos
  en `web/_pubs/` (el guion bajo evita que Quarto los renderice como parte del
  hub). Cada herramienta los localiza por una sola variable (`QBLOG_PUBS_SUBDIR`, `PUBINDEX_PUBS_SUBDIR`,
  `PUBS_SUBDIR`), por defecto `<hub>/_pubs`; `website-achalma` sigue aceptado como alias del hub
  (`QBLOG_WEBSITE_DIR`, `HUB_ALIASES`). Un blog se nombra por carpeta (`axiomata`) o en corto
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
- **Un solo camino de instalación documentado**: el `.venv` del repo con `pip install -r requirements.txt`
  (`studio/README.md`); `install.sh` (conda) del metadata manager es alternativa.

## Cómo se verifica un cambio

Desde `~/Documents`:

```bash
python3 core/archivos.py validar quarto-studio           # A01–A14 y D01–D12
python3 core/docs.py verificar quarto-studio             # índice de docs/ al día
python3 core/suites.py validar                                   # los suite.yml contra el esquema
python3 core/suites.py generar                                   # ¿bloques de README desfasados? (simula)
meta/doctor/main.sh --breve
```

Desde la raíz del repo:

```bash
bash -n backend/script_blogs_manager/main.sh                     # sintaxis; un archivo por invocación
python3 -m py_compile backend/*/main.py                        # sintaxis Python
( cd backend/script_metadata_manager && python3 main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run )  # simular antes de aplicar
backend/script_pub_index_symlink/main.sh --dry-run               # y --check-broken
backend/script_generador_publicacion_similar/main.sh "../web/_pubs/axiomata" --dry-run
```

Pruebas: `python3 -m pytest -q tests -p no:cacheprovider --basetemp ~/.cache/pytest/quarto-ola4` (nunca
`/tmp`; fixtures y remoto bare en temporal, jamás el hub ni los pubs: Netlify despliega con cada push) y, para la
ventana, `tests/run.sh` (`tests/studio/`, la familia de muestra, cada QML y `--smoke` con `/usr/bin/python3`).
Lo aplicado de verdad se confirma dentro del pub y luego el puntero del submódulo en el hub.

## Detalles que cuesta redescubrir

- **`chaska` publica en `chaska-x.netlify.app`**, no derivable de la carpeta. Por eso la URL base de
  cada blog se resuelve por voto mayoritario entre los `pdf-url` existentes (una URL mal pegada no
  envenena la detección) y `blog_base_urls` de `metadata_config.yml` tiene prioridad
  (`backend/script_metadata_manager/lib/path_sync.py`).
- **Nombres que ya no existen:** `script_tag_manager/` (los comandos de tags viven en el metadata manager), los
  scripts sueltos de fechas y `pdf-url` (hoy `sync-dates` y `sync-pdf-urls`); las herramientas son `backend/` y la
  GUI, `studio/` (antes `app/` y, de la ola 4 al 2026-10-27, la carpeta quarto/ de gui-suites).
- **`fix_qmd_files.py` es un alias** de `backend/script_format_yaml/main.py` (la lógica está en su `lib/`); Quarto Studio invoca el alias.
- **El asistente de posts no se automatiza** (`backend/script_blogs_manager/lib/07-post-creator.sh`, unas
  50 preguntas encadenadas): es la única lógica portada a Python (`studio/quarto_app/services/post_service.py`), que
  genera el mismo `index.qmd` desde «Nueva entrada…». Las confirmaciones de los scripts (`--clean-broken`, `clean-all`,
  el respaldo) se responden por la entrada estándar después de que la ventana confirmó con el usuario.
- **Una operación a la vez en Quarto Studio** (los backends no son seguros en paralelo) y el estado de cada sitio sigue
  la regla de la puerta R6 (`studio/quarto_app/services/sitios.py`): «con problemas» no deja publicar.
- **El Excel guarda `date` como texto**, no como fórmula: openpyxl no calcula y una fórmula sin valor
  guardado llega vacía y borra el campo. `backend/script_metadata_manager/excel_databases/quarto_metadata.xlsx` está versionado a
  propósito (`docs/decisiones.md`); `respaldos/` y `logs/` están ignorados.
- **`web/_indice/` es del vault**, ignorado en el hub: `pub_index_symlink` solo crea enlaces por año ahí; nunca se borra `web`.
- **`generador_publicacion_similar` escribe un fragmento (identidad en un comentario de la línea 1, sin frontmatter) en la carpeta de cada subblog**
  para `{{< include >}}`; ordena por el glob (con prefijo de fecha equivale a cronológico) y
  **borra** el índice de un subblog que se queda sin posts; la capitalización usa `sed` GNU.
- **`excel_output_dir` relativo se resuelve contra la carpeta del metadata manager** (sin la clave, su `excel_databases/`).

## Dónde está cada cosa

| pregunta | documento |
|---|---|
| qué escribe cada herramienta en el hub y los pubs | `README.md` §«Contrato con el hub» |
| la GUI: diseño, arquitectura, el .venv, cómo añadir una operación | `studio/README.md` |
| comandos y filtros del metadata manager | `backend/script_metadata_manager/README.md` |
| render, preview, publicar, posts APA, git, respaldos | `backend/script_blogs_manager/README.md` |
| qué es una publicación, conflictos, logs del índice | `backend/script_pub_index_symlink/README.md` |
| reparar bloques YAML y `---` pegados | `backend/script_format_yaml/README.md` |
| estructuras `website`/`blog`, URL base | `backend/script_generador_publicacion_similar/README.md` |
| columnas, formatos y fórmulas del Excel | `docs/excel-de-metadatos.md` |
| por qué se decidió algo; dónde está el repo y qué falta | `docs/decisiones.md`; `estado.md` |
| versiones y desde cuándo | `CHANGELOG.md` |
| el hub, los submódulos y el tema compartido | `web/docs/pubs-submodulos.md`, `web/CLAUDE.md` |
| el contrato de suite y los bloques generados | `core/suite.schema.yml`, `core/README.md` |
| normativa de archivos, fechas y cabeceras | `meta/docs/historial/NORMATIVA_ARCHIVOS.md` |
