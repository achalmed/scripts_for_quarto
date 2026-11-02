---
tipo: estado
estado: activo
actualizado: 2026-11-02
---
# estado.md — quarto-studio (repo `scripts_for_quarto`)

Lo primero que se lee y lo último que se escribe en cada sesión (regla 10 de la guía raíz). Lo decidido vive en
`docs/decisiones.md`; lo pendiente, aquí, en §Por hacer, con fecha y dueño.

**Repositorio público y blogs que despliegan solos.** Netlify publica cada `pub_*` y el hub `web` con cada
`git push`: ninguna prueba empuja ni confirma en ellos; las pruebas usan repos de fixture en un directorio temporal
en disco con un remoto «bare» local.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-11-02 | **Quarto Studio en QML + Kirigami sobre `gui-comun` 2.5** (fase 5 de la modernización de la familia; rama `wip/2026-11-02-qml`, sin fusionar): `docs/rediseno.md` (auditoría, ocho preguntas, arquitectura de información, decisiones Q1–Q11, lo construido con capturas), `studio/` reescrito (cuatro vistas: los sitios con su estado por la regla de la puerta R6 y filtros, las entradas con su fila del Excel, el índice del vault, los índices de contenido; un sitio y una operación actuales; F5 simula con la CLI o el plan de la ventana y Ctrl+Intro aplica tras confirmar; publicar y commit+push nombran el sitio y su dominio; problemas del render con su archivo; plan y registro por operación y por sitio; la entrada nueva en un diálogo; `/usr/bin/python3` relanzado al `.venv` del repo con openpyxl y pandas), `studio/muestra.py` (la familia de muestra con git y remotos bare) y `studio/capturar.py`, 28 pruebas en `tests/run.sh` (ninguna publica; el render real en `/var/tmp`), tres capturas reales sin rutas de la máquina, documentos al día. En `gui-comun`, 2.5.0 (`Tareas.proceso(entrada=, entorno=)`; la consola limpia ANSI; rama `wip/2026-11-02-qml-quarto`, etiqueta local). `project_scanner` deja de contar en el hub las entradas de sus pubs | `tests/run.sh`; `docs/figuras/quarto-studio-*.png`; `/usr/bin/python3 studio/main.py` |
| 2026-10-31 | **El repo pasa a llamarse `quarto-studio`** (antes `scripts-quarto`; remoto `scripts_for_quarto` intacto) con `core/renombrar.py`, y **Quarto Studio se renueva** con el diseño común de `gui_comun` (acento azul): barra lateral plegable, paleta Ctrl+K, avisos, consola oculta, portada «Inicio» con cifras y mosaicos, botones sin emojis; las hojas `.qss`, retiradas | `UNDO.sh` en `$RESPALDOS_DIR/renombres/2026-10-31-scripts-quarto-a-quarto-studio/`; `studio/README.md` §Uso |
| 2026-10-27 | **Quarto Studio vuelve** (sesión 9 de la cola de la auditoría posterior): la GUI en `studio/` con su historia, sus backends por ruta del repo, `gui_comun` desde `core`; `gui-suites` retirado | `docs/decisiones.md`; `tests/test_studio*.py` (5); `meta/programa/08-mantenimiento/studios-independientes-2026-10-27.md` |
| 2026-10-10 | **Los blogs por el registro** (ola 6, 6f): `metadata_manager` (`resolve_blog_dir`, `discover_blog_dirs`, `blog_label`, `path_sync.blog_dir_from_ruta`, `create_default_config`), `blogs_manager` (`utils_list_projects`, `utils_resolve_project_path`) y `pub_index_symlink` (`scanner_find_all_publications`) leen `core` (`pubs.py` / `pubs.sh`), no el prefijo `pub_`; `QBLOG_FUENTES` sin `THEME_VERSION` (igual que la puerta R6) | `tests/` (29); `main.sh list` = 12 |
| 2026-10-06 | ola 4, fase A (agente «quarto»): Q1 y Q2, un commit por ítem | la bitácora de abajo; `meta/programa/06-olas/ola-04-reingenieria.md` §2 |
| 2026-10-06 | ola 4, fase B (agente «studios»): la GUI sale al repo `gui-suites`; este repo queda como el de los backends de Quarto | la bitácora de abajo; `docs/decisiones.md` |

Bitácora de la ola 4:

