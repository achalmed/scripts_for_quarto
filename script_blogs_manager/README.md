# 🚀 Gestor de Publicaciones Quarto (blog-manager) — v3.0

Herramienta de línea de comandos para gestionar todos tus proyectos Quarto
(`pub_*` + `website-achalma`) dentro de `~/Documents`: renderizar, hacer
preview, limpiar, publicar, crear posts APAQuarto completos, gestionar Git,
crear blogs nuevos, verificar su integridad y hacer backups — todo desde un
único punto de entrada: `main.sh`.

Esta es la versión 3.0, reescrita en módulos a partir del antiguo
`build.sh` monolítico (v2.0) + sus scripts auxiliares (`init-blog.sh`,
`check-structure.sh`, `backup-blogs.sh`, `config.sh`). **Toda la
funcionalidad original se conserva**; solo cambia cómo está organizado el
código y cómo se detectan los proyectos.

---

## 📋 Índice

1. [Qué cambió respecto a la versión anterior](#-qué-cambió-respecto-a-la-versión-anterior)
2. [Estructura del proyecto](#-estructura-del-proyecto)
3. [Instalación](#-instalación)
4. [Uso rápido](#-uso-rápido)
5. [Comandos completos](#-comandos-completos)
6. [El asistente de creación de posts (APAQuarto)](#-el-asistente-de-creación-de-posts-apaquarto)
7. [Modo interactivo (menú)](#-modo-interactivo-menú)
8. [Configuración y personalización](#-configuración-y-personalización)
9. [Bugs corregidos respecto al script original](#-bugs-corregidos-respecto-al-script-original)
10. [Resolución de problemas](#-resolución-de-problemas)

---

## 🔄 Qué cambió respecto a la versión anterior

| Aspecto | v2.0 (build.sh) | v3.0 (blog-manager) |
|---|---|---|
| Organización | 1 archivo de ~2000 líneas | `main.sh` + 13 módulos en `lib/` |
| Scripts auxiliares | 4 archivos sueltos (`init-blog.sh`, `check-structure.sh`, `backup-blogs.sh`, `config.sh`) | Integrados como comandos de `main.sh` |
| Ubicación de proyectos | Carpeta contenedora `publicaciones/` | Directo en `~/Documents`, detectando `pub_*` + `website-achalma` |
| Detección de Documents | Ruta fija hardcodeada | Autodetección (o `QBLOG_DOCS_DIR` si la fuerzas) |
| Nombres de blog | Nombre exacto de carpeta | Nombre exacto **o** corto sin el prefijo `pub_` (ej: `axiomata`) |
| Documentación | `README.md` + `INSTALL.md` + `CHANGELOG.md` + `ACTUALIZACION.md` separados | Este único `README.md` |

Tu flujo de trabajo diario (comandos, menú interactivo, wizard de posts) es
el mismo; solo cambia la instalación y de dónde lee tus blogs.

---

## 📁 Estructura del proyecto

```
blog-manager/
├── main.sh                      ⭐ Punto de entrada único
├── README.md                    📖 Este archivo
└── lib/
    ├── 00-config.sh              Rutas, colores, emojis, listas configurables
    ├── 01-printing.sh            Funciones de salida visual (headers, cajas, etc.)
    ├── 02-utils.sh                Autodetección, listado y resolución de proyectos
    ├── 03-listing.sh              list_blogs, list_posts
    ├── 04-quarto-ops.sh           render, preview, clean, publish, check, inspect, convert
    ├── 05-batch-ops.sh            render-all, clean-all
    ├── 06-git-ops.sh              git-status, git-commit, git-init
    ├── 07-post-creator.sh         Asistente interactivo de posts APAQuarto (6 secciones)
    ├── 08-init-blog.sh            Creación de blogs nuevos
    ├── 09-structure-check.sh      Verificación de integridad de blogs
    ├── 10-backup.sh                Sistema de backups (individual/completo/incremental)
    ├── 11-interactive-menu.sh     Menú interactivo (modo -i)
    └── 12-help.sh                 Texto de ayuda (help/-h/--help)
```

Ningún módulo necesita ejecutarse por separado: `main.sh` los carga todos en
orden (`source`) y expone un único comando.

---

## ⚡ Instalación

### 1. Copiar la carpeta a tu ubicación de scripts

```bash
cp -r blog-manager /home/achalmaedison/Documents/scripts_for_quarto/
cd /home/achalmaedison/Documents/scripts_for_quarto/script_blogs_manager
chmod +x main.sh
```

### 2. Probar que detecta tus blogs

```bash
./main.sh list
```

Si todo está bien instalado, deberías ver tus proyectos `pub_*` y
`website-achalma` listados automáticamente — **no necesitas editar ninguna
ruta**, `main.sh` sube desde su propia ubicación buscando la carpeta
`Documents` que contiene tus proyectos.

Si por algún motivo la autodetección no encuentra tu carpeta `Documents`
(por ejemplo, si mueves el script muy lejos de tus proyectos), puedes
forzar la ruta:

```bash
QBLOG_DOCS_DIR="/home/achalmaedison/Documents" ./main.sh list
```

### 3. (Opcional) Crear un alias para acceso rápido

Añade a tu `~/.zshrc` o `~/.bashrc`:

```bash
alias qblog="/home/achalmaedison/Documents/scripts/scripts_for_quarto/blog-manager/main.sh"
```

Recarga la configuración:

```bash
source ~/.zshrc   # o ~/.bashrc
```

Ahora puedes usar simplemente:

```bash
qblog list
qblog render pub_axiomata
```

### 4. (Opcional) Añadir al PATH para acceso global

```bash
echo 'export PATH="$PATH:/home/achalmaedison/Documents/scripts/scripts_for_quarto/blog-manager"' >> ~/.zshrc
source ~/.zshrc
```

Y luego renombrar o symlinkear `main.sh` como `qblog` si prefieres un
nombre más corto:

```bash
ln -s /home/achalmaedison/Documents/scripts/scripts_for_quarto/blog-manager/main.sh \
      /home/achalmaedison/Documents/scripts/scripts_for_quarto/blog-manager/qblog
```

### Requisitos

- **Quarto** ≥ 1.3.0 (recomendado 1.4.0+) — `quarto --version` para verificar
- **Bash** ≥ 4.0
- **Git** (opcional, solo para las funciones `git-*`)
- **yq** (opcional, solo para validar sintaxis YAML en `check-structure`)

---

## 🎯 Uso rápido

```bash
# Modo interactivo (menú completo, recomendado para empezar)
./main.sh

# Listar todos tus blogs
./main.sh list

# Crear un post nuevo (asistente completo paso a paso)
./main.sh new-post pub_epsilon-y-beta

# Preview en vivo mientras escribes
./main.sh preview pub_epsilon-y-beta

# Renderizar versión final
./main.sh render pub_epsilon-y-beta

# Verificar que todos tus blogs estén bien estructurados
./main.sh check-structure

# Backup antes de hacer cambios grandes
./main.sh backup
```

### Sobre los nombres de blog

En todos los comandos que piden `BLOG`, puedes usar:

- El nombre **exacto** de la carpeta: `pub_axiomata`, `website-achalma`
- O el nombre **corto**, sin el prefijo `pub_`: `axiomata` (se resuelve
  automáticamente a `pub_axiomata` si existe)

```bash
./main.sh render axiomata          # equivalente a:
./main.sh render pub_axiomata
```

`website-achalma` no lleva prefijo `pub_` y se usa siempre con su nombre
exacto.

---

## 📚 Comandos completos

### Gestión de blogs

| Comando | Descripción |
|---|---|
| `list` | Lista todos los blogs disponibles (título, posts, estado Git) |
| `render BLOG` | Renderiza un blog completo |
| `preview BLOG [PORT]` | Inicia preview local (puerto opcional, default 4200) |
| `preview-browser BLOG [PORT]` | Igual que `preview`, abriendo el navegador automáticamente |
| `clean BLOG` | Elimina `_site`, `_freeze`, `.quarto` de ese blog |
| `publish BLOG [TARGET]` | Publica (`gh-pages`, `netlify`, `quarto-pub`, `confluence`) |
| `check BLOG` | Ejecuta `quarto check` sobre el blog |
| `inspect BLOG` | Muestra Type/Engine/Formats/Output del blog (sin ruido) |

### Gestión de posts

| Comando | Descripción |
|---|---|
| `list-posts BLOG` | Lista todos los posts agrupados por carpeta temática |
| `render-post RUTA` | Renderiza un solo post (ruta completa al `index.qmd`) |
| `new-post BLOG` | Lanza el asistente interactivo completo de creación de posts |

### Operaciones múltiples

| Comando | Descripción |
|---|---|
| `render-all` | Renderiza todos los blogs gestionables, uno por uno |
| `clean-all` | Limpia todos los blogs (pide confirmación antes de proceder) |

### Git

| Comando | Descripción |
|---|---|
| `git-init BLOG` | Inicializa un repositorio Git en ese blog (crea `.gitignore` si falta) |
| `git-status BLOG` | Muestra `git status` del blog |
| `git-commit BLOG [MSG]` | `git add .` + `commit` + `push` (mensaje opcional, default "Update blog") |

### Otras utilidades

| Comando | Descripción |
|---|---|
| `convert ARCHIVO [FORMATO]` | Convierte un documento con `quarto convert` (default html) |
| `init-blog NOMBRE [TITULO]` | Crea un blog nuevo (estructura completa, prefijo `pub_` automático) |
| `check-structure` | Verifica integridad de todos los blogs (archivos, Git, YAML) |
| `backup` | Sistema de backups interactivo (individual / completo / incremental) |
| `interactive`, `-i` | Abre el menú interactivo |
| `help`, `-h`, `--help` | Muestra la ayuda completa |
| `version`, `-v` | Muestra la versión de Quarto instalada |

### Ejemplos de uso encadenado

```bash
# Limpiar y volver a renderizar
./main.sh clean pub_axiomata && ./main.sh render pub_axiomata

# Crear un blog nuevo, inicializar Git y crear el primer post
./main.sh init-blog mi-nuevo-blog "Mi Nuevo Blog"
./main.sh git-init mi-nuevo-blog
./main.sh new-post mi-nuevo-blog

# Mantenimiento semanal típico
./main.sh check-structure
./main.sh render-all
./main.sh backup
./main.sh clean-all
```

---

## ✍️ El asistente de creación de posts (APAQuarto)

`new-post BLOG` lanza el mismo formulario interactivo completo de la
versión anterior, sin recortar nada. Te guía por 6 secciones:

1. **Opciones generales** — título, subtítulo, shorttitle, bibliografía,
   floatsintext, numbered-lines, mask, nocite, meta-analysis,
   impact-statement, supresión de elementos (title-page, author, orcid,
   abstract, keywords, etc.)
2. **Opciones de formato** — tipo de documento (`doc`/`jou`/`man`/`stu`),
   formatos de salida (docx/html/pdf/typst), fontsize, a4paper, y campos
   específicos según el tipo (revista para `jou`, curso/profesor/fecha de
   entrega para `stu`)
3. **Autores y afiliaciones** — autor por defecto o personalizado, ORCID,
   email, los 14 roles CRediT (conceptualization, methodology,
   investigation, etc.), afiliación institucional completa
4. **Author note** — cambios de estado, conflicto de intereses,
   financiamiento, registro de estudio, data sharing, agradecimientos,
   acuerdos de autoría
5. **Abstract y keywords** — resumen multilínea, palabras clave, impact
   statement, conteo de palabras
6. **Idioma** — código de idioma y, si no es inglés, personalizaciones
   (separador de autores en citas, textos de citas enmascaradas, títulos de
   bloques, etc.)

Al finalizar genera el `index.qmd` con todo el YAML correspondiente más
contenido boilerplate (Introducción/Desarrollo/Conclusiones/Referencias) y
un `references.bib` vacío, y te pregunta si quieres abrirlo de inmediato en
tu editor.

Antes de empezar el formulario, el asistente detecta automáticamente las
carpetas de posts existentes en el blog (`python`, `r`, `posts`, etc., y en
`website-achalma` también reconoce el caso especial `blog/posts` y
`talk`), o te permite crear una nueva. Si la carpeta es nueva, genera
también su `_metadata.yml` compartido con tu configuración institucional
real (UNSCH, ORCID, email) para que no tengas que repetirla en cada post.

> **Nota práctica:** el formulario tiene decenas de preguntas
> condicionales (algunas solo aparecen según el tipo de documento o si usas
> autor por defecto). Está pensado para uso interactivo real — si alguna
> vez necesitas automatizarlo con un archivo de input, asegúrate de que
> cada línea responda exactamente a la pregunta que le corresponde, o el
> YAML resultante quedará desalineado.

---

## 🖥️ Modo interactivo (menú)

Ejecutar `./main.sh` sin argumentos (o `./main.sh -i`) abre un menú
numerado con las mismas 16 opciones del script original, más 3 nuevas
(antes scripts separados):

```
Gestión de Blogs:        1-5
Gestión de Posts:        6-8
Operaciones Múltiples:   9-10
Git:                     11-13
Utilidades:              14-16
Otras herramientas:      17) init-blog   18) check-structure   19) backup
0) Salir
```

---

## ⚙️ Configuración y personalización

Toda la configuración vive en `lib/00-config.sh`. No deberías necesitar
tocar ningún otro archivo para personalizar el comportamiento.

### Excluir un blog puntual de las operaciones masivas

Por defecto **todos** tus `pub_*` + `website-achalma` se gestionan. Si en
algún momento quieres excluir uno (por ejemplo, mientras lo tienes en
borrador y no quieres que aparezca en `list`, `render-all`, `clean-all`,
`check-structure` o `backup`), edita:

```bash
# lib/00-config.sh
QBLOG_EXCLUDED_PROJECTS=("pub_borradores")
```

### Cambiar puerto de preview, target de publicación, autor por defecto, etc.

```bash
# lib/00-config.sh
QBLOG_DEFAULT_PREVIEW_PORT=4200
QBLOG_DEFAULT_PUBLISH_TARGET="gh-pages"
QBLOG_DEFAULT_AUTHOR="Edison Achalma"
QBLOG_DEFAULT_AUTHOR_ORCID="0000-0001-6996-3364"
QBLOG_DEFAULT_AUTHOR_EMAIL="elmer.achalma.09@unsch.edu.pe"
QBLOG_DEFAULT_INSTITUTION="Universidad Nacional de San Cristóbal de Huamanga"
```

### Forzar la ubicación de Documents o de los backups

Si alguna vez mueves el script a un lugar muy alejado de tus proyectos
(más de 6 niveles de profundidad) y la autodetección falla, usa variables
de entorno (no necesitas editar el código):

```bash
QBLOG_DOCS_DIR="/ruta/a/Documents" ./main.sh list
QBLOG_BACKUP_DIR="/ruta/a/backups" ./main.sh backup
```

### Añadir un comando nuevo

1. Escribe la función en el módulo `lib/` que corresponda temáticamente
   (o crea uno nuevo, ej. `lib/13-mi-funcion.sh`).
2. Si creaste un archivo nuevo, agrégalo al bloque de `source` en `main.sh`.
3. Añade un `case` nuevo en la función `main()` de `main.sh`.
4. Documéntalo en `lib/12-help.sh` y, si aplica, en el menú
   (`lib/11-interactive-menu.sh`).

---

## 🐛 Bugs corregidos respecto al script original

Durante la migración se identificaron y corrigieron dos bugs reales que
existían en `build.sh` v2.0:

1. **`clean-all` rota.** El menú interactivo (opción 10) y el comando CLI
   `build.sh clean-all` invocaban una función `clean_all_blogs` que
   **nunca llegó a definirse** en el script — el comando fallaba con
   `command not found`. En `blog-manager` esta función existe
   (`lib/05-batch-ops.sh`), sigue el mismo patrón que `render_all_blogs`,
   y pide confirmación antes de borrar archivos en todos tus blogs.

2. **`new-post` roto desde línea de comandos.** El comando CLI
   `build.sh new-post BLOG "Título"` invocaba una función `create_post`
   que tampoco existía (la función real siempre se llamó
   `create_post_interactive`, y no toma un título como argumento — todo se
   pregunta dentro del asistente). Por eso, ejecutar `new-post` desde
   terminal siempre fallaba con `command not found`; solo funcionaba
   entrando al menú interactivo y eligiendo la opción 6. En
   `blog-manager`, `new-post BLOG` ya invoca correctamente el asistente
   completo tanto desde el menú como desde la línea de comandos.

Ambas correcciones no cambian ningún comportamiento que ya funcionara — el
resto del wizard, el formato del `index.qmd` generado, y todas las demás
funciones, son una traducción fiel de tu script original.

---

## 🔧 Resolución de problemas

### "No se pudo autodetectar la carpeta Documents"

El script sube hasta 6 niveles desde su propia ubicación buscando una
carpeta con al menos un `pub_*` o `website-achalma`. Si la mueves muy lejos
de tus proyectos, fuerza la ruta:

```bash
QBLOG_DOCS_DIR="/home/achalmaedison/Documents" ./main.sh list
```

### "Quarto no está instalado"

```bash
which quarto
quarto --version
```

Si no aparece nada, instala Quarto desde
[quarto.org/docs/get-started](https://quarto.org/docs/get-started/).

### "Blog no encontrado: nombre-blog"

Verifica el nombre exacto con `./main.sh list`. Recuerda que puedes usar el
nombre corto (sin `pub_`) o el exacto, pero debe coincidir con una carpeta
real dentro de tu `Documents` detectado.

### "Permission denied" al ejecutar `./main.sh`

```bash
chmod +x main.sh
```

### El YAML del post generado por `new-post` salió mal formado

Esto ocurre si las respuestas al asistente no coincidieron exactamente con
las preguntas (por ejemplo, si automatizaste el input con un archivo de
texto que no estaba perfectamente alineado con las preguntas
condicionales). Usando el asistente de forma interactiva normal (tecleando
tus respuestas en pantalla) no debería pasar, ya que cada pregunta se
muestra antes de pedir su respuesta. Si te ocurre en uso interactivo
normal, bórralo y vuelve a correr `new-post` con más cuidado en las
respuestas s/n.

---

## 📞 Autor

**Edison Achalma**
Economista — Universidad Nacional de San Cristóbal de Huamanga (UNSCH)
ORCID: 0000-0001-6996-3364
GitHub: [@achalmed](https://github.com/achalmed)
Ayacucho, Perú

Para más información sobre Quarto: [quarto.org/docs](https://quarto.org/docs/)
Para APAQuarto: [wjschne.github.io/apaquarto](https://wjschne.github.io/apaquarto/)
