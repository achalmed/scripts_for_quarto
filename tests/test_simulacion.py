"""test_simulacion.py — cada suite del repo que escribe, en simulación, no escribe nada (ola 4, Q1b).

Para cada `suite.yml` del repo con `escribe_en` distinto de `[ninguno]` hay al menos un caso: se ejecuta la
herramienta en simulación (`--dry-run`, o sin `--aplicar` en `blogs_manager`) sobre un workspace de fixture
(conftest.py) y se compara el listado + mtime + tamaño de todo el directorio temporal y de todo el repo antes y
después. La GUI (`quarto_studio`) no tiene CLI: se omite con su motivo (sus `Command` se prueban en
`test_gui_blog_service.py`). Ningún caso necesita red.

    python3 -m pytest tests --basetemp ~/.cache/pytest/quarto-ola4 -p no:cacheprovider
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from conftest import BACKEND, CORE_ENV, PUERTA_REAL, RAIZ_REPO, instantanea

QMD_POST = """---
title: "Primero"
date: "02/01/2026"
tags:
  - Gestión Empresarial
  - economia
citation:
  pdf-url: https://ejemplo.invalid/viejo.pdf
---

Texto del post.
"""
QMD_PEGADO = "---\ntitle: Pegado\n---\n\n\n\n## Sección\nTexto.\n"   # líneas en blanco sobrantes para format_yaml


def _post(sitio: Path, carpeta: str, nombre: str, texto: str = QMD_POST) -> Path:
    d = sitio / carpeta / nombre
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.qmd").write_text(texto, encoding="utf-8")
    return d


@pytest.fixture
def blogs(workspace):
    """Hub y un pub con posts que cada herramienta querría cambiar; `_indice/` vacío para pub_index_symlink."""
    (workspace.hub / "_quarto.yml").write_text("project:\n  type: website\n")
    (workspace.hub / "_indice" / "2025").mkdir(parents=True)
    (workspace.hub / "_indice" / "2025" / "2025-01-01-roto").symlink_to(workspace.base / "no-existe")   # --clean-broken
    _post(workspace.hub, "blog/posts", "2026-02-03-del-hub")
    sitio = workspace.pubs / "pub_simulado"
    (sitio).mkdir()
    (sitio / "_quarto.yml").write_text("project:\n  type: website\n")
    (sitio / "index.qmd").write_text("---\ntitle: Simulado\n---\n")
    _post(sitio, "posts", "2026-01-01-primero")
    _post(sitio, "posts", "2026-01-05-segundo", QMD_PEGADO)
    config = workspace.base / "metadata_config.yml"
    config.write_text(yaml.safe_dump({"allowed_blogs": [], "excluded_folders": [],
                                      "excel_output_dir": str(workspace.base / "excel")}))
    return sitio, config


def _excel(workspace, config: Path) -> Path:
    """Excel de la colección de fixture (create-template, antes de la instantánea) con un título cambiado."""
    import openpyxl
    r = workspace.correr(sys.executable, str(BACKEND / "script_metadata_manager" / "main.py"),
                         "create-template", str(workspace.raiz), "--config", str(config), "-o", "meta.xlsx")
    assert r.returncode == 0, r.stdout + r.stderr
    ruta = workspace.base / "excel" / "meta.xlsx"
    libro = openpyxl.load_workbook(ruta)
    hoja = libro.worksheets[0]
    cabecera = [c.value for c in hoja[1]]
    if "title" in cabecera:
        hoja.cell(row=2, column=cabecera.index("title") + 1).value = "Título cambiado en el Excel"
    libro.save(ruta)
    return ruta


MM = BACKEND / "script_metadata_manager" / "main.py"

# (suite, caso, constructor de la orden: (workspace, sitio, config) -> list[str])
CASOS = [
    ("metadata_manager", "update", lambda ws, s, c: [sys.executable, str(MM), "update", str(ws.raiz),
                                                     str(_excel(ws, c)), "--config", str(c), "--dry-run"]),
    ("metadata_manager", "normalize-tags", lambda ws, s, c: [sys.executable, str(MM), "normalize-tags",
                                                             str(ws.raiz), "--config", str(c), "--dry-run"]),
    ("metadata_manager", "replace-tags", lambda ws, s, c: [sys.executable, str(MM), "replace-tags", str(ws.raiz),
                                                           "economia:economia_peruana", "--config", str(c),
                                                           "--dry-run"]),
    ("metadata_manager", "remove-tags", lambda ws, s, c: [sys.executable, str(MM), "remove-tags", str(ws.raiz),
                                                          "economia", "--config", str(c), "--dry-run"]),
    ("metadata_manager", "add-tags", lambda ws, s, c: [sys.executable, str(MM), "add-tags", str(ws.raiz),
                                                       "nuevo", "--config", str(c), "--dry-run"]),
    ("metadata_manager", "sync-dates", lambda ws, s, c: [sys.executable, str(MM), "sync-dates", str(ws.raiz),
                                                         "--config", str(c), "--dry-run"]),
    ("metadata_manager", "fechas-iso", lambda ws, s, c: [sys.executable, str(MM), "fechas-iso", str(s),
                                                         "--dry-run"]),
    ("metadata_manager", "sync-pdf-urls", lambda ws, s, c: [sys.executable, str(MM), "sync-pdf-urls", str(ws.raiz),
                                                            "--config", str(c), "--dry-run"]),
    ("format_yaml", "directorio", lambda ws, s, c: [sys.executable, str(BACKEND / "script_format_yaml" / "main.py"),
                                                    "--directory", str(s), "--recursive", "--dry-run"]),
    ("generador_publicacion_similar", "blog", lambda ws, s, c: [
        "bash", str(BACKEND / "script_generador_publicacion_similar" / "main.sh"), str(s),
        "--type", "blog", "--base-url", "https://ejemplo.invalid", "--dry-run"]),
    ("pub_index_symlink", "sincronizar", lambda ws, s, c: [
        "bash", str(BACKEND / "script_pub_index_symlink" / "main.sh"), "--dry-run"]),
    ("pub_index_symlink", "limpiar-rotos", lambda ws, s, c: [
        "bash", str(BACKEND / "script_pub_index_symlink" / "main.sh"), "--clean-broken", "--dry-run"]),
    ("blogs_manager", "publish", lambda ws, s, c: [
        "bash", str(BACKEND / "script_blogs_manager" / "main.sh"), "publish", "pub_prueba"]),
    ("blogs_manager", "git-commit", lambda ws, s, c: [
        "bash", str(BACKEND / "script_blogs_manager" / "main.sh"), "git-commit", "pub_prueba", "cambio"]),
]

OMITIDAS: dict[str, str] = {}   # la GUI (quarto_studio) vive en el repo studios desde la ola 4 (fase B) y se prueba allí


def _suites() -> dict[str, dict]:
    salida = {}
    for f in sorted(BACKEND.glob("*/suite.yml")):
        datos = yaml.safe_load(f.read_text(encoding="utf-8"))
        salida[datos["id"]] = datos
    return salida


def test_toda_suite_que_escribe_tiene_caso_de_simulacion():
    con_caso = {s for s, _, _ in CASOS} | set(OMITIDAS)
    escriben = {i for i, d in _suites().items() if d.get("escribe_en") not in (None, [], ["ninguno"])}
    assert escriben <= con_caso, f"suites que escriben sin caso de simulación: {sorted(escriben - con_caso)}"




@pytest.mark.parametrize("suite,caso,orden", CASOS, ids=[f"{s}:{c}" for s, c, _ in CASOS])
def test_simulacion_no_escribe(workspace, blogs, suite, caso, orden, request):
    sitio, config = blogs
    if suite == "blogs_manager":
        if PUERTA_REAL is None or not PUERTA_REAL.is_file():
            pytest.skip("sin 04 index/scripts/puerta-r6.sh")
        pub = request.getfixturevalue("pub")
        (pub / "index.qmd").write_text("---\ntitle: Cambio\n---\n")       # algo que confirmar
        (pub / "_site" / "index.html").write_text("<html>v2</html>\n")
        workspace.git(pub, "commit", "-qam", "render")                      # algo que empujar
        (pub / "foto.png").write_bytes(b"\x89PNG")
    if suite in {"metadata_manager"}:
        pytest.importorskip("openpyxl")
    cmd = orden(workspace, sitio, config)
    vigiladas = [workspace.base, RAIZ_REPO]
    if CORE_ENV is not None and (Path(CORE_ENV.INDEX_DIR) / "_indice").is_dir():
        vigiladas.append(Path(CORE_ENV.INDEX_DIR) / "_indice")              # el _indice real, por si acaso
    antes = instantanea(*vigiladas)

    r = workspace.correr(*cmd, entrada="n\n")

    assert r.returncode == 0, f"{' '.join(cmd)}\n{r.stdout}\n{r.stderr}"
    despues = instantanea(*vigiladas)
    nuevos = sorted(set(despues) - set(antes))
    borrados = sorted(set(antes) - set(despues))
    cambiados = sorted(k for k in set(antes) & set(despues) if antes[k] != despues[k])
    assert not (nuevos or borrados or cambiados), (
        f"{suite} {caso} escribió en simulación:\n nuevos={nuevos[:10]}\n borrados={borrados[:10]}\n"
        f" cambiados={cambiados[:10]}\n{r.stdout[-2000:]}")


@pytest.mark.parametrize("orden", [
    ["bash", str(BACKEND / "script_blogs_manager" / "main.sh"), "help"],
    ["bash", str(BACKEND / "script_blogs_manager" / "main.sh"), "--dry-run"],   # sin comando: ni menú ni escritura
    ["bash", str(BACKEND / "script_pub_index_symlink" / "main.sh"), "--help"],
    ["bash", str(BACKEND / "script_generador_publicacion_similar" / "main.sh"), "--help"],
    [sys.executable, str(BACKEND / "script_format_yaml" / "main.py"), "--help"],
    [sys.executable, str(MM), "--help"],
], ids=["blogs_manager", "blogs_manager-sin-comando", "pub_index_symlink", "generador_publicacion_similar", "format_yaml", "metadata_manager"])
def test_ayuda_sale_con_cero_y_no_escribe(workspace, orden):
    antes = instantanea(workspace.base, RAIZ_REPO)
    r = workspace.correr(*orden)
    assert r.returncode == 0, r.stdout + r.stderr
    assert instantanea(workspace.base, RAIZ_REPO) == antes
