"""test_sync.py — `sync-article` y `sync-batch` del gestor de metadatos (2026-11-03): con `--direccion` no preguntan (así
los usa Quarto Studio) y encuentran la fila del Excel por su clave (`ruta_archivo`) aunque el pub viva en
`<hub>/_pubs/` (antes comparaban `relative_to(base)` con la clave y no encontraban ninguna). Sobre el workspace de
fixture (conftest.py): un pub con dos entradas, el Excel de `create-template` con un título cambiado; nada real.
"""

from __future__ import annotations

import sys

import openpyxl
import pytest
import yaml

from conftest import BACKEND, instantanea

MM = BACKEND / "script_metadata_manager" / "main.py"
QMD = '---\ntitle: "{titulo}"\ndate: "2026-01-0{dia}"\ntags:\n  - economia\n---\n\nTexto.\n'


@pytest.fixture
def pub(workspace):
    sitio = workspace.pubs / "pub_sincro"
    sitio.mkdir()
    (sitio / "_quarto.yml").write_text("project:\n  type: website\n")
    (sitio / "index.qmd").write_text("---\ntitle: Sincro\n---\n")
    for dia, titulo in ((1, "Primero"), (2, "Segundo")):
        d = sitio / "posts" / f"2026-01-0{dia}-entrada-{dia}"
        d.mkdir(parents=True)
        (d / "index.qmd").write_text(QMD.format(titulo=titulo, dia=dia), encoding="utf-8")
    config = workspace.base / "metadata_config.yml"
    config.write_text(yaml.safe_dump({"allowed_blogs": [], "excluded_folders": [], "excel_output_dir": str(workspace.base / "excel")}))
    r = workspace.correr(sys.executable, str(MM), "create-template", str(workspace.raiz), "--config", str(config), "-o", "meta.xlsx")
    assert r.returncode == 0, r.stdout + r.stderr
    excel = workspace.base / "excel" / "meta.xlsx"
    libro = openpyxl.load_workbook(excel)
    hoja = libro["METADATOS"]
    cab = [c.value for c in hoja[1]]
    claves = {}
    for fila in range(2, hoja.max_row + 1):
        ruta = hoja.cell(fila, cab.index("ruta_archivo") + 1).value
        if ruta and ruta.endswith("entrada-1/index.qmd"):
            hoja.cell(fila, cab.index("title") + 1).value = "Título del Excel"       # la entrada 1 difiere
        if ruta:
            claves[ruta.split("/")[-2]] = ruta
    libro.save(excel)
    return sitio, config, excel, claves


def _titulo_excel(excel, clave):
    hoja = openpyxl.load_workbook(excel)["METADATOS"]
    cab = [c.value for c in hoja[1]]
    for fila in range(2, hoja.max_row + 1):
        if hoja.cell(fila, cab.index("ruta_archivo") + 1).value == clave:
            return hoja.cell(fila, cab.index("title") + 1).value
    return None


def _sync(workspace, config, excel, *args):
    return workspace.correr(sys.executable, str(MM), *args[:1], str(workspace.raiz), str(excel), *args[1:], "--config", str(config))


def test_la_clave_antigua_pub_x_se_resuelve_en_los_pubs_del_hub(workspace, pub):
    """Las filas de antes del 2026-09-06 dicen `pub_x/posts/…`: el artículo vive en `<hub>/_pubs/x/…`; antes de este
    arreglo sync-article no lo encontraba (comprobaba `<base>/pub_x/…`) y sync-batch caía al buscar la fila."""
    sitio, config, excel, claves = pub
    libro = openpyxl.load_workbook(excel)
    hoja = libro["METADATOS"]
    cab = [c.value for c in hoja[1]]
    antigua = "pub_sincro/posts/2026-01-01-entrada-1/index.qmd"
    for fila in range(2, hoja.max_row + 1):
        if hoja.cell(fila, cab.index("ruta_archivo") + 1).value == claves["2026-01-01-entrada-1"]:
            hoja.cell(fila, cab.index("ruta_archivo") + 1).value = antigua
    libro.save(excel)
    assert not (workspace.raiz / antigua).exists()
    r = _sync(workspace, config, excel, "sync-article", antigua, "--direccion", "a-documentos")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Título del Excel" in (sitio / "posts" / "2026-01-01-entrada-1" / "index.qmd").read_text(encoding="utf-8")
    (sitio / "posts" / "2026-01-01-entrada-1" / "index.qmd").write_text(QMD.format(titulo="Otro", dia=1), encoding="utf-8")
    r = _sync(workspace, config, excel, "sync-batch", "--blog", "pub_sincro", "--direccion", "al-excel")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _titulo_excel(excel, antigua) == "Otro"


def test_sync_article_simula_sin_escribir_y_aplica_en_las_dos_direcciones(workspace, pub):
    sitio, config, excel, claves = pub
    clave = claves["2026-01-01-entrada-1"]
    qmd = sitio / "posts" / "2026-01-01-entrada-1" / "index.qmd"
    antes = instantanea(workspace.base)
    r = _sync(workspace, config, excel, "sync-article", clave, "--direccion", "a-documentos", "--dry-run")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Título del Excel" in r.stdout and instantanea(workspace.base) == antes          # simula: nada cambia
    # Excel → documento (por la clave)
    r = _sync(workspace, config, excel, "sync-article", clave, "--direccion", "a-documentos")
    assert r.returncode == 0, r.stdout + r.stderr
    assert 'Título del Excel' in qmd.read_text(encoding="utf-8")
    # documento → Excel (por la ruta absoluta, como la manda la ventana)
    qmd.write_text(qmd.read_text(encoding="utf-8").replace("Título del Excel", "Título del documento"), encoding="utf-8")
    r = _sync(workspace, config, excel, "sync-article", str(qmd), "--direccion", "al-excel")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _titulo_excel(excel, clave) == "Título del documento"
    # sin --direccion ni --dry-run sigue preguntando (la terminal): «3» cancela
    r = workspace.correr(sys.executable, str(MM), "sync-article", str(workspace.raiz), str(excel), clave, "--config", str(config), entrada="3\n")
    assert r.returncode == 0 and "Cancelado" in r.stdout


def test_sync_article_de_algo_que_no_esta_sale_con_uno(workspace, pub):
    _sitio, config, excel, _claves = pub
    r = _sync(workspace, config, excel, "sync-article", "pub_sincro/posts/no-existe/index.qmd", "--direccion", "al-excel")
    assert r.returncode == 1


def test_sync_batch_con_filtro_y_direccion(workspace, pub):
    sitio, config, excel, claves = pub
    qmd1 = sitio / "posts" / "2026-01-01-entrada-1" / "index.qmd"
    antes = instantanea(workspace.base)
    r = _sync(workspace, config, excel, "sync-batch", "--blog", "pub_sincro", "--filter-path", "entrada-1", "--direccion", "a-documentos", "--dry-run")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Artículos con diferencias: 1" in r.stdout and instantanea(workspace.base) == antes
    r = _sync(workspace, config, excel, "sync-batch", "--blog", "pub_sincro", "--direccion", "al-excel")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _titulo_excel(excel, claves["2026-01-01-entrada-1"]) == "Primero"                 # el documento manda
    assert "Título del Excel" not in qmd1.read_text(encoding="utf-8")
