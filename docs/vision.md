---
tipo: plan
titulo: "Visión de producto — Quarto Studio (2026-07-13)"
estado: hecho
creado: 2026-07-13
---
El proyecto ya tiene una muy buena base. Lo que veo es que en realidad **no estás construyendo una aplicación**, sino el comienzo de un **IDE especializado para Quarto**. Ese cambio de perspectiva modifica completamente el diseño.

Yo lo llamaría algo como:

> **Quarto Studio**  
> *An integrated development environment (IDE) for Quarto publishing and academic writing.*

No lo pensaría como un "launcher de scripts", sino como una plataforma extensible.

---

# 1. Separar completamente el Backend del Frontend

> Visión de producto escrita en el vault el 2026-07-13 (`01 notes/proyecto-quarto-studio.md`, tipo idea) y trasladada a `docs/` del repo en
> DOC8 (2026-09-20, decisión D15): es el documento fundacional de lo que hoy es Quarto Studio. Lo construido y vigente está en
> `README.md` y `CLAUDE.md`; lo que aquí se prometió y no se hizo es historia, no pendiente.

Actualmente tienes:

```
app/
backend/
```

pero el frontend conoce demasiado del backend.

Yo haría algo así

```
scripts_quarto_studio/

├── app/
│
├── core/
│   ├── models/
│   ├── services/
│   ├── events/
│   ├── plugins/
│   ├── settings/
│   └── utils/
│
├── backend/
│
└── resources/
```

La idea es que **backend** sea únicamente una colección de herramientas.

El resto del programa nunca debería ejecutar directamente:

```
script_metadata_manager/main.py
```

sino algo como

```python
MetadataService.collect()
```

que internamente decide qué script llamar.

Así mañana puedes reemplazar un Bash por Python sin tocar la GUI.

---

# 2. Transformar backend en Plugins

Ahora tienes

```
backend/

script_metadata_manager
script_blogs_manager
script_pub_index_symlink
script_generador_publicacion_similar
script_format_yaml
```

Yo los convertiría en módulos independientes.

```
backend/

plugins/

metadata/

plugin.yaml

run.py

README.md

blogs/

plugin.yaml

run.py

README.md

yaml/

plugin.yaml
```

Cada plugin tendría un manifiesto.

Ejemplo

```yaml
name: Metadata Manager

version: 2.0

author: Edison Achalma

entry: run.py

description:
  Gestiona los metadatos de proyectos Quarto.

commands:

- collect

- update

- sync

icon: metadata.svg
```

Entonces la GUI carga automáticamente los plugins.

No necesita conocerlos.

---

# 3. Sistema de comandos

Actualmente tienes

```
command.py
```

Yo lo volvería un Command Bus.

```
RunCommand

CancelCommand

RefreshCommand

BuildCommand

RenderCommand

DeployCommand
```

Ejemplo

```python
CommandBus.execute(
    BuildWebsite(project)
)
```

Eso hace muchísimo más limpio todo el código.

---

# 4. Sistema de Eventos

Algo que le falta.

En una aplicación grande jamás haces

```
botón

↓

controller

↓

service

↓

actualiza GUI
```

En vez de eso

```
Service

↓

Event

↓

GUI escucha
```

Ejemplo

```
MetadataUpdatedEvent

BlogCreatedEvent

PostCreatedEvent

BuildFinishedEvent

IndexGeneratedEvent
```

Entonces cualquier parte de la GUI se actualiza sola.

---

# 5. Project Manager

Yo agregaría

```
core/project.py
```

Porque Quarto Studio debe entender proyectos.

No carpetas.

Ejemplo

```python
Project

nombre

ruta

tipo

estado

último build

último deploy

índice

posts

assets
```

La aplicación abre proyectos.

No directorios.

---

# 6. Dashboard mucho más potente

Actualmente imagino que solo muestra botones.

Yo mostraría

```
Proyecto activo

Quarto version

Git branch

Último build

Cantidad de posts

Cantidad de páginas

Cantidad de imágenes

Errores YAML

Errores Links

Metadata incompleta

Publicaciones pendientes
```

