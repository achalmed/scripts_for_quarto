# pub-index-sync

Script en Bash que mantiene la carpeta `04 index` actualizada con enlaces
simbólicos (symlinks), organizados por año, a todas las carpetas de
publicación que existen dentro de tus proyectos `pub_*` y de
`website-achalma/blog/posts` y `website-achalma/talk`.

El objetivo: dejar de buscar publicación por publicación, proyecto por
proyecto. Un solo lugar (`04 index/<año>/`) con accesos directos a todo.

## ¿Qué hace exactamente?

1. Recorre cada carpeta que empieza con `pub_` dentro de `Documents`, en
   cualquier nivel de profundidad, buscando subcarpetas cuyo **nombre**
   empiece con una fecha `YYYY-MM-DD-` (por ejemplo
   `2022-09-12-01-introduccion-al-mundo-de-bi-y-la-suite-power`).
2. Recorre también `website-achalma/blog/posts` y `website-achalma/talk`,
   buscando carpetas con el mismo patrón de fecha.
3. Ignora siempre las carpetas técnicas/generadas por Quarto u otras
   herramientas: `_freeze`, `_partials`, `_site`, `_extensions`, `.quarto`,
   `.git`, `site_libs`, `node_modules` (y cualquier cosa dentro de ellas).
4. Por cada publicación encontrada, crea (o actualiza) un symlink dentro de
   `04 index/<año>/<nombre-original-de-la-carpeta>` apuntando a la carpeta
   real del proyecto.
5. Si el symlink ya existe y apunta correctamente, lo **omite** (no lo toca).
6. Si encuentra symlinks rotos (la carpeta original fue borrada o movida),
   los reporta, y opcionalmente los elimina con tu confirmación.
7. Nunca borra ni sobrescribe carpetas o archivos reales que no sean
   symlinks creados por el propio script — si detecta un conflicto, te
   avisa y lo deja para revisión manual.

## Estructura del proyecto

El script está dividido en módulos (uno por responsabilidad), todos
orquestados desde `main.sh`. Así, si algo falla, es fácil saber en qué
archivo mirar:

```
pub-index-sync/
├── main.sh                    # Orquestador principal, parseo de argumentos
├── lib/
│   ├── 00-config.sh           # Rutas, patrones y constantes centrales
│   ├── 01-logging.sh          # Funciones de impresión y registro en log
│   ├── 02-utils.sh            # Utilidades: extraer año, detectar Documents, etc.
│   ├── 03-scanner.sh          # Busca las carpetas de publicación (solo lectura)
│   ├── 04-symlinker.sh        # Crea/actualiza symlinks en 04 index
│   ├── 05-broken-detector.sh  # Detecta y opcionalmente limpia symlinks rotos
│   └── 06-maintenance.sh      # Limpieza de carpetas de año vacías + resumen
└── logs/                      # Se crea automáticamente, un log por día
```

Cada archivo en `lib/` se puede leer y entender de forma aislada. Si en el
futuro quieres agregar una funcionalidad nueva (por ejemplo, indexar otro
tipo de carpeta), basta con agregar un módulo nuevo y un par de líneas en
`main.sh` — no hace falta tocar el resto.

## Instalación

1. Copia la carpeta `pub-index-sync/` dentro de `~/Documents` (al mismo
   nivel que `04 index`, `pub_numerus-scriptum`, `website-achalma`, etc.).
2. Dale permisos de ejecución:

```bash
chmod +x ~/Documents/scripts_for_quarto/script_pub_index_symlink/main.sh
```

El script **autodetecta** la ubicación de `Documents` subiendo desde su
propia ubicación hasta encontrar una carpeta `04 index`. Si por algún
motivo la autodetección falla (por ejemplo si mueves el script fuera de
`Documents`), puedes forzar la ruta manualmente:

```bash
PUBINDEX_DOCS_DIR=/home/achalmaedison/Documents ~/Documents/pub-index-sync/main.sh
```

## Uso

### Sincronización normal (modo más común)

```bash
cd ~/Documents/scripts_for_quarto/script_pub_index_symlink
./main.sh
```

Esto escanea todo, crea los symlinks nuevos, omite los que ya existían,
reporta symlinks rotos (sin borrarlos), y al final muestra un resumen de
cuántas publicaciones hay indexadas por año.

### Simular sin tocar nada (dry-run)

