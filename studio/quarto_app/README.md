---
tipo: readme
estado: activo
---
# app/ — Quarto Studio, la aplicación de escritorio (PySide6 / Qt6) que unifica los backends

## Qué es

Una sola ventana para las cinco herramientas de `../backend/`. Los scripts **no se reescriben**: actúan
como motor y la GUI los invoca como procesos a través de una capa de servicios desacoplada; la consola
integrada muestra el comando exacto, stdout, stderr, código de salida y duración, nada se oculta. La
entrada es `../main.py`: crea la `QApplication`, aplica el tema persistido y muestra `MainWindow`; toda
la lógica vive aquí. Nombre y versión (`Quarto Studio`, `1.0.0`) se declaran una sola vez en `__init__.py`.

```
┌────────────────────────────────────────────────────────────┐
│  Menú · Toolbar                                            │
├──────────┬─────────────────────────────────┬───────────────┤
│ Sidebar  │  Páginas (QStackedWidget)       │  Explorador   │
│ Dashboard│  Dashboard / Blogs / Metadata   │  de proyectos │
│ Blogs    │  YAML / Índices / Contenido     │  (dock)       │
│ Metadata ├─────────────────────────────────┴───────────────┤
│ YAML     │  Consola integrada  |  Logs (historial)         │
│ Índices  ├─────────────────────────────────────────────────┤
│ Contenido│  Barra de estado · progreso · directorio        │
└──────────┴─────────────────────────────────────────────────┘
```

## Uso

```bash
pip install -r requirements.txt    # desde la raíz del repo: PySide6 y las dependencias del metadata manager
python3 main.py                    # desde la raíz del repo
./build_resources.sh               # opcional: compila resources.qrc a resources_rc.py (requiere pyside6-rcc)
```

La aplicación funciona sin compilar los recursos: si `resources_rc.py` no existe, carga iconos y temas
desde disco. Las preferencias (directorio de trabajo, tema) se guardan con `QSettings` y se editan en
el diálogo de preferencias.

## Estructura

| carpeta / archivo | qué es | dueño / generador |
|---|---|---|
| `application.py` | `QApplication`, tema claro/oscuro (QSS), icono de la app | a mano |
| `settings.py` | `QSettings` centralizado: la única puerta a las preferencias; ningún otro módulo instancia `QSettings` | a mano |
| `models/` | dominio puro (`blog.py`, `operation.py`): no importan nada de Qt | a mano |
| `services/` | construyen `Command` (programa + args + cwd + stdin) por herramienta: `command.py`; `paths.py` (localiza los backends y `~/Documents`); `blog_service.py` → `../backend/script_blogs_manager/main.sh`; `metadata_service.py` → `../backend/script_metadata_manager/main.py`; `yaml_service.py` → `../backend/script_format_yaml/fix_qmd_files.py` (alias de `main.py`); `index_service.py` → `../backend/script_pub_index_symlink/main.sh`; `similar_service.py` → `../backend/script_generador_publicacion_similar/main.sh`; `post_service.py` (posts APAQuarto, portado); `project_scanner.py` (escaneo de blogs y posts, Python puro) | a mano |
| `workers/` | `process_runner.py` (`QProcess` asíncrono con señales de salida y progreso; una operación a la vez), `scan_worker.py` (`QThread` para el escaneo) | a mano |
| `controllers/` | vista → servicio → worker (MVC): `main_controller.py`, `blogs_controller.py`, `metadata_controller.py`, `tools_controller.py` | a mano |
| `ui/` | `main_window.py` y `ui/pages/`: una página por funcionalidad (dashboard, blogs, metadata, yaml, índices, similares) | a mano |
| `widgets/` | consola, panel de logs, sidebar (`SECCIONES`), explorador de proyectos (dock), cabecera de página | a mano |
| `dialogs/` | preferencias, nuevo post, nuevo blog | a mano |
| `utils/` | limpieza de secuencias ANSI de la salida de los scripts | a mano |
| `resources/` | `resources.qrc`, `icons/` (SVG), `themes/` (`claro.qss`, `oscuro.qss`), `ui/` (`.ui`); `resources_rc.py` se genera y está ignorado | `../build_resources.sh` |

**Regla de dependencias:** `ui → controllers → services → workers`. La UI nunca conoce rutas de
scripts (las resuelve `services/paths.py`; si un script se mueve, se toca solo ese archivo); los
servicios nunca importan Qt Widgets; los modelos no importan nada de Qt.

## Decisiones de diseño

- **Reutilización primero.** Todos los subcomandos no interactivos de los scripts se invocan tal cual
  (`QProcess`). La consola muestra el comando exacto, stdout, stderr, código de salida y duración.
- **Una sola excepción portada a Python:** el asistente de posts APAQuarto
  (`../backend/script_blogs_manager/lib/07-post-creator.sh`, unas 50 preguntas encadenadas de terminal)
  no puede automatizarse de forma fiable; `services/post_service.py` genera el mismo `index.qmd` (mismo
  orden de campos y misma plantilla de contenido) desde el diálogo Qt.
- **Confirmaciones de los scripts** (`--clean-broken`, respaldo) se responden por stdin después de que
  la GUI ya confirmó con el usuario.
- **`sync-article` y `sync-batch`** (interactivos en terminal) se cubren con el flujo equivalente de la
  GUI: *Ver diferencias* → *Aplicar Excel → .qmd* con filtros de blog y ruta.
- **Simulación marcada por defecto** en las páginas de metadatos e índices («Dry-run»); las operaciones
  sobre todos los blogs piden confirmación. Los backends en terminal no simulan por defecto.
- **Una operación a la vez**: el runner rechaza ejecuciones concurrentes porque los scripts mutan los
  mismos árboles de archivos y no son seguros en paralelo. El preview (proceso largo) se detiene con el
  botón ■.

## Extender la aplicación

Para añadir una herramienta nueva: crear su `*_service.py` (funciones que devuelven `Command`), añadir
métodos al controlador correspondiente (o uno nuevo), crear la página en `ui/pages/` y registrarla en
`SECCIONES` de `widgets/sidebar.py` y en `ui/main_window.py`. Ni la consola, ni los logs, ni el progreso
necesitan cambios.

## Límite honesto

- **No hay pruebas de la GUI** ni de los servicios: se comprueba abriendo la aplicación y leyendo la
  consola integrada.
- **No reimplementa ningún backend**: si un script cambia su CLI, cambia el servicio que lo llama; la
  GUI no valida argumentos que el script no valide.
- **Los flujos interactivos de terminal** (asistente de posts, `sync-article`, `sync-batch`, menú de
  respaldos) no se lanzan desde aquí: se sustituyen por diálogos o por el flujo equivalente.
- **Una operación a la vez**, sin cola: mientras una corre, las demás esperan al usuario.
- **Requiere PySide6 ≥ 6.5 y un escritorio**: no hay modo sin ventana ni línea de comandos propia; para
  eso están los backends.
