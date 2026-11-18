"""quarto_app/controladores/arbol.py — el árbol de sitios y entradas de la izquierda (rediseño del 2026-11-18, la forma
de escritor aprobada): los sitios (el hub primero) con su estado por la regla de la puerta R6 y, desplegado bajo el
sitio actual, sus documentos por carpeta, con cada entrada como una sola fila (su título y su fecha). Es una lista plana
con `nivel` (una `ListView` la pinta como árbol); se rehace cuando cambian los sitios, el sitio actual o sus documentos.
Solo lee: lo que pinta sale de `sitios.proyectos` y de los documentos que lista `controladores/documentos.py`.
"""
from __future__ import annotations

from pathlib import PurePosixPath

from gui_comun.modelos import ModeloLista
from gui_comun.qt import QObject, Property, Signal, Slot

ROLES = ("tipo", "clave", "texto", "detalle", "icono", "ruta", "nivel", "estado", "estadoTexto", "motivo", "plegable", "abierta", "sitio")
RAIZ = "(raíz del sitio)"


def grupo_de(fila: dict) -> str:
    """La carpeta bajo la que va un documento: una entrada (`posts/AAAA-MM-DD-x/index.qmd`) va bajo `posts`, no bajo la suya."""
    carpeta = fila.get("carpeta", "") or RAIZ
    if fila.get("entrada") and carpeta != RAIZ:
        padre = str(PurePosixPath(carpeta).parent)
        return RAIZ if padre in ("", ".") else padre
    return carpeta


def filas_arbol(proyectos: list[dict], actual: str, documentos: list[dict], texto: str = "", plegadas: set | None = None) -> list[dict]:
    """Las filas del árbol (sin Qt; se prueba solo). `plegadas`: las claves cerradas a mano (un sitio o una carpeta)."""
    plegadas = plegadas or set()
    texto = (texto or "").strip().lower()
    salida = []
    for p in proyectos:
        nombre = p["nombre"]
        clave = f"sitio:{nombre}"
        abierta = nombre == actual and clave not in plegadas
        salida.append({"tipo": "sitio", "clave": clave, "texto": nombre + (" (hub)" if p.get("esHub") else ""),
                       "detalle": (p.get("dominio") or "sin dominio") + " · " + str(p.get("entradas", 0)) + " entradas",
                       "icono": "go-home" if p.get("esHub") else "folder-html", "ruta": "", "nivel": 0, "estado": p.get("clave", ""),
                       "estadoTexto": p.get("estado", ""), "motivo": p.get("motivo", ""), "plegable": True, "abierta": abierta, "sitio": nombre})
        if not abierta:
            continue
        grupos: dict[str, list[dict]] = {}
        for d in documentos:
            if texto and texto not in d.get("rel", "").lower() and texto not in (d.get("titulo") or "").lower():
                continue
            grupos.setdefault(grupo_de(d), []).append(d)
        for grupo, docs in grupos.items():
            clave_g = f"carpeta:{nombre}:{grupo}"
            abierta_g = bool(texto) or clave_g not in plegadas
            salida.append({"tipo": "carpeta", "clave": clave_g, "texto": grupo, "detalle": str(len(docs)), "icono": "folder", "ruta": "",
                           "nivel": 1, "estado": "", "estadoTexto": "", "motivo": "", "plegable": True, "abierta": abierta_g, "sitio": nombre})
            if not abierta_g:
                continue
            for d in docs:
                if d.get("entrada"):
                    detalle = d.get("fecha", "")
                elif d.get("titulo"):
                    detalle = d.get("nombre", "")
                else:
                    detalle = ""
                salida.append({"tipo": "documento", "clave": "doc:" + d["ruta"], "texto": d.get("titulo") or d.get("nombre", ""), "detalle": detalle,
                               "icono": d.get("icono", "text-plain"), "ruta": d["ruta"], "nivel": 2, "estado": "", "estadoTexto": "",
                               "motivo": d.get("rel", ""), "plegable": False, "abierta": False, "sitio": nombre})
    return salida


class Arbol(QObject):
    cambiado = Signal()

    def __init__(self, sitios, documentos, parent=None):
        super().__init__(parent)
        self.sitios, self.documentos = sitios, documentos
        self._modelo = ModeloLista(ROLES, parent=self)
        self._texto = ""
        self._plegadas: set[str] = set()
        sitios.cambiado.connect(self.rehacer)
        documentos.cambiado.connect(self.rehacer)       # recarga también al cambiar de sitio (después de leer sus documentos)
        self.rehacer()

    modelo = Property(QObject, lambda self: self._modelo, constant=True)

    @Slot()
    def rehacer(self) -> None:
        self._modelo.poner(filas_arbol(self.sitios.proyectos, self.sitios.nombre, self.documentos._filas.todas(), self._texto, self._plegadas))
        self.cambiado.emit()

    @Slot(str)
    def filtrar(self, texto: str) -> None:
        texto = (texto or "").strip()
        if texto != self._texto:
            self._texto = texto
            self.rehacer()

    @Slot(str)
    def alternar(self, clave: str) -> None:
        """Clic en la flecha (o ← y →): un sitio que no es el actual pasa a serlo y se despliega; lo demás se pliega o despliega."""
        if clave.startswith("sitio:") and clave[6:] != self.sitios.nombre:
            self._plegadas.discard(clave)
            self.sitios.fijarPorNombre(clave[6:])
            return
        if clave in self._plegadas:
            self._plegadas.discard(clave)
        else:
            self._plegadas.add(clave)
        self.rehacer()

    @Slot(str)
    def elegirSitio(self, nombre: str) -> None:
        """Clic en un sitio: pasa a ser el actual y se despliega."""
        self._plegadas.discard(f"sitio:{nombre}")
        if nombre == self.sitios.nombre:
            self.rehacer()
        else:
            self.sitios.fijarPorNombre(nombre)

    @Slot(result=str)
    def primeraRuta(self) -> str:
        """Intro en el campo de búsqueda: el primer documento que queda a la vista."""
        return next((f["ruta"] for f in self._modelo.todas() if f["tipo"] == "documento"), "")

    @Property(int, notify=cambiado)
    def filas(self) -> int:
        return self._modelo.filas