Como VS Code.

---

# 7. Consola integrada

Tienes

```
console_widget.py
```

Yo la convertiría en una consola profesional.

Con:

✓ colores ANSI

✓ filtros

✓ copiar

✓ guardar

✓ buscar

✓ progreso

✓ timestamps

Ejemplo

```
15:31:22

[INFO]

Metadata actualizada

15:31:23

[SUCCESS]

32 posts sincronizados

15:31:24

[WARNING]

3 imágenes sin usar
```

---

# 8. Task Manager

Actualmente hay

```
workers/
```

Yo haría algo parecido al de VS Code.

```
Tasks

Running

Queued

Finished

Failed

Cancelled
```

Con barra de progreso.

---

# 9. File Watcher

Esto sería enorme.

```
watchdog
```

Observa

```
*.qmd

*.yml

*.yaml

*.bib

*.css

*.scss
```

Cuando cambia uno

↓

actualiza automáticamente

↓

sin presionar Refresh.

---

# 10. Git integrado

No solamente ejecutar Git.

Mostrar

```
Branch

Status

Commit

Push

Pull

Fetch

Stash

Diff
```

Dentro de la aplicación.

---

# 11. Arquitectura MVC → MVVM

Actualmente parece MVC.

Yo migraría a MVVM.

```
Views

↓

ViewModels

↓

Services

↓

Backend
```

La GUI queda muchísimo más limpia.

---

# 12. Sistema de Configuración

En vez de

```
settings.py
```

Yo usaría

```
config/

general.yml

appearance.yml

paths.yml

plugins.yml

git.yml

quarto.yml
```

Así el usuario puede editar todo.

---

# 13. Mejor explorador

El explorador podría reconocer automáticamente

```
posts/

books/

slides/

articles/

talks/

courses/

projects/

assets/
```

con iconos distintos.

---

# 14. Sistema de Logs

Actualmente veo

```
logger
```

Yo tendría

```
logs/

app.log

backend.log

git.log

quarto.log

plugins.log

crash.log
```

Con rotación automática.

---

# 15. Base de datos local

En lugar de depender siempre de escanear carpetas.

Usaría SQLite.

```
studio.db

Projects

Posts

Tags

Metadata

Images

Builds

Logs
```

Las búsquedas serían instantáneas.

---

# 16. Motor de índices

No solo symlinks.

Generar índices de

```
Autores

Tags

Series

Categorías

Años

Cursos

Libros

Notas
```

---

# 17. Validadores

Muy útil.

Una pestaña

```
Validators

✓ YAML

✓ Links

✓ Metadata

✓ Images

✓ Bibliography

✓ Cross References

✓ APA

✓ Front Matter
```

---

# 18. Integración con IA

Aquí es donde el proyecto puede diferenciarse mucho.

Por ejemplo:

- Generar automáticamente metadatos para un nuevo artículo.

- Sugerir etiquetas basadas en el contenido.

- Detectar categorías apropiadas.

- Revisar consistencia del YAML.

- Generar resúmenes y descripciones SEO.

- Sugerir publicaciones relacionadas.

- Detectar enlaces rotos y proponer correcciones.

- Revisar estilo académico para documentos Quarto.

---

# 19. Sistema de Plugins oficial

Que cualquiera pueda desarrollar

```
plugins/

export_pdf

render_beamer

publish_medium

publish_devto

publish_hugo

translate

spellcheck

citations

bibtex
```

Instalables desde la interfaz.

---

# 20. Visión a largo plazo

Creo que el cambio más importante es conceptual. En lugar de verlo como una colección de utilidades para Quarto, plantéalo como un ecosistema modular.

Una arquitectura de este tipo podría organizarse así:

