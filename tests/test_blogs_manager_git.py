"""test_blogs_manager_git.py — `publish` y `git-commit` de blogs_manager (ola 4, Q2).

Sobre un pub de fixture con remoto bare local (conftest.py) se demuestra que:
  · sin `--aplicar` no hay commit ni push (ni cambia nada en el repo ni en el remoto);
  · con `_site/` más viejo que una fuente, la puerta R6 bloquea el push;
  · con todo al día, `git-commit --aplicar` confirma solo fuentes y `_site/` y empuja al bare;
  · el destino por defecto es el `git push` (Netlify), no `quarto publish gh-pages`;
  · los pathspecs de fuentes son los mismos que los de `04 index/scripts/puerta-r6.sh`.
"""

from __future__ import annotations

import shlex
from pathlib import Path

import pytest

from conftest import BACKEND, FECHA_PASADA, PUERTA_REAL, instantanea

MAIN = BACKEND / "script_blogs_manager" / "main.sh"

pytestmark = pytest.mark.skipif(PUERTA_REAL is None or not PUERTA_REAL.is_file(),
                                reason="sin 04 index/scripts/puerta-r6.sh no hay puerta que probar")


def _bm(ws, *args):
    return ws.correr("bash", str(MAIN), *args)


def _head(ws, repo: Path, ref: str = "HEAD") -> str:
    return ws.git(repo, "rev-parse", ref)


def _remoto(ws) -> Path:
    return ws.base / "remoto.git"


def test_git_commit_sin_aplicar_no_confirma_ni_empuja(workspace, pub):
    (pub / "index.qmd").write_text("---\ntitle: Prueba 2\n---\n")
    (pub / "_site" / "index.html").write_text("<html>v2</html>\n")
    (pub / "foto.png").write_bytes(b"\x89PNG")
    antes = instantanea(pub, _remoto(workspace))
    head, remoto = _head(workspace, pub), _head(workspace, _remoto(workspace), "main")

    r = _bm(workspace, "git-commit", "pub_prueba", "cambio")

    assert r.returncode == 0, r.stdout + r.stderr
    assert "Simulación" in r.stdout
    assert "foto.png" in r.stdout                      # se informa de lo que queda fuera
    assert _head(workspace, pub) == head
    assert _head(workspace, _remoto(workspace), "main") == remoto
    assert instantanea(pub, _remoto(workspace)) == antes   # ni el índice de git cambió


def test_publish_sin_aplicar_no_empuja(workspace, pub):
    (pub / "index.qmd").write_text("---\ntitle: Prueba 2\n---\n")
    (pub / "_site" / "index.html").write_text("<html>v2</html>\n")
    workspace.git(pub, "commit", "-qam", "render al día")
    remoto = _head(workspace, _remoto(workspace), "main")
    antes = instantanea(pub, _remoto(workspace))

    r = _bm(workspace, "publish", "pub_prueba")

    assert r.returncode == 0, r.stdout + r.stderr
    assert "empujaría 1 commit" in r.stdout
    assert _head(workspace, _remoto(workspace), "main") == remoto
    assert instantanea(pub, _remoto(workspace)) == antes
    assert not workspace.registro_quarto.exists()      # el destino por defecto no es quarto publish


def test_puerta_r6_bloquea_si_site_es_mas_viejo_que_una_fuente(workspace, pub):
    # La fuente cambia y se confirma; _site/ sigue con el render de FECHA_PASADA.
    (pub / "posts" / "2026-01-01-primero" / "index.qmd").write_text("---\ntitle: Primero\n---\nCambio.\n")
    remoto = _head(workspace, _remoto(workspace), "main")

    r = _bm(workspace, "git-commit", "pub_prueba", "solo la fuente", "--aplicar")

    assert r.returncode != 0
    assert "R6" in r.stdout + r.stderr
    assert _head(workspace, _remoto(workspace), "main") == remoto      # no se empujó
    assert _head(workspace, pub) != remoto                            # el commit local sí se hizo

    r = _bm(workspace, "publish", "pub_prueba", "--aplicar")          # tampoco por publish
    assert r.returncode != 0
    assert _head(workspace, _remoto(workspace), "main") == remoto


def test_git_commit_aplicar_con_todo_al_dia_empuja_solo_fuentes_y_site(workspace, pub):
    (pub / "index.qmd").write_text("---\ntitle: Prueba 2\n---\n")
    (pub / "nuevo.qmd").write_text("---\ntitle: Nuevo\n---\n")
    (pub / "_site" / "index.html").write_text("<html>v2</html>\n")
    (pub / "_site" / "nuevo.html").write_text("<html>nuevo</html>\n")
    (pub / "foto.png").write_bytes(b"\x89PNG")
    (pub / "_freeze").mkdir()
    (pub / "_freeze" / "x.json").write_text("{}")

    r = _bm(workspace, "git-commit", "pub_prueba", "render al día", "--aplicar")

    assert r.returncode == 0, r.stdout + r.stderr
    assert _head(workspace, pub) == _head(workspace, _remoto(workspace), "main")
    confirmadas = set(workspace.git(pub, "show", "--name-only", "--format=", "HEAD").splitlines())
    assert confirmadas == {"index.qmd", "nuevo.qmd", "_site/index.html", "_site/nuevo.html"}
    pendientes = workspace.git(pub, "status", "--porcelain", "--untracked-files=all")
    assert "foto.png" in pendientes and "_freeze/x.json" in pendientes
    assert "foto.png" in r.stdout                       # informado como fuera


def test_quarto_publish_solo_con_destino_explicito_y_aplicar(workspace, pub):
    r = _bm(workspace, "publish", "pub_prueba", "netlify")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not workspace.registro_quarto.exists()

    r = _bm(workspace, "publish", "pub_prueba", "netlify", "--aplicar")
    assert r.returncode == 0, r.stdout + r.stderr
    assert workspace.registro_quarto.read_text().strip() == "publish netlify"


def test_sin_puerta_no_se_empuja(workspace, pub):
    (workspace.hub / "scripts" / "puerta-r6.sh").unlink()
    (pub / "index.qmd").write_text("---\ntitle: Prueba 2\n---\n")
    (pub / "_site" / "index.html").write_text("<html>v2</html>\n")
    remoto = _head(workspace, _remoto(workspace), "main")

    r = _bm(workspace, "git-commit", "pub_prueba", "x", "--aplicar")

    assert r.returncode != 0
    assert _head(workspace, _remoto(workspace), "main") == remoto


def _fuentes(archivo: Path, variable: str) -> list[str]:
    """Los elementos del arreglo Bash `variable=( … )` tal como los ve Bash (comillas y comentarios fuera)."""
    texto = archivo.read_text(encoding="utf-8")
    inicio = texto.index(f"{variable}=(") + len(variable) + 2
    lexico = shlex.shlex(texto[inicio:], posix=True, punctuation_chars=")")
    lexico.whitespace_split = True
    elementos = []
    for pieza in lexico:
        if pieza == ")":
            return elementos
        elementos.append(pieza)
    raise AssertionError(f"{archivo}: {variable}=( sin cerrar")


def test_fuentes_iguales_a_las_de_la_puerta():
    propias = _fuentes(BACKEND / "script_blogs_manager" / "lib" / "00-config.sh", "QBLOG_FUENTES")
    puerta = _fuentes(PUERTA_REAL, "FUENTES")
    assert propias and propias == puerta
