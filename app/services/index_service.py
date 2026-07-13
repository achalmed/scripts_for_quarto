"""
index_service.py — Servicio del índice de symlinks (script_pub_index_symlink).
"""

from __future__ import annotations

from app.services import paths
from app.services.command import Command
from app.settings import settings


def _cmd(args: list[str], descripcion: str, stdin_data: str | None = None) -> Command:
    st = settings()
    return Command(
        programa="bash",
        args=[str(paths.pub_index_symlink()), *args],
        cwd=str(st.docs_dir()),
        stdin_data=stdin_data,
        descripcion=descripcion,
        entorno={"PUBINDEX_DOCS_DIR": str(st.docs_dir())},
    )


def sincronizar(dry_run: bool = False) -> Command:
    args = ["--dry-run"] if dry_run else []
    return _cmd(args, "Sincronizar symlinks de '04 index'" + (" (simulación)" if dry_run else ""))


def detectar_rotos() -> Command:
    return _cmd(["--check-broken"], "Detectar symlinks rotos")


def limpiar_rotos() -> Command:
    """El script pide confirmación (s/n): la GUI ya confirmó, se responde 's'."""
    return _cmd(["--clean-broken"], "Eliminar symlinks rotos", stdin_data="s\n")


def resumen() -> Command:
    return _cmd(["--summary"], "Resumen del índice por año")
