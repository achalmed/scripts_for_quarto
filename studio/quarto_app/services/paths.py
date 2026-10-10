"""
quarto_app/services/paths.py — Localización de los scripts backend y del directorio Documents.

La raíz (DOCS_ROOT), la carpeta del hub (INDEX_DIR) y la de los backends (SCRIPTS_QUARTO) salen de
core/env.py a través de comun.rutas, igual que en los scripts Bash (que cargan core/env.sh), de modo que la
GUI y el backend siempre coincidan. Ninguna ruta es relativa a este archivo salvo los recursos propios.
"""

from __future__ import annotations

from pathlib import Path

from comun import rutas


def core_env():
    """El módulo core/env.py del workspace (lo carga comun.rutas)."""
    return rutas.core_env()


def detectar_docs_dir() -> Path:
    """~/Documents: DOCS_ROOT de core/env (respeta un DOCS_ROOT previo del entorno)."""
    return Path(core_env().DOCS_ROOT)


def pubs_registro():
    """core/py-common/pubs.py: los blogs por `_pubs/pubs.yml` del hub, nunca por el prefijo de carpeta (ola 6, 6f)."""
    import importlib.util
    ruta = Path(core_env().__file__).resolve().parent / "py-common" / "pubs.py"
    spec = importlib.util.spec_from_file_location("core_pubs", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hub_dir(docs_dir: Path | None = None) -> Path:
    """Carpeta del hub (repo website-achalma): INDEX_DIR de core/env, trasladada a `docs_dir` si se da otra raíz."""
    env = core_env()
    if docs_dir is None:
        return Path(env.INDEX_DIR)
    return Path(docs_dir) / Path(env.INDEX_DIR).relative_to(env.DOCS_ROOT)


# --- Entradas (entry points) de cada herramienta backend --------------------

def blogs_manager() -> Path:
    return rutas.backend("quarto", "blogs_manager") / "main.sh"


def metadata_manager() -> Path:
    return rutas.backend("quarto", "metadata_manager") / "main.py"


def metadata_config() -> Path:
    return rutas.backend("quarto", "metadata_manager") / "metadata_config.yml"


def yaml_formatter() -> Path:
    return rutas.backend("quarto", "format_yaml") / "fix_qmd_files.py"


def pub_index_symlink() -> Path:
    return rutas.backend("quarto", "pub_index_symlink") / "main.sh"


def pub_index_logs_dir() -> Path:
    return rutas.backend("quarto", "pub_index_symlink") / "logs"


def generador_similar() -> Path:
    return rutas.backend("quarto", "generador_similar") / "main.sh"


def recursos_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources"


def icono(nombre: str) -> str:
    """Ruta a un icono SVG del tema de recursos."""
    return str(recursos_dir() / "icons" / f"{nombre}.svg")


def tema_qss(nombre: str) -> Path:
    return recursos_dir() / "themes" / f"{nombre}.qss"
