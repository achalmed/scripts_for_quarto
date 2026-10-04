---
tipo: readme
estado: activo
---
# backend/script_generador_publicacion_similar/ — generador de índices de contenido (_contenido_<subblog>.qmd) de un blog Quarto (v4.0)

<!-- suite:inicio -->
**Suite `generador_publicacion_similar`** · objetivo *publicacion* · estado *activo* · bash · interfaz cli

Genera los índices de contenido (_contenido_<subblog>.qmd) de un blog con enlaces a artículo y PDF.

- Escribe en: web · simula por defecto: no
- Depende de: bash

Comandos:

```bash
main.sh <BLOG_DIR>
main.sh <BLOG_DIR> --dry-run
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-09-20); no se edita a mano.</sub>
<!-- suite:fin -->

## Qué es

Recorre los subblogs (subcarpetas) de un blog Quarto, toma las carpetas de publicación
`AAAA-MM-DD-título/` que tienen `index.qmd` y escribe en cada subblog un índice
`_contenido_<subblog>.qmd`: una lista numerada con el enlace al PDF y al artículo de cada publicación,
lista para `{{< include >}}`. Quarto Studio lo invoca desde la página «Contenido».

```markdown
1. [{{< fa regular file-pdf >}}](https://dominio/subblog/2022-01-23-titulo/index.pdf) [Titulo](https://dominio/subblog/2022-01-23-titulo)
```

El índice lleva frontmatter `tipo: fragmento` y se incluye desde la página del subblog:

```markdown
{{< include _contenido_posts.qmd >}}
```

## Uso

```bash
cd backend/script_generador_publicacion_similar
./main.sh "../../../04 index/_pubs/pub_axiomata" --base-url https://axiomata.netlify.app --dry-run   # qué escribiría
./main.sh "../../../04 index/_pubs/pub_axiomata" --base-url https://axiomata.netlify.app             # escribe
./main.sh "../../../04 index/blog"                                                                    # sección del hub, URL base por defecto
```

La ruta del blog va **entre comillas**: las carpetas del espacio de trabajo tienen espacios.

| opción | qué hace |
|---|---|
| `BLOG_DIR` | directorio del blog (posicional, obligatorio) |
| `-u, --base-url URL` | URL base del sitio; por defecto `GENIDX_DEFAULT_BASE_URL` (la del hub); la barra final se quita sola |
| `-t, --type auto\|website\|blog` | estructura; `auto` (por defecto) la detecta |
| `-n, --dry-run` | anuncia lo que escribiría o borraría, sin tocar nada |
| `-h, --help` · `--version` | ayuda · versión (`GENIDX_VERSION`) |

Dos estructuras: `blog`, un proyecto independiente con su `_quarto.yml` (URL
`base/<subblog>/<post>/`), y `website`, una sección del hub cuyo `_quarto.yml` está en la carpeta padre
(URL `base/<sección>/<subblog>/<post>/`). Códigos de salida: `0` éxito, `2` argumentos inválidos, `3`
directorio inexistente; un fallo al escribir un índice se informa en el registro.

## Estructura

| carpeta | qué es | dueño |
|---|---|---|
| `main.sh` | carga `lib/` y ejecuta el flujo | a mano |
| `lib/00-config.sh` | versión, URL base, prefijo de salida, carpetas ignoradas (`GENIDX_*`) | a mano |
| `lib/01-logging.sh` · `02-cli.sh` · `03-validator.sh` | registro sobre `core/shell-lib`; argumentos y ayuda; validación | a mano |
| `lib/04-detector.sh` · `05-linker.sh` · `06-generator.sh` | estructura por `_quarto.yml`; título y URL de cada post; recorrido y escritura | a mano |
| `suite.yml` | manifiesto de la suite | a mano; el bloque de arriba lo genera `core/suites.py` |

Una opción nueva se declara en `lib/02-cli.sh` y en su ayuda; un módulo nuevo es `lib/NN-nombre.sh` con
su guarda `GENIDX_<NOMBRE>_LOADED` y su `source` en `main.sh`, en orden.

## Límite honesto

- **Escribe un `_contenido_<subblog>.qmd` en la carpeta de cada subblog**: no toca los posts ni `_quarto.yml`, y la página que incluye el fragmento la escribe el autor.
- **Si un subblog se queda sin publicaciones válidas, borra su índice anterior**; `--dry-run` lo anuncia sin borrar.
- **Una publicación es una carpeta cuyo nombre empieza por `AAAA-MM-DD-`**; las carpetas que empiezan por `.` o `_` y las de `GENIDX_IGNORE_DIRS` no cuentan, y el orden es el del glob (cronológico por el prefijo).
- **La URL base no se deduce del blog**: se pasa con `--base-url` o se usa la del hub (`pub_chaska` publica en `chaska-x.netlify.app`).
- **Requiere `sed` GNU** para capitalizar los títulos; en macOS/BSD haría falta `gsed`.
