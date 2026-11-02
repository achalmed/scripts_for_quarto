"""tests/studio/test_studio.py — Quarto Studio (QML + Kirigami sobre gui-comun 2.x) abre su ventana sin pantalla con el
Python del sistema (o el .venv del studio) sobre la familia de muestra: la ventana entera (acciones, menús, barra,
resumen, el estado de los sitios), cada componente QML, `--smoke`, y las reglas de la familia (sin colores propios, sin
marca dentro, sin QtWidgets, el Python del sistema en main.py e install.sh; ninguna prueba publica)."""
from __future__ import annotations

import json
import re
import subprocess

import pytest

from conftest import PYTHON_SISTEMA, REPO, STUDIO, correr_python, entorno_gui, requiere_quarto, requiere_sistema

QML = STUDIO / "quarto_app" / "qml"

ABRIR = """
import sys, json, os; sys.path.insert(0, sys.argv[1])
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
piezas = aplicacion.construir(app)
piezas["ajustes"].excel = os.environ.get("QUARTO_STUDIO_EXCEL", "")
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
ok = app.cargar(aplicacion.QML_DIR / "Main.qml")
raiz = app.motor.rootObjects()[0] if ok else None
titulo = raiz.property("title") if raiz else ""
a, s, o = piezas["acciones"], piezas["sitios"], piezas["operaciones"]
sin_sitio = (a.accion("op.aplicar").habilitada, a.accion("sitio.nueva_entrada").habilitada, a.accion("archivo.navegador").habilitada)
s.irA("axiomata")
con_sitio = (a.accion("op.simular").habilitada, a.accion("op.aplicar").habilitada, a.accion("op.aplicar").visible, a.accion("sitio.nueva_entrada").habilitada, a.accion("archivo.navegador").habilitada, a.accion("op.simular").textoPlano)
o.fijar("publicar")
publicar = (a.accion("op.aplicar").habilitada, a.accion("op.simular").textoPlano)
s.irA("web")
publicar_web = a.accion("op.aplicar").habilitada
o.fijar("verificar")
leer = (a.accion("op.aplicar").visible, a.accion("op.simular").textoPlano)
QTimer.singleShot(800, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "titulo": titulo, "errores": errores, "acciones": a.nombres(), "menus": [m["titulo"] for m in a.menus], "barra": a.barra,
                  "sin_sitio": sin_sitio, "con_sitio": con_sitio, "publicar": publicar, "publicar_web": publicar_web, "leer": leer,
                  "resumen": piezas["espacio"].resumen, "contexto": piezas["espacio"].contexto, "vista": piezas["espacio"].vista, "sitios": s.nombres}))
"""

COMPONENTE = """
import sys, json, os; sys.path.insert(0, sys.argv[1])
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
aplicacion.construir(app)
app.motor.addImportPath(str(aplicacion.QML_DIR))
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
nombre, carpeta = sys.argv[2], sys.argv[3]
ruta = os.path.join(os.environ["XDG_CACHE_HOME"], "Prueba_" + nombre + ".qml")
os.makedirs(os.path.dirname(ruta), exist_ok=True)
open(ruta, "w").write('import QtQuick\\nimport GuiComun\\nimport "file://%s/%s"\\nVentanaStudio { id: ventana; acciones: studio.acciones; visible: false; %s { id: objeto } }\\n' % (str(aplicacion.QML_DIR), carpeta, nombre))
ok = app.cargar(ruta)
QTimer.singleShot(400, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores}))
"""


RENDER = """
import sys, json, time, os; sys.path.insert(0, sys.argv[1])
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
piezas = aplicacion.construir(app)
s, o, t = piezas["sitios"], piezas["operaciones"], piezas["tareas"]
s.irA("aequilibria"); o.fijar("render")
puede = o.puedeAplicar
ok = o.aplicar()
inicio = time.monotonic()
while t.activa and time.monotonic() - inicio < 300:
    app.app.processEvents(); time.sleep(0.05)
app.app.processEvents()
print(json.dumps({"puede": puede, "ok": ok, "site": os.path.isfile(os.path.join(s.ruta, "_site", "index.html")), "estado": s.estadoClave,
                  "registro": s.registro[:400], "problemas": s.nProblemas, "plan_registro": o.registro[:120], "salida": piezas["consola"].salida.texto[-1500:]}))
app.cerrar()
"""


def _graves(errores):
    return [e for e in errores if "TypeError" in e or "ReferenceError" in e or "is not a type" in e or "Cannot assign" in e or "No se puede asignar" in e]


