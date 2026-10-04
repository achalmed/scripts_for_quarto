---
tipo: readme
estado: activo
---
# backend/script_pub_index_symlink/ — enlaces simbólicos por año en 04 index/_indice a cada publicación de los blogs (pub-index-sync)

<!-- suite:inicio -->
**Suite `pub_index_symlink`** · objetivo *publicacion* · estado *activo* · bash · interfaz cli

Mantiene 04 index/_indice con enlaces simbólicos por año a cada carpeta de publicación de los blogs.

- Escribe en: vault · simula por defecto: no
- Depende de: bash

Comandos:

```bash
main.sh
main.sh --dry-run
main.sh --check-broken
main.sh --clean-broken
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-09-20); no se edita a mano.</sub>
<!-- suite:fin -->

## Qué es

Mantiene `04 index/_indice/<año>/` con un enlace simbólico a cada carpeta de publicación de la
familia de blogs, para encontrar cualquier publicación por año sin recorrer blog por blog. Es del vault:
`04 index/_indice/` está ignorado en el hub y no se publica. Quarto Studio lo invoca desde la página
«Índices».

Qué hace en cada corrida:

1. Recorre los `pub_*` de `04 index/_pubs/` a cualquier profundidad, y `blog/posts` y `talk` del hub,
   buscando carpetas cuyo **nombre** empieza por `AAAA-MM-DD-`.
2. Ignora las carpetas técnicas (`_freeze`, `_site`, `_partials`, `_extensions`, `.quarto`, `.git`,
   `site_libs`, `node_modules`, `_indice`, `_vault`); las subcarpetas de una publicación viajan con ella.
3. Crea `04 index/_indice/<año>/<carpeta>` apuntando a la carpeta real; si ya apunta bien, la omite; si
   la publicación cambió de sitio, actualiza el enlace.
4. Informa de los enlaces rotos (la carpeta original se borró o se movió) y, si se pide, los elimina.
5. No toca archivos ni carpetas reales: si en el lugar del enlace hay uno, lo informa como conflicto.

## Uso

```bash
backend/script_pub_index_symlink/main.sh --dry-run        # desde la raíz del repo: qué crearía o actualizaría
backend/script_pub_index_symlink/main.sh                  # sincroniza y muestra el resumen por año
backend/script_pub_index_symlink/main.sh --check-broken   # solo lista los enlaces rotos
```

| opción | qué hace |
|---|---|
| (ninguna) | sincroniza, informa de rotos sin borrarlos y muestra el resumen por año |
| `--dry-run` | anuncia lo que haría, sin escribir |
| `--check-broken` | lista los enlaces rotos de `04 index/_indice/` |
| `--clean-broken` | lista los enlaces rotos de `04 index/_indice/`, pide confirmación (`s`/`N`) y los borra; después borra las carpetas de año vacías |
| `--summary` · `--no-summary` | solo el resumen por año · sincronizar sin resumen |
| `--help`, `-h` | ayuda |

Es idempotente: repetirlo solo añade lo nuevo. Para reindexar desde cero basta borrar el **contenido de
`04 index/_indice/`** (solo enlaces) y volver a ejecutarlo; nunca la carpeta `04 index`.

| variable | para qué |
|---|---|
| `PUBINDEX_DOCS_DIR` | raíz del espacio de trabajo si la autodetección falla (sube desde la carpeta del script hasta hallar `04 index`) |
| `PUBINDEX_PUBS_SUBDIR` | carpeta de los pubs (por defecto `04 index/_pubs`) |

Cada corrida añade su registro a `logs/<AAAA-MM-DD>.log` de esta carpeta (ignorado en git).

## Estructura

| carpeta | qué es | dueño |
|---|---|---|
| `main.sh` | argumentos y orquestación | a mano |
| `lib/00-config.sh` | destino, prefijos, carpetas ignoradas, patrón de fecha | a mano |
| `lib/01-logging.sh` · `02-utils.sh` | registro sobre `core/shell-lib`; año, raíz del espacio de trabajo | a mano |
| `lib/03-scanner.sh` · `04-symlinker.sh` | busca publicaciones (solo lectura); crea y actualiza enlaces | a mano |
| `lib/05-broken-detector.sh` · `06-maintenance.sh` | enlaces rotos; carpetas de año vacías y resumen | a mano |
| `suite.yml` | manifiesto de la suite | a mano; el bloque de arriba lo genera `core/suites.py` |

## Límite honesto

- **Solo crea enlaces simbólicos, nunca copia**: si la carpeta original se borra o se mueve, el enlace queda roto hasta `--clean-broken` o la siguiente corrida.
- **No toca archivos ni carpetas reales** dentro de `04 index/_indice/`: un conflicto se resuelve a mano.
- **El criterio es solo el nombre de la carpeta** (`AAAA-MM-DD-…`): no lee el frontmatter ni distingue borradores de publicados.
- **No simula por defecto**: `--dry-run` hay que pedirlo.
