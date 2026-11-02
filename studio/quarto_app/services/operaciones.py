"""quarto_app/services/operaciones.py — el catálogo de las operaciones de Quarto Studio (sin Qt; se prueba solo): cada
una es una orden de un backend de `../backend/` (los `Command` de `blog_service`, `metadata_service`, `yaml_service`,
`index_service` y `similar_service`, que no cambian), agrupada por la vista en la que se ofrece.

Cómo se corre cada una (rediseño Q3): **F5 simula** con la simulación de la CLI cuando la hay (`publish` y
`git-commit` simulan sin `--aplicar`; metadatos, YAML, índice y contenido con `--dry-run`) y, cuando la CLI no simula
(`render`, `clean`, `backup`, `init-blog`), con el **plan** que la ventana calcula sin correr nada; las que solo leen se
ejecutan con F5 y no tienen Aplicar. **Ctrl+Intro aplica** tras un diálogo con la orden exacta; publicar y commit+push
nombran además el sitio y su dominio (Q4). Las confirmaciones que un guion pide por terminal se responden por la
entrada estándar después de que la ventana confirmó (`entrada`).
"""
from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from quarto_app.services import blog_service, index_service, metadata_service, paths, similar_service, yaml_service
from quarto_app.services import sitios as svc_sitios
from quarto_app.services.command import Command

VISTAS = (("sitios", "Sitios", "folder-html"), ("entradas", "Entradas y metadatos", "text-markdown"),
          ("indice", "Índice del vault", "emblem-symbolic-link"), ("contenido", "Índices de contenido", "view-list-text"))
NOMBRES_VISTAS = tuple(v[0] for v in VISTAS)


@dataclass
class Contexto:
    """Lo que una operación necesita del estado de la ventana para armar su orden."""
    sitio: str = ""                   # el nombre del sitio actual
    ruta: str = ""                    # su carpeta
    estado: dict = field(default_factory=dict)      # su estado (servicios.sitios)
    sitios: list = field(default_factory=list)      # [(nombre, ruta, estado)] de todos, en el orden de la tabla
    entrada: str = ""                 # la ruta del index.qmd de la entrada actual
    valor: str = ""                   # lo que pide la operación (texto, carpeta o archivo)
    excel: str = ""                   # el Excel de metadatos
    filtro_ruta: str = ""             # --filter-path de metadatos
    usar_excel: bool = False          # tags y fechas sobre el Excel en vez de sobre los .qmd
    hub: str = ""


@dataclass(frozen=True)
class Operacion:
    id: str
    titulo: str
    descripcion: str
    vista: str
    simular: Callable[[Contexto], Command] | None = None     # la simulación de la CLI (F5); None: el plan de la ventana o solo lectura
    aplicar: Callable[[Contexto], Command] | None = None     # lo que escribe (Ctrl+Intro); None: no tiene modo aplicar
    plan: Callable[[Contexto], str] | None = None            # el plan de la ventana (F5) cuando la CLI no simula
    sobre_sitio: bool = False         # exige un sitio actual
    sobre_entrada: bool = False       # exige una entrada actual
    publica: bool = False             # el diálogo nombra el sitio y su dominio: Netlify despliega con el push
    larga: bool = False               # un servidor (preview): F5 lo arranca y Esc lo detiene
    borra: str = ""                   # qué borra (va en el diálogo)
    entrada: str = ""                 # «texto», «carpeta» o «archivo»
    etiqueta: str = ""
    defecto: str = ""                 # «sitio» (la carpeta del sitio actual) · «entrada» (el .qmd actual) · un texto
    admite_excel: bool = False        # ofrece «operar sobre el Excel»

    @property
    def escribe(self) -> bool:
        return self.aplicar is not None

    @property
    def verbo(self) -> str:
        if self.larga:
            return "Arrancar"
        return "Simular" if self.escribe else "Ejecutar"

    def orden_simular(self, ctx: Contexto) -> Command | None:
        return self.simular(ctx) if self.simular else None

    def orden_aplicar(self, ctx: Contexto) -> Command | None:
        return self.aplicar(ctx) if self.aplicar else None


def texto_orden(cmd: Command | None) -> str:
    """La orden tal como se escribiría en la terminal, relativa al repo."""
    if cmd is None:
        return ""
    raiz = str(paths.REPO) + "/"
    partes = [cmd.programa, *cmd.args]
    return shlex.join(p[len(raiz):] if p.startswith(raiz) else p for p in partes)