- 2026-10-06 · Q1a · etiqueta `antes-ola-04-2026-10-06`; `estado.md`; los pendientes de `docs/decisiones.md` pasan a §Por hacer.
- 2026-10-06 · Q2 · `blogs_manager` 4.0.0: `publish` y `git-commit` simulan salvo `--aplicar`; todo push pasa la puerta R6 del hub; `git-commit` solo añade fuentes y `_site/` y lista lo demás; sin destino, `publish` es `git push` (Netlify); la GUI simula, pregunta y aplica (`tests/test_blogs_manager_git.py`, `tests/test_gui_blog_service.py`, remoto bare local).
- 2026-10-06 · Q1b · `tests/test_simulacion.py`: las cinco suites CLI en simulación sobre un workspace de fixture no escriben nada (listado + mtime del temporal y del repo); la GUI, omitida con motivo. Arreglos que destapó: `pub_index_symlink --dry-run` escribía su log en el repo; `metadata_manager` creaba `excel_output_dir` (literal `~/Documents/…`, ahora relativo a su carpeta) aun simulando; `blogs_manager --dry-run` sin comando abría el menú. `pruebas:` en los seis `suite.yml`.
- 2026-10-06 · B · etiqueta `antes-ola-04-studios-2026-10-06`; `app/` se copia con su historia (`git subtree split`) a `gui-suites/quarto/quarto_app/` y `main.py`, `build_resources.sh` y el `suite.yml` raíz (`quarto_studio`) a la carpeta quarto/ de gui-suites; con las pruebas de `gui-suites` en verde salen de aquí con `git rm`, junto con `tests/test_gui_blog_service.py` (hoy `gui-suites/tests/test_quarto_blog_service.py`). `requirements.txt` sin PySide6.
- 2026-10-06 · Q2 (ajuste del director) · `git-commit` añade también las carpetas de contenido (las que contienen `.qmd`, con imágenes y datos) y `_freeze/`; fuera quedan, con aviso, los sueltos de la raíz y los punteros de submódulo (`tests/test_blogs_manager_git.py`).

## En curso

nada en curso

## Por hacer

- 2026-11-02 · dueño: **el autor** · usar Quarto Studio en la sesión real sobre `web` (`/usr/bin/python3 ~/Documents/quarto-studio/studio/main.py`:
  Sitios con sus filtros y el Resumen de un pub; «Renderizar» (F5 el plan, Ctrl+Intro el render) y leer Problemas; «Publicar» (F5 la
  simulación de la puerta R6, Ctrl+Intro con el sitio y su dominio); Entradas con la pestaña Metadatos y «Ver diferencias»; el
  índice del vault; la paleta; claro y oscuro); lo que no convenza se anota aquí y se corrige en `main` o vuelve a `gui-comun`.
  El director fusiona `wip/2026-11-02-qml` y `gui-comun` `wip/2026-11-02-qml-quarto` (`v2.5.0`) cuando el autor apruebe.
- 2026-11-02 · dueño: director · lo que quedó fuera de la ventana: `sync-article` y `sync-batch` (interactivos; su flujo es
  Ver diferencias → Aplicar el Excel con el sitio y el filtro de ruta), `convert`, `git-init`, `preview-browser` y
  `add-columns` (no estaban en 1.x; se corren en la terminal); los problemas del render se leen de la salida de Quarto
  (ERROR, WARN, `archivo:línea`), no de un registro propio; el Excel se lee entero en cada relectura (unas 600 filas, sin
  caché); las operaciones de metadatos no muestran el plan de la ventana (la CLI simula con `--dry-run`); «Configurar
  atajos…» y «Configurar barras…» no existen (como en toda la familia).
- 2026-11-02 · dueño: director · el validador avisa en `docs/rediseno.md` (RQ-DOC-06: rutas de ejemplo como index.html de _site) y
  el `CLAUDE.md` sigue cerca de las 150 líneas; RQ-COD-01 de los tres `main.sh` de Bash es el pendiente del 2026-10-06.

- 2026-10-27 · dueño: la sesión del hub · `tests/test_blogs_manager_git.py::test_fuentes_iguales_a_las_de_la_puerta` falla: la puerta R6 del hub ya excluye `_vitrina/` y `_ediciones/` y `QBLOG_FUENTES` (`backend/script_blogs_manager/lib/00-config.sh`) no; no viene de la sesión 9.
- 2026-10-06 · dueño: director · `core/suites.py probar --repo quarto-studio`: RQ-MAN-05 en `pub_index_symlink` y en `quarto_studio` (escriben en `vault`, pero el manifiesto no declara ese `escribe_en` para el proyecto); se corrige en `meta/workspace.yml`.
- 2026-10-04 · dueño: el autor · dos comentarios de código dan como ejemplo de raíz forzada una ruta de la máquina: `backend/script_blogs_manager/lib/00-config.sh` y `backend/script_pub_index_symlink/lib/00-config.sh`.
- 2026-10-04 · dueño: el autor · `backend/script_metadata_manager/metadata_config.yml` (`excluded_folders`) publica en este repositorio público nombres de carpetas personales. ¿Se mueven a un archivo local ignorado?
- 2026-10-04 · dueño: el autor · orden de etiquetas de cabecera (aviso A10) en `backend/script_metadata_manager/lib/excel_writer.py` y `backend/script_metadata_manager/lib/path_sync.py`.
- 2026-10-06 · dueño: el autor · los `main.sh` de `blogs_manager`, `pub_index_symlink` y `generador_publicacion_similar` arrancan sin `set -e` (RQ-COD-01): el menú y las funciones devuelven ≠ 0 a propósito; se revisa función a función antes de activarlo.

## Futuro

- Las pruebas de la ventana están en `tests/studio/` (`tests/run.sh`, desde el 2026-11-02).
