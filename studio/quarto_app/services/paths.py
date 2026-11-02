"""
quarto_app/services/paths.py — Localización de los scripts backend y del directorio Documents.

La raíz (DOCS_ROOT) y la carpeta del hub (INDEX_DIR) salen de core/env.py a través de gui_comun.rutas, igual que
en los scripts Bash (que cargan core/env.sh), de modo que la GUI y el backend siempre coincidan. Los backends
son de este mismo repo: cuelgan de `backend/`, junto a `studio/` (sesión 9, 2026-10-27); si un script se mueve,
se toca `BACKENDS` y nada más.
"""

from __future__ import annotations

from pathlib import Path

from gui_comun import rutas

REPO = Path(__file__).resolve().parents[3]          # quarto-studio (studio/quarto_app/services/paths.py)
BACKEND_DIR = REPO / "backend"
BACKENDS = {
    "blogs_manager": "script_blogs_manager",
    "metadata_manager": "script_metadata_manager",
    "format_yaml": "script_format_yaml",
    "pub_index_symlink": "script_pub_index_symlink",
    "generador_similar": "script_generador_publicacion_similar",
}


def backend(clave: str) -> Path:
    """Carpeta de un backend: `backend("blogs_manager")` → `quarto-studio/backend/script_blogs_manager`."""
    return BACKEND_DIR / BACKENDS[clave]


def core_env():
    """El módulo core/env.py del workspace (lo carga gui_comun.rutas)."""
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
    return backend("blogs_manager") / "main.sh"


def metadata_manager() -> Path:
    return backend("metadata_manager") / "main.py"


def metadata_config() -> Path:
    return backend("metadata_manager") / "metadata_config.yml"


def yaml_formatter() -> Path:
    return backend("format_yaml") / "fix_qmd_files.py"


def pub_index_symlink() -> Path:
    return backend("pub_index_symlink") / "main.sh"


def pub_index_logs_dir() -> Path:
    return backend("pub_index_symlink") / "logs"


def generador_similar() -> Path:
    return backend("generador_similar") / "main.sh"


def recursos_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "recursos"


def venv_dir() -> Path:
    """El entorno del studio (`<repo>/.venv`, creado con `/usr/bin/python3 -m venv --system-site-packages`): ahí viven
    `openpyxl` y `pandas`, que el Python del sistema no trae (rediseño Q7)."""
    return REPO / ".venv"


def interprete() -> str:
    """El Python con el que corren los backends de Python y el propio studio: el del `.venv` si existe; si no, el
    del sistema (los backends que necesiten `pandas` u `openpyxl` fallarán y la ventana dice qué crear)."""
    candidato = venv_dir() / "bin" / "python"
    return str(candidato) if candidato.is_file() else "/usr/bin/python3"


def orden_crear_venv() -> str:
    """La orden que crea el entorno del studio (se muestra, no se corre sola)."""
    return f"/usr/bin/python3 -m venv --system-site-packages {venv_dir()} && {venv_dir()}/bin/pip install openpyxl pandas pyyaml"


def excel_por_defecto() -> Path:
    return metadata_manager().parent / "excel_databases" / "quarto_metadata.xlsx"


def indice_dir(hub: Path | None = None) -> Path:
    """`web/_indice/`: los enlaces por año del vault que mantiene pub_index_symlink."""
    return (hub or hub_dir()) / "_indice"

