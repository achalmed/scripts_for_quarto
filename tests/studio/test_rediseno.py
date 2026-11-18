"""tests/studio/test_rediseno.py — la forma de escritor aprobada el 2026-11-18: el árbol de sitios y entradas, el botón
principal «Renderizar este archivo» (Ctrl+Mayús+K, N 5.16) con el sitio entero en Ctrl+Mayús+B, la franja de abajo (el
estado del render y los sitios con cambios sin publicar), la dirección publicada de la vista previa y la regla de la
familia (cero colores, radios y tamaños de letra propios en QML). Todo sobre la familia de muestra; el render real es de
un solo archivo de la muestra, en /var/tmp; nada se publica."""
from __future__ import annotations

import json
import re

from conftest import STUDIO, correr_python, entorno_gui, requiere_binding, requiere_quarto, requiere_sistema

QML = STUDIO / "quarto_app" / "qml"

PROYECTOS = [{"nombre": "web", "esHub": True, "clave": "problemas", "estado": "Con problemas", "motivo": "m", "entradas": 1, "dominio": ""},
             {"nombre": "axiomata", "esHub": False, "clave": "sin_render", "estado": "Cambios sin render", "motivo": "m", "entradas": 2,
              "dominio": "axiomata.netlify.app"}]
DOCS = [{"ruta": "/s/_quarto.yml", "rel": "_quarto.yml", "nombre": "_quarto.yml", "carpeta": "(raíz del sitio)", "titulo": "", "fecha": "", "entrada": False},
        {"ruta": "/s/posts/2026-01-08-a/index.qmd", "rel": "posts/2026-01-08-a/index.qmd", "nombre": "index.qmd", "carpeta": "posts/2026-01-08-a",
         "titulo": "Matrices", "fecha": "2026-01-08", "entrada": True},
        {"ruta": "/s/posts/2025-12-02-b/index.qmd", "rel": "posts/2025-12-02-b/index.qmd", "nombre": "index.qmd", "carpeta": "posts/2025-12-02-b",
         "titulo": "Límites", "fecha": "2025-12-02", "entrada": True}]


@requiere_binding
def test_arbol_de_sitios_y_entradas():
    from quarto_app.controladores.arbol import filas_arbol, grupo_de
    assert grupo_de(DOCS[1]) == "posts" and grupo_de(DOCS[0]) == "(raíz del sitio)"
    filas = filas_arbol(PROYECTOS, "axiomata", DOCS)
    assert [(f["tipo"], f["nivel"], f["texto"]) for f in filas] == [
        ("sitio", 0, "web (hub)"), ("sitio", 0, "axiomata"),
        ("carpeta", 1, "(raíz del sitio)"), ("documento", 2, "_quarto.yml"),
        ("carpeta", 1, "posts"), ("documento", 2, "Matrices"), ("documento", 2, "Límites")]
    assert filas[1]["abierta"] and not filas[0]["abierta"]
    assert filas[5]["detalle"] == "2026-01-08"                       # una entrada: su título y su fecha
    # plegar el sitio actual o una carpeta; filtrar abre lo que coincide
    assert [f["tipo"] for f in filas_arbol(PROYECTOS, "axiomata", DOCS, plegadas={"sitio:axiomata"})] == ["sitio", "sitio"]
    plegada = filas_arbol(PROYECTOS, "axiomata", DOCS, plegadas={"carpeta:axiomata:posts"})
    assert [f["texto"] for f in plegada if f["tipo"] == "documento"] == ["_quarto.yml"]
    filtrada = filas_arbol(PROYECTOS, "axiomata", DOCS, texto="lími", plegadas={"carpeta:axiomata:posts"})
    assert [f["texto"] for f in filtrada if f["tipo"] != "sitio"] == ["posts", "Límites"]


def test_renderizar_este_archivo_en_el_catalogo(tmp_path):
    from quarto_app.services import operaciones as ops
    qmd = tmp_path / "index.qmd"
    qmd.write_text("---\ntitle: x\n---\n", encoding="utf-8")
    o = ops.operacion("render_archivo")
    assert o is not None and o.escribe and o.sobre_archivo and o.sobre_sitio and not o.publica
    orden = ops.texto_orden(o.orden_aplicar(ops.Contexto(sitio="axiomata", archivo=str(qmd))))
    assert "render-post" in orden and orden.endswith(str(qmd))
    assert "N 5.16" in o.plan(ops.Contexto(sitio="axiomata", archivo=str(qmd)))
    assert ops.renderizable(str(qmd)) and not ops.renderizable(str(tmp_path / "_quarto.yml")) and not ops.renderizable("")


