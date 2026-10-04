---
tipo: changelog
estado: activo
---
# CHANGELOG — scripts_quarto_studio (repo `scripts_for_quarto`)

Versiones de las cinco herramientas y de la GUI, con fecha ISO, lo más reciente arriba (formato
inspirado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); números [SemVer](https://semver.org/lang/es/)).
Cada herramienta declara su versión una sola vez en el código: `QBLOG_VERSION`
(`backend/script_blogs_manager/lib/00-config.sh`), `GENIDX_VERSION`
(`backend/script_generador_publicacion_similar/lib/00-config.sh`), `VERSION`
(`backend/script_metadata_manager/lib/config.py`) y `APP_VERSION` (`app/__init__.py`); `format_yaml` y
`pub_index_symlink` no llevan número en el código. Los porqués están en [`docs/decisiones.md`](docs/decisiones.md).

Vigentes: `blogs_manager` 3.0.0 · `metadata_manager` 2.3.0 · `generador_publicacion_similar` 4.0.0 ·
`format_yaml` 2.0 · `pub_index_symlink` (sin número) · Quarto Studio 1.0.0.

## Sin versión nueva

### Cambiado

- 2026-09-15 · Los índices `_contenido_<subblog>.qmd` del generador llevan frontmatter `tipo: fragmento`.
- 2026-09-07 · Las cinco herramientas siguen el patrón `main` + `config` + `lib` y toman la raíz del
  espacio de trabajo y el registro de `core/`; `format_yaml` gana `main.py`, `config.py` y
  `lib/formato.py`, y `fix_qmd_files.py` queda como alias.
- 2026-09-06 · `blogs_manager`, `pub_index_symlink` y `metadata_manager` localizan los `pub_*` en
  `04 index/_pubs/` (variables `QBLOG_PUBS_SUBDIR`, `PUBINDEX_PUBS_SUBDIR`, `PUBS_SUBDIR`) y el hub en
  `04 index`, con `website-achalma` como alias; el índice por año pasa a `04 index/_indice/`.

## metadata_manager 2.3.0 — 2026-09-15

### Añadido

- Comando `fechas-iso`: lleva `date` a `AAAA-MM-DD` sin cambiar la fecha; `lib/fechas.py`.

### Cambiado

- `date` canónico en ISO `AAAA-MM-DD` en los `.qmd` y en el Excel, como texto y no como fórmula; si solo
  cambia `date`, se sustituye esa línea y el resto del archivo queda intacto.
- `find-differences` y `update` resuelven los pubs por nombre dentro de `_pubs/`.

## Quarto Studio 1.0.0 — 2026-07-13

### Añadido

- Aplicación de escritorio PySide6 (`app/`, `main.py`, `build_resources.sh`, `requirements.txt`) que
  lanza las herramientas como procesos. Las herramientas pasan a `backend/`.

## metadata_manager 2.2 y 2.1; generador_publicacion_similar 4.0.0 — 2026-07-03

### Añadido

- `metadata_manager` 2.2: `sync-dates` y `sync-pdf-urls` (URL base por voto entre los `pdf-url` y
  `blog_base_urls`), que sustituyen dos scripts sueltos.
- `metadata_manager` 2.1: `normalize-tags`, `replace-tags`, `remove-tags`, `add-tags`, `tag-stats` y
  `audit-tags`, que sustituyen al antiguo gestor de tags.
- `generador_publicacion_similar` 4.0.0: el directorio del blog es argumento; `--base-url`,
  `--type auto|website|blog` y `--dry-run`.

### Corregido

- Generador: detección de las secciones del hub por la ubicación de `_quarto.yml`; rutas con espacios;
  URL base con barra final; el índice ya no se vacía antes de saber si hay publicaciones.

## metadata_manager 2.0 — 2026-06-22

### Cambiado

- El script único pasa a `main.py` + módulos en `lib/`; `quick_start.sh` como menú; blogs con nombre `pub_*`.

## blogs_manager 3.0.0; pub_index_symlink — 2026-06-21

### Añadido

- `pub_index_symlink`: enlaces simbólicos por año a cada carpeta de publicación.
- `blogs_manager` 3.0.0: los auxiliares (`init-blog`, `check-structure`, `backup`) son comandos de
  `main.sh`; autodetección de `~/Documents` (`QBLOG_DOCS_DIR`); nombre corto sin `pub_`.

### Corregido

- `blogs_manager`: `clean-all` y `new-post` desde la línea de comandos llamaban a funciones inexistentes.
