"""test_blogs_manager_git.py — `publish` y `git-commit` de blogs_manager (ola 4, Q2).

Sobre un pub de fixture con remoto bare local (conftest.py) se demuestra que:
  · sin `--aplicar` no hay commit ni push (ni cambia nada en el repo ni en el remoto);
  · con `_site/` más viejo que una fuente, la puerta R6 bloquea el push;
  · con todo al día, `git-commit --aplicar` confirma fuentes, contenido (con imágenes), `_freeze/` y `_site/`,
    deja fuera los sueltos de la raíz y los punteros de submódulo, y empuja al bare;
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


def test_git_commit_aplicar_con_todo_al_dia_empuja_sitio_y_deja_sueltos(workspace, pub):
    post = pub / "posts" / "2026-01-01-primero"
    (post / "index.qmd").write_text("---\ntitle: Primero\n---\n![](figura.png)\n")
    (post / "figura.png").write_bytes(b"\x89PNG")                       # imagen nueva del post: entra
    (post / "datos.csv").write_text("a,b\n1,2\n")                       # datos del post: entran
    (pub / "nuevo.qmd").write_text("---\ntitle: Nuevo\n---\n")
    (pub / "_site" / "index.html").write_text("<html>v2</html>\n")
    (pub / "_site" / "nuevo.html").write_text("<html>nuevo</html>\n")
    (pub / "_freeze" / "posts").mkdir(parents=True)
    (pub / "_freeze" / "posts" / "x.json").write_text("{}")              # _freeze/ nuevo: entra
    (pub / "suelto.txt").write_text("nota")                                # suelto en la raíz: fuera
    (pub / "foto.png").write_bytes(b"\x89PNG")                            # suelto en la raíz: fuera
    (pub / ".gitignore").write_text("*.tmp\n")
    (post / "borrador.tmp").write_text("x")                                # ignorado: ni entra ni se lista

    r = _bm(workspace, "git-commit", "pub_prueba", "render al día", "--aplicar")

    assert r.returncode == 0, r.stdout + r.stderr
    assert _head(workspace, pub) == _head(workspace, _remoto(workspace), "main")
    confirmadas = set(workspace.git(pub, "show", "--name-only", "--format=", "HEAD").splitlines())
    assert confirmadas == {"posts/2026-01-01-primero/index.qmd", "posts/2026-01-01-primero/figura.png",
                           "posts/2026-01-01-primero/datos.csv", "nuevo.qmd", "_site/index.html",
                           "_site/nuevo.html", "_freeze/posts/x.json"}
    pendientes = workspace.git(pub, "status", "--porcelain", "--untracked-files=all")
    for suelto in ("suelto.txt", "foto.png", ".gitignore"):
        assert suelto in pendientes and suelto in r.stdout              # fuera, y avisado
    assert "borrador.tmp" not in pendientes + r.stdout


def test_git_commit_no_anade_punteros_de_submodulo(workspace, pub):
    # Un «hub» de juguete con el pub como submódulo dentro de una carpeta de contenido.
    hub = workspace.base / "hub"
    (hub / "blog" / "posts" / "2026-01-02-h").mkdir(parents=True)
    (hub / "blog" / "posts" / "2026-01-02-h" / "index.qmd").write_text("---\ntitle: H\n---\n")
    (hub / "_site").mkdir()
    (hub / "_site" / "index.html").write_text("<html>h</html>\n")
    (hub / "_quarto.yml").write_text("project:\n  type: website\n")
    workspace.git(hub, "init", "-q", "-b", "main")
    workspace.git(hub, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(pub), "blog/sub")
    workspace.git(hub, "add", "-A")
    workspace.git(hub, "commit", "-qm", "inicio")
    workspace.git(pub, "commit", "-q", "--allow-empty", "-m", "otro")
    workspace.git(hub / "blog" / "sub", "pull", "-q")                     # el puntero cambia
    (hub / "blog" / "posts" / "2026-01-02-h" / "index.qmd").write_text("---\ntitle: H2\n---\n")
    destino = workspace.raiz / ("04" + " index") / "_pubs" / "pub_hub"
    hub.rename(destino)

    r = _bm(workspace, "git-commit", "pub_hub", "m", "--aplicar")       # sin remoto: el push falla después

    confirmadas = set(workspace.git(destino, "show", "--name-only", "--format=", "HEAD").splitlines())
    assert confirmadas == {"blog/posts/2026-01-02-h/index.qmd"}
    assert "blog/sub" in r.stdout


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
