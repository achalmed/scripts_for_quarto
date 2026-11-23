"""quarto_app/services/ayuda_ia.py — «Ayuda de la IA para la entrada…» (Ctrl+Alt+A), sin Qt: el prompt de posts del
ecosistema con la entrada abierta, listo para un chat externo, y la lectura de lo que el chat devolvió, como cambio
sugerido; ninguna orden llama a un modelo ni escribe el post.

Objetivo: lo que LaTeX Studio ofrece por parte de un escrito, también en un post (plan «aprender y enseñar», fase 4.5):
  copiar el prompt que corresponde (`07 produccion/contenido_web/prompt_01_metadatos_y_seo_del_post`, el único del
  repo de prompts que escribe un post) con su «4 Entrada» rellena con la entrada, pegar la respuesta y ver qué cambiaría
  antes de ponerlo en el editor. Al aceptarlo, el uso queda en `_ia/registro.yml` del post y su declaración en
  `_ia/declaracion.md`, que es lo que exige el control «Uso de la IA declarado» de «Antes de publicar» (campo 15 de la
  norma del flujo; `escritura/scripts/antes_de_publicar.py registrar_ia`).
Método: el ciclo común de `core/py-common/ia_externa.py` (2026-11-23), cargado por su ruta como `pubs.py`: `leer_prompt`
  (con la guarda del repo), `para_ia` (el traductor de `prompts/scripts/para_ia_externa.py`), `aviso_sensible` (C12.3, si
  el prompt declara `datos_sensibles`) y `pegado()` para leer el bloque (`prompts/scripts/pegado.py`: `bloque` da el
  ```markdown de una sección o el ```yaml del frontmatter, y `cargar_yaml` lo lee con la reparación de los dos puntos).
  Antes de copiar, `sensibles()` corre `escritura/scripts/sensibles.py revisar`, la misma revisión de LaTeX Studio, sobre
  lo que el prompt lleva de la entrada (no sobre el método, que es público y trae el correo y el ORCID del autor). Los modos son los del prompt que producen algo que se pone en el post (una sección, la introducción, el
  frontmatter) o que se lee (la auditoría editorial); el índice SEO y las metadescripciones se piden en el chat.
Fundamento: el prompt 07/01 (su §4 y su §7) y su C12.1 (lo que propuso la IA va marcado como suyo y se declara); COPE
  (2023), en `escritura/scripts/entrega/ia.py`.
Límite: no hay todavía un prompt para la lección de un curso en el pub (`docencia`, fase 4.3): una lección se trabaja con
  el de posts hasta que exista el suyo (estado.md § Por hacer). No comprueba las cifras ni las citas: eso es de «Antes de
  publicar».
"""
from __future__ import annotations

import difflib
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path

from quarto_app.services import paths

PROMPT_POST = "07 produccion/contenido_web/prompt_01_metadatos_y_seo_del_post.md"
LARGO = 60000              # caracteres: por encima, un chat externo puede cortar el mensaje (como en LaTeX Studio)
MAX_ENTRADA = 40000        # lo que va de la entrada abierta
INTERPRETE = "/usr/bin/python3"
RE_FRONTMATTER = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)

# Los modos del prompt 07/01 que se piden desde el editor: `modo` es su palabra en el «4 Entrada»; `pone`, qué hace la
# ventana al aceptar: en el cursor (o en lugar de lo seleccionado), en lugar del frontmatter, o nada (se lee y se declara).
MODOS = (
    {"clave": "seccion", "nombre": "Una sección", "modo": "sección", "lenguas": ("markdown", "md", "qmd"), "pone": "cursor",
     "descripcion": "Redacta la sección seleccionada (o la que pidas en el chat) con rigor académico y su tabla de verificación."},
    {"clave": "introduccion", "nombre": "La introducción", "modo": "introducción", "lenguas": ("markdown", "md", "qmd"),
     "pone": "cursor", "descripcion": "De 200 a 300 palabras, con su gancho según el público; va en el cursor."},
    {"clave": "metadatos", "nombre": "Los metadatos", "modo": "metadatos YAML", "lenguas": ("yaml", "yml"), "pone": "frontmatter",
     "descripcion": "El frontmatter completo del index.qmd (título, description, abstract o resumen, autoría…); reemplaza el actual."},
    {"clave": "auditoria", "nombre": "La auditoría editorial", "modo": "auditoría editorial de un post escrito", "lenguas": (),
     "pone": "nada", "descripcion": "Hechos y normas, argumento, estructura, voz y citas, por prioridad; no cambia el post: lo corriges tú."},
)
POR_CLAVE = {m["clave"]: m for m in MODOS}

