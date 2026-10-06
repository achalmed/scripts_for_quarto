---
tipo: readme
estado: activo
---
# backend/script_blogs_manager/ — gestor de publicaciones Quarto: render, preview, publicar, posts APA, git y respaldos del hub y los pubs (v4.0)

<!-- suite:inicio -->
**Suite `blogs_manager`** · objetivo *publicacion* · estado *activo* · bash · interfaz cli

Gestiona el hub 04 index y sus pubs: listar, render, preview, publicar, crear posts APA, operaciones git y backups.

- Escribe en: web, git, archivos · simula por defecto: no
- Entrada: 04 index y 04 index/_pubs/pub_*
- Depende de: quarto, git

Comandos:

```bash
main.sh                      # menú
main.sh list
main.sh render <blog>
main.sh publish <blog> [--aplicar]
main.sh git-commit <blog> <mensaje> [--aplicar]
main.sh help
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-10-06); no se edita a mano.</sub>
<!-- suite:fin -->

## Qué es

El gestor de la familia de blogs desde la terminal: lista los sitios, los renderiza, los previsualiza,
los limpia y los publica, crea posts APA con un asistente, opera git sobre cada blog, crea blogs nuevos,
revisa su estructura y hace respaldos. Ve el hub `04 index` y los `pub_*` de `04 index/_pubs/`. No
gestiona metadatos ni índices: para eso están [`script_metadata_manager`](../script_metadata_manager/)
y [`script_pub_index_symlink`](../script_pub_index_symlink/). Quarto Studio lo invoca desde la página
«Blogs».

## Uso

```bash
cd backend/script_blogs_manager           # desde la raíz del repo
./main.sh                                 # menú interactivo (también: ./main.sh -i)
./main.sh list                            # los sitios que ve el gestor, con sus posts y estado git
./main.sh render axiomata                 # nombre corto, o el de la carpeta: pub_axiomata
./main.sh preview axiomata 4200           # servidor local; el puerto es opcional
./main.sh help                            # la ayuda completa
```

Un blog se nombra por su carpeta (`pub_axiomata`) o sin el prefijo (`axiomata`); el hub, como
`website-achalma` (alias de `04 index`). Requiere Bash ≥ 4 y Quarto; git para los comandos `git-*`;
`yq`, opcional, para validar `_quarto.yml` en `check-structure`.

| comando | qué hace |
|---|---|
| `list` | lista los sitios gestionables |
| `render BLOG` · `render-all` | renderiza un sitio · todos, uno tras otro |
| `preview BLOG [PUERTO]` · `preview-browser BLOG [PUERTO]` | previsualización local (puerto por defecto 4200), con o sin abrir el navegador |
| `clean BLOG` | borra `_site/`, `_freeze/` y la caché .quarto de ese sitio |
| `clean-all` | lo mismo en todos los sitios, tras pedir confirmación |
| `publish BLOG [DESTINO] [--aplicar]` | sin destino, la puerta R6 y `git push` de la rama a su remota (Netlify despliega con cada push); con destino, `quarto publish` hacia `gh-pages` (también tras la puerta), `netlify`, `quarto-pub` o `confluence`. Simula salvo `--aplicar` |
| `check BLOG` · `inspect BLOG` | `quarto check` · tipo, motor, formatos y salida del sitio |
| `list-posts BLOG` | posts agrupados por carpeta temática |
| `render-post RUTA` | renderiza un solo `index.qmd` |
| `new-post BLOG` | asistente interactivo de post APA |
| `git-init BLOG` · `git-status BLOG` | inicia un repositorio (y su `.gitignore`) · muestra su estado |
| `git-commit BLOG [MENSAJE] [--aplicar]` | confirma lo rastreable (respetando `.gitignore`) de las fuentes del sitio (los pathspecs `FUENTES` de `04 index/scripts/puerta-r6.sh`), de las carpetas de contenido (las de primer nivel que contienen algún `.qmd`, con sus imágenes y datos), `_freeze/` y `_site/`; avisa de lo que queda fuera, corre la puerta R6 y empuja. Simula salvo `--aplicar` |
| `convert ARCHIVO [FORMATO]` | `quarto convert` (por defecto, html) |
| `init-blog NOMBRE [TÍTULO]` | crea un blog `pub_<nombre>` con su estructura |
| `check-structure` | revisa archivos, git y YAML de todos los sitios |
| `backup` | respaldo interactivo (de un sitio, completo o incremental) en `06 archives/backups-publicaciones/` |
| `version` | versión de Quarto instalada |

Los sitios de la familia (el hub y los `pub_*`) se despliegan en Netlify con cada `git push`: por eso
`publish` sin destino empuja con git, y `quarto publish` queda para un destino explícito. `publish` y
`git-commit` **simulan por defecto** (dicen qué añadirían, qué queda fuera y cuántos commits
empujarían) y solo actúan con `--aplicar`; el menú simula, pregunta y entonces aplica. Ningún push sale
sin pasar la **puerta R6** del hub (`$INDEX_DIR/scripts/puerta-r6.sh`, normativa 7.10): no se empuja un
sitio sin portada renderizada en `_site/` o con ella confirmada antes que su última fuente; si la puerta no está,
tampoco se empuja. Antes de `clean-all`, `list` y `git-status` muestran sobre qué se va a actuar.

El asistente `new-post` pregunta, en seis bloques, las opciones generales del documento, el formato
(`doc`, `jou`, `man`, `stu` y sus campos), los autores con ORCID y roles CRediT, la nota de autor, el
resumen y las palabras clave, y el idioma. Antes detecta las carpetas de posts del blog o crea una
nueva con su `_metadata.yml`. Escribe `index.qmd` y un `references.bib` vacío.

## Configuración

Todo lo editable está en `lib/00-config.sh`: proyectos excluidos de las operaciones masivas
(`QBLOG_EXCLUDED_PROJECTS`), puerto y destino de publicación por defecto (vacío: `git push`), las fuentes que confirma `git-commit` (`QBLOG_FUENTES`), autor e institución que
rellena el asistente, carpetas que nunca son carpetas de posts. Por entorno, sin tocar el código:

| variable | para qué |
|---|---|
| `DOCS_ROOT` | raíz del espacio de trabajo; por defecto la resuelve `core/env.sh` (sin alias propio desde la ola 0) |
| `QBLOG_WEBSITE_DIR` · `QBLOG_PUBS_SUBDIR` | carpeta del hub (por defecto `INDEX_DIR` de `core/env.sh`, relativa a la raíz) y de los pubs (`<hub>/_pubs`) |
| `QBLOG_BACKUP_DIR` | destino de `backup` |

## Estructura

| carpeta | qué es | dueño |
|---|---|---|
| `main.sh` | carga `lib/` en orden y despacha el comando | a mano |
| `lib/00-config.sh` | configuración, versión (`QBLOG_VERSION`), colores | a mano |
| `lib/01…12-*.sh` | salida, utilidades y resolución de blogs, listados, operaciones Quarto, operaciones masivas, git, asistente de posts, blogs nuevos, revisión de estructura, respaldos, menú y ayuda | a mano |
| `suite.yml` | manifiesto de la suite | a mano; el bloque de arriba lo genera `core/suites.py` |

Un comando nuevo: su función en el módulo temático de `lib/`, un `case` en `main()` de `main.sh` y su
línea en `lib/12-help.sh` y, si va en el menú, en `lib/11-interactive-menu.sh`.

## Límite honesto

- **Simula solo lo que publica.** `publish` y `git-commit` simulan salvo `--aplicar` (las pruebas: `tests/test_blogs_manager_git.py`, con un remoto bare local); `clean`, `clean-all`, `render` e `init-blog` escriben de verdad; `clean-all` pide confirmación.
- **No es seguro en paralelo.** Dos instancias sobre el mismo blog se pisan (`_site/`, `_freeze/`); la GUI lo serializa y en terminal hay que hacer lo mismo.
- **El asistente `new-post` es interactivo** y no se automatiza; la GUI lo replica con `gui-suites/quarto/quarto_app/services/post_service.py`, que genera el mismo `index.qmd`.
- **Solo ve el hub y los `pub_*` de `04 index/_pubs/`**: un blog fuera de ahí no existe para `list`, `render-all`, `check-structure` ni `backup`.
- **`git-commit` no confirma todo**: los archivos sueltos de la raíz que no son fuentes y los punteros de submódulo quedan fuera con un aviso; se confirman a mano. Los pubs son submódulos: después hay que confirmar el puntero en el hub.
