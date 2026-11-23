"""quarto_app/controladores/ayuda.py — «Ayuda de la IA para la entrada…» (Ctrl+Alt+A): copiar el prompt de posts con la
entrada abierta, revisar antes de copiar si lleva datos que no deben salir (C12.3), leer lo que respondió el chat como
cambio sugerido y, al ponerlo en el editor, registrar el uso para «Antes de publicar».

Objetivo: el mismo ciclo que la ayuda por parte de LaTeX Studio (plan «aprender y enseñar», fase 4.5), sin llamar a
  ningún modelo: la ventana copia, la persona pega en su chat y trae la respuesta; lo que acepta lo pone el QML en el
  editor (Ctrl+Z lo deshace, Ctrl+S lo guarda) y el uso queda en `_ia/registro.yml` del post, con su declaración.
Método: el prompt, la revisión y la lectura son de `services/ayuda_ia.py` y corren en hilos (`tareas.funcion`); el
  registro es la orden `registrar_ia --aplicar` del motor de «Antes de publicar» (`services/antes_de_publicar.py`), con
  la ruta del post que el editor tiene abierto. Ningún paso escribe el post.
Límite: un documento que no es una entrada (`.qmd`/`.md`) no tiene ayuda; sin el prompt de posts o sin el módulo común,
  la acción queda apagada con su motivo.
"""
from __future__ import annotations

import json

from gui_comun.qt import QGuiApplication, QObject, Property, Signal, Slot

from quarto_app.services import antes_de_publicar as adp
from quarto_app.services import ayuda_ia


class AyudaIA(QObject):
    cambiado = Signal()
    promptListo = Signal("QVariantMap")          # {prompt, modo, nombre, pone, fuente, aviso, largo} o {error}
    promptRevisado = Signal("QVariantMap")       # {sensible, nivel, hallazgos, porque, fuente} (C12.3)
    pegadoListo = Signal("QVariantMap")          # {ok, errores, avisos, pone, antes, despues, diff}
    registrado = Signal("QVariantMap")           # {uso, total, registro, declaracion, escrito} o {error}

    def __init__(self, documentos, tareas, consola, parent=None):
        super().__init__(parent)
        self.documentos, self.tareas, self.consola = documentos, tareas, consola
        documentos.actualCambiado.connect(self.cambiado)

    @Property(bool, notify=cambiado)
    def disponible(self) -> bool:
        return ayuda_ia.disponible() and bool(adp.post_de(self.documentos.actual))

    @Property(str, notify=cambiado)
    def motivo(self) -> str:
        m = ayuda_ia.motivo_no_disponible()
        if m:
            return m
        return "" if adp.post_de(self.documentos.actual) else "Abre en Escribir el .qmd de la entrada que vas a trabajar."

    @Property("QVariantList", constant=True)
    def modos(self) -> list:
        return ayuda_ia.modos()

    @Property(str, notify=cambiado)
    def post(self) -> str:
        return adp.post_de(self.documentos.actual)

    def _en_hilo(self, nombre: str, trabajo, senal, operacion: str = "lectura") -> None:
        def correr(progress_cb=None, cancel_cb=None, message_cb=None):
            return trabajo()

        def fin(r):
            dato = r if isinstance(r, dict) else {"error": "no respondió"}
            if dato.get("error"):
                self.consola.registrar("warn", f"{nombre}: {dato['error']}")
            senal.emit(dato)
        self.tareas.funcion(nombre, correr, silenciosa=True, operacion=operacion, error=False, al_terminar=fin)

    @Slot(str, str, str)
    def pedirPrompt(self, modo: str, texto: str, seleccion: str) -> None:
        """El prompt de posts en el modo `modo`, con el texto del editor (puede tener cambios sin guardar) y lo seleccionado."""
        ruta = self.post
        if not ruta:
            return
        self._en_hilo("Preparar el prompt", lambda: ayuda_ia.prompt(modo, ruta, texto, seleccion), self.promptListo)

    @Slot(str)
    def revisarPrompt(self, texto: str) -> None:
        """Antes de copiar: si lo que el prompt lleva de la entrada tiene datos de estudiantes o del despacho (C12.3);
        `promptRevisado` trae el resultado."""
        from pathlib import Path
        carpeta = str(Path(self.post).parent) if self.post else ""
        self._en_hilo("Revisar el prompt antes de copiarlo", lambda: ayuda_ia.sensibles(texto, ayuda_ia.cache_dir(), carpeta), self.promptRevisado)

    @Slot(str)
    def copiar(self, texto: str) -> None:
        """El prompt al portapapeles (sin copiarlo al registro de la consola: es largo y es de la persona)."""
        if texto:
            QGuiApplication.clipboard().setText(texto)
            self.consola.registrar("info", f"Prompt de posts copiado ({len(texto)} caracteres)")

    @Slot(str, str, str, str)
    def comprobar(self, modo: str, pegado: str, texto: str, seleccion: str) -> None:
        """Lo pegado, leído contra el texto del editor; `pegadoListo` trae el cambio sugerido."""
        self._en_hilo("Comprobar lo pegado", lambda: ayuda_ia.leer(modo, pegado, texto, seleccion), self.pegadoListo)

    @Slot(str, "QVariantMap", str, str)
    def registrar(self, modo: str, fuente: dict, texto_prompt: str, parte: str) -> None:
        """El uso aceptado, a `_ia/registro.yml` del post y su `_ia/declaracion.md` (`registrar_ia --aplicar`)."""
        ruta = self.post
        if not ruta:
            return
        datos = json.dumps(ayuda_ia.uso(modo, ruta, dict(fuente or {}), texto_prompt, parte), ensure_ascii=False)
        argv = adp.orden("registrar_ia", ruta, datos, aplicar=True)

        def trabajo():
            dato, error = adp.correr(argv)
            return dato if isinstance(dato, dict) else {"error": error or "el motor no respondió"}
        self._en_hilo("Registrar el uso de la IA", trabajo, self.registrado, operacion="escritura")