VUELTA = {
    "cursor": ("Devuelve PRIMERO un solo bloque ```markdown con el texto que va en la entrada (Markdown de Quarto, sin "
               "frontmatter ni `---`) y después, fuera del bloque, la tabla de verificación del «7 Formato de salida»."),
    "frontmatter": ("Devuelve PRIMERO un solo bloque ```yaml con el frontmatter completo, entre sus dos líneas `---`, y "
                    "después, fuera del bloque, la tabla de longitudes del «7 Formato de salida». Conserva los campos de la "
                    "entrada que no cambias."),
    "nada": "Devuelve la lista de hallazgos por prioridad con su corrección, como pide el prompt; no reescribas el post.",
}
CIERRE = ("Lo que propongas lo revisa la persona antes de ponerlo en la entrada, y su uso queda declarado en ella (C12.1): "
          "no inventes cifras, autores, fuentes ni hallazgos; lo que falte, marcado como el prompt lo pide.")


# --- el módulo común y las carpetas ----------------------------------------------------------------------------------

def _modulo(nombre: str, ruta: Path):
    if not ruta.is_file():
        return None
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except Exception:                                        # noqa: BLE001  un módulo ajeno roto no tumba la ventana
        return None
    return m


_COMUN: dict[str, object] = {}


def comun():
    """`core/py-common/ia_externa.py` (lo común de copiar el prompt y pegar lo de la IA), una vez; None sin él."""
    try:
        ruta = Path(paths.core_env().__file__).resolve().parent / "py-common" / "ia_externa.py"
    except Exception:                                        # noqa: BLE001  sin core/env.py
        return None
    clave = str(ruta)
    if clave not in _COMUN:
        _COMUN[clave] = _modulo("quarto_ia_externa", ruta)
    return _COMUN[clave]


def prompts_dir() -> Path | None:
    c = comun()
    return c.repo_prompts() if c is not None else None


def escritura_dir() -> Path | None:
    c = comun()
    return c.repo_escritura() if c is not None else None


def motivo_no_disponible() -> str:
    if comun() is None:
        return "No se encontró core/py-common/ia_externa.py (el ciclo común de copiar y pegar)."
    if prompts_dir() is None or not (prompts_dir() / PROMPT_POST).is_file():
        return f"No se encontró el prompt de posts ({PROMPT_POST}) en la carpeta de prompts (PROMPTS_DIR)."
    return ""


def disponible() -> bool:
    return motivo_no_disponible() == ""


def modos() -> list[dict]:
    return [{k: m[k] for k in ("clave", "nombre", "descripcion", "pone")} for m in MODOS]


# --- la entrada ----------------------------------------------------------------------------------------------------

def partes_del_post(texto: str) -> tuple[str, dict, str]:
    """(el frontmatter tal como está, con sus `---`; lo leído de él; el cuerpo)."""
    m = RE_FRONTMATTER.match(texto or "")
    if not m:
        return "", {}, texto or ""
    import yaml
    try:
        datos = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        datos = {}
    return m.group(0), datos if isinstance(datos, dict) else {}, (texto or "")[m.end():]


def _autores(fm: dict) -> str:
    a = fm.get("author")
    lista = a if isinstance(a, list) else [a] if a else []
    nombres = [str(x.get("name") if isinstance(x, dict) else x) for x in lista if x]
    return ", ".join(nombres)


def _fuente(texto: str) -> dict:
    _fm, datos, _c = partes_del_post(texto)
    return {"ruta": PROMPT_POST, "titulo": str(datos.get("titulo") or Path(PROMPT_POST).stem), "version": str(datos.get("version") or "")}