VENTANA = """
import sys, json, os; sys.path.insert(0, sys.argv[1])
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
piezas = aplicacion.construir(app)
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
ok = app.cargar(aplicacion.QML_DIR / "Main.qml")
a, s, d, e, o, arbol = (piezas[k] for k in ("acciones", "sitios", "documentos", "editor", "operaciones", "arbol"))
atajos = {n: a.accion(n).atajo for n in ("sitio.renderizar_archivo", "sitio.renderizar")}
sin_doc = a.accion("sitio.renderizar_archivo").habilitada
o.fijar("render"); puede = o.puedeSimular; motivo = o.motivoNoSimular        # sin sitio: no se puede simular
if not puede:
    o.simular(); app.app.processEvents()
pista = app.motor.rootObjects()[0].property("footer").property("textoDerecha")
s.fijarPorNombre("axiomata"); app.app.processEvents()
tipos = [arbol._modelo.fila(i)["tipo"] for i in range(arbol.filas)]
entrada = next(f["ruta"] for f in d._filas.todas() if f["entrada"])
yml = next(f["ruta"] for f in d._filas.todas() if f["nombre"] == "_quarto.yml")
e.abrir(yml); app.app.processEvents()
con_yml = (a.accion("sitio.renderizar_archivo").habilitada, o.contexto().archivo == yml)
e.abrir(entrada); app.app.processEvents()
con_entrada = a.accion("sitio.renderizar_archivo").habilitada
o.fijar("render_archivo")
orden = o.ordenAplicar
pendientes = [(p["nombre"], p["clave"]) for p in s.pendientes]
QTimer.singleShot(800, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores, "atajos": atajos, "sin_doc": sin_doc, "puede": puede, "motivo": motivo, "pista": pista, "tipos": tipos, "con_yml": con_yml, "con_entrada": con_entrada,
                  "orden": orden, "entrada": entrada, "pendientes": pendientes, "url": d.urlPublicada, "conflictos": a.conflictos(),
                  "menu_sitio": next(m for m in a.menus if m["titulo"] == "&Sitio")}))
"""


@requiere_sistema
def test_ventana_de_escritor(tmp_path, muestra):
    r = correr_python(VENTANA, entorno_gui(tmp_path, muestra))
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    graves = [x for x in datos["errores"] if "TypeError" in x or "ReferenceError" in x or "is not a type" in x]
    assert not graves, "\n".join(graves)
    assert datos["atajos"] == {"sitio.renderizar_archivo": "Ctrl+Shift+K", "sitio.renderizar": "Ctrl+Shift+B"}
    assert not datos["conflictos"], datos["conflictos"]
    assert datos["sin_doc"] is False                                  # sin documento abierto no hay archivo que renderizar
    # el motivo de no poder simular es una pista (gui-comun 4.1): a la barra de estado, no a las notificaciones
    assert datos["puede"] is False and "Elige primero un sitio" in datos["motivo"] and datos["pista"] == datos["motivo"]
    assert datos["tipos"][:4].count("sitio") >= 1 and "carpeta" in datos["tipos"] and "documento" in datos["tipos"]
    assert datos["con_yml"] == [False, True]                           # _quarto.yml no se renderiza solo
    assert datos["con_entrada"] is True
    assert "render-post" in datos["orden"] and datos["orden"].endswith(datos["entrada"])
    assert ["chaska", "sin_publicar"] in datos["pendientes"] and ["axiomata", "sin_render"] in datos["pendientes"]
    assert all(c in ("sin_publicar", "sin_render") for _n, c in datos["pendientes"])
    assert datos["url"].startswith("https://axiomata.netlify.app/posts/") and datos["url"].endswith("/")


RENDER_ARCHIVO = """
import sys, json, time, os; sys.path.insert(0, sys.argv[1])
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
piezas = aplicacion.construir(app)
a, s, d, e, o, t = (piezas[k] for k in ("acciones", "sitios", "documentos", "editor", "operaciones", "tareas"))
s.fijarPorNombre("aequilibria"); app.app.processEvents()
entrada = next(f["ruta"] for f in d._filas.todas() if f["entrada"])
e.abrir(entrada); app.app.processEvents()
version = d.version
a.accion("sitio.renderizar_archivo").disparar()
inicio = time.monotonic()
while t.activa and time.monotonic() - inicio < 300:
    app.app.processEvents(); time.sleep(0.05)
app.app.processEvents()
html = os.path.join(os.path.dirname(entrada).replace(s.ruta, os.path.join(s.ruta, "_site"), 1), "index.html")
print(json.dumps({"render": o.ultimoRender, "version": d.version > version, "html": os.path.isfile(html), "propia": d.paginaDelDocumento,
                  "salida": piezas["consola"].salida.texto[-1500:]}))
app.cerrar()
"""


@requiere_sistema
@requiere_quarto
def test_render_real_de_un_archivo_de_la_muestra(tmp_path, muestra_renderizable):
    """El botón principal sobre una entrada de aequilibria (quarto de verdad, en /var/tmp): renderiza solo ese archivo, la
    vista previa se recarga y la franja de abajo tiene su resultado. Nada se publica."""
    r = correr_python(RENDER_ARCHIVO, entorno_gui(tmp_path, muestra_renderizable), plazo=400)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["render"].get("id") == "render_archivo" and datos["render"].get("codigo") == 0, datos
    assert datos["render"]["sitio"] == "aequilibria"
    assert datos["version"] and datos["html"] and datos["propia"], datos["salida"]


PROHIBIDO = re.compile(r'"#[0-9a-fA-F]{3,8}"|Qt\.(rgba|rgb|hsla|hsva|lighter|darker|tint)\s*\(|\bradius\s*:|\bfont\.(pointSize|pixelSize|family)\s*:')


def test_qml_sin_colores_radios_ni_letra_propios():
    malos = []
    for qml in QML.rglob("*.qml"):
        for n, linea in enumerate(qml.read_text(encoding="utf-8").splitlines(), 1):
            if PROHIBIDO.search(linea.split("//")[0]):
                malos.append(f"{qml.relative_to(STUDIO)}:{n}: {linea.strip()}")
    assert not malos, "\n".join(malos)


def test_avisos_por_la_base():
    """Los avisos van por `ventana.mensajes` (gui-comun: sin acciones, a las notificaciones de KDE); ningún aviso propio."""
    for qml in QML.rglob("*.qml"):
        texto = qml.read_text(encoding="utf-8")
        assert "Popup {" not in texto and "ToolTip.show(" not in texto and "Toast" not in texto, qml
