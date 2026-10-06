"""test_gui_blog_service.py — la GUI simula antes y pasa `--aplicar` solo al confirmar (ola 4, Q2).

Corre en un proceso aparte con `QT_QPA_PLATFORM=offscreen` y `XDG_CONFIG_HOME` temporal (QSettings no toca la
configuración del autor). No abre ventanas ni lanza procesos: un `MainController` falso recoge los `Command`.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

import pytest

from conftest import RAIZ_REPO

pytestmark = pytest.mark.skipif(importlib.util.find_spec("PySide6") is None, reason="sin PySide6")

GUION = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from PySide6.QtCore import QCoreApplication, QObject, Signal
app = QCoreApplication([])
from app.models.operation import Operacion
from app.services import blog_service
from app.controllers.blogs_controller import BlogsController

class Runner(QObject):
    terminado = Signal(object)

class Principal(QObject):
    def __init__(self):
        super().__init__(); self.runner = Runner(); self.lanzados = []
    def ejecutar(self, cmd):
        self.lanzados.append(cmd); return True

salida = {
    "publish": blog_service.publish("pub_x").args[1:],
    "publish_aplicar": blog_service.publish("pub_x", aplicar=True).args[1:],
    "publish_destino": blog_service.publish("pub_x", "netlify").args[1:],
    "commit": blog_service.git_commit("pub_x", "m").args[1:],
    "commit_aplicar": blog_service.git_commit("pub_x", "m", aplicar=True).args[1:],
}
p = Principal(); ctl = BlogsController(p)
propuestas = []
ctl.aplicacion_propuesta.connect(lambda pregunta, cmd: propuestas.append(cmd))
ctl.publish("pub_x")
salida["lanzado_primero"] = p.lanzados[0].args[1:]
p.runner.terminado.emit(Operacion("x", p.lanzados[0].linea(), 1, 0.1))        # simulación fallida
salida["propuestas_tras_fallo"] = len(propuestas)
ctl.git_commit("pub_x", "m")
p.runner.terminado.emit(Operacion("x", p.lanzados[1].linea(), 0, 0.1))        # simulación correcta
salida["propuesta"] = propuestas[0].args[1:] if propuestas else None
ctl.aplicar(propuestas[0])
salida["lanzado_al_confirmar"] = p.lanzados[-1].args[1:]
print(json.dumps(salida))
"""


def test_simula_y_aplica_solo_al_confirmar(workspace):
    r = subprocess.run([sys.executable, "-c", GUION, str(RAIZ_REPO)], env=workspace.env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    s = json.loads(r.stdout.strip().splitlines()[-1])
    assert s["publish"] == ["publish", "pub_x"]                     # sin destino: git push, sin gh-pages
    assert s["publish_aplicar"] == ["publish", "pub_x", "--aplicar"]
    assert s["publish_destino"] == ["publish", "pub_x", "netlify"]
    assert s["commit"] == ["git-commit", "pub_x", "m"]
    assert s["commit_aplicar"] == ["git-commit", "pub_x", "m", "--aplicar"]
    assert "--aplicar" not in s["lanzado_primero"]
    assert s["propuestas_tras_fallo"] == 0                          # si la simulación falla, no se ofrece aplicar
    assert s["propuesta"] == ["git-commit", "pub_x", "m", "--aplicar"]
    assert s["lanzado_al_confirmar"] == ["git-commit", "pub_x", "m", "--aplicar"]