Útil para revisar qué haría el script antes de ejecutarlo de verdad:

```bash
./main.sh --dry-run
```

### Solo revisar si hay symlinks rotos

```bash
./main.sh --check-broken
```

### Revisar y limpiar symlinks rotos (con confirmación)

```bash
./main.sh --clean-broken
```

Te mostrará la lista de symlinks rotos y pedirá confirmación (`s`/`N`)
antes de borrar nada. Después de borrar, también elimina las carpetas de
año que hayan quedado vacías.

### Solo ver el resumen por año (sin sincronizar)

```bash
./main.sh --summary
```

### Sincronizar sin mostrar el resumen final

```bash
./main.sh --no-summary
```

### Ver la ayuda

```bash
./main.sh --help
```

## Recomendación de uso

Puedes ejecutar `./main.sh` cada vez que termines de escribir una
publicación nueva en cualquiera de tus proyectos `pub_*` o en el blog de
`website-achalma`. El script es **idempotente**: ejecutarlo varias veces
seguidas no duplica ni rompe nada, solo agrega lo nuevo y omite lo que ya
estaba.

Si quieres automatizarlo (por ejemplo con una entrada de `cron` o un atajo
de teclado en tu entorno), simplemente apunta al script:

```bash
~/Documents/pub-index-sync/main.sh --no-summary >> ~/Documents/pub-index-sync/logs/cron.log 2>&1
```

## Logs

Cada ejecución registra su actividad en `logs/<fecha>.log` (un archivo por
día, se va acumulando si ejecutas el script varias veces el mismo día).
Útil para revisar qué pasó en una corrida anterior sin tener que volver a
ejecutar el script.

## Cómo funciona la detección de "qué es una publicación"

El criterio es **únicamente el nombre de la carpeta**: debe empezar con
una fecha en formato `YYYY-MM-DD-` seguida de cualquier texto. No importa
en qué subcarpeta temática esté (`python/`, `r/`, `latex/`, `blog/posts/`,
`talk/`, etc.) ni qué tan profundo esté anidada — el script la encuentra
igual, siempre que no esté dentro de una carpeta técnica ignorada.

Carpetas como `index_files` o `figure-pdf` que viven *dentro* de una
carpeta de publicación (por ejemplo
`2025-05-10-visualizacion-de-datos-con-python/index_files/figure-pdf`) no
se symlinkean por separado: solo se symlinkea la carpeta padre con fecha,
y esas subcarpetas viajan con ella automáticamente al ser parte del mismo
symlink.

## Manejo de conflictos

Si dentro de `04 index/<año>/` ya existe un archivo o carpeta **real**
(no un symlink) con el mismo nombre que debería tener un symlink nuevo, el
script **no lo toca** y lo reporta como conflicto en la salida. Esto es
para protegerte de perder algo que hayas puesto ahí manualmente. En ese
caso, revisa el conflicto a mano: si la carpeta real ya no la necesitas,
bórrala tú mismo y vuelve a ejecutar el script para que cree el symlink.

## Variables de entorno

| Variable             | Para qué sirve                                                                 |
|-----------------------|---------------------------------------------------------------------------------|
| `PUBINDEX_DOCS_DIR`   | Fuerza la ruta absoluta de `Documents` si la autodetección no la encuentra.     |

## Solución de problemas

**"No se pudo autodetectar la carpeta Documents"**
Significa que el script no encontró una carpeta `04 index` subiendo hasta
5 niveles desde su propia ubicación. Verifica que `pub-index-sync/` esté
dentro de `Documents`, o usa `PUBINDEX_DOCS_DIR` para forzar la ruta.

**Un symlink no se actualiza aunque la publicación cambió de ubicación**
Si la carpeta original cambió de ruta (no solo de contenido), el script lo
detecta como un destino distinto y actualiza el symlink automáticamente en
la siguiente corrida — no necesitas hacer nada manual.

**Quiero reindexar todo desde cero**
Borra la carpeta `04 index` (o su contenido) y vuelve a correr
`./main.sh`. Como son solo symlinks, no se pierde ningún archivo real.

## Requisitos

- Bash 4+ (cualquier Kubuntu o Arch Linux moderno lo trae por defecto).
- Utilidades estándar de GNU: `find`, `readlink`, `mkdir`, `ln`. Todas
  vienen preinstaladas en Kubuntu y Arch Linux.
