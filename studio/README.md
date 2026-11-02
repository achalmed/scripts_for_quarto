---
tipo: readme
estado: activo
---
# studio/ — Quarto Studio, la ventana (QML + Kirigami sobre gui-comun 2.x) de los backends de la familia de blogs
<!-- suite:inicio -->
**Suite `quarto_studio`** · objetivo *publicacion* · estado *activo* · python · interfaz gui

Ventana de la familia de blogs Quarto (QML + Kirigami sobre gui-comun 2.x): el hub y los doce sitios con su estado por la regla de la puerta R6, las entradas con su frontmatter y su fila del Excel, el índice del vault y los índices de contenido; cada operación es la CLI de un backend: F5 simula (o muestra el plan), Ctrl+Intro aplica tras confirmar y publicar nombra el sitio y su dominio.

- Escribe en: web, vault · simula por defecto: sí
- Depende de: /usr/bin/python3 con PySide6 del sistema (python3-pyside6.*) y Kirigami (qml6-module-org-kde-kirigami), gui-comun 2.5 (módulo QML GuiComun), .venv del repo con openpyxl, pandas y pyyaml para los backends de metadatos (requirements.txt; opcional), blogs_manager, metadata_manager, pub_index_symlink, format_yaml, generador_publicacion_similar
- Nota: No renderiza ni publica por su cuenta: corre la CLI de cada backend; publicar y commit+push simulan primero y se aplican tras confirmar con el sitio y su dominio (Netlify despliega con el push).

Comandos:

```bash
main.py
main.py --smoke
../install.sh
```

<sub>Bloque generado desde `suite.yml` por `core/suites.py generar` (2026-11-02); no se edita a mano.</sub>
<!-- suite:fin -->

## Qué es

La ventana de los cinco backends de `../backend/` con el espacio de trabajo de la familia de studios (`gui-comun` 2.x; el
diseño, en [../docs/rediseno.md](../docs/rediseno.md)): menú, barra corta, navegación, centro, detalles, panel inferior,
barra de estado y paleta de órdenes (Ctrl+Alt+I · Ctrl+K). Cuatro vistas (Ctrl+1 … Ctrl+4), un **sitio actual** y una
**operación actual** por vista, elegida en la lista de la barra, en el menú Sitio o Flujo, en el menú contextual o en la
paleta: **Simular (F5)** corre la simulación de la CLI (`publish`, `git-commit`, `--dry-run`) o muestra el **plan** que
la ventana calcula sin correr nada (render, limpiar, respaldar, crear sitio); **Aplicar (Ctrl+Intro)** corre de verdad
tras un diálogo con la orden exacta y lo que toca; publicar y commit+push nombran el sitio y su dominio.

| vista | centro | operaciones | detalles |
|---|---|---|---|
| **Sitios** (filtros Todos · Al día · Cambios sin render · Render sin publicar · Con problemas; en Flujo, Render y Publicar llevan al filtro con la operación elegida) | el hub y los doce sitios del registro de pubs del hub con su estado por la regla de la puerta R6 (fecha del último commit de fuentes frente a la del último index.html de _site confirmado, fuentes sin confirmar, commits sin empujar), entradas, rama, tema, dominio | Renderizar · Publicar · Commit y push · Preview · Limpiar · Verificar · Inspeccionar · Git status · Listar entradas · Renderizar la entrada · Renderizar todos · Limpiar todos · Verificar estructura · Respaldar todos · Crear sitio… · Nueva entrada… (Ctrl+N, el formulario del asistente APAQuarto) | Resumen (estado y por qué, git, fechas) · Entradas · Problemas (los errores y avisos del último render con su archivo; Intro abre) · Registro (la última corrida sobre el sitio) · Operación · Plan |
| **Entradas y metadatos** | todas las entradas con fecha, título, sitio, tags y si están en el Excel | las del gestor de metadatos (plantilla, diferencias, aplicar el Excel, tags, fechas, pdf-url) y el formateador YAML; el sitio actual filtra (`--blog`) | Metadatos (la fila del Excel frente al frontmatter, campo a campo) · Operación · Plan |
| **Índice del vault** | los enlaces de `web/_indice/<año>/` y si están rotos | sincronizar, detectar rotos, eliminar rotos, resumen | Elemento · Operación · Plan |
| **Índices de contenido** | los `_contenido_*.qmd` de cada sitio | generar los del sitio actual | Resumen del sitio · Elemento (el fragmento) · Operación · Plan |

**La ventana no renderiza ni publica por su cuenta**: cada operación es la CLI de su backend (las órdenes de
`quarto_app/services/*_service.py`, las mismas de la terminal); la salida corre en el panel inferior (F4), Esc cancela
(también el preview), y el plan y el registro de cada operación y de cada sitio quedan en la caché del studio. El tema
compartido por hardlinks no se toca.