def prompt(clave: str, ruta: str, texto: str, seleccion: str = "") -> dict:
    """El prompt de posts para la entrada `ruta` (su texto, el del editor) en el modo `clave`, traducido y con su entrada.
    → {prompt, entrada, modo, nombre, fuente, aviso, largo, problemas} o {error}. `entrada` es lo que el prompt lleva de la
    entrada abierta: lo que se revisa antes de copiar (el método del prompt es del ecosistema y trae los datos públicos del
    autor, que la revisión daría por sensibles)."""
    m = POR_CLAVE.get(clave)
    if m is None:
        return {"error": f"Modo desconocido: {clave}."}
    motivo = motivo_no_disponible()
    if motivo:
        return {"error": motivo}
    c = comun()
    try:
        crudo = c.leer_prompt(PROMPT_POST, prompts_dir())
    except ValueError as e:
        return {"error": f"No se pudo leer el prompt de posts: {e}"}
    fm_texto, fm, cuerpo = partes_del_post(texto)
    seleccion = (seleccion or "").strip()
    titulo = str(fm.get("title") or Path(ruta).parent.name)
    contenido = seleccion if seleccion and m["pone"] == "cursor" else cuerpo.strip()
    recortado = len(contenido) > MAX_ENTRADA
    contenido = contenido[:MAX_ENTRADA].rstrip() + ("\n(… recortado)" if recortado else "")
    entrada = [
        f"Modo: {m['modo']}.",
        f"Tema o palabra clave principal: el de la entrada «{titulo}»" + (f" ({fm['subtitle']})" if fm.get("subtitle") else "")
        + "; si no basta, pregúntalo antes de generar.",
        ("Sección a redactar: la de este borrador (lo que la persona seleccionó en el editor)." if seleccion and m["pone"] == "cursor"
         else "Sección a redactar y fuentes: las dirá la persona en el chat; pregúntalas si faltan." if m["clave"] == "seccion" else
         "Sección a redactar: no aplica."),
        "Intención de búsqueda, público y tipo de post: no están declarados en la entrada; pregúntalos si el modo los necesita.",
        "Fecha y coautoría: " + ", ".join(x for x in (f"fecha {fm['date']}" if fm.get("date") else "",
                                                       f"autoría {_autores(fm)}" if _autores(fm) else "") if x) + "."
        if fm.get("date") or _autores(fm) else "Fecha y coautoría: no declaradas.",
        *([f"Frontmatter actual de la entrada (`{Path(ruta).name}`):\n```yaml\n{fm_texto.strip()}\n```"] if fm_texto and m["pone"] == "frontmatter" else []),
        ("Borrador de la sección (lo seleccionado):\n" if seleccion and m["pone"] == "cursor" else "Contenido de la entrada (sin su frontmatter):\n")
        + (contenido or "(vacío: la entrada todavía no tiene texto)"),
    ]
    fuente = _fuente(crudo)
    bloques = [f"# {fuente['titulo']} · {m['nombre'].lower()} de «{titulo}»",
               f"(Versión {fuente['version'] or '—'} de este prompt. Su sección «4 Entrada» la trae, ya rellena, el bloque "
               "«entrada» de abajo: no hace falta abrir nada más.)",
               c.para_ia(crudo, prompts_dir()).strip(),
               "<entrada>\n" + "\n\n".join(entrada) + "\n</entrada>",
               "## Formato de vuelta para el editor (manda sobre el «7 Formato de salida» del prompt en lo que va al editor)\n"
               + VUELTA[m["pone"]] + "\n\n" + CIERRE]
    texto_prompt = "\n\n".join(b for b in bloques if b.strip())
    t = c.traductor(prompts_dir())
    return {"prompt": texto_prompt, "entrada": "\n\n".join(entrada), "modo": clave, "nombre": m["nombre"], "pone": m["pone"], "fuente": fuente,
            "aviso": c.aviso_sensible(crudo, prompts_dir()) or "", "largo": len(texto_prompt) > LARGO,
            "problemas": t.problemas(texto_prompt) if t is not None and hasattr(t, "problemas") else []}


# --- antes de copiar (C12.3) ---------------------------------------------------------------------------------------

