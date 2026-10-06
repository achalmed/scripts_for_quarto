"""conftest.py — fixtures comunes de las pruebas de scripts_quarto_studio (ola 4, Q1b y Q2).

Ninguna prueba toca el hub `04 index` ni los `_pubs` reales (Netlify despliega con cada push): todo ocurre en un
workspace de fixture bajo el directorio temporal de pytest (en disco, por `--basetemp`), con un `core/` que
apunta al real (solo se lee), un hub de juguete con una copia de la puerta R6, un `quarto` falso que anota sus
llamadas y, para git, un remoto «bare» local.

    python3 -m pytest tests --basetemp ~/.cache/pytest/quarto-ola4 -p no:cacheprovider
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

RAIZ_REPO = Path(__file__).resolve().parents[1]
BACKEND = RAIZ_REPO / "backend"


def _cargar_core_env():
    d = RAIZ_REPO
    while d != d.parent and not (d / "core" / "env.py").exists():
        d = d.parent
    if not (d / "core" / "env.py").exists():
        return None
    spec = importlib.util.spec_from_file_location("core_env_pruebas", d / "core" / "env.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CORE_ENV = _cargar_core_env()
CORE_DIR = Path(CORE_ENV.CORE_DIR) if CORE_ENV else None
PUERTA_REAL = Path(CORE_ENV.INDEX_DIR) / "scripts" / "puerta-r6.sh" if CORE_ENV else None

# Variables de core/env que el entorno del autor podría traer exportadas y que apuntarían a lo real.
_VARIABLES_CORE = ("DOCS_ROOT", "INDEX_DIR", "CORE_DIR", "META_DIR", "NOTES_DIR", "WRITING_DIR", "CLASS_DIR",
                   "QBLOG_WEBSITE_DIR", "QBLOG_PUBS_SUBDIR", "PUBINDEX_PUBS_SUBDIR", "PUBS_SUBDIR",
                   "QBLOG_BACKUP_DIR", "RESPALDOS_DIR", "GIT_DIR", "GIT_WORK_TREE")

QUARTO_FALSO = """#!/usr/bin/env bash
# quarto falso de las pruebas: responde a --version y anota cualquier otra llamada.
if [[ "${1:-}" == "--version" ]]; then echo "0.0.0-prueba"; exit 0; fi
echo "$*" >> "$QUARTO_REGISTRO"
"""


@dataclass
class Workspace:
    raiz: Path          # DOCS_ROOT de fixture
    hub: Path           # INDEX_DIR de fixture
    pubs: Path          # <hub>/_pubs
    base: Path          # carpeta temporal de la prueba
    registro_quarto: Path
    env: dict

    def git(self, cwd: Path, *args: str, fecha: str | None = None) -> str:
        env = dict(self.env)
        if fecha:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = fecha
        r = subprocess.run(["git", "-C", str(cwd), *args], env=env, capture_output=True, text=True)
        assert r.returncode == 0, f"git {' '.join(args)}: {r.stderr}"
        return r.stdout.strip()

    def correr(self, *args: str, cwd: Path | None = None, entrada: str | None = None,
               plazo: int = 60) -> subprocess.CompletedProcess:
        return subprocess.run(list(args), cwd=str(cwd or self.base), env=self.env, input=entrada or "",
                              capture_output=True, text=True, timeout=plazo)


def instantanea(*raices: Path) -> dict[str, tuple[int, int]]:
    """Listado + mtime + tamaño de todo lo que cuelga de las raíces (incluido .git), sin seguir enlaces."""
    vista: dict[str, tuple[int, int]] = {}
    for raiz in raices:
        if not raiz.exists():
            continue
        for d, subdirs, archivos in os.walk(raiz):
            if "__pycache__" in subdirs:
                subdirs.remove("__pycache__")
            for nombre in archivos + subdirs:
                p = Path(d) / nombre
                st = p.lstat()
                vista[str(p)] = (st.st_mtime_ns, st.st_size if not p.is_dir() else 0)
    return vista


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    if CORE_DIR is None or not (CORE_DIR / "env.sh").is_file():
        pytest.skip("sin core/ del workspace: las suites no arrancan")
    raiz = tmp_path / "docs"
    hub = raiz / "04 index"
    pubs = hub / "_pubs"
    pubs.mkdir(parents=True)
    (raiz / "core").symlink_to(CORE_DIR, target_is_directory=True)   # core/ real, solo se lee
    (hub / "scripts").mkdir()
    if PUERTA_REAL and PUERTA_REAL.is_file():
        shutil.copy2(PUERTA_REAL, hub / "scripts" / "puerta-r6.sh")

    binarios = tmp_path / "bin"
    binarios.mkdir()
    quarto = binarios / "quarto"
    quarto.write_text(QUARTO_FALSO)
    quarto.chmod(0o755)

    hogar = tmp_path / "home"
    hogar.mkdir()
    gitconfig = tmp_path / "gitconfig"
    gitconfig.write_text("[user]\n\tname = Prueba\n\temail = prueba@example.invalid\n"
                         "[init]\n\tdefaultBranch = main\n[advice]\n\tdetachedHead = false\n")

    env = {k: v for k, v in os.environ.items() if k not in _VARIABLES_CORE and not k.startswith("GIT_")}
    env.update({
        "DOCS_ROOT": str(raiz),
        "INDEX_DIR": str(hub),
        "HOME": str(hogar),
        "XDG_STATE_HOME": str(tmp_path / "state"),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "RESPALDOS_DIR": str(tmp_path / "respaldos"),
        "PATH": f"{binarios}{os.pathsep}{os.environ.get('PATH', '')}",
        "QUARTO_REGISTRO": str(tmp_path / "quarto.log"),
        "GIT_CONFIG_GLOBAL": str(gitconfig),
        "GIT_CONFIG_NOSYSTEM": "1",
        "QT_QPA_PLATFORM": "offscreen",
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C.UTF-8",
    })
    return Workspace(raiz=raiz, hub=hub, pubs=pubs, base=tmp_path,
                     registro_quarto=tmp_path / "quarto.log", env=env)


FECHA_PASADA = "2026-01-01T10:00:00+00:00"


@pytest.fixture
def pub(workspace: Workspace) -> Path:
    """Un pub de juguete con fuentes, `_site/` confirmado (en el pasado) y un remoto bare local al día."""
    sitio = workspace.pubs / "pub_prueba"
    (sitio / "posts" / "2026-01-01-primero").mkdir(parents=True)
    (sitio / "_site").mkdir()
    (sitio / "_quarto.yml").write_text("project:\n  type: website\n")
    (sitio / "index.qmd").write_text("---\ntitle: Prueba\n---\n")
    (sitio / "posts" / "2026-01-01-primero" / "index.qmd").write_text("---\ntitle: Primero\n---\nHola.\n")
    (sitio / "_site" / "index.html").write_text("<html>v1</html>\n")
    workspace.git(sitio, "init", "-q", "-b", "main")
    workspace.git(sitio, "add", "-A")
    workspace.git(sitio, "commit", "-q", "-m", "inicio", fecha=FECHA_PASADA)
    remoto = workspace.base / "remoto.git"
    workspace.git(workspace.base, "init", "-q", "--bare", str(remoto))
    workspace.git(sitio, "remote", "add", "origin", str(remoto))
    workspace.git(sitio, "push", "-q", "-u", "origin", "main")
    return sitio