## El entorno del studio

La ventana corre con el Python del sistema (`/usr/bin/python3`), cuyo Qt es el que trae Kirigami. Los backends de
metadatos necesitan `openpyxl` y `pandas`, que el sistema no trae: viven en `.venv/` del repo, creado sobre el Python
del sistema para que vea su PySide6 (rediseño Q7), y `main.py` se relanza con él si existe:

```bash
/usr/bin/python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r requirements.txt   # sin sudo ni apt
```

Sin el `.venv`, la ventana avisa qué crear (también Herramientas › El entorno del studio…), la columna «Excel» y la
pestaña Metadatos quedan vacías y las operaciones de metadatos fallan con el mensaje del backend. PySide6 no se
instala en el `.venv`: el de pip no carga Kirigami.

## Estructura

| archivo | qué es |
|---|---|
| `main.py` | el punto de entrada, sin lógica (`/usr/bin/python3`; se relanza con `.venv/bin/python` si existe) |
| `quarto_app/aplicacion.py` | arma la aplicación: controladores, el registro de acciones (menú, barra, menú contextual, paleta, atajos: cada operación una sola vez) y `quarto_app/qml/Main.qml` |
| `quarto_app/controladores/` | lo que QML ve: `espacio` (vista, filtro, barra de estado, rutas), `sitios` (la tabla con su estado, el sitio y la entrada actuales, la entrada nueva), `flujo` (entradas con el Excel, índice, fragmentos), `operaciones` (la actual, Simular y Aplicar por `gui_comun.tareas`, plan y registro), `ajustes` |
| `quarto_app/services/` | sin Qt: los `Command` de cada backend (`blog_service`, `metadata_service`, `yaml_service`, `index_service`, `similar_service`, intactos), `operaciones` (el catálogo: simular, aplicar, plan, qué pide), `sitios` (el estado por la regla de la puerta R6), `render` (progreso y problemas de `quarto render`), `datos` (entradas, Excel, índice, fragmentos), `project_scanner`, `post_service`, `paths` |
| `quarto_app/models/` | `blog.py`, `operation.py`, `filas.py` (las filas de las tablas, sin Qt) |
| `quarto_app/qml/` | `Main.qml` sobre `GuiComun.VentanaStudio` y los componentes propios (`componentes/`) |
| `quarto_app/settings.py` | las preferencias de 1.x (`QSettings`), que se conservan |
| `quarto_app/recursos/marca.svg` | el icono del lanzador: la única marca del studio |
| `muestra.py` | la familia de sitios de muestra (un hub y tres pubs con git y remotos bare, cada uno en un estado; `_indice/`; un fragmento; un Excel) de las pruebas y las capturas; nunca `web` ni los pubs |
| `capturar.py` | las capturas de la documentación sobre la muestra, con `HOME` temporal fuera de la carpeta de inicio |

## Uso

```bash
/usr/bin/python3 studio/main.py                      # desde quarto-studio/, en la sesión real (se relanza con .venv si existe)
QT_QPA_PLATFORM=offscreen /usr/bin/python3 studio/main.py --smoke     # construye la interfaz y sale
./install.sh                                         # acceso directo en el menú (con -n, simula)
/usr/bin/python3 studio/capturar.py docs/figuras/quarto-studio-oscuro.png --esquema <LliphiOscuro.colors> --vista sitios --fila 1 --pestana 7
tests/run.sh                                         # desde quarto-studio/: la muestra en un temporal, cada QML y --smoke; nada publica
```

## Límite honesto

- **El estado se lee de git y del disco cada vez** (F6 relee): lo que se renderice o publique desde la terminal se refleja igual.
- **Los problemas del render salen de la salida de Quarto** (ERROR, WARN, `archivo:línea`): un error que Quarto no anuncie así no aparece.
- **Render y limpiar no simulan en la CLI**: F5 muestra el plan de la ventana (qué sitios, en qué orden, por qué; qué borraría) y Ctrl+Intro corre la CLI.
- **Las operaciones de metadatos corren sobre todos los sitios salvo que haya un sitio actual** (`--blog`); el filtro de ruta vive en la pestaña Operación.
- **El Excel se lee con `openpyxl`** (del `.venv`): sin él, la columna «Excel» y la pestaña Metadatos quedan vacías.
- **Una operación a la vez**, sin cola; el preview se detiene con Esc.
- **`sync-article` y `sync-batch`** (interactivos) no se ofrecen: su flujo es Ver diferencias → Aplicar el Excel con el sitio y el filtro de ruta.
