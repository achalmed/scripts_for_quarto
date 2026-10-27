"""quarto_app — Quarto Studio, aplicación de escritorio para gestionar la familia de blogs Quarto.

Frontend Qt (PySide6) desacoplado: los scripts de `backend/` de este mismo repo (scripts-quarto, repo
scripts_for_quarto) actúan como motor y se invocan a través de la capa de servicios. Al importarse pone
`core/py-common` en `sys.path` (subiendo carpetas hasta hallar `core/`, como los envoltorios del logger): ahí vive
`gui_comun`, lo que comparten los tres studios.
"""

import sys as _sys
from pathlib import Path as _Path

_d = _Path(__file__).resolve().parent
while _d != _d.parent and not (_d / "core" / "py-common" / "gui_comun").is_dir():
    _d = _d.parent
if not (_d / "core" / "py-common" / "gui_comun").is_dir():
    raise ImportError(f"no encuentro core/py-common/gui_comun subiendo desde {__file__}")
if str(_d / "core" / "py-common") not in _sys.path:
    _sys.path.append(str(_d / "core" / "py-common"))
del _d

APP_NAME = "Quarto Studio"
APP_VERSION = "1.0.0"
ORG_NAME = "achalma"
ORG_DOMAIN = "achalmaedison.netlify.app"
