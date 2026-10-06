---
tipo: estado
estado: activo
actualizado: 2026-10-06
---
# estado.md — scripts_quarto_studio (repo `scripts_for_quarto`, suite `quarto_studio`)

Lo primero que se lee y lo último que se escribe en cada sesión (regla 10 de la guía raíz). Lo decidido vive en
`docs/decisiones.md`; lo pendiente, aquí, en §Por hacer, con fecha y dueño.

**Repositorio público y blogs que despliegan solos.** Netlify publica cada `pub_*` y el hub `04 index` con cada
`git push`: ninguna prueba empuja ni confirma en ellos; las pruebas usan repos de fixture en un directorio temporal
en disco con un remoto «bare» local.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-10-06 | ola 4, fase A (agente «quarto»): Q1 y Q2, un commit por ítem | la bitácora de abajo; `meta/programa/06-olas/ola-04-reingenieria.md` §2 |

Bitácora de la ola 4:

- 2026-10-06 · Q1a · etiqueta `antes-ola-04-2026-10-06`; `estado.md`; los pendientes de `docs/decisiones.md` pasan a §Por hacer.
- 2026-10-06 · Q2 · `blogs_manager` 4.0.0: `publish` y `git-commit` simulan salvo `--aplicar`; todo push pasa la puerta R6 del hub; `git-commit` solo añade fuentes y `_site/` y lista lo demás; sin destino, `publish` es `git push` (Netlify); la GUI simula, pregunta y aplica (`tests/test_blogs_manager_git.py`, `tests/test_gui_blog_service.py`, remoto bare local).
- 2026-10-06 · Q1b · `tests/test_simulacion.py`: las cinco suites CLI en simulación sobre un workspace de fixture no escriben nada (listado + mtime del temporal y del repo); la GUI, omitida con motivo. Arreglos que destapó: `pub_index_symlink --dry-run` escribía su log en el repo; `metadata_manager` creaba `excel_output_dir` (literal `~/Documents/…`, ahora relativo a su carpeta) aun simulando; `blogs_manager --dry-run` sin comando abría el menú. `pruebas:` en los seis `suite.yml`.

## En curso

nada en curso

## Por hacer

- 2026-10-06 · dueño: director · `core/suites.py probar --repo scripts_quarto_studio`: RQ-MAN-05 en `pub_index_symlink` y `quarto_studio` (escriben en `vault`, pero el manifiesto no declara ese `escribe_en` para el proyecto); se corrige en `meta/workspace.yml`.
- 2026-10-04 · dueño: el autor · dos comentarios de código dan como ejemplo de raíz forzada una ruta de la máquina: `backend/script_blogs_manager/lib/00-config.sh` y `backend/script_pub_index_symlink/lib/00-config.sh`.
- 2026-10-04 · dueño: el autor · `backend/script_metadata_manager/metadata_config.yml` (`excluded_folders`) publica en este repositorio público nombres de carpetas personales. ¿Se mueven a un archivo local ignorado?
- 2026-10-04 · dueño: el autor · orden de etiquetas de cabecera (aviso A10) en `backend/script_metadata_manager/lib/excel_writer.py` y `backend/script_metadata_manager/lib/path_sync.py`.
- 2026-10-06 · dueño: el autor · los `main.sh` de `blogs_manager`, `pub_index_symlink` y `generador_publicacion_similar` arrancan sin `set -e` (RQ-COD-01): el menú y las funciones devuelven ≠ 0 a propósito; se revisa función a función antes de activarlo.

## Futuro

- Una prueba de humo de la GUI (`QT_QPA_PLATFORM=offscreen`) que construya cada `Command` sin lanzarlo.
