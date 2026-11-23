"""tests/studio/test_ayuda_ia.py — «Ayuda de la IA para la entrada…» (Ctrl+Alt+A; plan «aprender y enseñar», fase 4.5): el
servicio que arma el prompt de posts con la entrada y lee lo pegado (`services/ayuda_ia.py`, por el módulo común de core)
y, en la ventana entera sobre la familia de muestra, la acción, el prompt, el cambio sugerido y el uso registrado en
`_ia/registro.yml` de la entrada, que es lo que pide «Antes de publicar». El prompt es el del repo de prompts y el motor
el de escritura (los dos se leen; lo que escribe el motor va a la entrada de la muestra). Ningún modelo se llama."""
from __future__ import annotations

import json

import pytest

from conftest import REPO, correr_python, entorno_gui, requiere_sistema

PROMPTS = REPO.parent / "prompts"
ESCRITURA = REPO.parent / "escritura"
POST = ("---\ntitle: \"El salario mínimo en Ayacucho\"\ndate: 2026-11-20\nauthor:\n  - name: Edison Achalma\ncategories: [economía]\n"
        "citation: true\n---\n\n## Qué cambió\n\nUn borrador de la sección.\n")

pytestmark = pytest.mark.skipif(not (PROMPTS / "07 produccion" / "contenido_web").is_dir(), reason="sin el repo de prompts")


@pytest.fixture()
def servicio(monkeypatch, muestra_sesion):
    monkeypatch.setenv("PROMPTS_DIR", str(PROMPTS))
    monkeypatch.setenv("WRITING_DIR", str(ESCRITURA))
    from quarto_app.services import ayuda_ia
    if ayuda_ia.comun() is None:
        pytest.skip("sin core/py-common/ia_externa.py")
    return ayuda_ia


def test_el_prompt_de_posts_con_la_entrada(servicio):
    assert servicio.disponible(), servicio.motivo_no_disponible()
    assert [m["clave"] for m in servicio.modos()] == ["seccion", "introduccion", "metadatos", "auditoria", "leccion"]
    p = servicio.prompt("seccion", "/s/posts/2026-11-20-salario/index.qmd", POST, "## Qué cambió\n\nUn borrador de la sección.")
    assert not p.get("error"), p
    assert p["fuente"]["ruta"] == servicio.PROMPT_POST and p["fuente"]["version"]
    assert not p["prompt"].startswith("---"), "sin el frontmatter del prompt"
    assert "Modo: sección." in p["prompt"] and "«El salario mínimo en Ayacucho»" in p["prompt"]
    assert "lo que la persona seleccionó" in p["prompt"] and "Edison Achalma" in p["prompt"] and "```markdown" in p["prompt"]
    assert "Un borrador de la sección." in p["entrada"] and "Rol" not in p["entrada"], "se revisa solo lo que va de la entrada"
    m = servicio.prompt("metadatos", "/s/posts/x/index.qmd", POST)
    assert "Frontmatter actual" in m["prompt"] and "citation: true" in m["prompt"] and "```yaml" in m["prompt"]
    assert servicio.prompt("otro", "/s/x.qmd", POST)["error"]


LECCION = ("---\ntitle: \"Regresión simple\"\ncurso: econometria-i\ntema: \"1.2\"\n---\n\n## Objetivos\n\nPor escribir.\n")


