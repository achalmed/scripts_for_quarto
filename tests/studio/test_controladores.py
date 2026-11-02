"""tests/studio/test_controladores.py — los controladores de la ventana en proceso (sin QML) sobre la familia de muestra:
espacio (vistas y filtros), sitios (la tabla con su estado, los filtros, el sitio y la entrada actuales, la entrada
nueva), flujo (entradas con el Excel, índice, fragmentos, el elemento), operaciones (la actual por vista, el plan de
render, las órdenes, por qué no se puede aplicar, correr de verdad lo que solo lee sobre la muestra y, con quarto, un
render real). Nada toca el hub ni los pubs reales y nada publica."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from conftest import requiere_binding

from quarto_app.services import operaciones as ops  # noqa: E402


def _esperar(app, tareas, segundos=240):
    inicio = time.monotonic()
    while tareas.activa and time.monotonic() - inicio < segundos:
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()


@pytest.fixture
def piezas(app, muestra_sesion, ajustes_temporales):
    from gui_comun.consola import Consola
    from gui_comun.tareas import Tareas
    from quarto_app.controladores.ajustes import Ajustes
    from quarto_app.controladores.espacio import Espacio
    from quarto_app.controladores.flujo import Flujo
    from quarto_app.controladores.operaciones import Operaciones
    from quarto_app.controladores.sitios import Sitios
    from quarto_app.services import paths
    env = paths.core_env()
    assert Path(env.DOCS_ROOT) == muestra_sesion.raiz, "core/env debe ver la muestra"
    consola = Consola()
    tareas = Tareas(consola)
    ajustes = Ajustes()
    ajustes.excel = str(muestra_sesion.excel or "")
    espacio = Espacio(consola, ajustes)
    sitios = Sitios(espacio, consola, env, cache=ajustes_temporales / "cache" / "studio", docs_dir=muestra_sesion.raiz)
    flujo = Flujo(espacio, sitios, ajustes, consola, hub=muestra_sesion.hub)
    operaciones = Operaciones(espacio, sitios, flujo, ajustes, consola, tareas, cache=ajustes_temporales / "cache" / "studio")
    yield dict(consola=consola, tareas=tareas, espacio=espacio, sitios=sitios, flujo=flujo, operaciones=operaciones, ajustes=ajustes, muestra=muestra_sesion)
    _esperar(app, tareas, 10)


@requiere_binding
def test_sitios_tabla_filtros_y_actual(piezas):
    s, e = piezas["sitios"], piezas["espacio"]
    assert s.total == 4 and s.nombres == ["aequilibria", "axiomata", "chaska", "web"]
    assert s.contadores == {"al_dia": 1, "sin_render": 1, "sin_publicar": 1, "problemas": 1, "todos": 4}
    assert s.resumen.startswith("4 sitios")
    assert [f["nombre"] for f in s.filasNavegacion] == ["sitios", "sitios.al_dia", "sitios.sin_render", "sitios.sin_publicar", "sitios.problemas"]
    assert [f["nombre"] for f in s.filasFlujo] == ["flujo.render", "flujo.publicar"]
    e.fijarFiltro("sin_render")
    assert s.modelo.filas == 1
    e.fijarFiltro("todos")
    assert not s.hayActual
    s.fijarFila(1)
    assert s.nombre == "axiomata" and s.estadoClave == "sin_render" and s.cambios == 1 and s.tema == "Matemática" and s.dominio == "https://axiomata.netlify.app/"
    assert s.rutaCorta == "web/_pubs/axiomata" and s.repo == "achalmed/axiomata" and s.nEntradas == 3 and s.entradasModelo.filas == 3
    assert s.nProblemas == 0 and s.registro == "" and s.hayGit and s.haySite and s.hayQuartoYml
    s.fijarEntradaFila(0)
    assert s.hayEntrada and s.entrada.endswith("index.qmd") and s.entradaNombre.startswith("2026-01-08")
    recibido = []
    s.seleccionar.connect(recibido.append)
    e.fijarVista("entradas")
    assert s.irA("web") and e.vista == "sitios" and s.nombre == "web" and s.estadoClave == "problemas" and s.esHub and recibido == [3]
    assert not s.hayEntrada                                            # la entrada era de otro sitio
    assert s.irA("no-existe") is False
    assert any(x["texto"] == "Sitio: chaska" for x in s.entradas_paleta(""))
    assert s.carpetasDeEntradas() == ["blog/posts"]


@requiere_binding
def test_sitios_entrada_nueva(piezas):
    s = piezas["sitios"]
    s.fijarPorNombre("chaska")
    error = s.crearEntrada({"titulo": "", "carpeta_posts": "posts"})
    assert error == "El título es obligatorio."
    error = s.crearEntrada({"titulo": "Una entrada de prueba", "carpeta_posts": "posts", "tags": "quarto, prueba", "categorias": "Muestra", "lang": "es", "formato_pdf": False})
    assert error == ""
    ruta = Path(s.entrada)
    assert ruta.is_file() and ruta.parent.name.endswith("-una-entrada-de-prueba") and (ruta.parent / "references.bib").is_file()
    texto = ruta.read_text(encoding="utf-8")
    assert 'title: "Una entrada de prueba"' in texto and 'tags: ["quarto", "prueba"]' in texto and "apaquarto-pdf" not in texto
    assert s.nEntradas == 2 and s.estadoClave == "sin_render"            # una fuente nueva sin confirmar


@requiere_binding
def test_flujo_entradas_excel_indice_y_contenido(piezas):
    f, s = piezas["flujo"], piezas["sitios"]
    c = f.contadores
    assert c["entradas"] >= 7 and c["indice"] == 2 and c["indice_rotos"] == 1 and c["contenido"] == 1
    assert [x["nombre"] for x in f.filasNavegacion] == ["entradas", "indice", "contenido"]
    m = f.modeloDe("entradas")
    fila_axiomata = next(i for i in range(m.filas) if s.nombre != "axiomata" and f._tablas["entradas"].fila(m.filaOrigen(i))["carpeta"] == "2026-01-08-matrices-y-determinantes")
    f.fijarFila("entradas", fila_axiomata)
    assert f.hayElemento and f.vistaElemento == "entradas" and f.elementoTitulo == "Matrices y determinantes"
    assert s.nombre == "axiomata" and s.entrada.endswith("2026-01-08-matrices-y-determinantes/index.qmd")
    if piezas["muestra"].excel:
        assert f.hayExcel and f.enExcel and f.nDiferencias >= 1 and any(x["campo"] == "title" and x["difiere"] for x in f.comparacion)
    assert any(x["campo"] == "title" for x in f.frontmatterCampos)
    f.fijarFila("indice", 0)
    assert f.elementoTitulo == "2026-01-01-borrado" and f.elementoSubtitulo.startswith("2026 → ")
    f.fijarFila("contenido", 0)
    assert f.elementoTexto.startswith("<!-- fragmento") and s.nombre == "axiomata"
    f.fijarFila("contenido", -1)
    assert not f.hayElemento


@requiere_binding
def test_operaciones_actual_ordenes_y_disponibilidad(piezas):
    o, s, e = piezas["operaciones"], piezas["sitios"], piezas["espacio"]
    e.fijarVista("sitios")
    assert o.actual == "render" and o.escribe and o.verbo == "Simular" and o.sobreSitio
    assert "Elige primero un sitio" in o.motivoNoSimular and not o.puedeAplicar
    s.fijarPorNombre("axiomata")
    assert o.puedeSimular and o.puedeAplicar and o.ordenSimular.startswith("(el plan") and o.ordenAplicar == "bash backend/script_blogs_manager/main.sh render axiomata"
    assert o.simular() is True                                         # el plan de la ventana, sin correr nada
    assert "sin confirmar (1)" in o.plan and not o.enCurso
    o.fijar("publicar")
    assert o.publica and o.ordenSimular.endswith("publish axiomata") and o.ordenAplicar.endswith("publish axiomata --aplicar")
    assert "axiomata → https://axiomata.netlify.app/" in o.textoConfirmacion and "Netlify" in o.queToca
    s.fijarPorNombre("web")
    assert not o.puedeAplicar and "problemas" in o.motivoNoAplicar
    o.fijar("commit")
    assert o.entradaTipo == "texto"
    o.fijarValor("mi mensaje")
    assert o.valor == "mi mensaje" and o.ordenAplicar.endswith("git-commit web 'mi mensaje' --aplicar")
    o.fijar("preview")
    assert o.larga and o.verbo == "Arrancar" and not o.escribe
    o.fijar("aplicar_excel")
    assert e.vista == "entradas" and o.indiceActual == [x.id for x in ops.de_vista("entradas")].index("aplicar_excel")
    assert "--dry-run" in o.ordenSimular and "--dry-run" not in o.ordenAplicar
    o.fijar("yaml_carpeta")
    assert o.valor == s.ruta                                            # el defecto: la carpeta del sitio actual
    e.fijarVista("sitios")
    assert o.actual == "preview"                                        # se recuerda por vista
    assert any(x["texto"] == "Operación: Publicar" for x in o.entradas_paleta(""))


@requiere_binding
def test_correr_lo_que_solo_lee_sobre_la_muestra(piezas, app):
    """`main.sh check` y `--check-broken` de verdad sobre la muestra; `format_yaml --dry-run` sobre una entrada."""
    o, s, tareas, consola = piezas["operaciones"], piezas["sitios"], piezas["tareas"], piezas["consola"]
    terminadas = []
    o.terminada.connect(lambda i, a, c: terminadas.append((i, a, c)))
    s.fijarPorNombre("aequilibria")
    o.fijar("verificar")
    assert o.simular() is True and o.enCurso
    assert o.simular() is False
    _esperar(app, tareas)
    assert terminadas[-1][0] == "verificar" and terminadas[-1][1] is False
    assert s.registro.startswith("# ") and "main.sh check aequilibria" in s.registro
    o.fijar("indice_rotos")
    assert o.simular() is True
    _esperar(app, tareas)
    assert terminadas[-1][0] == "indice_rotos" and "2026-01-01-borrado" in o.plan
    o.fijar("yaml_archivo")
    s.fijarPorNombre("aequilibria")
    s.fijarEntradaFila(0)
    o.fijarValor(s.entrada)
    antes = Path(s.entrada).read_text(encoding="utf-8")
    assert o.simular() is True
    _esperar(app, tareas)
    assert terminadas[-1][0] == "yaml_archivo" and Path(s.entrada).read_text(encoding="utf-8") == antes
    assert any("fix_qmd_files.py" in l or "main.py" in l for l in consola.salida.texto.splitlines())
