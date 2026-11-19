"""quarto_app/controladores/entrega.py — «Antes de publicar…» (Ctrl+Alt+E): los controles del flujo de conocimiento sobre la
entrada abierta (campo 15 de la norma, C15.1 a C15.8), los puntos manuales que el autor marca, «Traer las cifras» del
paquete de datafw y la constancia de que se revisó antes de publicar.

Objetivo: cerrar la cadena de evidencia de un post sin salir de la ventana, como «Antes de entregar» de LaTeX Studio:
  ver cada control con su estado, su porqué con la fuente y sus hallazgos (un clic lleva al archivo y la línea), marcar
  o justificar lo manual y saber si está «Listo para publicar». En la vista de publicación, el veredicto de cada entrada
  que la publicación lleva.
Método: corre en hilos las órdenes de `escritura/scripts/antes_de_publicar.py` (`services/antes_de_publicar.py`): `revisar`
  (o `medir --aplicar` con «Revisar de nuevo», que anota la corrida, C14.1/C15.8), `marcar --aplicar` al tocar la casilla
  o guardar la nota (el clic es la confirmación), `falso --aplicar`, `cifras` (simula) y `cifras --aplicar` tras ver lo
  que cambia, `constancia` (con «Faltan N» pide el motivo) y `resumen` de las entradas de una publicación.
Límite: la ventana no sabe qué es una cifra viva ni qué lista corresponde: lo dice el motor de escritura. Sin escritura,
  la acción queda apagada con su motivo.
"""
from __future__ import annotations

from pathlib import Path

from gui_comun.qt import QObject, Property, Signal, Slot

from quarto_app.services import antes_de_publicar as adp

NIVEL = {"ok": "positivo", "aviso": "activo", "falla": "negativo", "manual": "neutro"}
ICONO = {"ok": "dialog-ok", "aviso": "dialog-warning", "falla": "dialog-error", "manual": "checkbox"}


def filas(dato: dict) -> list[dict]:
    """Los controles del motor, por grupo, como filas para la lista del diálogo (con la ruta absoluta de cada hallazgo)."""
    if not dato or dato.get("error"):
        return []
    carpeta, sitio = Path(dato.get("carpeta", "")), Path(dato.get("sitio") or dato.get("carpeta", ""))
    salida = []
    for g in dato.get("grupos", []):
        controles = [c for c in dato.get("controles", []) if c.get("grupo") == g["clave"]]
        if not controles:
            continue
        salida.append({"tipo": "grupo", "nombre": g["nombre"]})
        for c in controles:
            hallazgos = []
            for h in c.get("hallazgos") or []:
                ruta = carpeta / h["archivo"] if (carpeta / h["archivo"]).exists() or not (sitio / h["archivo"]).exists() else sitio / h["archivo"]
                hallazgos.append({"ruta": str(ruta), "archivo": h["archivo"], "linea": int(h.get("linea") or 0), "texto": h["texto"]})
            medido = c.get("medicion") or {}
            salida.append({"tipo": "control", "id": c["id"], "nombre": c["nombre"], "estado": c["estado"],
                           "nivel": NIVEL.get(c["estado"], "neutro"), "icono": ICONO.get(c["estado"], "dialog-information"),
                           "detalle": c.get("detalle", ""), "porque": c.get("porque", ""), "fuente": c.get("fuente", ""),
                           "manual": c["estado"] == "manual", "marcado": c.get("marcado", ""), "nota": c.get("nota", ""),
                           "hallazgos": hallazgos,
                           "medido": (f"Medido: {medido['corridas']} corridas · atrapó {medido['atrapo']} · {medido['falsos']} falsos positivos"
                                      + (f" · {medido['marca']}" if medido.get("marca") else "")) if medido else ""})
    return salida


