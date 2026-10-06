"""
paths.py — Localización de los scripts backend y del directorio Documents.

La raíz (DOCS_ROOT) y la carpeta del hub (INDEX_DIR) salen de core/env.py,
igual que en los scripts Bash (que cargan core/env.sh), de modo que la GUI y
el backend siempre coincidan.
"""

from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path

# app/services/paths.py → raíz del repositorio (scripts_quarto_studio)
_SCRIPTS_ROOT = Path(__file__).resolve().parents[3]

# Los script_* viven en backend/
_BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"


def scripts_root() -> Path:
    """Raíz del repositorio scripts_quarto_studio."""
    return _SCRIPTS_ROOT


def backend_dir() -> Path:
    """Directorio backend/ (donde viven los script_*)."""
    return _BACKEND_DIR


@lru_cache(maxsize=1)
def core_env():
    """El módulo core/env.py del workspace: se sube desde este archivo hasta hallarlo."""
    d = Path(__file__).resolve()
    while d != d.parent and not (d / "core" / "env.py").is_file():
        d = d.parent
    spec = importlib.util.spec_from_file_location("core_env", d / "core" / "env.py")
    env = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(env)
    return env


def detectar_docs_dir() -> Path:
    """~/Documents: DOCS_ROOT de core/env (respeta un DOCS_ROOT previo del entorno)."""
    return Path(core_env().DOCS_ROOT)


def hub_dir(docs_dir: Path | None = None) -> Path:
    """Carpeta del hub (repo website-achalma): INDEX_DIR de core/env, trasladada a `docs_dir` si se da otra raíz."""
    env = core_env()
    if docs_dir is None:
        return Path(env.INDEX_DIR)
    return Path(docs_dir) / Path(env.INDEX_DIR).relative_to(env.DOCS_ROOT)


# --- Entradas (entry points) de cada herramienta backend --------------------

def blogs_manager() -> Path:
    return backend_dir() / "script_blogs_manager" / "main.sh"


def metadata_manager() -> Path:
    return backend_dir() / "script_metadata_manager" / "main.py"


def metadata_config() -> Path:
    return backend_dir() / "script_metadata_manager" / "metadata_config.yml"


def yaml_formatter() -> Path:
    return backend_dir() / "script_format_yaml" / "fix_qmd_files.py"


def pub_index_symlink() -> Path:
    return backend_dir() / "script_pub_index_symlink" / "main.sh"


def pub_index_logs_dir() -> Path:
    return backend_dir() / "script_pub_index_symlink" / "logs"


def generador_similar() -> Path:
    return backend_dir() / "script_generador_publicacion_similar" / "main.sh"


def recursos_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources"


def icono(nombre: str) -> str:
    """Ruta a un icono SVG del tema de recursos."""
    return str(recursos_dir() / "icons" / f"{nombre}.svg")


def tema_qss(nombre: str) -> Path:
    return recursos_dir() / "themes" / f"{nombre}.qss"