@requiere_sistema
def test_abre_y_cierra_su_ventana(tmp_path, muestra):
    r = correr_python(ABRIR, entorno_gui(tmp_path, muestra))
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))
    assert datos["sitios"] == ["aequilibria", "axiomata", "chaska", "web"]
    for n in ("archivo.abrir", "archivo.carpeta", "archivo.terminal", "archivo.navegador", "archivo.copiar", "archivo.excel", "editar.filtrar", "editar.todo",
              "ver.vista.sitios", "ver.vista.entradas", "ver.vista.indice", "ver.vista.contenido", "ver.releer",
              "op.simular", "op.aplicar", "op.cancelar", "op.render", "op.publicar", "op.commit", "op.preview", "op.aplicar_excel", "op.indice_sincronizar", "op.contenido_generar",
              "sitio.nueva_entrada", "sitio.entradas", "sitio.problemas", "herr.lanzador", "herr.venv", "ayuda.manual", "ayuda.backend",
              "ventana.navegacion", "ventana.detalles", "ventana.inferior", "ventana.paleta", "app.ajustes", "app.acerca", "app.salir"):
        assert n in datos["acciones"], n
    assert datos["menus"] == ["&Archivo", "&Editar", "&Ver", "&Sitio", "&Flujo", "&Herramientas", "A&justes", "Ay&uda"]
    assert datos["barra"] == ["op.simular", "op.aplicar", "|", "sitio.nueva_entrada"]
    assert datos["sin_sitio"] == [False, False, False]
    assert datos["con_sitio"] == [True, True, True, True, True, "Simular"]          # render: F5 = plan, Ctrl+Intro renderiza
    assert datos["publicar"] == [True, "Simular"]                                    # axiomata: la CLI simula, aplicar confirma
    assert datos["publicar_web"] is False                                            # web tiene problemas: no se publica
    assert datos["leer"] == [False, "Ejecutar"]
    assert datos["resumen"] == "4 sitios · 1 al día · 1 sin render · 1 sin publicar · 1 con problemas"
    assert datos["contexto"].startswith("web · Con problemas") and datos["vista"] == "sitios"


@requiere_sistema
def test_main_smoke(tmp_path, muestra):
    r = subprocess.run([PYTHON_SISTEMA, str(STUDIO / "main.py"), "--smoke"], env=entorno_gui(tmp_path, muestra), capture_output=True, text=True, timeout=180, cwd=tmp_path)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    ruido = [l for l in r.stderr.splitlines() if "TypeError" in l or "ReferenceError" in l or "polish() loop" in l]
    assert not ruido, "\n".join(ruido)


@requiere_sistema
@requiere_quarto
def test_render_real_de_un_sitio_de_la_muestra(tmp_path, muestra_renderizable):
    """Ctrl+Intro de «Renderizar» sobre aequilibria (quarto de verdad, en /var/tmp): escribe su _site/, el estado deja de ser
    «al día» (_site/ cambió sin confirmar) y el registro queda en la caché por sitio. Nada se publica."""
    r = correr_python(RENDER, entorno_gui(tmp_path, muestra_renderizable), plazo=400)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["puede"] and datos["ok"], datos
    assert datos["site"], datos["salida"]
    assert datos["estado"] == "sin_publicar", datos
    assert datos["registro"].startswith("# ") and "render aequilibria" in datos["registro"]
    assert "aplicado" in datos["plan_registro"]
    remoto = subprocess.run(["git", "-C", str(muestra_renderizable.pubs / "aequilibria"), "status", "--porcelain", "--", "_site"], capture_output=True, text=True)
    assert remoto.stdout.strip(), "el render cambió _site/ sin confirmar ni empujar"


COMPONENTES = sorted((p.parent.name, p.stem) for p in QML.glob("*/*.qml"))


@requiere_sistema
@pytest.mark.parametrize("carpeta,nombre", COMPONENTES, ids=[f"{c}/{n}" for c, n in COMPONENTES])
def test_cada_componente_qml(carpeta, nombre, tmp_path, muestra):
    r = correr_python(COMPONENTE, entorno_gui(tmp_path, muestra), nombre, carpeta)
    assert r.returncode == 0, r.stderr[-3000:]
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))


def test_sin_colores_propios_en_qml():
    malos = []
    for qml in QML.rglob("*.qml"):
        for n, linea in enumerate(qml.read_text(encoding="utf-8").splitlines(), 1):
            sin_comentario = linea.split("//")[0]
            if re.search(r'"#[0-9a-fA-F]{3,8}"', sin_comentario) or re.search(r'\bfont\.(pointSize|pixelSize|family)\s*:\s*["\d]', sin_comentario):
                malos.append(f"{qml.relative_to(STUDIO)}:{n}: {linea.strip()}")
    assert not malos, "\n".join(malos)


def test_sin_marca_dentro_de_la_ventana():
    codigo = "\n".join(l.split("//")[0] for l in (QML / "Main.qml").read_text(encoding="utf-8").splitlines())
    assert "logotipo" not in codigo.lower() and "logo_svg" not in codigo and "marca.svg" not in codigo
    assert 'text: "Quarto Studio"' not in codigo and "Kirigami.Heading" not in codigo.split("centro:")[0]


def test_sin_qtwidgets_y_con_el_python_del_sistema():
    for py in (STUDIO / "quarto_app").rglob("*.py"):
        texto = py.read_text(encoding="utf-8")
        assert "QtWidgets" not in texto and "gui_comun.widgets" not in texto and "gui_comun.diseno" not in texto, py
    assert (STUDIO / "main.py").read_text(encoding="utf-8").startswith("#!/usr/bin/python3")
    instalador = (REPO / "install.sh").read_text(encoding="utf-8")
    assert "/usr/bin/python3" in instalador and ".venv" in instalador
    assert "PySide6" not in (REPO / "requirements.txt").read_text(encoding="utf-8").replace("# ", "#")
    assert "ninguna prueba publica" in (REPO / "tests" / "studio" / "test_studio.py").read_text(encoding="utf-8")
