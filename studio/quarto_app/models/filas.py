"""quarto_app/models/filas.py — las filas de las tablas de Quarto Studio (sitios, entradas, enlaces del índice, fragmentos)
y de la lista de problemas, sin Qt (se prueban solas); los modelos de Qt son los de `gui_comun.modelos`."""
from __future__ import annotations

from quarto_app.models.blog import Blog

COLUMNAS = {
    "sitios": [("Sitio", "sitio"), ("Estado", "estado"), ("Entradas", "entradas"), ("Rama", "rama"), ("Cambios", "cambios"),
               ("Por empujar", "por_empujar"), ("Último render", "render"), ("Tema", "tema"), ("Dominio", "dominio")],
    "entradas": [("Fecha", "fecha"), ("Título", "titulo"), ("Sitio", "sitio"), ("Carpeta", "carpeta"), ("Tags", "tags"), ("Excel", "excel")],
    "indice": [("Año", "anio"), ("Enlace", "enlace"), ("Estado", "estado"), ("Destino", "destino")],
    "contenido": [("Sitio", "sitio"), ("Subblog", "subblog"), ("Fragmento", "fragmento"), ("Entradas", "entradas"), ("Modificado", "modificado")],
}
COLUMNAS_ENTRADAS_SITIO = [("Fecha", "fecha"), ("Título", "titulo"), ("Carpeta", "carpeta")]
ICONO_SITIO = "folder-html"
ICONO_ENTRADA = "text-markdown"
FILTROS = (("todos", "Todos"), ("al_dia", "Al día"), ("sin_render", "Cambios sin render"), ("sin_publicar", "Render sin publicar"),
           ("problemas", "Con problemas"))
ORDEN_ESTADO = {"problemas": 0, "sin_render": 1, "sin_publicar": 2, "al_dia": 3}


def fila_sitio(b: Blog, e: dict, pub) -> dict:
    """Una fila de la tabla Sitios: el blog del escáner, su estado (`servicios.sitios`) y su registro (`core/pubs.Pub` o None)."""
    return {"sitio": b.nombre, "estado": e["texto_estado"], "entradas": str(b.num_posts), "rama": e.get("rama") or "—",
            "cambios": str(e.get("cambios", 0)) if e.get("cambios") else "—", "por_empujar": ("sin remoto" if e.get("sin_remoto") else (str(e["por_empujar"]) if e.get("por_empujar") else "—")),
            "render": e.get("fecha_render", "—"), "tema": getattr(pub, "tema", "") or ("el hub" if b.es_website else ""),
            "dominio": (getattr(pub, "url", "") or "").replace("https://", "").rstrip("/"),
            "nivel": e["nivel"], "icono": {"sitio": ICONO_SITIO}, "habilitado": True, "clave": e["estado"], "ruta": str(b.ruta),
            "crudo": {"estado": ORDEN_ESTADO.get(e["estado"], 9), "entradas": b.num_posts, "cambios": e.get("cambios", 0),
                      "por_empujar": e.get("por_empujar", 0), "render": e.get("ts_render", 0)}}


def fila_entrada(f: dict) -> dict:
    return {**f, "nivel": "positivo" if f.get("excel") == "sí" else ("neutro" if f.get("excel") == "no" else ""),
            "icono": {"titulo": ICONO_ENTRADA}, "habilitado": True}


def fila_entrada_sitio(p) -> dict:
    return {"fecha": p.fecha, "titulo": p.titulo or p.nombre, "carpeta": p.ruta.parent.name + "/" + p.ruta.name, "ruta": str(p.ruta / "index.qmd"),
            "icono": {"titulo": ICONO_ENTRADA}, "habilitado": True}


def fila_enlace(f: dict) -> dict:
    return {**f, "icono": {"enlace": "emblem-symbolic-link"}, "habilitado": True}


def fila_fragmento(f: dict) -> dict:
    return {**f, "icono": {"fragmento": ICONO_ENTRADA}, "habilitado": True}


def campos_elemento(fila: dict, columnas: list[tuple[str, str]]) -> list[dict]:
    """[{etiqueta, valor}] con las columnas de la tabla y lo demás que la fila trae (para un Resumen genérico)."""
    ocultas = {"nivel", "icono", "habilitado", "crudo", "frontmatter", "clave"}
    vistos, salida = set(), []
    for etiqueta, clave in columnas:
        vistos.add(clave)
        salida.append({"etiqueta": etiqueta, "valor": str(fila.get(clave, "") or "—")})
    for clave, valor in fila.items():
        if clave in vistos or clave in ocultas or valor in ("", None):
            continue
        salida.append({"etiqueta": clave.replace("_", " ").capitalize(), "valor": str(valor)})
    return salida
