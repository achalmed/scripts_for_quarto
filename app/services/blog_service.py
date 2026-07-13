"""
blog_service.py — Servicio del Blog Manager (script_blogs_manager/main.sh).

Construye objetos Command para cada subcomando del script. Reutiliza el
backend Bash tal cual: la GUI solo aporta los argumentos que el modo CLI
ya acepta. Los flujos exclusivamente interactivos del script (new-post,
backup con menú) se cubren con diálogos Qt + post_service / stdin.
"""

from __future__ import annotations

from app.services import paths
from app.services.command import Command
from app.settings import settings


def _cmd(args: list[str], descripcion: str, stdin_data: str | None = None) -> Command:
    st = settings()
    return Command(
        programa="bash",
        args=[str(paths.blogs_manager()), *args],
        cwd=str(st.docs_dir()),
        stdin_data=stdin_data,
        descripcion=descripcion,
        entorno={"QBLOG_DOCS_DIR": str(st.docs_dir())},
    )


# --- Operaciones sobre un blog ------------------------------------------------

def listar() -> Command:
    return _cmd(["list"], "Listar blogs")


def render(blog: str) -> Command:
    return _cmd(["render", blog], f"Renderizar {blog}")


def preview(blog: str, puerto: int | None = None) -> Command:
    puerto = puerto or settings().get_int("blogs/preview_port")
    return _cmd(["preview", blog, str(puerto)], f"Preview de {blog} (puerto {puerto})")


def clean(blog: str) -> Command:
    return _cmd(["clean", blog], f"Limpiar artefactos de {blog}")


def publish(blog: str, destino: str | None = None) -> Command:
    destino = destino or settings().get("blogs/publish_target")
    return _cmd(["publish", blog, destino], f"Publicar {blog} → {destino}")


def check(blog: str) -> Command:
    return _cmd(["check", blog], f"Verificar {blog}")


def inspect(blog: str) -> Command:
    return _cmd(["inspect", blog], f"Inspeccionar {blog}")


def listar_posts(blog: str) -> Command:
    return _cmd(["list-posts", blog], f"Listar posts de {blog}")


def render_post(ruta_post: str) -> Command:
    return _cmd(["render-post", ruta_post], f"Renderizar post {ruta_post}")


# --- Operaciones por lotes ------------------------------------------------------

def render_all() -> Command:
    return _cmd(["render-all"], "Renderizar TODOS los blogs")


def clean_all() -> Command:
    return _cmd(["clean-all"], "Limpiar TODOS los blogs")


def check_structure() -> Command:
    return _cmd(["check-structure"], "Verificar estructura de todos los blogs")


# --- Git -----------------------------------------------------------------------

def git_init(blog: str) -> Command:
    return _cmd(["git-init", blog], f"Inicializar git en {blog}")


def git_status(blog: str) -> Command:
    return _cmd(["git-status", blog], f"Git status de {blog}")


def git_commit(blog: str, mensaje: str) -> Command:
    return _cmd(["git-commit", blog, mensaje], f"Commit+push en {blog}")


# --- Creación / mantenimiento ----------------------------------------------------

def init_blog(nombre: str, titulo: str = "") -> Command:
    args = ["init-blog", nombre]
    if titulo:
        args.append(titulo)
    return _cmd(args, f"Crear blog {nombre}")


def backup_todos() -> Command:
    """
    Backup de todos los blogs. El script es interactivo (menú 1-3 + limpieza
    s/n): se alimentan las respuestas por stdin — opción 1 (todos) y "n"
    (no borrar backups antiguos, decisión conservadora).
    """
    return _cmd(["backup"], "Backup de todos los blogs", stdin_data="1\nn\n")


def convertir(archivo: str, formato: str = "html") -> Command:
    return _cmd(["convert", archivo, formato], f"Convertir {archivo} → {formato}")