# ------------------------------------------------------------------------------------------------------ planes
def _git(ruta: str, *args: str) -> list[str]:
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ruta, *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return []
    return [l for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []


def plan_render(ctx: Contexto) -> str:
    e = ctx.estado or {}
    lineas = [f"Renderizar {ctx.sitio} ({ctx.ruta}) con `quarto render`.", f"Estado: {e.get('texto_estado', '?')} — {e.get('motivo', '')}."]
    if ctx.ruta:
        sin_confirmar = _git(ctx.ruta, "status", "--porcelain", "--untracked-files=all", "--", *svc_sitios.FUENTES)
        if sin_confirmar:
            lineas.append(f"Fuentes sin confirmar ({len(sin_confirmar)}):")
            lineas += ["  " + l for l in sin_confirmar[:40]]
        ultimo = _git(ctx.ruta, "log", "-1", "--format=%H", "--", "_site/index.html")
        if ultimo:
            cambiadas = _git(ctx.ruta, "diff", "--name-only", f"{ultimo[0]}..HEAD", "--", *svc_sitios.FUENTES)
            if cambiadas:
                lineas.append(f"Fuentes confirmadas después del último render ({len(cambiadas)}):")
                lineas += ["  " + l for l in cambiadas[:40]]
    lineas.append("El render escribe _site/ (y _freeze/ si el proyecto congela) dentro del sitio; nada se publica.")
    return "\n".join(lineas)


def plan_render_todos(ctx: Contexto) -> str:
    orden = sorted(ctx.sitios, key=lambda s: {"sin_render": 0, "problemas": 1, "sin_publicar": 2, "al_dia": 3}.get(s[2].get("estado", ""), 9))
    lineas = [f"Renderizar los {len(ctx.sitios)} sitios, uno tras otro (`main.sh render-all`), en el orden de la CLI; los que piden render primero según la tabla:"]
    for i, (nombre, _ruta, e) in enumerate(orden, start=1):
        lineas.append(f"  {i:2d}. {nombre}: {e.get('texto_estado', '?')} — {e.get('motivo', '')}")
    lineas.append("Nada se publica: cada sitio escribe su _site/.")
    return "\n".join(lineas)


def plan_render_entrada(ctx: Contexto) -> str:
    return f"Renderizar solo la entrada {ctx.entrada} (`main.sh render-post`): escribe su salida dentro de _site/ del sitio {ctx.sitio}."


def _tamano(ruta: Path) -> str:
    total = 0
    for p in ruta.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            pass
    return f"{total / 1_048_576:.1f} MB"


def plan_limpiar(ctx: Contexto) -> str:
    lineas = [f"Limpiar {ctx.sitio}: borra los artefactos generados (`main.sh clean`); las fuentes no se tocan."]
    for nombre in ("_site", "_freeze", ".quarto"):
        p = Path(ctx.ruta) / nombre
        lineas.append(f"  {nombre}/: {'existe · ' + _tamano(p) if p.is_dir() else 'no existe'}")
    lineas.append("Después del limpiado el sitio queda «con problemas» hasta volver a renderizar.")
    return "\n".join(lineas)


def plan_limpiar_todos(ctx: Contexto) -> str:
    lineas = [f"Limpiar los {len(ctx.sitios)} sitios (`main.sh clean-all`; la confirmación del guion la responde la ventana):"]
    for nombre, ruta, _e in ctx.sitios:
        partes = [f"{d}/ {_tamano(Path(ruta) / d)}" for d in ("_site", "_freeze", ".quarto") if (Path(ruta) / d).is_dir()]
        lineas.append(f"  {nombre}: " + (", ".join(partes) if partes else "nada que borrar"))
    return "\n".join(lineas)


def plan_respaldar(ctx: Contexto) -> str:
    destino = blog_service.settings().get("rutas/backup_dir") or "la carpeta de respaldos del gestor (QBLOG_BACKUP_DIR: archivo/backups-publicaciones)"
    lineas = [f"Respaldar los {len(ctx.sitios)} sitios (`main.sh backup`, opción 1; no se borran respaldos antiguos) en {destino}:"]
    lineas += [f"  {nombre} ({ruta})" for nombre, ruta, _e in ctx.sitios]
    return "\n".join(lineas)


def plan_crear_sitio(ctx: Contexto) -> str:
    partes = shlex.split(ctx.valor) if ctx.valor.strip() else []
    if not partes:
        return "Escribe el nombre del sitio nuevo (y, si quieres, su título entre comillas) en la pestaña Operación."
    nombre, titulo = partes[0], " ".join(partes[1:])
    return (f"Crear el sitio {nombre}{' («' + titulo + '»)' if titulo else ''} con `main.sh init-blog`: una carpeta nueva bajo los pubs del hub "
            "con _quarto.yml, index.qmd y posts/. No lo añade al registro _pubs/pubs.yml ni como submódulo: eso se hace a mano en el hub.")


# --------------------------------------------------------------------------------------------------- el catálogo
def _blog(ctx: Contexto) -> str:
    return ctx.sitio


def _partes(ctx: Contexto) -> list[str]:
    return shlex.split(ctx.valor) if ctx.valor.strip() else []


O = Operacion
OPERACIONES = (
    # --- Sitios
    O("render", "Renderizar", "`quarto render` del sitio actual por el gestor de blogs; la salida corre en el panel inferior y sus errores y avisos quedan en Problemas.",
      "sitios", aplicar=lambda c: blog_service.render(c.sitio), plan=plan_render, sobre_sitio=True),
    O("publicar", "Publicar", "Sin destino, `git push` detrás de la puerta R6 (Netlify despliega); con destino (Ajustes), `quarto publish`. Simula primero.",
      "sitios", simular=lambda c: blog_service.publish(c.sitio), aplicar=lambda c: blog_service.publish(c.sitio, aplicar=True), sobre_sitio=True, publica=True),
    O("commit", "Commit y push", "Confirma fuentes, contenido, _freeze/ y _site/ (nunca `git add .`) y empuja tras la puerta R6. Simula primero.",
      "sitios", simular=lambda c: blog_service.git_commit(c.sitio, c.valor.strip() or "Actualización"),
      aplicar=lambda c: blog_service.git_commit(c.sitio, c.valor.strip() or "Actualización", aplicar=True), sobre_sitio=True, publica=True,
      entrada="texto", etiqueta="mensaje del commit"),
    O("preview", "Preview", "El servidor local de Quarto del sitio actual (puerto en Ajustes); Esc lo detiene.",
      "sitios", simular=lambda c: blog_service.preview(c.sitio), sobre_sitio=True, larga=True),
    O("limpiar", "Limpiar artefactos", "Borra _site/, _freeze/ y .quarto del sitio actual; las fuentes no se tocan.",
      "sitios", aplicar=lambda c: blog_service.clean(c.sitio), plan=plan_limpiar, sobre_sitio=True, borra="_site/, _freeze/ y .quarto del sitio"),
    O("verificar", "Verificar", "`main.sh check`: la configuración del sitio actual (solo lee).", "sitios", simular=lambda c: blog_service.check(c.sitio), sobre_sitio=True),
    O("inspeccionar", "Inspeccionar", "`main.sh inspect`: la estructura del sitio actual (solo lee).", "sitios", simular=lambda c: blog_service.inspect(c.sitio), sobre_sitio=True),
    O("git_status", "Git status", "El estado de git del sitio actual (solo lee).", "sitios", simular=lambda c: blog_service.git_status(c.sitio), sobre_sitio=True),
    O("listar_entradas", "Listar entradas (CLI)", "`main.sh list-posts`: las entradas del sitio actual según el gestor (solo lee).", "sitios",
      simular=lambda c: blog_service.listar_posts(c.sitio), sobre_sitio=True),
    O("render_entrada", "Renderizar la entrada", "`main.sh render-post`: solo la entrada actual (pestaña Entradas o vista Entradas).", "sitios",
      aplicar=lambda c: blog_service.render_post(c.entrada), plan=plan_render_entrada, sobre_entrada=True),
    O("render_todos", "Renderizar todos", "`main.sh render-all`: los trece sitios, uno tras otro.", "sitios", aplicar=lambda c: blog_service.render_all(), plan=plan_render_todos),
    O("limpiar_todos", "Limpiar todos", "`main.sh clean-all`: _site/, _freeze/ y .quarto de todos los sitios.", "sitios",
      aplicar=lambda c: _con_entrada(blog_service.clean_all(), "s\n"), plan=plan_limpiar_todos, borra="_site/, _freeze/ y .quarto de TODOS los sitios"),
    O("estructura", "Verificar estructura", "`main.sh check-structure`: la integridad de todos los sitios (solo lee).", "sitios",
      simular=lambda c: blog_service.check_structure()),
    O("respaldar", "Respaldar todos", "`main.sh backup`, opción 1 (todos) sin borrar respaldos antiguos.", "sitios",
      aplicar=lambda c: blog_service.backup_todos(), plan=plan_respaldar),
    O("crear_sitio", "Crear sitio…", "`main.sh init-blog NOMBRE [TÍTULO]`: un sitio nuevo bajo los pubs del hub.", "sitios",
      aplicar=lambda c: blog_service.init_blog(*(_partes(c)[:1] + [" ".join(_partes(c)[1:])])) if _partes(c) else blog_service.init_blog("nuevo"),
      plan=plan_crear_sitio, entrada="texto", etiqueta="nombre del sitio y, opcional, su título"),
    # --- Entradas y metadatos
    O("plantilla", "Plantilla del Excel", "`create-template`: el Excel de metadatos desde los .qmd (del sitio actual si hay uno; si no, de todos). Escribe el Excel del repo, no los sitios.",
      "entradas", simular=lambda c: metadata_service.create_template(c.sitio, False)),
    O("plantilla_incremental", "Plantilla incremental", "`create-template --incremental`: añade al Excel las entradas que faltan.",
      "entradas", simular=lambda c: metadata_service.create_template(c.sitio, True)),
    O("diferencias", "Ver diferencias", "`find-differences`: el Excel frente a los .qmd (solo lee).", "entradas",
      simular=lambda c: metadata_service.find_differences(c.excel, c.sitio, c.filtro_ruta)),
    O("aplicar_excel", "Aplicar el Excel", "`update`: escribe en cada .qmd lo que difiere del Excel (una celda vacía borra el campo). Simula con --dry-run.",
      "entradas", simular=lambda c: metadata_service.update(c.excel, c.sitio, c.filtro_ruta, dry_run=True),
      aplicar=lambda c: metadata_service.update(c.excel, c.sitio, c.filtro_ruta, dry_run=False)),
    O("campos_nuevos", "Detectar campos nuevos", "`detect-new-fields`: campos YAML que el Excel no declara (solo lee).", "entradas",
      simular=lambda c: metadata_service.detect_new_fields()),
    O("crear_config", "Crear configuración", "`create-config`: metadata_config.yml del gestor de metadatos (escribe en el repo).", "entradas",
      simular=lambda c: metadata_service.create_config()),
    O("normalizar_tags", "Normalizar tags", "Minúsculas, sin tildes, espacios → `_`, sin duplicados; solo donde ya hay `tags`.", "entradas",
      simular=lambda c: metadata_service.normalize_tags(c.usar_excel, c.excel, blog=c.sitio, dry_run=True),
      aplicar=lambda c: metadata_service.normalize_tags(c.usar_excel, c.excel, blog=c.sitio, dry_run=False), admite_excel=True),
    O("reemplazar_tags", "Reemplazar tags…", "`replace-tags viejo:nuevo …`.", "entradas",
      simular=lambda c: metadata_service.replace_tags(c.usar_excel, c.excel, _partes(c), blog=c.sitio, dry_run=True),
      aplicar=lambda c: metadata_service.replace_tags(c.usar_excel, c.excel, _partes(c), blog=c.sitio, dry_run=False),
      entrada="texto", etiqueta="reemplazos «viejo:nuevo» separados por espacio", admite_excel=True),
    O("eliminar_tags", "Eliminar tags…", "`remove-tags tag …`.", "entradas",
      simular=lambda c: metadata_service.remove_tags(c.usar_excel, c.excel, _partes(c), blog=c.sitio, dry_run=True),
      aplicar=lambda c: metadata_service.remove_tags(c.usar_excel, c.excel, _partes(c), blog=c.sitio, dry_run=False),
      entrada="texto", etiqueta="tags a eliminar, separados por espacio", admite_excel=True),
    O("agregar_tags", "Agregar tags…", "`add-tags tag …` a las entradas que ya tienen `tags`.", "entradas",
      simular=lambda c: metadata_service.add_tags(c.usar_excel, c.excel, _partes(c), blog=c.sitio, dry_run=True),
      aplicar=lambda c: metadata_service.add_tags(c.usar_excel, c.excel, _partes(c), blog=c.sitio, dry_run=False),
      entrada="texto", etiqueta="tags a agregar, separados por espacio", admite_excel=True),
    O("stats_tags", "Estadísticas de tags", "`tag-stats --top 30` (solo lee).", "entradas", simular=lambda c: metadata_service.tag_stats(c.usar_excel, c.excel, top=30, blog=c.sitio), admite_excel=True),
    O("auditoria_tags", "Auditoría de tags", "`audit-tags --threshold 0.8` (solo lee).", "entradas", simular=lambda c: metadata_service.audit_tags(c.usar_excel, c.excel, umbral=0.8, blog=c.sitio), admite_excel=True),
    O("sync_fechas", "Sincronizar fechas", "`sync-dates`: `date` en ISO desde la carpeta de cada entrada.", "entradas",
      simular=lambda c: metadata_service.sync_dates(c.usar_excel, c.excel, blog=c.sitio, dry_run=True),
      aplicar=lambda c: metadata_service.sync_dates(c.usar_excel, c.excel, blog=c.sitio, dry_run=False), admite_excel=True),
    O("sync_pdf", "Sincronizar pdf-url", "`sync-pdf-urls`: `citation.pdf-url` donde ya existe (nunca lo crea).", "entradas",
      simular=lambda c: metadata_service.sync_pdf_urls(c.usar_excel, c.excel, blog=c.sitio, dry_run=True),
      aplicar=lambda c: metadata_service.sync_pdf_urls(c.usar_excel, c.excel, blog=c.sitio, dry_run=False), admite_excel=True),
    O("yaml_carpeta", "Formatear YAML (carpeta)", "Repara el bloque YAML de los .qmd de una carpeta, recursivo e idempotente.", "entradas",
      simular=lambda c: yaml_service.formatear_directorio(c.valor, True, True), aplicar=lambda c: yaml_service.formatear_directorio(c.valor, True, False),
      entrada="carpeta", etiqueta="carpeta con .qmd", defecto="sitio"),
    O("yaml_archivo", "Formatear YAML (archivo)", "Repara el bloque YAML de un .qmd.", "entradas",
      simular=lambda c: yaml_service.formatear_archivo(c.valor, True), aplicar=lambda c: yaml_service.formatear_archivo(c.valor, False),
      entrada="archivo", etiqueta="archivo .qmd", defecto="entrada"),
    # --- Índice del vault
    O("indice_sincronizar", "Sincronizar el índice", "Los enlaces por año de web/_indice/ hacia cada entrada (omite lo que ya apunta bien).", "indice",
      simular=lambda c: index_service.sincronizar(True), aplicar=lambda c: index_service.sincronizar(False)),
    O("indice_rotos", "Detectar rotos", "`--check-broken` (solo lee).", "indice", simular=lambda c: index_service.detectar_rotos()),
    O("indice_limpiar", "Eliminar rotos", "`--clean-broken`: borra los enlaces rotos y las carpetas de año vacías; F5 los lista.", "indice",
      simular=lambda c: index_service.detectar_rotos(), aplicar=lambda c: index_service.limpiar_rotos(), borra="los enlaces rotos de web/_indice/"),
    O("indice_resumen", "Resumen por año", "`--summary` (solo lee).", "indice", simular=lambda c: index_service.resumen()),
    # --- Índices de contenido
    O("contenido_generar", "Generar los índices del sitio", "Los _contenido_<subblog>.qmd del sitio actual (sobrescribe; un subblog sin entradas pierde el suyo).", "contenido",
      simular=lambda c: similar_service.generar(c.ruta, c.valor.strip(), "auto", True), aplicar=lambda c: similar_service.generar(c.ruta, c.valor.strip(), "auto", False),
      sobre_sitio=True, entrada="texto", etiqueta="URL base (vacío: la detecta)", borra="los _contenido_*.qmd de los subblogs que se quedaron sin entradas"),
)

_POR_ID = {o.id: o for o in OPERACIONES}


def _con_entrada(cmd: Command, texto: str) -> Command:
    cmd.stdin_data = texto
    return cmd


def todas() -> list[Operacion]:
    return list(OPERACIONES)


def operacion(id_: str) -> Operacion | None:
    return _POR_ID.get(id_)


def de_vista(vista: str) -> list[Operacion]:
    return [o for o in OPERACIONES if o.vista == vista]