def test_la_leccion_con_su_prompt_y_el_esqueleto(servicio, monkeypatch):
    if not (PROMPTS / servicio.PROMPT_LECCION).is_file():
        pytest.skip("sin el prompt 05/05")
    pedidos = []

    def falso(curso, tema, timeout=60):
        pedidos.append((curso, tema))
        return "## Objetivos\n- R1: estimar e interpretar la pendiente", ""
    monkeypatch.setattr(servicio, "esqueleto_leccion", falso)
    p = servicio.prompt("leccion", "/s/cursos/econometria-i/1-2/index.qmd", LECCION)
    assert not p.get("error"), p
    assert pedidos == [("econometria-i", "1.2")], "el curso y el tema salen del frontmatter"
    assert p["fuente"]["ruta"] == servicio.PROMPT_LECCION and p["fuente"]["version"]
    assert "leccion.py proponer econometria-i 1.2" in p["prompt"] and "R1: estimar" in p["entrada"]
    assert "Por escribir." in p["entrada"] and "Modo:" not in p["entrada"]
    assert "Para decidir o comprobar" in p["prompt"], "el formato de vuelta es el de la lección"
    sin = servicio.prompt("leccion", "/s/posts/x/index.qmd", POST)
    assert "no declara `curso:` y `tema:`" in sin["entrada"] and len(pedidos) == 1
    r = servicio.leer("leccion", "```markdown\n## Objetivos\n\nEstimar la pendiente [VERIFICAR].\n```\n\nPara decidir: la cifra.", LECCION)
    assert r["ok"] and r["pone"] == "cursor" and any("pendiente" in a for a in r["avisos"])
    u = servicio.uso("leccion", "/s/x/index.qmd", p["fuente"], p["prompt"])
    assert "prompt de la lección" in u["resumen"] and u["prompt"]["ruta"] == servicio.PROMPT_LECCION


def test_la_declaracion_se_incluye_una_sola_vez(servicio):
    r = servicio.incluir_declaracion(POST)
    assert r["cambiado"] and r["texto"].endswith("\n\n{{< include _ia/declaracion.md >}}\n") and r["texto"].startswith(POST.rstrip())
    otra = servicio.incluir_declaracion(r["texto"])
    assert not otra["cambiado"] and otra["texto"] == r["texto"]
    assert not servicio.incluir_declaracion("Texto\n\n{{<include  _ia/declaracion.md>}}\n")["cambiado"]
    assert servicio.incluir_declaracion("")["texto"] == "{{< include _ia/declaracion.md >}}\n"


def test_lo_pegado_como_cambio_sugerido(servicio):
    r = servicio.leer("seccion", "Aquí va:\n\n```markdown\n## Qué cambió en 2026\n\nTexto nuevo {cita APA pendiente: buscar «salario»}.\n```\n\n"
                      "| Criterio | Valor |", POST, "Un borrador de la sección.")
    assert r["ok"] and r["pone"] == "cursor" and r["antes"] == "Un borrador de la sección."
    assert r["despues"].startswith("## Qué cambió en 2026") and "| Criterio" in r["resto"]
    assert any("pendiente" in a for a in r["avisos"])
    sin = servicio.leer("introduccion", "Sin bloque, solo prosa.", POST)
    assert not sin["ok"] and "```markdown" in sin["errores"][0]
    fm = servicio.leer("metadatos", "```yaml\n---\ntitle: Salario mínimo: lo que cambió\ndate: 2026-11-20\n---\n```", POST)
    assert fm["ok"] and fm["pone"] == "frontmatter" and fm["antes"].startswith("---\ntitle:") and fm["despues"].startswith("---\n")
    assert any("comillas" in a for a in fm["avisos"]) and any("`citation`" in a for a in fm["avisos"])
    assert not servicio.leer("metadatos", "```yaml\n---\nfecha: hoy\n---\n```", POST)["ok"], "sin title no es un frontmatter"
    assert servicio.leer("auditoria", "1. La cifra del INEI no tiene año.", POST)["pone"] == "nada"
    u = servicio.uso("introduccion", "/s/posts/x/index.qmd", {"titulo": "T", "ruta": servicio.PROMPT_POST, "version": "3"}, "el prompt")
    assert u["archivo"] == "index.qmd" and u["prompt"]["texto"] == "el prompt" and "la puso en la entrada" in u["resumen"]


def test_antes_de_copiar_se_revisa(servicio, tmp_path):
    r = servicio.sensibles("Corrige esto. Notas de Juana, DNI 45678912.", tmp_path / "cache")
    assert r["sensible"] and r["nivel"] == "alto"
    assert not servicio.sensibles("Corrige esto.", tmp_path / "cache")["sensible"]