class AntesDePublicar(QObject):
    cambiado = Signal()
    resultadoCambiado = Signal()
    cifrasListas = Signal("QVariantMap")          # lo que respondió `cifras` ({paquetes, cambian, nuevas, quitadas, escrito} o {error})
    marcado = Signal("QVariantMap")
    falsoDeclarado = Signal("QVariantMap")
    constanciaLista = Signal("QVariantMap")      # {constancia, escrito}, {bloqueado, mensaje, faltan} o {error}
    entradasCambiadas = Signal()

    def __init__(self, documentos, tareas, consola, parent=None):
        super().__init__(parent)
        self.documentos, self.tareas, self.consola = documentos, tareas, consola
        self._dato: dict = {}
        self._revisando = False
        self._pedido = 0
        self._entradas: list[dict] = []
        self._pedido_entradas = 0
        documentos.actualCambiado.connect(self._post_cambiado)

    def _post_cambiado(self) -> None:
        if self._dato and self._dato.get("carpeta") and adp.post_de(self.documentos.actual) and \
                Path(adp.post_de(self.documentos.actual)).parent != Path(self._dato["carpeta"]):
            self._dato = {}
            self.resultadoCambiado.emit()
        self.cambiado.emit()

    # ------------------------------------------------------------------ propiedades
    @Property(bool, notify=cambiado)
    def disponible(self) -> bool:
        return adp.disponible() and bool(adp.post_de(self.documentos.actual))

    @Property(str, notify=cambiado)
    def motivo(self) -> str:
        if not adp.disponible():
            return adp.motivo_no_disponible()
        return "" if adp.post_de(self.documentos.actual) else "Abre en Escribir el .qmd de la entrada que vas a publicar."

    @Property(str, notify=cambiado)
    def post(self) -> str:
        return adp.post_de(self.documentos.actual)

    @Property(bool, notify=resultadoCambiado)
    def revisando(self) -> bool:
        return self._revisando

    @Property("QVariantList", notify=resultadoCambiado)
    def filas(self) -> list:
        return filas(self._dato)

    @Property(str, notify=resultadoCambiado)
    def error(self) -> str:
        return str(self._dato.get("error") or "")

    @Property(str, notify=resultadoCambiado)
    def titulo(self) -> str:
        return str(self._dato.get("titulo") or self._dato.get("post") or "")

    @Property(str, notify=resultadoCambiado)
    def veredicto(self) -> str:
        return adp.veredicto(self._dato.get("resumen") or {})

    @Property(bool, notify=resultadoCambiado)
    def listo(self) -> bool:
        return bool((self._dato.get("resumen") or {}).get("listo"))

    @Property(int, notify=resultadoCambiado)
    def faltan(self) -> int:
        return int((self._dato.get("resumen") or {}).get("faltan") or 0)

    @Property(str, notify=resultadoCambiado)
    def resumenTexto(self) -> str:
        r = self._dato.get("resumen") or {}
        if not r:
            return ""
        partes = [f"{r.get('fallas', 0)} fallas", f"{r.get('avisos', 0)} avisos", f"{r.get('pendientes', 0)} puntos sin marcar"]
        if r.get("por_cotejar"):
            partes.append(f"{r['por_cotejar']} reglas fundadas en normas por cotejar")
        return " · ".join(partes)

    @Property("QVariantMap", notify=resultadoCambiado)
    def revisado(self) -> dict:
        return dict(self._dato.get("revisado") or {})

    @Property(bool, notify=resultadoCambiado)
    def usaCifras(self) -> bool:
        return any(c.get("id") == "cifras" and ("paquete" in c.get("detalle", "") or c.get("hallazgos")) for c in self._dato.get("controles", []))

    # ------------------------------------------------------------------ revisar
    @Slot()
    def revisar(self) -> None:
        self._revisar(False)

    @Slot()
    def revisarMidiendo(self) -> None:
        """«Revisar de nuevo»: la misma revisión, anotada como una corrida en _registro/controles.yml (C14.1, C15.8)."""
        self._revisar(True)

    def _revisar(self, medir: bool) -> None:
        post = self.post
        if not post:
            return
        self._pedido += 1
        pedido = self._pedido
        self._revisando = True
        self.resultadoCambiado.emit()
        argv = adp.orden("medir", post, aplicar=True) if medir else adp.orden("revisar", post)

        def trabajo(progress_cb=None, cancel_cb=None, message_cb=None):
            return adp.correr(argv)

        def fin(r):
            if pedido != self._pedido:
                return
            dato, error = r
            if medir and isinstance(dato, dict) and not dato.get("error"):
                if dato.get("escrito"):
                    self.consola.registrar("info", "Antes de publicar: corrida anotada en _registro/controles.yml")
                dato = dato.get("revision") if isinstance(dato.get("revision"), dict) else {"error": "medir no devolvió la revisión"}
            self._dato = dato if isinstance(dato, dict) else {"error": error or "el motor no respondió"}
            self._revisando = False
            if self._dato.get("error"):
                self.consola.registrar("warn", f"Antes de publicar: {self._dato['error']}")
            self.resultadoCambiado.emit()
        self.tareas.funcion("Revisar antes de publicar", trabajo, silenciosa=True, operacion="lectura", error=False, al_terminar=fin)

    def _escribir(self, nombre: str, argv: list[str], senal, revisar_despues: bool = True) -> None:
        def trabajo(progress_cb=None, cancel_cb=None, message_cb=None):
            return adp.correr(argv)

        def fin(r):
            dato, error = r
            dato = dato if isinstance(dato, dict) else {"error": error or "la orden no devolvió nada"}
            if dato.get("error"):
                self.consola.registrar("warn", f"{nombre}: {dato['error']}")
            senal.emit(dato)
            if revisar_despues and not dato.get("error") and not dato.get("bloqueado"):
                self.revisar()
        self.tareas.funcion(nombre, trabajo, silenciosa=True, operacion="escritura", error=False, al_terminar=fin)

    @Slot(str, bool, str)
    def marcar(self, id: str, hecho: bool, nota: str) -> None:
        """La casilla y la nota de un punto manual: hecho, justificado (sin casilla y con nota) o pendiente."""
        if not self.post:
            return
        nota = (nota or "").strip()
        estado = "hecho" if hecho else "justificado" if nota else "pendiente"
        self._escribir("Marcar un punto", adp.orden("marcar", self.post, id, estado, *([nota] if nota else []), aplicar=True), self.marcado)

    @Slot(str, str)
    def falso(self, control: str, nota: str) -> None:
        if self.post and (nota or "").strip():
            self._escribir("Declarar un falso positivo", adp.orden("falso", self.post, control, nota.strip(), aplicar=True), self.falsoDeclarado)

    @Slot(bool)
    def cifras(self, aplicar: bool) -> None:
        """«Traer las cifras»: sin aplicar, qué cambiaría en _cifras.yml; aplicando, lo escribe y revisa de nuevo."""
        if self.post:
            self._escribir("Traer las cifras" if aplicar else "Simular las cifras", adp.orden("cifras", self.post, aplicar=aplicar),
                           self.cifrasListas, revisar_despues=aplicar)

    @Slot(str)
    def darPorRevisado(self, motivo: str) -> None:
        """La constancia de que se revisó antes de publicar; con «Faltan N» y sin motivo, el motor se detiene."""
        if self.post:
            argv = adp.orden("constancia", self.post, *(["--motivo", motivo.strip()] if (motivo or "").strip() else []), aplicar=True)
            self._escribir("Dar por revisado", argv, self.constanciaLista)

    # ------------------------------------------------------------------ las entradas de una publicación
    @Property("QVariantList", notify=entradasCambiadas)
    def entradas(self) -> list:
        return list(self._entradas)

    @Property(str, notify=entradasCambiadas)
    def resumenEntradas(self) -> str:
        if not self._entradas:
            return ""
        con_faltas = [e for e in self._entradas if not e.get("listo")]
        sin_constancia = [e for e in self._entradas if not e.get("vigente")]
        partes = [f"{len(self._entradas)} entrada(s) cambiadas"]
        if con_faltas:
            partes.append(f"{len(con_faltas)} con faltas")
        if sin_constancia:
            partes.append(f"{len(sin_constancia)} sin revisar desde el último cambio")
        return " · ".join(partes)

    def revisarEntradas(self, posts: list[str]) -> None:
        """El veredicto de cada entrada de la publicación (`resumen`), en un hilo; el último pedido manda."""
        self._pedido_entradas += 1
        pedido = self._pedido_entradas
        if not posts or not adp.disponible():
            self._entradas = []
            self.entradasCambiadas.emit()
            return
        argv = adp.orden("resumen", *posts)

        def trabajo(progress_cb=None, cancel_cb=None, message_cb=None):
            return adp.correr(argv, plazo=60 + 20 * len(posts))

        def fin(r):
            if pedido != self._pedido_entradas:
                return
            dato, error = r
            filas_ = []
            for e, ruta in zip((dato or {}).get("posts") or [], posts):
                rev = e.get("revisado") or {}
                filas_.append({"ruta": ruta, "post": e.get("post", ruta), "titulo": e.get("titulo") or e.get("post", ""),
                               "listo": bool(e.get("listo")), "veredicto": e.get("error") or adp.veredicto(e),
                               "nivel": "positivo" if e.get("listo") else "negativo", "vigente": bool(rev.get("vigente")),
                               "revisado": (f"revisado el {str(rev.get('fecha', ''))[:16].replace('T', ' ')}" + ("" if rev.get("vigente") else ", cambió después"))
                                           if rev else "sin revisar"})
            if error:
                self.consola.registrar("warn", f"Antes de publicar (entradas): {error}")
            self._entradas = filas_
            self.entradasCambiadas.emit()
        self.tareas.funcion("Revisar las entradas de la publicación", trabajo, silenciosa=True, operacion="lectura", error=False, al_terminar=fin)
