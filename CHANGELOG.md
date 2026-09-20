---
tipo: changelog
estado: activo
---
# CHANGELOG — scripts_quarto_studio (repo `scripts_for_quarto`)

Versiones de las cinco herramientas y de la GUI, con la fecha ISO del `git log` del repo, lo más
reciente arriba. Cada herramienta declara su versión una sola vez en su código (`QBLOG_VERSION`,
`GENIDX_VERSION`, `VERSION` en `backend/script_metadata_manager/lib/config.py`, `APP_VERSION` en
`app/__init__.py`) y el H1 de su README la repite. Las razones de diseño están en `CLAUDE.md` y en el
README de cada herramienta.

Vigentes: `blogs_manager` 3.0.0 · `metadata_manager` 2.3.0 · `generador_publicacion_similar` 4.0.0 ·
`format_yaml` 2.0 · `pub_index_symlink` (sin número) · Quarto Studio 1.0.0.

## 2026-09-20 — DOC5: documentación bajo la normativa

- `README.md` reescrito según `meta/NORMATIVA_ARCHIVOS.md` §15.4: un solo H1 (eran dos README
  concatenados: el de «Scripts for Quarto» de 2024 y el de «Quarto Studio»), secciones `Qué es · Contrato
  con el hub · Uso · Estructura · Documentación · Límite honesto`, bloques `suite:` y `suites:` intactos.
  Fuera: «Última actualización: Diciembre 2024», badges sociales, «Próximas características» sin dueño,
  agradecimientos, estadísticas y contacto; las 29 rutas con el prefijo `quarto_studio/` (que nunca
  existió) apuntan ahora a `app/` y `backend/`.
- `CLAUDE.md` en español y ≤ 150 líneas, con las 16 rutas corregidas y todos los detalles conservados.
- Nuevos: `app/README.md` (la sección «Quarto Studio» del README, con las rutas reales), este
  `CHANGELOG.md` (absorbe «Actualizaciones Recientes») y `LICENSE` (MIT, que el README prometía desde 2024
  sin archivo).
- Los cinco `backend/*/README.md` reciben frontmatter, H1 según §9.6 y una sección «Límite honesto»;
  el de `generador_publicacion_similar` deja de decir que los índices van sin frontmatter.

## 2026-09-20 — DOC2: higiene documental

- Fuera de git: `estructura.txt`, los cuatro logs de `backend/script_pub_index_symlink/logs/` y
  `quarto_metadata_original.xlsx` (a `excel_databases/respaldos/`, ignorado); `.gitignore` comentado por
  clase (`logs/`, `*.log`, `respaldos/`). `AGENTS.md` pasa a ser un enlace simbólico a `CLAUDE.md`.
- Bloques de suite del README regenerados por `core/suites.py generar`.

## 2026-09-15 — M5 y M6: normativa de archivos; `metadata_manager` 2.3.0

- v2.3.0: `date` canónico en ISO `AAAA-MM-DD`; nuevo comando `fechas-iso` (solo cambia el formato);
  `lib/fechas.py` con los analizadores puros; el Excel guarda las fechas como texto en vez de la fórmula
  `=TEXT(DATE(…),"mm/dd/yyyy")`; cuando solo cambia `date` se sustituye esa única línea del frontmatter.
- `find-differences` y `update` resuelven los pubs por nombre dentro de `_pubs/`; el generador de
  índices escribe el frontmatter `tipo: fragmento` en cada `_contenido_*.qmd`.
- M5: `suite.yml` con `id` y línea de identidad en las seis suites; identidad §6.2 en `lib/` y
  `__init__.py`; la versión se declara una sola vez en el config de cada herramienta; `app/` con
  identidad del paquete por su ruta (A02).

## 2026-09-07 — FS1 a FS3: las suites sobre `core/`

- FS1: un `suite.yml` por suite (seis) y bloques de README generados por `core/suites.py`.
- FS2: raíz y logger desde `core/` (`env.sh`, `env.py`, `shell-lib`, `py-common`); los loggers de cada
  herramienta pasan a ser envoltorios; sin rutas literales.
- FS3: patrón `main` + `config` + `lib` en las cinco; `format_yaml` gana `main.py`, `config.py` y
  `lib/formato.py`, y `fix_qmd_files.py` queda como alias.

## 2026-09-06 — F3a: los pubs como submódulos del hub

- `blogs_manager`, `pub_index_symlink` y `metadata_manager` localizan los `pub_*` en `04 index/_pubs/`
  (variables `QBLOG_PUBS_SUBDIR`, `PUBINDEX_PUBS_SUBDIR`, `PUBS_SUBDIR`); el hub es `04 index`
  (`QBLOG_WEBSITE_DIR`, `HUB_DIR`, alias `website-achalma`); el índice del vault pasa a
  `04 index/_indice/`.

## 2026-07-13 — Quarto Studio 1.0.0

- GUI PySide6 modular (`app/`: modelos, servicios, workers, controladores, páginas, widgets, diálogos,
  recursos), `main.py`, `build_resources.sh` y `requirements.txt`. Los scripts pasan a `backend/`.

## 2026-07-03 — reorganización; `metadata_manager` 2.1 y 2.2; generador 4.0

- v2.1: `script_tag_manager/` absorbido por el metadata manager (`normalize-tags`, `replace-tags`,
  `remove-tags`, `add-tags`, `tag-stats`, `audit-tags`; `tag_utils.py`, `tag_operations.py`,
  `tag_reports.py`): una herramienta, un parser YAML, una CLI.
- v2.2: los scripts sueltos `1_sincronizar_fecha_carpeta_en_index_qmd.py` y
  `3_actualizar_enlace_pdf_en_qmd.py` absorbidos como `sync-dates` y `sync-pdf-urls` (`path_sync.py`,
  URL base por voto mayoritario y `blog_base_urls`).
- Generador de índices 4.0: `main.sh` + `lib/00…06`; el directorio del blog se pasa como argumento (ya
  no se edita el script), `--base-url`, `--type auto|website|blog`, `--dry-run`.

## 2026-06-22 — `metadata_manager` 2.0

- El monolito `quarto_metadata_manager.py` (~2 460 líneas) pasa a `main.py` + 7 módulos en `lib/`;
  `quick_start.sh` con 13 opciones; nombres de blog `pub_*`; se retira la documentación Excel en
  español.

## 2026-06-21 — `blogs_manager` 3.0 y `pub_index_symlink`

- `build.sh` v2.0 (~2 000 líneas) pasa a `main.sh` + 13 módulos en `lib/`; los auxiliares
  (`init-blog.sh`, `check-structure.sh`, `backup-blogs.sh`, `config.sh`) son comandos de `main.sh`;
  autodetección de `~/Documents` (`QBLOG_DOCS_DIR`); nombre corto sin `pub_`; corregido `clean-all`.
- Nuevo `pub_index_symlink`: enlaces simbólicos por año a cada carpeta de publicación.

## 2026-06-18 — primer commit

## Antes del repo (README de diciembre de 2024)

- `metadata_manager` 1.2 (filtros avanzados, Excel unificado), `script_tag_manager` 1.1 (hoy absorbido),
  `format_yaml` 2.0 (idempotente) y generador de índices 2.0 (estructuras `website` y `blog`). Es lo que
  el README anunciaba como «Actualizaciones recientes»; se conserva aquí como historia.