```text
Quarto Studio
│
├── Core
│   ├── Project Manager
│   ├── Plugin Manager
│   ├── Event Bus
│   ├── Command Bus
│   ├── Settings
│   └── Task Manager
│
├── UI
│   ├── Dashboard
│   ├── Explorer
│   ├── Console
│   ├── Logs
│   ├── Validators
│   └── Preferences
│
├── Services
│   ├── Metadata
│   ├── Blogs
│   ├── Posts
│   ├── YAML
│   ├── Index
│   ├── Similar Posts
│   ├── Git
│   ├── Quarto
│   └── AI
│
├── Plugins
│   ├── Metadata
│   ├── Deploy
│   ├── Publish
│   ├── Export
│   ├── Academic
│   └── Custom
│
└── Backend
    ├── Bash
    ├── Python
    ├── Quarto CLI
    ├── Git
    └── Pandoc
```

Con esta evolución, **Quarto Studio** dejaría de ser una interfaz gráfica para ejecutar scripts y se convertiría en un **IDE especializado para Quarto y la escritura académica**, comparable conceptualmente con herramientas como RStudio para R, JupyterLab para notebooks u Obsidian para la gestión del conocimiento, pero enfocado en la creación, publicación y mantenimiento de proyectos Quarto. Esto también facilitaría integrar, en el futuro, tu *Academic Writing Framework*, tus herramientas de conversión documental (*docflow*) y otros proyectos relacionados en una única plataforma coherente y escalable.



# Quarto Studio — Propuesta de arquitectura por fases

> Un IDE especializado para Quarto y escritura académica, construido de forma incremental para que cada fase entregue valor por sí sola, sin comprometerte a una arquitectura completa antes de saber si la necesitas.

## Principio rector

La propuesta original de 20 puntos es arquitectónicamente correcta, pero está pensada para un equipo manteniendo una aplicación grande. Este documento reordena las mismas ideas en **tres fases**, priorizando lo que reduce fricción real hoy sobre lo que se ve bien en un diagrama. Cada fase es útil aunque nunca llegues a la siguiente.

---

## Fase 1 — Fundación (desacoplar sin sobrediseñar)

Objetivo: que la GUI deje de invocar scripts directamente, sin construir todavía un sistema de plugins.

```
scripts_quarto_studio/
├── app/                    # GUI (sin cambios de fondo)
├── core/
│   ├── services/            # Una clase por dominio
│   │   ├── metadata_service.py
│   │   ├── blogs_service.py
│   │   ├── yaml_service.py
│   │   ├── index_service.py
│   │   └── similar_posts_service.py
│   ├── models/               # Project, Post, BuildResult...
│   └── utils/
├── backend/                 # Los scripts existentes, sin tocar
└── resources/
```

**Regla única:** la GUI nunca importa `backend/*` directamente. Siempre pasa por un servicio en `core/services/`.

```python
# Antes
subprocess.run(["backend/script_metadata_manager/main.py"])

# Después
MetadataService.collect()
```

Internamente, `MetadataService.collect()` decide si llama a un script Bash, uno Python, o lógica nueva. La GUI nunca lo sabe. Esto solo es una capa de funciones — nada de manifiestos YAML, nada de carga dinámica. Migrar un backend de Bash a Python el día de mañana no toca la GUI.

**Project Manager mínimo** (`core/project.py`): una clase `Project` con lo esencial —nombre, ruta, tipo, último build— sin base de datos detrás. Se recalcula al abrir el proyecto; no necesita persistencia todavía.

**Por qué primero:** todo lo demás (dashboard, consola, watcher) se apoya en esta capa. Si la saltas, cualquier mejora de UI queda atada a los scripts actuales y es más cara de revertir después.

---

## Fase 2 — Experiencia de uso (lo que se siente todos los días)

Objetivo: que usar la app sea mejor, sin tocar la arquitectura de nuevo.

