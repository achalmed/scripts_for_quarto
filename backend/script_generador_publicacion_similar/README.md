# Generador de Índices de Contenido para Blogs Quarto

> Genera automáticamente archivos `_contenido_<subblog>.qmd` con enlaces
> numerados (artículo + PDF) a las publicaciones de un blog Quarto,
> soportando blogs independientes (`pub_*`) y secciones de página web
> (`website-achalma/blog`, `/teching`, etc.).

**Versión:** 4.0.0 · **Autor:** Edison Achalma

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Requisitos](#️-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura](#️-arquitectura)
- [Bugs Corregidos](#-bugs-corregidos)
- [Solución de Problemas](#-solución-de-problemas)
- [Cómo Contribuir](#-cómo-contribuir--agregar-nuevas-funcionalidades)
- [Notas y Advertencias](#️-notas-y-advertencias)

## 📖 Descripción

Recorre los subblogs (subcarpetas) de un blog Quarto, localiza las carpetas
de publicación con formato `YYYY-MM-DD-titulo/` que contengan un `index.qmd`,
y genera en cada subblog un índice Markdown listo para incluir con
`{{< include >}}`:

```markdown
1. [{{< fa regular file-pdf >}}](https://dominio.com/posts/2022-01-23-titulo/index.pdf) [Titulo](https://dominio.com/posts/2022-01-23-titulo)
2. ...
```

### Estructuras soportadas

| Tipo                              | Ejemplo de directorio                 | URL generada                       |
| --------------------------------- | ------------------------------------- | ---------------------------------- |
| `blog` (proyecto independiente)   | `~/Documents/pub_actus-mercator`      | `base/<subblog>/<post>/`           |
| `website` (sección de página web) | `~/Documents/website-achalma/teching` | `base/<seccion>/<subblog>/<post>/` |

Con `--type auto` (por defecto) la estructura se detecta por la ubicación del
`_quarto.yml`: si está en el propio directorio es un proyecto independiente;
si está en el directorio padre, se trata de una sección de la página web.

## ⚙️ Requisitos

### Sistema Operativo

- Linux (usa `sed` GNU para capitalizar títulos; no compatible con BSD/macOS sin ajustes)

### Dependencias

- Bash >= 4.x
- Coreutils estándar: `sed`, `tr`, `date`, `basename`, `dirname`

No requiere Python ni paquetes externos.

## 🚀 Instalación

### Paso 1: Obtener el código

```bash
git clone https://github.com/achalmed/scripts_for_quarto.git
cd scripts_for_quarto/script_generador_publicacion_similar
```

### Paso 2: Dar permisos de ejecución

```bash
chmod +x main.sh
```

### Paso 3 (opcional): Crear alias

```bash
echo 'alias generar-indices="~/Documents/scripts_for_quarto/script_generador_publicacion_similar/main.sh"' >> ~/.zshrc
source ~/.zshrc
```

## 💻 Uso

### Sintaxis

```bash
./main.sh BLOG_DIR [OPCIONES]
```

### Opciones disponibles

| Flag                 | Descripción                                                                        | Requerido |
| -------------------- | ---------------------------------------------------------------------------------- | --------- |
| `BLOG_DIR`           | Directorio del blog a procesar (posicional)                                        | Sí        |
| `-u, --base-url URL` | URL base del sitio, sin barra final (default: `https://achalmaedison.netlify.app`) | No        |
| `-t, --type TIPO`    | `auto` \| `website` \| `blog` (default: `auto`)                                    | No        |
| `-n, --dry-run`      | Simula sin escribir ni borrar archivos                                             | No        |
| `-h, --help`         | Muestra la ayuda                                                                   | No        |
| `--version`          | Muestra la versión                                                                 | No        |

### Ejemplos de uso

```bash
# Blog independiente (URL base propia)
./main.sh ~/Documents/pub_actus-mercator --base-url https://actus-mercator.netlify.app

# Sección de la página web (URL base por defecto)
./main.sh ~/Documents/website-achalma/teching

# Simular primero (recomendado antes de cambios masivos)
./main.sh ~/Documents/pub_axiomata --dry-run
./main.sh ~/Documents/website-achalma/teching          # usa la URL base por defecto

# Forzar tipo de estructura si la autodetección no aplica
./main.sh ~/Documents/mi-blog-nuevo --type blog
```

### Códigos de salida

| Código | Significado                        |
| ------ | ---------------------------------- |
| 0      | Éxito                              |
| 1      | Error general (fallo de escritura) |
| 2      | Error de argumentos / uso          |
| 3      | Directorio de blog no encontrado   |

### Integración con Quarto

```markdown
## Publicaciones Recientes

{{< include posts/_contenido_posts.qmd >}}
```

## 🗂️ Arquitectura

Sigue el mismo patrón modular que `script_blogs_manager` y
`script_pub_index_symlink`: un `main.sh` delgado que carga módulos
numerados desde `lib/` en orden de dependencia.

```
script_generador_publicacion_similar/
├── main.sh                  # Punto de entrada — orquesta los módulos
├── README.md                # Esta documentación
└── lib/
    ├── 00-config.sh         # Versión, defaults, carpetas ignoradas
    ├── 01-logging.sh        # log_info/success/warn/error con timestamp
    ├── 02-cli.sh            # Parsing de argumentos y ayuda
    ├── 03-validator.sh      # Validación y normalización de entradas
    ├── 04-detector.sh       # Autodetección website/blog vía _quarto.yml
    ├── 05-linker.sh         # Título, URL y línea Markdown de cada post
    └── 06-generator.sh      # Recorrido de subblogs, escritura y resumen
```

### Descripción de módulos

| Archivo               | Responsabilidad                                                             |
| --------------------- | --------------------------------------------------------------------------- |
| `main.sh`             | Carga módulos, resuelve el tipo de estructura y ejecuta el flujo            |
| `lib/00-config.sh`    | Única fuente de configuración (`GENIDX_*`); nada se hardcodea fuera         |
| `lib/01-logging.sh`   | Formato de log consistente; WARN/ERROR a stderr                             |
| `lib/02-cli.sh`       | `parse_arguments` + `show_help`; valida presencia de valores en flags       |
| `lib/03-validator.sh` | Directorio existente → ruta absoluta; URL sin barra final; tipo válido      |
| `lib/04-detector.sh`  | `detect_blog_structure`: `_quarto.yml` propio = blog, en el padre = website |
| `lib/05-linker.sh`    | `format_post_title`, `build_post_url`, `convert_folder_to_link`             |
| `lib/06-generator.sh` | Acumula el índice en memoria y escribe una sola vez; totales y resumen      |

Convenciones: prefijo `GENIDX_` para todos los globales, guardas
`GENIDX_*_LOADED` contra doble carga, y `set -uo pipefail` con chequeos de
error explícitos (igual que el resto de herramientas del repositorio).

## 🐛 Bugs Corregidos

### Bug #1: Ruta hardcodeada obsoleta e inexistente

- **Ubicación**: `generar_indices.sh:23` (variable `main_blog`)
- **Descripción**: Apuntaba a `/home/achalmaedison/Documents/publicaciones/website-achalma/teching`, ruta que ya no existe (los blogs viven ahora directamente en `~/Documents`). Además obligaba a editar el script para cada blog.
- **Impacto**: El script terminaba con error en toda ejecución; procesar otro blog requería modificar el código fuente.
- **Corrección**: El directorio del blog es ahora un argumento posicional obligatorio; la URL base y el tipo son flags con defaults en `lib/00-config.sh`.

### Bug #2: Detección de estructura incorrecta para secciones web

- **Ubicación**: `generar_indices.sh:48-66` (`detect_blog_structure`)
- **Descripción**: Solo reconocía la estructura `website` si la carpeta se llamaba literalmente `blog`. Secciones como `teching/` o `talk/` se clasificaban como blog independiente.
- **Impacto**: URLs generadas sin el segmento de sección (`base/subblog/post` en vez de `base/teching/subblog/post`) → todos los enlaces del índice rotos.
- **Corrección**: La detección usa la ubicación del `_quarto.yml` (raíz real del sitio Quarto); la heurística por nombre se conserva solo como fallback. Verificado: `teching` ahora se detecta como `website`.

### Bug #3: Truncado prematuro del índice existente

- **Ubicación**: `generar_indices.sh:213` (`> "$output_file"`)
- **Descripción**: El archivo de índice se vaciaba _antes_ de saber si había publicaciones, y se escribía línea a línea durante el bucle.
- **Impacto**: Una interrupción (Ctrl+C, error a mitad de bucle) dejaba el índice vacío o incompleto, destruyendo el contenido anterior. También imposibilitaba un modo de simulación.
- **Corrección**: El contenido se acumula en memoria y se escribe de una sola vez, solo si hay publicaciones. Esto habilitó además el flag `--dry-run`. Se conserva el comportamiento original de eliminar índices obsoletos (ahora con `rm -f` en lugar de `rm`, que podía quedar interactivo por alias).

### Bug #4: Rotura con rutas que contienen espacios

- **Ubicación**: `generar_indices.sh:120` (`dirname "$path" | xargs basename`)
- **Descripción**: `xargs` divide su entrada por espacios, por lo que rutas como `~/Documents/01 notes/...` producían un nombre de subblog incorrecto.
- **Impacto**: URLs y nombres de archivo corruptos para cualquier ruta con espacios.
- **Corrección**: `basename "$(dirname "$path")"` — sustitución de comandos anidada, inmune a espacios.

### Bug #5: URL base con barra final sin normalizar

- **Ubicación**: Configuración (`base_url`)
- **Descripción**: El README advertía "sin barra final" pero el script no lo validaba ni corregía.
- **Impacto**: URLs con doble barra (`https://dominio.com//posts/...`) en todos los enlaces generados.
- **Corrección**: `lib/03-validator.sh` elimina la barra final automáticamente y avisa si la URL no empieza con `http(s)://`.

### Bug #6: `echo -e` sobre contenido variable

- **Ubicación**: `generar_indices.sh:130` y `227`
- **Descripción**: `echo -e` interpreta secuencias de escape (`\n`, `\t`) presentes en los datos, y el título pasaba dos veces por él.
- **Impacto**: Un título de carpeta con secuencias tipo `\n` corrompería el índice generado.
- **Corrección**: Toda la salida usa `printf` con formato explícito.

## 🔧 Solución de Problemas

### Error: "Permission denied"

```bash
chmod +x main.sh
```

### La estructura no se detecta correctamente

La autodetección requiere que el proyecto tenga `_quarto.yml`. Si el blog
está en construcción y aún no lo tiene, fuerza el tipo manualmente:

```bash
./main.sh ~/ruta/al/blog --type blog      # proyecto independiente
./main.sh ~/ruta/al/blog --type website   # sección de página web
```

### Las URLs generadas son incorrectas

1. Verifica el tipo detectado en la primera línea del log.
2. Confirma la `--base-url` (el script ya tolera la barra final).
3. Ejecuta con `--dry-run` y revisa qué archivos se generarían.

### Un subblog aparece como "sin publicaciones"

- Las carpetas de posts deben llamarse `YYYY-MM-DD-titulo/` y contener `index.qmd`.
- Las carpetas que empiezan con `.` o `_` y las listadas en `GENIDX_IGNORE_DIRS` se omiten siempre.

## 🤝 Cómo Contribuir / Agregar Nuevas Funcionalidades

### Para agregar un nuevo módulo

1. Crea `lib/NN-nombre.sh` con el siguiente número disponible y la guarda `GENIDX_<NOMBRE>_LOADED`.
2. Define funciones con responsabilidad única y prefijo coherente.
3. Añade el `source` correspondiente en `main.sh` respetando el orden numérico.
4. Si agrega flags, decláralas en `lib/02-cli.sh` y documéntalas en `show_help` y en este README.

### Estándares de código

- Máximo ~30 líneas por función.
- Toda configuración vive en `lib/00-config.sh`; ningún módulo hardcodea rutas ni valores.
- Toda salida a consola pasa por `lib/01-logging.sh`.
- Comenta el "por qué", no el "qué".
- Prueba con `--dry-run` y `bash -n` antes de hacer commit.

## ⚠️ Notas y Advertencias

- **Cambio de interfaz respecto a v3.0**: ya no se edita el script para
  configurarlo; el directorio se pasa como argumento. Si usabas alias del
  estilo `generar_indices_web.sh` (copias del script con distinta
  configuración), reemplázalos por alias con argumentos:
  `alias indices-actus='main.sh ~/Documents/pub_actus-mercator -u https://actus-mercator.netlify.app'`.
- La capitalización de títulos usa `sed 's/\b\(.\)/\u\1/g'` (extensión GNU):
  en macOS/BSD requeriría `gsed`.
- Los índices se generan **sin encabezado YAML** (comportamiento original),
  pensados para usarse vía `{{< include >}}`.
- El orden de las publicaciones es el alfabético del glob, que con el
  prefijo `YYYY-MM-DD-` equivale a orden cronológico ascendente.
- Si un subblog se queda sin publicaciones válidas, su índice previo se
  **elimina** (comportamiento original preservado); `--dry-run` lo anuncia
  sin borrarlo.

## 👤 Autor

**Edison Achalma**

- Website: [achalmaedison.netlify.app](https://achalmaedison.netlify.app)
- GitHub: [@achalmed](https://github.com/achalmed)
