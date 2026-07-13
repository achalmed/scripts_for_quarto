"""
metadata_service.py — Servicio del Metadata Manager (script_metadata_manager).

Envuelve los comandos no interactivos del CLI Python existente. Se invoca
como subproceso (no import) para: 1) mantener el desacoplamiento, 2) mostrar
en consola exactamente la misma salida que en terminal, 3) no bloquear la UI.

Los comandos interactivos del script (sync-article, sync-batch) NO se
exponen: su flujo se cubre en la GUI con find-differences + update filtrado.
"""

from __future__ import annotations

from pathlib import Path

from app.services import paths
from app.services.command import Command
from app.settings import settings


def _cmd(args: list[str], descripcion: str) -> Command:
    st = settings()
    return Command(
        programa=st.get("rutas/python"),
        args=[str(paths.metadata_manager()), *args],
        cwd=str(paths.metadata_manager().parent),
        descripcion=descripcion,
    )


def _filtros(blog: str = "", filtro_ruta: str = "", dry_run: bool = False) -> list[str]:
    extra: list[str] = []
    if blog:
        extra += ["--blog", blog]
    if filtro_ruta:
        extra += ["--filter-path", filtro_ruta]
    if dry_run:
        extra += ["--dry-run"]
    return extra


def _config_args() -> list[str]:
    cfg = paths.metadata_config()
    return ["--config", str(cfg)] if cfg.is_file() else []


# --- Configuración y plantilla ---------------------------------------------------

def create_config() -> Command:
    return _cmd(["create-config", str(settings().docs_dir())], "Crear metadata_config.yml")


def create_template(blog: str = "", incremental: bool = False) -> Command:
    args = ["create-template", str(settings().docs_dir()), *_config_args()]
    if blog:
        args += ["--blog", blog]
    if incremental:
        args.append("--incremental")
    desc = "Generar plantilla Excel" + (" (incremental)" if incremental else "")
    return _cmd(args, desc)


# --- Sincronización Excel ↔ archivos ---------------------------------------------

def update(excel: str, blog: str = "", filtro_ruta: str = "", dry_run: bool = False) -> Command:
    args = ["update", str(settings().docs_dir()), excel, *_config_args(),
            *_filtros(blog, filtro_ruta, dry_run)]
    return _cmd(args, "Aplicar Excel → archivos .qmd" + (" (simulación)" if dry_run else ""))


def find_differences(excel: str, blog: str = "", filtro_ruta: str = "", max_show: int = 10) -> Command:
    args = ["find-differences", str(settings().docs_dir()), excel, *_config_args(),
            *_filtros(blog, filtro_ruta), "--max-show", str(max_show)]
    return _cmd(args, "Ver diferencias Excel vs archivos")


def detect_new_fields() -> Command:
    return _cmd(["detect-new-fields", str(settings().docs_dir()), *_config_args()],
                "Detectar campos YAML no declarados")


def add_columns(excel: str, campos: list[str], dry_run: bool = False) -> Command:
    args = ["add-columns", str(settings().docs_dir()), excel, *campos, *_config_args()]
    if dry_run:
        args.append("--dry-run")
    return _cmd(args, f"Agregar columnas al Excel: {', '.join(campos)}")


# --- Tags (destino: Excel .xlsx o directorio de blogs) ----------------------------

def _destino(usar_excel: bool, excel: str) -> str:
    return excel if usar_excel else str(settings().docs_dir())


def _tag_cmd(nombre: str, destino: str, extra: list[str], descripcion: str,
             blog: str = "", filtro_ruta: str = "", dry_run: bool = False) -> Command:
    args = [nombre, destino, *extra, *_filtros(blog, filtro_ruta, dry_run)]
    if not Path(destino).suffix:  # modo archivos → pasar config
        args += _config_args()
    return _cmd(args, descripcion)


def normalize_tags(usar_excel: bool, excel: str, **kw) -> Command:
    return _tag_cmd("normalize-tags", _destino(usar_excel, excel), [], "Normalizar tags", **kw)


def replace_tags(usar_excel: bool, excel: str, reemplazos: list[str], **kw) -> Command:
    return _tag_cmd("replace-tags", _destino(usar_excel, excel), reemplazos,
                    f"Reemplazar tags: {', '.join(reemplazos)}", **kw)


def remove_tags(usar_excel: bool, excel: str, tags: list[str], **kw) -> Command:
    return _tag_cmd("remove-tags", _destino(usar_excel, excel), tags,
                    f"Eliminar tags: {', '.join(tags)}", **kw)


def add_tags(usar_excel: bool, excel: str, tags: list[str], **kw) -> Command:
    return _tag_cmd("add-tags", _destino(usar_excel, excel), tags,
                    f"Agregar tags: {', '.join(tags)}", **kw)


def tag_stats(usar_excel: bool, excel: str, top: int = 20, blog: str = "") -> Command:
    return _tag_cmd("tag-stats", _destino(usar_excel, excel), ["--top", str(top)],
                    "Estadísticas de tags", blog=blog)


def audit_tags(usar_excel: bool, excel: str, umbral: float = 0.8, blog: str = "") -> Command:
    return _tag_cmd("audit-tags", _destino(usar_excel, excel), ["--threshold", str(umbral)],
                    "Auditoría de taxonomía de tags", blog=blog)


# --- Sincronización desde la ruta -------------------------------------------------

def sync_dates(usar_excel: bool, excel: str, **kw) -> Command:
    return _tag_cmd("sync-dates", _destino(usar_excel, excel), [],
                    "Sincronizar fechas desde carpetas", **kw)


def sync_pdf_urls(usar_excel: bool, excel: str, **kw) -> Command:
    return _tag_cmd("sync-pdf-urls", _destino(usar_excel, excel), [],
                    "Sincronizar citation.pdf-url", **kw)