- **File Watcher** (`watchdog`) sobre `*.qmd`, `*.yml`, `*.bib`, `*.css`. Dispara `MetadataService.collect()` u otro servicio de Fase 1 automáticamente al detectar cambios. Alto impacto, bajo costo.
- **Dashboard con datos reales**: proyecto activo, versión de Quarto, branch de Git, último build, conteo de posts/páginas/imágenes, errores de YAML pendientes. Es una vista que llama a los servicios existentes — no requiere Event Bus para actualizarse; basta con refrescar al terminar una tarea o al detectar un cambio del watcher.
- **Consola mejorada**: colores ANSI, timestamps, filtro y búsqueda, botón de guardar/copiar. Mejora directa sobre `console_widget.py` actual.
- **Task Manager simple**: una cola visible (running / queued / done / failed) sobre los `workers/` que ya tienes, sin necesidad de Command Bus formal — un diccionario de estado y una señal Qt (o equivalente) alcanzan.
- **Git básico integrado**: mostrar branch y status en el dashboard; comandos de commit/push/pull como botones que llaman `git` vía subprocess. No es "Git completo estilo VS Code" todavía, es visibilidad.

**Por qué aquí:** estas son las mejoras que vas a notar cada vez que abras la app. Ninguna requiere rediseñar la arquitectura de Fase 1.

---

## Fase 3 — Escalar solo si aparece el dolor

Esta fase **no se planifica de antemano**. Se activa un punto a la vez, cuando algo concreto en Fase 1–2 empieza a doler. No es una lista de tareas, es un catálogo de soluciones a problemas que todavía no tienes:

| Si empieza a doler esto...                                                                  | Entonces considera...                                                                                           |
| ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Tienes 15+ scripts y cuesta saber cuáles existen o cómo invocarlos                          | Sistema de plugins con manifiesto (`plugin.yaml`) — hoy con 5 servicios, un diccionario en Python es suficiente |
| Varias partes de la GUI necesitan reaccionar al mismo evento sin acoplarse entre sí         | Event Bus — hoy, actualizar el dashboard tras un build es una llamada directa, no un problema de arquitectura   |
| Escanear el filesystem en cada búsqueda se vuelve lento (cientos/miles de archivos)         | SQLite como caché derivado (nunca como fuente de verdad — el filesystem sigue siendo el original)               |
| Distintas vistas necesitan la misma lógica de comandos con undo/redo o cancelación compleja | Command Bus formal                                                                                              |
| Quieres que **terceros** desarrollen plugins para Quarto Studio                             | Plugin Manager instalable desde la interfaz (punto 19 de la propuesta original)                                 |
| El core ya es estable y quieres diferenciarte                                               | Integración con IA: sugerencia de tags, metadatos automáticos, revisión de estilo APA                           |

**Regla de activación:** cada fila de esta tabla se implementa solo cuando puedes nombrar el problema concreto que resuelve — no antes.

---

## Lo que se descarta explícitamente (por ahora)

- **MVVM completo**: para una app mantenida por una sola persona, MVC directo (botón → controller → servicio → actualiza GUI) es más fácil de depurar que un ViewModel intermedio. Se reconsidera solo si el equipo crece.
- **Config dividida en 6 archivos YAML**: un solo `settings.yml` con secciones internas cubre el mismo caso de uso con menos archivos que sincronizar.
- **Logs separados por subsistema** (`app.log`, `git.log`, `quarto.log`...): un solo log con niveles y un campo `source` es más fácil de grep que seis archivos.

Estos tres puntos son reversibles: si en algún momento se vuelven insuficientes, migrar de "un archivo" a "varios archivos" es trivial. Lo caro es el camino inverso.

---

## Resumen visual

```
Fase 1 — Fundación          →  Servicios + Project básico     (desbloquea todo lo demás)
Fase 2 — Experiencia diaria →  Watcher, Dashboard, Consola     (se siente de inmediato)
Fase 3 — Escalar bajo demanda → Plugins / Events / SQLite / IA  (una fila a la vez, con motivo)
```

El nombre **Quarto Studio** y la visión de largo plazo (comparable a RStudio/JupyterLab/Obsidian, con espacio para integrar *Academic Writing Framework* y *docflow* más adelante) se mantienen intactos — lo que cambia es el orden en que se construye, para que cada fase sea útil por sí misma y ninguna dependa de terminar primero toda la anterior.


