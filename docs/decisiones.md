---
tipo: decision
titulo: 'Decisiones y pendientes de scripts_quarto_studio'
estado: activo
---
# Decisiones y pendientes de scripts_quarto_studio

Registro único y acumulativo de por qué el repositorio es como es. Cada entrada lleva su fecha; una
decisión revocada no se borra: se marca «Superada por …». Lo que se hizo en una sesión va al mensaje de
commit, no aquí. Las versiones de cada herramienta están en [`CHANGELOG.md`](../CHANGELOG.md).

## Arquitectura

- **2026-07-13 · La GUI lanza procesos; no importa el código de los backends.** Quarto Studio construye un
  `Command` y lo ejecuta con `QProcess` (`app/services/`, `app/workers/process_runner.py`). Así un backend
  puede cambiar de lenguaje sin tocar la GUI y la consola muestra el comando exacto. La capa de servicios
  vive en `app/services/` y no en un `core/` propio del repo, para no confundirse con el `core/` del
  espacio de trabajo.
- **2026-07-13 · Crecer solo cuando duela.** De la visión de producto inicial se adoptó la fundación
  (servicios por dominio, modelos sin Qt, consola integrada) y se dejaron como catálogo, a activar uno a
  uno y con un problema concreto que resolver: sistema de plugins con manifiesto, bus de eventos, caché
  SQLite derivada del sistema de archivos (nunca fuente de verdad), bus de comandos, vigilancia de
  archivos, integración con IA. Se descartaron MVVM (MVC basta para un mantenedor), la configuración
  repartida en varios archivos (las preferencias van a `QSettings` desde `app/settings.py`) y un log por
  subsistema.
- **2026-07-13 · Una sola lógica portada a Python: el asistente de posts.** `backend/script_blogs_manager/lib/07-post-creator.sh`
  encadena unas 50 preguntas de terminal que no se automatizan con fiabilidad; `app/services/post_service.py`
  genera el mismo `index.qmd` desde un diálogo. Ninguna otra lógica de backend se duplica en la GUI.
- **2026-07-13 · Una operación a la vez.** Los backends mutan los mismos árboles; el runner de la GUI
  rechaza ejecuciones concurrentes en lugar de ofrecer una cola.
- **2026-09-07 · Patrón `main` + `config` + `lib` en las cinco herramientas, raíz y logger desde `core/`.**
  Ninguna suite escribe la ruta de `~/Documents` ni define su logger; `format_yaml` conserva
  `fix_qmd_files.py` como alias de `main.py` porque la GUI lo invoca (`app/services/paths.py`).

## Metadatos y blogs

- **2026-09-20 · El frontmatter del `.qmd` es la verdad; el Excel es la mesa de trabajo.** `update` solo
  escribe donde la fila difiere del archivo y una celda vacía elimina el campo. El Excel
  `backend/script_metadata_manager/excel_databases/quarto_metadata.xlsx` se versiona a propósito: es el estado
  de la edición en masa (la `verdad` que declara `meta/workspace.yml` para este repo) y guarda las
  columnas auxiliares del autor.
- **2026-07-03 · Una herramienta, un parser YAML.** El antiguo gestor de tags y los scripts sueltos de
  fechas y `pdf-url` se absorbieron en `metadata_manager` (v2.1 y v2.2): un solo escritor
  (`qmd_updater.write_yaml_to_qmd`) y un solo reordenador (`field_mapper.reorder_yaml`), para que dos
  herramientas no normalicen el mismo YAML de formas distintas.
- **2026-07-03 · La URL base de un blog se vota.** No se deriva del nombre de carpeta (`pub_chaska`
  publica en `chaska-x.netlify.app`): `sync-pdf-urls` toma la mayoría entre los `pdf-url` existentes y
  `blog_base_urls` de `metadata_config.yml` tiene prioridad.
- **2026-07-03 · El generador de índices recibe el blog como argumento.** Antes había que editar el
  script para cada blog; desde la 4.0 el directorio es posicional y la URL base y el tipo son opciones.
  Escribe el índice en memoria y de una vez, lo que permitió `--dry-run`.
- **2026-09-06 · Los pubs se localizan por una sola variable.** Los `pub_*` son submódulos del hub en
  `04 index/_pubs/`; cada herramienta los busca por `QBLOG_PUBS_SUBDIR`, `PUBINDEX_PUBS_SUBDIR` o
  `PUBS_SUBDIR`, y acepta `website-achalma` como alias del hub.
- **2026-09-15 · `date` en ISO y sustitución de una sola línea.** `sync-dates` escribe `AAAA-MM-DD`;
  cuando solo cambia `date` se sustituye esa línea y el resto del archivo queda byte a byte igual. El
  Excel guarda la fecha como texto, no como fórmula: openpyxl no calcula fórmulas y una celda sin valor
  guardado borraría `date`.
- **2026-09-15 · Los índices `_contenido_<subblog>.qmd` llevan `tipo: fragmento`.** Son fragmentos para
  `{{< include >}}`, no páginas.

## Documentación

- **2026-10-04 · `docs/` existe para la referencia del Excel y estas decisiones.** La variante `suite`
  solo admite `docs/` cuando un README no basta: la referencia de columnas y fórmulas del Excel tiene su
  propio lector y está en [`excel-de-metadatos.md`](excel-de-metadatos.md); cada herramienta se documenta
  en su carpeta.
- **2026-10-04 · `CHANGELOG.md` se conserva aunque la versión no esté en un manifiesto.** Apartamiento
  del perfil del ecosistema (`meta/NORMATIVA_ARCHIVOS.md` §15.11): cada herramienta declara su versión
  en el código y el usuario la ve (H1 del README, `--version`, «Acerca de» de la GUI); el archivo
  registra solo versiones, no sesiones de trabajo.
- **2026-10-04 · Se retira la visión de producto.** Superada la decisión D15 de DOC8 (2026-09-20), que la
  había traído del vault a docs/vision.md: era la transcripción de una propuesta de asistente, no un
  documento del proyecto. Lo que sigue vigente quedó arriba («Crecer solo cuando duela»); el texto
  completo queda en el historial de git.

## Pendientes

| fecha | pendiente | dueño |
|---|---|---|
| 2026-10-04 | `backend/script_metadata_manager/suite.yml` declara `simula_por_defecto: true`, pero el CLI aplica salvo `--dry-run` (solo la GUI simula por defecto). Se corrige con la regeneración global de suites. | orquestador de la campaña documental |
| 2026-10-04 | Dos comentarios de código citan una ruta absoluta de la máquina: `backend/script_blogs_manager/lib/00-config.sh` y `backend/script_pub_index_symlink/lib/00-config.sh`. | autor |
| 2026-10-04 | `backend/script_metadata_manager/metadata_config.yml` (`excluded_folders`) publica en este repositorio público nombres de carpetas personales. ¿Se mueven a un archivo local ignorado? | autor |
| 2026-10-04 | `blogs_manager publish` usa por defecto el destino `gh-pages` (`QBLOG_DEFAULT_PUBLISH_TARGET`), pero los sitios de la familia se despliegan en Netlify. ¿Se cambia el valor por defecto? | autor |
| 2026-10-04 | Orden de etiquetas de cabecera (aviso A10) en `backend/script_metadata_manager/lib/excel_writer.py` y `backend/script_metadata_manager/lib/path_sync.py`. | autor |
