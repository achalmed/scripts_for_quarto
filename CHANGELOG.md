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

Vigentes: `blogs_manager` 4.0.0 · `metadata_manager` 2.3.0 · `generador_publicacion_similar` 4.0.0 ·
`format_yaml` 2.0 · `pub_index_symlink` (sin número) · Quarto Studio 1.0.0.

## blogs_manager 4.0.0 — 2026-10-06

### Cambiado

- `publish` y `git-commit` simulan por defecto y solo actúan con `--aplicar`; el menú simula, pregunta y
  aplica, y la GUI muestra la simulación en la consola y pasa `--aplicar` solo si el usuario confirma.
- Ningún `git push` sin la puerta R6 del hub (`$INDEX_DIR/scripts/puerta-r6.sh`); sin la puerta no se empuja.
- `git-commit` deja `git add .`: confirma las fuentes del sitio (los pathspecs `FUENTES` de la puerta),
  las carpetas de contenido con sus imágenes y datos, `_freeze/` y `_site/`, y avisa de lo que queda fuera
  (sueltos de la raíz, punteros de submódulo).
- `publish` sin destino empuja con git (Netlify despliega); `quarto publish` solo con destino explícito.
  El ajuste de la GUI pasa a `blogs/destino_publicacion` (vacío por defecto).

### Corregido

- `git-status` y `git-commit` reconocen los pubs, que son submódulos (su `.git` es un archivo).

## Sin versión nueva

### Cambiado

- 2026-10-06 · Ola 4 (Q1b): `pub_index_symlink --dry-run` ya no escribe su log; `metadata_manager`
  resuelve `excel_output_dir` relativo a su carpeta (por defecto su `excel_databases/`) y solo la crea al
  escribir el Excel; `blogs_manager --dry-run` sin comando no abre el menú y el menú termina sin stdin.
  Pruebas en `tests/` (simulación de cada suite y flujo de publicación con remoto bare local).
- 2026-10-05 · Ola 0: `blogs_manager`, `pub_index_symlink`, `metadata_manager` y la GUI toman la raíz
  (`DOCS_ROOT`) y la carpeta del hub (`INDEX_DIR`) de `core/env`; los alias propios de la raíz y la
  búsqueda hacia arriba de reserva se retiran (la raíz se fuerza exportando `DOCS_ROOT`).
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