def sensibles(texto: str, cache: Path, carpeta: str = "") -> dict:
    """La revisión de LaTeX Studio antes de copiar (`escritura/scripts/sensibles.py revisar`): {sensible, nivel, hallazgos,
    porque, fuente}; sin escritura o si falla, {sensible: true, nivel: desconocido, error}, para que la persona decida."""
    d = escritura_dir()
    guion = d / "scripts" / "sensibles.py" if d else None
    if guion is None or not guion.is_file():
        return {"sensible": True, "nivel": "desconocido", "hallazgos": [], "error": "no se encontró escritura/scripts/sensibles.py"}
    cache.mkdir(parents=True, exist_ok=True)
    archivo = cache / "prompt.txt"
    archivo.write_text(texto or "", encoding="utf-8")
    argv = [INTERPRETE, str(guion), "revisar", str(archivo)] + (["--proyecto", carpeta] if carpeta else [])
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        dato = json.loads(r.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return {"sensible": True, "nivel": "desconocido", "hallazgos": [], "error": str(e)[:200]}
    return dato if isinstance(dato, dict) else {"sensible": True, "nivel": "desconocido", "hallazgos": [], "error": "respuesta rara"}


# --- lo pegado -----------------------------------------------------------------------------------------------------

def _diff(antes: str, despues: str) -> str:
    return "".join(difflib.unified_diff((antes or "").splitlines(keepends=True), (despues or "").splitlines(keepends=True),
                                        fromfile="lo que está", tofile="lo sugerido"))


def leer(clave: str, pegado: str, texto: str, seleccion: str = "") -> dict:
    """Lo que devolvió el chat, leído sin IA. → {ok, errores, avisos, pone, antes, despues, diff, resto}: con `pone`
    «cursor», `antes` es lo seleccionado (o vacío: va en el cursor); con «frontmatter», el frontmatter actual; con «nada»,
    no se pone nada (la auditoría se lee y se declara)."""
    m = POR_CLAVE.get(clave)
    vacio = {"ok": False, "errores": [], "avisos": [], "pone": m["pone"] if m else "nada", "antes": "", "despues": "", "diff": "", "resto": ""}
    if m is None:
        return {**vacio, "errores": [f"Modo desconocido: {clave}."]}
    if not (pegado or "").strip():
        return {**vacio, "errores": ["No llegó nada: pegue la respuesta entera del chat."]}
    if m["pone"] == "nada":
        return {**vacio, "ok": True, "resto": pegado.strip()}
    c = comun()
    pg = c.pegado(prompts_dir()) if c is not None else None
    if pg is None or not hasattr(pg, "bloque"):
        return {**vacio, "errores": ["No se encontró el lector común de lo pegado (prompts/scripts/pegado.py, por core/py-common/ia_externa.py)."]}
    bloque = pg.bloque(pegado, *m["lenguas"])
    if not bloque.strip():
        return {**vacio, "errores": [f"No llegó el bloque ```{m['lenguas'][0]} que pide el formato de vuelta: pegue la respuesta entera."]}
    avisos: list[str] = []
    fm_texto, _fm, _cuerpo = partes_del_post(texto)
    if m["pone"] == "frontmatter":
        interior = re.sub(r"\A\s*---[ \t]*\n", "", bloque)
        interior = re.sub(r"\n---[ \t]*\s*\Z", "", interior).strip("\n")
        datos, error, reparadas = pg.cargar_yaml(interior)
        if error:
            return {**vacio, "errores": [error]}
        if not isinstance(datos, dict) or not datos.get("title"):
            return {**vacio, "errores": ["El frontmatter no trae `title`: no es el de una entrada."]}
        if reparadas:
            avisos.append(f"Se pusieron entre comillas {reparadas} valor{'es' if reparadas != 1 else ''} con dos puntos para poder "
                          "leer el bloque: revise que digan lo que la IA quiso.")
        if reparadas:
            interior, _n = pg.reparar_yaml(interior)
        despues = f"---\n{interior}\n---\n"
        antes = fm_texto
        if antes and not antes.endswith("\n"):
            antes += "\n"
        perdidos = sorted(set(_fm) - set(datos))
        if perdidos:
            avisos.append("El frontmatter sugerido no trae " + ", ".join(f"`{k}`" for k in perdidos) + ": si lo pones, se quitan.")
    else:
        if RE_FRONTMATTER.match(bloque):
            return {**vacio, "errores": ["El bloque trae un frontmatter (`---`): en este modo va solo el texto de la entrada."]}
        antes = (seleccion or "")
        despues = bloque.strip("\n") + ("\n" if antes.endswith("\n") or not antes else "")
    pendientes = len(re.findall(r"\{cita APA pendiente|\[(?:dato|ficha) pendiente|\[VERIFICAR", despues, re.I))
    if pendientes:
        avisos.append(f"La IA dejó {pendientes} marca{'s' if pendientes != 1 else ''} de pendiente: complétalas antes de publicar.")
    return {**vacio, "ok": True, "avisos": avisos, "antes": antes, "despues": despues, "diff": _diff(antes, despues),
            "resto": pegado.replace(bloque, "").strip()}


def uso(clave: str, ruta: str, fuente: dict, texto_prompt: str, parte: str = "") -> dict:
    """El uso para `registrar_ia` del motor de escritura: {archivo, parte, prompt: {titulo, ruta, version, texto}, resumen}
    (el motor guarda la huella del texto del prompt, no el texto)."""
    m = POR_CLAVE.get(clave) or {"nombre": clave, "pone": "nada"}
    que = m["nombre"].lower()
    resumen = (f"la IA propuso {que} con el prompt de posts; el autor la revisó y la puso en la entrada" if m["pone"] != "nada"
               else f"la IA hizo {que} de la entrada; el autor corrigió lo que aceptó")
    return {"archivo": Path(ruta).name, "parte": parte or m["nombre"],
            "prompt": {"titulo": fuente.get("titulo", ""), "ruta": fuente.get("ruta", ""), "version": fuente.get("version", ""),
                       "texto": texto_prompt or ""},
            "resumen": resumen}


def cache_dir() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "quarto-studio" / "ayuda"
