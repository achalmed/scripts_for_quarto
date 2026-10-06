---
tipo: readme
estado: activo
---
# backend/script_format_yaml/ — formateador idempotente del bloque YAML de los .qmd (v2.0)

<!-- suite:inicio -->
**Suite `format_yaml`** · objetivo *publicacion* · estado *activo* · python · interfaz cli

Repara el bloque YAML de los .qmd (delimitador --- pegado y líneas en blanco sobrantes) en una carpeta, de forma recursiva e idempotente.

- Escribe en: web · simula por defecto: no
- Nota: fix_qmd_files.py queda como alias de main.py (FS3)

Comandos:

```bash
main.py --directory <carpeta> --recursive --dry-run
main.py --directory <carpeta> --recursive
main.py --file archivo.qmd
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-09-20); no se edita a mano.</sub>
<!-- suite:fin -->

## Qué es

Repara los bordes del bloque YAML de los `.qmd`: separa el `---` de cierre pegado a la última clave
(`draft: false---`) y deja exactamente una línea en blanco entre el cierre y el contenido. Es
idempotente: una segunda pasada no cambia nada. No toca claves ni valores; eso es
[`script_metadata_manager`](../script_metadata_manager/). Quarto Studio lo invoca desde la página
«YAML» (a través del alias `fix_qmd_files.py`).

Resultado en un archivo con el cierre pegado:

```text
antes                      después
---                        ---
title: Mi título           title: Mi título
draft: false---            draft: false
## Contenido               ---

                           ## Contenido
```

## Uso

```bash
python3 backend/script_format_yaml/main.py --directory "../04 index/_pubs/pub_axiomata" --recursive --dry-run   # desde la raíz del repo: qué cambiaría
python3 backend/script_format_yaml/main.py --directory "../04 index/_pubs/pub_axiomata" --recursive             # aplica
python3 backend/script_format_yaml/main.py --file ruta/al/index.qmd                                             # un archivo
grep -rl --include='*.qmd' -e 'false---' "../04 index/_pubs/pub_axiomata"                                       # localizar cierres pegados
```

| opción | qué hace |
|---|---|
| `-d, --directory DIR` | carpeta con `.qmd` (por defecto, la actual) |
| `--recursive` | incluye subcarpetas |
| `-f, --file ARCHIVO` | repara un solo archivo |
| `--dry-run` | informa sin escribir |
| `-v, --verbose` | informa también de los archivos ya correctos |

Termina con 1 si algún archivo no tenía bloque YAML legible. Antes de aplicarlo a un pub, ese pub debe
estar sin cambios pendientes en git, para revisar el resultado con `git diff` dentro de él.

## Estructura

| carpeta | qué es | dueño |
|---|---|---|
| `main.py` | argumentos y recorrido | a mano |
| `config.py` | extensión, recursividad por defecto, líneas en blanco tras el cierre | a mano |
| `lib/formato.py` | la reparación | a mano |
| `fix_qmd_files.py` | alias de `main.py`; lo usa la GUI (`gui-suites/quarto/quarto_app/services/paths.py`) | a mano |
| `suite.yml` | manifiesto de la suite | a mano; el bloque de arriba lo genera `core/suites.py` |

## Límite honesto

- **Solo toca los bordes del bloque YAML**: no valida, reordena ni renombra claves, ni cambia comillas o valores.
- **La separación del `---` pegado se aplica a todo el archivo**: cualquier línea que termine en `---` tras otro carácter se parte, también en el cuerpo.
- **No repara un frontmatter roto** (sin cierre o con YAML inválido): lo informa y lo deja como está.
- **Sin respaldo propio y sin confirmación**: sin `--dry-run` escribe directamente; el respaldo es git.
