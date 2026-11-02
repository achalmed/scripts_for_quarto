"""quarto_app/controladores/espacio.py — lo transversal: la vista activa (Sitios · Entradas y metadatos · Índice del
vault · Índices de contenido), el filtro de la vista Sitios, el resumen y el contexto de la barra de estado, el título y
las acciones sobre una ruta (abrir con el sistema, Dolphin, terminal, navegador, portapapeles). La vista y el filtro se
recuerdan en QSettings."""
from __future__ import annotations

import os
import shutil
import subprocess

from gui_comun.qt import QGuiApplication, QObject, QSettings, Property, Signal, Slot

from quarto_app.models import filas as mod
from quarto_app.services import operaciones as ops

NOMBRES_VISTAS = ops.NOMBRES_VISTAS


class Espacio(QObject):
    vistaCambiada = Signal()
    filtroCambiado = Signal()
    resumenCambiado = Signal()
    contextoCambiado = Signal()
    aviso = Signal(str, str)

    def __init__(self, consola, ajustes=None, parent=None):
        super().__init__(parent)
        self.consola, self.ajustes = consola, ajustes
        self._s = QSettings()
        self._vista = str(self._s.value("ventana/vista", NOMBRES_VISTAS[0]) or NOMBRES_VISTAS[0])
        if self._vista not in NOMBRES_VISTAS:
            self._vista = NOMBRES_VISTAS[0]
        self._filtro = str(self._s.value("ventana/filtro", "todos") or "todos")
        if self._filtro not in dict(mod.FILTROS):
            self._filtro = "todos"
        self._resumen = self._contexto = ""

    @Property("QVariantList", constant=True)
    def vistas(self) -> list:
        return [{"nombre": n, "texto": t, "icono": i} for n, t, i in ops.VISTAS]

    @Property(str, notify=vistaCambiada)
    def vista(self) -> str:
        return self._vista

    @Property(int, notify=vistaCambiada)
    def indiceVista(self) -> int:
        return NOMBRES_VISTAS.index(self._vista)

    @Property(str, notify=vistaCambiada)
    def textoVista(self) -> str:
        return next(t for n, t, _i in ops.VISTAS if n == self._vista)

    @Slot(str)
    def fijarVista(self, nombre: str) -> None:
        if nombre in NOMBRES_VISTAS and nombre != self._vista:
            self._vista = nombre
            self._s.setValue("ventana/vista", nombre)
            self.vistaCambiada.emit()

    @Slot(int)
    def fijarVistaPorIndice(self, i: int) -> None:
        if 0 <= i < len(NOMBRES_VISTAS):
            self.fijarVista(NOMBRES_VISTAS[i])

    # ------------------------------------------------------------- el filtro de Sitios
    @Property(str, notify=filtroCambiado)
    def filtro(self) -> str:
        return self._filtro

    @Property(str, notify=filtroCambiado)
    def textoFiltro(self) -> str:
        return dict(mod.FILTROS).get(self._filtro, "Todos")

    @Slot(str)
    def fijarFiltro(self, filtro: str) -> None:
        filtro = filtro if filtro in dict(mod.FILTROS) else "todos"
        if filtro != self._filtro:
            self._filtro = filtro
            self._s.setValue("ventana/filtro", filtro)
            self.filtroCambiado.emit()

    # ------------------------------------------------------------- barra de estado
    @Property(str, notify=resumenCambiado)
    def resumen(self) -> str:
        return self._resumen

    @Slot(str)
    def fijarResumen(self, texto: str) -> None:
        if texto != self._resumen:
            self._resumen = texto
            self.resumenCambiado.emit()

    @Property(str, notify=contextoCambiado)
    def contexto(self) -> str:
        return self._contexto

    @Slot(str)
    def fijarContexto(self, texto: str) -> None:
        if texto != self._contexto:
            self._contexto = texto
            self.contextoCambiado.emit()

    # ------------------------------------------------------------- sobre una ruta
    @Slot(str)
    def abrir(self, ruta: str) -> None:
        if ruta and os.path.exists(ruta):
            subprocess.Popen(["xdg-open", ruta])
            self.consola.registrar("info", f"Abierto con el sistema: {ruta}")
        else:
            self.aviso.emit(f"No existe: {ruta or '(nada seleccionado)'}", "aviso")

    @Slot(str)
    def abrirEnlace(self, url: str) -> None:
        if url:
            subprocess.Popen(["xdg-open", url])
            self.consola.registrar("info", f"Enlace: {url}")

    @Slot(str)
    def abrirDolphin(self, ruta: str) -> None:
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if os.path.isdir(carpeta):
            subprocess.Popen(["xdg-open", carpeta])
        else:
            self.aviso.emit(f"No existe la carpeta: {carpeta}", "aviso")

    def _terminal(self) -> str:
        preferido = (self.ajustes.terminal if self.ajustes is not None else "konsole") or "konsole"
        for candidato in (preferido, "konsole", "x-terminal-emulator"):
            if shutil.which(candidato):
                return candidato
        return ""

    @Slot(str)
    def abrirTerminal(self, ruta: str) -> None:
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if not os.path.isdir(carpeta):
            return
        terminal = self._terminal()
        if terminal == "konsole":
            subprocess.Popen(["konsole", "--workdir", carpeta])
        elif terminal:
            subprocess.Popen([terminal], cwd=carpeta)
        else:
            self.aviso.emit("No se encontró un emulador de terminal (konsole).", "aviso")

    @Slot(str)
    def copiar(self, texto: str) -> None:
        if texto:
            QGuiApplication.clipboard().setText(texto)
            self.consola.registrar("info", f"Copiado: {texto}")

    def entradas_paleta(self, _texto: str) -> list[dict]:
        salida = [{"nombre": f"ir.{n}", "texto": f"Ir a {t}", "grupo": "Vistas", "icono": i, "ejecutar": lambda n=n: self.fijarVista(n)}
                  for n, t, i in ops.VISTAS]
        salida += [{"nombre": f"filtro.{f}", "texto": f"Sitios: {t}", "grupo": "Vistas", "icono": "folder-html",
                    "ejecutar": lambda f=f: (self.fijarVista("sitios"), self.fijarFiltro(f))} for f, t in mod.FILTROS if f != "todos"]
        return salida
