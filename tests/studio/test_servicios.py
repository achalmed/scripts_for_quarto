"""tests/studio/test_servicios.py — los servicios y los modelos de Quarto Studio, sin QML: el catálogo de operaciones
(cada vista tiene las suyas; simular nunca lleva --aplicar ni escribe; lo que publica lo declara), el estado de cada
sitio de la muestra por la regla de la puerta R6, la lectura de la salida de quarto render (progreso y problemas), las
lecturas de la muestra (entradas, Excel, índice, fragmentos) y las filas de las tablas."""
from __future__ import annotations

from pathlib import Path

import pytest

from conftest import requiere_binding

from quarto_app.models import filas as mod  # noqa: E402
from quarto_app.models.blog import Blog  # noqa: E402
from quarto_app.services import datos, operaciones as ops, project_scanner, render, sitios  # noqa: E402


def _blogs(m) -> list[Blog]:
    """Los sitios de una muestra sin pasar por core/env (la muestra de la sesión la cambian los controladores)."""
    import muestra as muestra_mod
    rutas = [m.pubs / n for n, _t, _d in muestra_mod.PUBS] + [m.hub]
    return [Blog(ruta=r, posts=project_scanner.listar_posts(r), tiene_git=(r / ".git").exists(), tiene_quarto_yml=(r / "_quarto.yml").is_file()) for r in rutas]


def test_el_catalogo_cubre_las_cuatro_vistas():
    ids = [o.id for o in ops.todas()]
    assert len(ids) == len(set(ids))
    for v in ops.NOMBRES_VISTAS:
        assert ops.de_vista(v), v
    assert {o.id for o in ops.de_vista("sitios")} >= {"render", "publicar", "commit", "preview", "limpiar", "verificar", "render_todos", "respaldar", "crear_sitio"}
    for o in ops.todas():
        assert o.simular is not None or o.plan is not None, f"{o.id}: ni simula ni tiene plan"
        if o.publica:
            assert o.escribe and o.simular is not None and o.sobre_sitio, o.id
        if o.larga:
            assert not o.escribe
        assert o.verbo in ("Simular", "Ejecutar", "Arrancar")


@requiere_binding
def test_simular_nunca_aplica_y_aplicar_escribe(muestra_sesion):
    ctx = ops.Contexto(sitio="axiomata", ruta=str(muestra_sesion.pubs / "axiomata"), valor="mensaje", excel=str(muestra_sesion.excel or "x.xlsx"))
    for o in ops.todas():
        if o.simular is not None:
            args = o.simular(ctx).args
            assert "--aplicar" not in args, o.id
            if o.escribe and o.vista != "sitios" and o.id != "indice_limpiar":
                assert "--dry-run" in args, o.id
        if o.aplicar is not None:
            args = o.aplicar(ctx).args
            assert "--dry-run" not in args, o.id
            if o.publica:
                assert args[-1] == "--aplicar", o.id
    assert ops.texto_orden(ops.operacion("publicar").simular(ctx)) == "bash backend/script_blogs_manager/main.sh publish axiomata"
    assert ops.texto_orden(ops.operacion("commit").aplicar(ctx)) == "bash backend/script_blogs_manager/main.sh git-commit axiomata mensaje --aplicar"
    assert ops.operacion("limpiar_todos").aplicar(ctx).stdin_data == "s\n"
    assert ops.operacion("respaldar").aplicar(ctx).stdin_data == "1\nn\n"
    assert ops.operacion("indice_limpiar").aplicar(ctx).stdin_data == "s\n"


@requiere_binding
def test_planes_de_la_ventana(muestra_sesion):
    m = muestra_sesion
    ruta = m.pubs / "axiomata"
    e = sitios.estado_sitio(ruta)
    ctx = ops.Contexto(sitio="axiomata", ruta=str(ruta), estado=e, sitios=[("axiomata", str(ruta), e), ("aequilibria", str(m.pubs / "aequilibria"), sitios.estado_sitio(m.pubs / "aequilibria"))])
    plan = ops.plan_render(ctx)
    assert "Renderizar axiomata" in plan and "sin confirmar (1)" in plan and "2025-12-02-limites-y-continuidad" in plan
    assert "después del último render (1)" in plan and "2026-01-08-matrices" in plan
    todos = ops.plan_render_todos(ctx)
    assert todos.splitlines()[1].strip().startswith("1. axiomata")
    assert "_site/: existe" in ops.plan_limpiar(ctx)
    assert "Escribe el nombre" in ops.plan_crear_sitio(ctx)
    assert "Crear el sitio nuevo («Un título»)" in ops.plan_crear_sitio(ops.Contexto(valor='nuevo "Un título"'))


