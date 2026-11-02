"""tests/studio/conftest.py — utilidades de las pruebas de Quarto Studio (fase 5 QML, 2026-11-02).

El temporal va al disco (XDG_CACHE_HOME), no a /tmp (tmpfs: es RAM). Nada toca el hub `web` ni los pubs reales (Netlify
despliega con cada push): cada prueba parte de la familia de sitios de muestra de `studio/muestra.py` (un hub y tres pubs
con git y remotos bare locales, cada uno en un estado; `_indice/`; un fragmento; un Excel si hay openpyxl) en una carpeta
temporal, y el entorno (`core/env` respeta DOCS_ROOT e INDEX_DIR) apunta ahí.

Dos clases de prueba:
- en proceso (servicios, modelos, controladores): con el binding del Python que corre pytest; la muestra es una por
  sesión y DOCS_ROOT/INDEX_DIR se fijan antes de que nadie cargue core/env; QSettings apunta a un temporal;
- en un proceso hijo (cada QML, la ventana entera, `--smoke`): con el Python del sistema (/usr/bin/python3; el .venv del
  studio si existe), el único cuyo Qt trae Kirigami, y HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME temporales.

    tests/run.sh            # = python3 -m pytest tests/studio --basetemp ~/.cache/pytest/quarto-studio-studio -p no:cacheprovider
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
STUDIO = REPO / "studio"
BASETEMP = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "pytest" / "quarto-studio-studio" / "basetemp"

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

import muestra as muestra_mod  # noqa: E402

HAY_BINDING = importlib.util.find_spec("PySide6") is not None or importlib.util.find_spec("PyQt6") is not None
requiere_binding = pytest.mark.skipif(not HAY_BINDING, reason="sin PySide6 ni PyQt6")
requiere_quarto = pytest.mark.skipif(shutil.which("quarto") is None, reason="sin quarto")

_VARIABLES_CORE = ("DOCS_ROOT", "INDEX_DIR", "CORE_DIR", "META_DIR", "NOTES_DIR", "WRITING_DIR", "CLASS_DIR", "RESPALDOS_DIR", "GIT_DIR",
                   "GIT_WORK_TREE", "QBLOG_WEBSITE_DIR", "QBLOG_PUBS_SUBDIR", "PUBINDEX_PUBS_SUBDIR", "PUBS_SUBDIR", "QBLOG_BACKUP_DIR")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.basetemp:
        return
    args = [Path(a.split("::")[0]).resolve() for a in (config.args or [])]
    if args and all(REPO in a.parents or a == REPO for a in args):
        BASETEMP.parent.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(BASETEMP)


def _python_del_sistema() -> str | None:
    venv = REPO / ".venv" / "bin" / "python"
    for candidato in (venv, Path("/usr/bin/python3")):
        if not candidato.is_file():
            continue
        r = subprocess.run([str(candidato), "-c", "import importlib.util as u; print(bool(u.find_spec('PySide6') or u.find_spec('PyQt6')))"],
                           capture_output=True, text=True)
        if r.stdout.strip() == "True":
            return str(candidato)
    return None


PYTHON_SISTEMA = _python_del_sistema()
requiere_sistema = pytest.mark.skipif(PYTHON_SISTEMA is None, reason="sin binding de Qt en /usr/bin/python3 (Kirigami)")


@pytest.fixture(scope="session")
def muestra_sesion(tmp_path_factory):
    """La familia de muestra de las pruebas en proceso: una por sesión, y el entorno del proceso apunta a ella antes de
    que nadie cargue core/env (DOCS_ROOT, INDEX_DIR)."""
    m = muestra_mod.crear(tmp_path_factory.mktemp("muestra") / "familia")
    for k in _VARIABLES_CORE:
        os.environ.pop(k, None)
    os.environ.update({k: v for k, v in m.entorno.items() if k not in ("HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME")})
    return m


@pytest.fixture
def muestra(tmp_path):
    """Una familia de muestra nueva por prueba (para los procesos hijos y para lo que escribe)."""
    return muestra_mod.crear(tmp_path / "familia")


@pytest.fixture
def muestra_renderizable():
    """Una familia de muestra en /var/tmp (disco, no RAM): Quarto omite los archivos de un proyecto cuya ruta pasa por una
    carpeta oculta (`~/.cache/pytest/…`), así que un `quarto render` real necesita una ruta sin componentes `.x`."""
    base = Path("/var/tmp") / "quarto-studio-pruebas"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        pytest.skip("/var/tmp no es escribible")
    import tempfile
    carpeta = Path(tempfile.mkdtemp(prefix="familia-", dir=base))
    try:
        yield muestra_mod.crear(carpeta / "familia")
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)


@pytest.fixture
def ajustes_temporales(tmp_path, monkeypatch):
    from gui_comun.qt import QSettings
    QSettings.setPath(QSettings.Format.NativeFormat, QSettings.Scope.UserScope, str(tmp_path / "config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return tmp_path


def entorno_gui(tmp_path: Path, muestra, **extra: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in _VARIABLES_CORE}
    env.update({"QT_QPA_PLATFORM": "offscreen", "PYTHONDONTWRITEBYTECODE": "1"})
    env.update(muestra.entorno)
    env["QUARTO_STUDIO_EXCEL"] = str(muestra.excel or "")
    env.update(extra)
    return env


def correr_python(guion: str, env: dict, *args: str, plazo: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run([PYTHON_SISTEMA or sys.executable, "-c", guion, str(STUDIO), *args], env=env, capture_output=True, text=True, timeout=plazo)


@pytest.fixture(scope="session")
def app(muestra_sesion):
    from gui_comun.qt import QGuiApplication
    QGuiApplication.setOrganizationName("quarto-studio-pruebas")
    QGuiApplication.setApplicationName("quarto-studio-pruebas")
    instancia = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
    yield instancia
