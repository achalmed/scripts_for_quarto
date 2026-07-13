"""
paths.py — Localización de los scripts backend y del directorio Documents.

Replica la autodetección de los scripts Bash (subir desde la ubicación
propia hasta encontrar pub_* o website-achalma), de modo que la GUI y el
backend siempre coincidan.
"""

from __future__ import annotations

from pathlib import Path

# quarto_studio/app/services/paths.py → raíz del repositorio
_SCRIPTS_ROOT = Path(__file__).resolve().parents[3]

# Los script_* viven en quarto_studio/backend/
_BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"


def scripts_root() -> Path:
    """Raíz del repositorio scripts_quarto_studio."""
    return _SCRIPTS_ROOT


def backend_dir() -> Path:
    """Directorio quarto_studio/backend (donde viven los script_*)."""
    return _BACKEND_DIR


def detectar_docs_dir() -> Path:
    """
    Autodetecta ~/Documents subiendo desde scripts_for_quarto hasta encontrar
    un directorio que contenga proyectos pub_* o website-achalma.
    """
    actual = scripts_root()
    for candidato in [actual, *actual.parents]:
        if (candidato / "website-achalma").is_dir() or any(candidato.glob("pub_*")):
            return candidato
    # Último recurso razonable
    return Path.home() / "Documents"


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