def test_estado_de_cada_sitio_de_la_muestra(muestra):
    m = muestra
    estados = {n: sitios.estado_sitio(m.pubs / n) for n in ("aequilibria", "axiomata", "chaska")}
    estados["web"] = sitios.estado_sitio(m.hub)
    assert estados["aequilibria"]["estado"] == "al_dia" and estados["aequilibria"]["por_empujar"] == 0
    assert estados["axiomata"]["estado"] == "sin_render" and estados["axiomata"]["cambios"] == 1
    assert estados["chaska"]["estado"] == "sin_publicar" and estados["chaska"]["por_empujar"] == 1
    assert estados["web"]["estado"] == "problemas" and not estados["web"]["site"]
    for e in estados.values():
        assert e["texto_estado"] and e["nivel"] and e["motivo"]
    c = sitios.contar(list(estados.values()))
    assert c == {"al_dia": 1, "sin_render": 1, "sin_publicar": 1, "problemas": 1, "todos": 4}
    assert sitios.resumen(c) == "4 sitios · 1 al día · 1 sin render · 1 sin publicar · 1 con problemas"
    assert sitios.clasificar({"quarto_yml": True, "git": True, "site": True, "cambios": 0, "ts_fuentes": 10, "ts_render": 20, "site_sin_confirmar": True})[0] == "sin_publicar"
    assert sitios.clasificar({"quarto_yml": True, "git": True, "site": True, "cambios": 0, "ts_fuentes": 30, "ts_render": 20})[0] == "sin_render"


def test_progreso_y_problemas_del_render():
    assert render.progreso_de("[ 3/41] posts/2025-06-01-x/index.qmd") == (4, "3 de 41 · posts/2025-06-01-x/index.qmd")
    assert render.progreso_de("Output created: _site/index.html") is None
    salida = ("[ 1/2] posts/2026-01-05-a/index.qmd\nWARNING: Unable to resolve link target: x.html\n[ 2/2] index.qmd\n"
              "ERROR: YAMLError: posts/2026-01-05-a/index.qmd:3 bad indentation\nOutput created: _site/index.html\n")
    p = render.problemas_de(salida)
    assert [x["nivel"] for x in p] == ["aviso", "error"]
    assert p[0]["archivo"] == "posts/2026-01-05-a/index.qmd" and p[1]["linea"] == 3 and "bad indentation" in p[1]["mensaje"]
    assert render.resumen_problemas(p) == "1 error · 1 aviso" and render.resumen_problemas([]) == "sin problemas"


def test_entradas_excel_indice_y_fragmentos(muestra):
    m = muestra
    blogs = _blogs(m)
    assert sorted(b.nombre for b in blogs) == ["aequilibria", "axiomata", "chaska", "web"]
    assert {b.nombre: b.num_posts for b in blogs}["web"] == 1            # el hub no cuenta las entradas de sus pubs
    excel = datos.leer_excel(m.excel) if m.excel else {}
    if m.excel:
        assert set(excel) == {"aequilibria/posts/2026-01-05-curva-de-phillips/index.qmd", "axiomata/posts/2026-01-08-matrices-y-determinantes/index.qmd"}
    filas = datos.entradas(blogs, set(excel) if excel else None)
    assert len(filas) == 7 and filas[0]["fecha"] >= filas[-1]["fecha"]
    por_carpeta = {f["carpeta"]: f for f in filas}
    assert por_carpeta["2026-01-05-curva-de-phillips"]["tags"] == "macroeconomía, inflación"
    if m.excel:
        assert por_carpeta["2026-01-05-curva-de-phillips"]["excel"] == "sí" and por_carpeta["2026-01-02-configuracion-de-quarto"]["excel"] == "no"
        comp = datos.comparar(por_carpeta["2026-01-08-matrices-y-determinantes"]["frontmatter"], excel["axiomata/posts/2026-01-08-matrices-y-determinantes/index.qmd"])
        difieren = {c["campo"] for c in comp if c["difiere"]}
        assert "title" in difieren and "date" not in difieren
    enlaces = datos.enlaces_indice(m.hub / "_indice", m.raiz)
    assert [(e["enlace"], e["estado"]) for e in enlaces] == [("2026-01-01-borrado", "roto"), ("2026-01-05-curva-de-phillips", "bien")]
    assert enlaces[1]["destino"] == "web/_pubs/aequilibria/posts/2026-01-05-curva-de-phillips"
    frag = datos.fragmentos(blogs)
    assert len(frag) == 1 and frag[0]["sitio"] == "axiomata" and frag[0]["subblog"] == "posts" and frag[0]["entradas"] == "3"
    assert datos.frontmatter(Path(filas[0]["ruta"]))["title"]


def test_filas_de_las_tablas(muestra):
    m = muestra
    b = next(x for x in _blogs(m) if x.nombre == "chaska")
    f = mod.fila_sitio(b, sitios.estado_sitio(b.ruta), None)
    assert f["sitio"] == "chaska" and f["estado"] == "Render sin publicar" and f["nivel"] == "activo" and f["por_empujar"] == "1" and f["crudo"]["estado"] == 2
    campos = mod.campos_elemento({"anio": "2026", "enlace": "x", "estado": "roto", "destino": "y", "nivel": "negativo", "ruta": "/r"}, mod.COLUMNAS["indice"])
    assert campos[0] == {"etiqueta": "Año", "valor": "2026"} and all(c["etiqueta"] != "Nivel" for c in campos)
    assert [x[0] for x in mod.FILTROS] == ["todos", "al_dia", "sin_render", "sin_publicar", "problemas"]
