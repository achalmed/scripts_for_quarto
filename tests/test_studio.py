"""test_studio.py — Quarto Studio abre su ventana sin pantalla y encuentra sus backends en este mismo repo (sesión 9).

Vino de gui-suites/tests/test_studios.py (la parte de Quarto) cuando la GUI volvió aquí, el 2026-10-27:
- las entradas de los cinco backends existen y cuelgan de `backend/` de este repo, no de otro;
- `gui_comun` (lo común de los studios) se importa de `core/py-common`;
- la ventana principal se abre y se cierra con `QT_QPA_PLATFORM=offscreen` y `studio/main.py --smoke` sale con 0.
Cada GUI corre en un proceso aparte con `XDG_CONFIG_HOME` temporal: QSettings no toca la configuración del autor.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import RAIZ_REPO

STUDIO = RAIZ_REPO / "studio"
requiere_pyside = pytest.mark.skipif(importlib.util.find_spec("PySide6") is None, reason="sin PySide6")

ENTRADAS = """
import sys, json; sys.path.insert(0, sys.argv[1])
from quarto_app.services import paths
import gui_comun
print(json.dumps({"gui_comun": gui_comun.__file__,
                  **{n: str(getattr(paths, n)()) for n in ("blogs_manager", "metadata_manager", "metadata_config",
                                                          "yaml_formatter", "pub_index_symlink", "generador_similar")}}))
"""

ABRIR = """
import sys; sys.path.insert(0, sys.argv[1])
from quarto_app.application import crear_aplicacion
from quarto_app.ui.main_window import MainWindow
app = crear_aplicacion([])
w = MainWindow(); w.show(); app.processEvents()
print(w.windowTitle()); w.close(); app.processEvents()
"""


def test_backends_en_este_repo(workspace):
    r = subprocess.run([sys.executable, "-c", ENTRADAS, str(STUDIO)], env=workspace.env, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    s = json.loads(r.stdout.strip().splitlines()[-1])
    assert s.pop("gui_comun").endswith("core/py-common/gui_comun/__init__.py")
    for nombre, ruta in s.items():
        p = (RAIZ_REPO / "backend").resolve()
        assert p in Path(ruta).resolve().parents, f"{nombre}: {ruta} no cuelga de {p}"
        assert Path(ruta).is_file(), f"{nombre}: no existe {ruta}"


def test_ningun_backend_por_core_env():
    """Los backends ya no se buscan por SCRIPTS_QUARTO (retirada de core/env): ninguna línea la cita."""
    malos = [f"{f.relative_to(RAIZ_REPO)}:{n}" for f in STUDIO.rglob("*.py")
             for n, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if "SCRIPTS_QUARTO" in linea]
    assert not malos, malos


@requiere_pyside
def test_abre_y_cierra_su_ventana(workspace):
    r = subprocess.run([sys.executable, "-c", ABRIR, str(STUDIO)], env=workspace.env, capture_output=True,
                       text=True, timeout=90)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    assert "Studio" in r.stdout


@requiere_pyside
def test_main_smoke(workspace):
    r = subprocess.run([sys.executable, str(STUDIO / "main.py"), "--smoke"], env=workspace.env, capture_output=True,
                       text=True, timeout=90, cwd=workspace.base)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