VENTANA = """
import sys, json, time; sys.path.insert(0, sys.argv[1])
from pathlib import Path
from quarto_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("quarto-studio", "Quarto Studio", version="prueba", organizacion="quarto-studio-pruebas", nombre_ajustes="Quarto Studio pruebas")
piezas = aplicacion.construir(app)
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
ok = app.cargar(aplicacion.QML_DIR / "Main.qml")
a, s, d, e, t, ay, esp = (piezas[k] for k in ("acciones", "sitios", "documentos", "editor", "tareas", "ayuda", "espacio"))
def esperar():
    inicio = time.monotonic()
    app.app.processEvents()
    while t.activa and time.monotonic() - inicio < 120:
        app.app.processEvents(); time.sleep(0.05)
    for _ in range(20):
        app.app.processEvents(); time.sleep(0.02)
accion = a.accion("herr.ayuda_ia")
antes = accion.habilitada
esp.fijarArea("escribir")
s.fijarPorNombre("axiomata"); app.app.processEvents()
entrada = next(f["ruta"] for f in d._filas.todas() if f["entrada"])
e.abrir(entrada); app.app.processEvents()
despues = accion.habilitada
texto = Path(entrada).read_text(encoding="utf-8")
prompts, pegados, registros = [], [], []
ay.promptListo.connect(lambda x: prompts.append(dict(x)))
ay.pegadoListo.connect(lambda x: pegados.append(dict(x)))
ay.registrado.connect(lambda x: registros.append(dict(x)))
ay.pedirPrompt("introduccion", texto, ""); esperar()
ay.comprobar("introduccion", "```markdown\\nUna introducción nueva.\\n```", texto, ""); esperar()
p = prompts[0] if prompts else {}
ay.registrar("introduccion", p.get("fuente") or {}, p.get("prompt") or "", ""); esperar()
registro = Path(entrada).parent / "_ia" / "registro.yml"
declaracion = Path(entrada).parent / "_ia" / "declaracion.md"
QTimer.singleShot(400, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores, "atajo": accion.atajo, "antes": antes, "despues": despues,
                  "prompt": {k: v for k, v in p.items() if k != "prompt"}, "largo": len(p.get("prompt") or ""), "pegado": pegados[0] if pegados else {},
                  "registros": registros, "registro": registro.read_text() if registro.is_file() else "", "declaracion": declaracion.is_file(),
                  "menu": next(m for m in a.menus if m["titulo"] == "&Herramientas"), "conflictos": a.conflictos(),
                  "sin_cambios": Path(entrada).read_text(encoding="utf-8") == texto}))
"""


@requiere_sistema
def test_la_ayuda_en_la_ventana(tmp_path, muestra):
    r = correr_python(VENTANA, entorno_gui(tmp_path, muestra, WRITING_DIR=str(ESCRITURA), PROMPTS_DIR=str(PROMPTS)), plazo=300)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    graves = [x for x in datos["errores"] if "TypeError" in x or "ReferenceError" in x or "is not a type" in x or "DialogoAyudaIA" in x]
    assert not graves, "\n".join(graves)
    assert datos["atajo"] == "Ctrl+Alt+A" and not datos["conflictos"], datos["conflictos"]
    assert datos["antes"] is False and datos["despues"] is True          # sin una entrada abierta no hay qué pedir
    assert not datos["prompt"].get("error") and datos["prompt"]["fuente"]["ruta"].endswith("prompt_01_metadatos_y_seo_del_post.md")
    assert datos["largo"] > 2000
    assert datos["pegado"]["ok"] and datos["pegado"]["despues"].startswith("Una introducción nueva.")
    assert datos["registros"] and datos["registros"][0].get("escrito"), datos["registros"]
    assert "prompt_01_metadatos_y_seo_del_post" in datos["registro"] and "huella" in datos["registro"] and datos["declaracion"]
    assert datos["sin_cambios"], "ninguna orden escribe la entrada"
    assert "herr.ayuda_ia" in json.dumps(datos["menu"])
