"""tests/studio/test_antes_de_publicar.py — «Antes de publicar…» (Ctrl+Alt+E; campo 15 de la norma del flujo de
conocimiento): el servicio que arma las órdenes del motor de escritura (`services/antes_de_publicar.py`), las filas del
diálogo y, en la ventana entera sobre la familia de muestra, la acción, la revisión de una entrada, marcar un punto
manual, la constancia que se detiene con faltas y el veredicto de las entradas de una publicación. El motor es el de
escritura (WRITING_DIR apunta al repo real, que solo se lee); lo que escribe va a la entrada de la muestra. Nada publica."""
from __future__ import annotations

import json

from conftest import REPO, correr_python, entorno_gui, requiere_sistema

ESCRITURA = REPO.parent / "escritura"


def test_entradas_de_una_publicacion(tmp_path):
    from quarto_app.services import antes_de_publicar as adp
    sitio = tmp_path / "sitio"
    (sitio / "posts" / "2026-11-19-a" / "_registro").mkdir(parents=True)
    (sitio / "posts" / "2026-11-19-a" / "index.qmd").write_text("---\ntitle: a\n---\n")
    (sitio / "posts" / "2026-11-19-a" / "g.png").write_bytes(b"x")
    (sitio / "acerca.qmd").write_text("---\ntitle: b\n---\n")
    archivos = [{"archivo": "posts/2026-11-19-a/g.png", "estado": "A"}, {"archivo": "posts/2026-11-19-a/index.qmd", "estado": "M"},
                {"archivo": "acerca.qmd", "estado": "M"}, {"archivo": "_site/index.html", "estado": "M"},
                {"archivo": "styles.css", "estado": "M"}, {"archivo": "posts/viejo/index.qmd", "estado": "D"}]
    assert adp.entradas(sitio, archivos) == [str(sitio / "posts" / "2026-11-19-a" / "index.qmd"), str(sitio / "acerca.qmd")]
    assert adp.veredicto({"listo": True}) == "Listo para publicar" and adp.veredicto({"listo": False, "faltan": 3}) == "Faltan 3"
    assert adp.post_de(str(sitio / "acerca.qmd")) and not adp.post_de(str(sitio / "styles.css"))


def test_filas_del_dialogo():
    from quarto_app.controladores.entrega import filas
    dato = {"carpeta": "/s/posts/a", "sitio": "/s", "grupos": [{"clave": "cifras", "nombre": "Cifras y datos"}, {"clave": "ia", "nombre": "IA"}],
            "controles": [{"id": "cifras", "grupo": "cifras", "nombre": "Cifras vivas", "estado": "aviso", "detalle": "1 número",
                           "porque": "p", "fuente": "Gentzkow y Shapiro (2014)", "hallazgos": [{"archivo": "index.qmd", "linea": 4, "texto": "«1» a mano"}],
                           "medicion": {"corridas": 2, "atrapo": 1, "falsos": 0, "marca": ""}}]}
    f = filas(dato)
    assert [x["tipo"] for x in f] == ["grupo", "control"]                 # un grupo sin controles no sale
    assert f[1]["nivel"] == "activo" and f[1]["hallazgos"][0]["ruta"] == "/s/posts/a/index.qmd"
    assert f[1]["medido"].startswith("Medido: 2 corridas · atrapó 1")
    assert filas({"error": "x"}) == []


VENTANA = """
import sys, json, os, time; sys.path.insert(0, sys.argv[1])
from pathlib import Path
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
piezas = aplicacion.construir(app)
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
ok = app.cargar(aplicacion.QML_DIR / "Main.qml")
a, s, d, e, t, en, pub = (piezas[k] for k in ("acciones", "sitios", "documentos", "editor", "tareas", "entrega", "publicacion"))
def esperar():
    inicio = time.monotonic()
    app.app.processEvents()
    while t.activa and time.monotonic() - inicio < 120:
        app.app.processEvents(); time.sleep(0.05)
    for _ in range(20):
        app.app.processEvents(); time.sleep(0.02)
accion = a.accion("sitio.antes_de_publicar")
antes = accion.habilitada
s.fijarPorNombre("axiomata"); app.app.processEvents()
entrada = next(f["ruta"] for f in d._filas.todas() if f["entrada"])
e.abrir(entrada); app.app.processEvents()
despues = accion.habilitada
en.revisar(); esperar()
filas = en.filas
grupos = [f["nombre"] for f in filas if f["tipo"] == "grupo"]
ids = [f["id"] for f in filas if f["tipo"] == "control"]
veredicto, error = en.veredicto, en.error
marcados = []
en.marcado.connect(lambda dd: marcados.append(dict(dd)))
en.marcar("lista.leido", True, ""); esperar()
registro = Path(entrada).parent / "_registro" / "publicacion.yml"
constancias = []
en.constanciaLista.connect(lambda dd: constancias.append(dict(dd)))
en.darPorRevisado(""); esperar()
cifras = []
en.cifrasListas.connect(lambda dd: cifras.append(dict(dd)))
en.cifras(False); esperar()
en.revisarEntradas([entrada]); esperar()
entradas = en.entradas
QTimer.singleShot(500, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores, "atajo": accion.atajo, "antes": antes, "despues": despues, "grupos": grupos, "ids": ids,
                  "veredicto": veredicto, "error": error, "marcados": marcados, "registro": registro.read_text() if registro.is_file() else "",
                  "constancias": constancias, "cifras": cifras, "entradas": entradas,
                  "menu_sitio": next(m for m in a.menus if m["titulo"] == "&Sitio"), "conflictos": a.conflictos()}))
"""


@requiere_sistema
def test_antes_de_publicar_en_la_ventana(tmp_path, muestra):
    r = correr_python(VENTANA, entorno_gui(tmp_path, muestra, WRITING_DIR=str(ESCRITURA)), plazo=400)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    graves = [x for x in datos["errores"] if "TypeError" in x or "ReferenceError" in x or "is not a type" in x or "DialogoAntesDePublicar" in x]
    assert not graves, "\n".join(graves)
    assert datos["atajo"] == "Ctrl+Alt+E" and not datos["conflictos"], datos["conflictos"]
    assert datos["antes"] is False and datos["despues"] is True          # sin documento abierto no hay qué revisar
    assert not datos["error"], datos["error"]
    assert datos["grupos"][0] == "Cifras y datos" and any(g.startswith("Lista de control") for g in datos["grupos"])
    for c in ("cifras", "lista.leido", "referencias", "citas", "parafrasis", "ia", "alt", "licencia", "html"):
        assert c in datos["ids"], (c, datos["ids"])
    assert datos["veredicto"].startswith("Faltan")
    assert datos["marcados"] and datos["marcados"][0].get("escrito") and "leido:" in datos["registro"]
    assert datos["constancias"] and datos["constancias"][0].get("bloqueado") is True     # con faltas y sin motivo, se detiene
    assert datos["cifras"] and "resultados" in datos["cifras"][0].get("error", "")       # la muestra no declara paquetes
    assert len(datos["entradas"]) == 1 and datos["entradas"][0]["veredicto"].startswith("Faltan")
    assert "sitio.antes_de_publicar" in json.dumps(datos["menu_sitio"])
