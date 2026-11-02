"""quarto_app/services/publicacion.py — lo que la vista de publicación muestra de un sitio (reingeniería E8–E10), sin Qt.

Solo lee el disco y git. `destino(...)`: las comprobaciones de que el destino corresponde al sitio elegido —el dominio del
registro de pubs del hub, el `site-url` del `_quarto.yml`, el remoto `origin` frente al repositorio del registro y la rama
con su remoto— y si se puede publicar. `por_publicar(sitio)`: los archivos que cambiarán (sin confirmar y en commits sin
empujar). `ultima(sitio)` e `historial(sitio)`: los commits del remoto que tocaron la carpeta de salida (lo que Netlify
desplegó). Nada se escribe ni se empuja aquí.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from quarto_app.services import documentos

_SITE_URL = re.compile(r"^\s*site-url:\s*['\"]?([^'\"\s#]+)", re.M)
TOPE_ARCHIVOS = 400


def _git(ruta: Path, *args: str, plazo: int = 20) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(ruta), *args], capture_output=True, text=True, timeout=plazo)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def host(url: str) -> str:
    """El dominio de una URL («https://x.netlify.app/» → «x.netlify.app»), sin «www.» ni barras."""
    url = (url or "").strip()
    if not url:
        return ""
    p = urlparse(url if "://" in url else "https://" + url)
    return (p.hostname or "").lower().removeprefix("www.")


def site_url(sitio: Path) -> str:
    try:
        m = _SITE_URL.search((Path(sitio) / "_quarto.yml").read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ""
    return m.group(1).strip() if m else ""


def _repo_de(remoto: str) -> str:
    """El nombre del repositorio de una URL de remoto (git@…:u/x.git, https://…/u/x, /ruta/x.git → «x»)."""
    remoto = (remoto or "").strip().rstrip("/")
    nombre = re.split(r"[/:]", remoto)[-1] if remoto else ""
    return nombre.removesuffix(".git")


def destino(sitio: Path, dominio: str, repo: str) -> dict:
    """{comprobaciones: [{nombre, ok (True · False · None), detalle}], coincide, dominio, motivo}."""
    sitio = Path(sitio)
    repo = (repo or "").strip().split("/")[-1]                 # «achalmed/axiomata» → «axiomata»
    comprobaciones = []
    dom = host(dominio)
    comprobaciones.append({"nombre": "Dominio del registro de pubs", "ok": bool(dom),
                           "detalle": dom or "el sitio no tiene «url» en _pubs/pubs.yml: no hay a dónde publicar"})
    su = site_url(sitio)
    if not su:
        comprobaciones.append({"nombre": "site-url del _quarto.yml", "ok": None, "detalle": "el _quarto.yml no declara site-url (no se puede contrastar)"})
    else:
        ok = host(su) == dom
        comprobaciones.append({"nombre": "site-url del _quarto.yml", "ok": ok,
                               "detalle": host(su) + ("" if ok else f" ≠ {dom}: el sitio se construye para otro dominio")})
    remoto = (_git(sitio, "remote", "get-url", "origin") or "").strip()
    if not remoto:
        comprobaciones.append({"nombre": "Remoto origin", "ok": False, "detalle": "sin remoto origin: el push no publica nada"})
    elif repo:
        ok = _repo_de(remoto).lower() == repo.lower()
        comprobaciones.append({"nombre": "Remoto origin", "ok": ok,
                               "detalle": f"«{_repo_de(remoto)}»" + ("" if ok else f" ≠ «{repo}» del registro: el push iría a otro repositorio")})
    else:
        comprobaciones.append({"nombre": "Remoto origin", "ok": None, "detalle": f"«{_repo_de(remoto)}» (el registro no declara repo)"})
    upstream = (_git(sitio, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") or "").strip()
    comprobaciones.append({"nombre": "Rama con su remoto", "ok": bool(upstream),
                           "detalle": upstream or "la rama no sigue a ningún remoto: nada se publica"})
    fallos = [c for c in comprobaciones if c["ok"] is False]
    return {"comprobaciones": comprobaciones, "coincide": not fallos, "dominio": dom,
            "motivo": "" if not fallos else fallos[0]["nombre"] + ": " + fallos[0]["detalle"]}


def por_publicar(sitio: Path, tope: int = TOPE_ARCHIVOS) -> dict:
    """{archivos: [{archivo, estado, donde}], total, sin_confirmar, por_empujar, commits}: lo que el próximo push lleva."""
    sitio = Path(sitio)
    archivos = []
    estado = _git(sitio, "status", "--porcelain", "--untracked-files=all") or ""
    sin_confirmar = 0
    for linea in estado.splitlines():
        if len(linea) > 3:
            sin_confirmar += 1
            if len(archivos) < tope:
                archivos.append({"archivo": linea[3:].strip().strip('"'), "estado": linea[:2].strip() or "M", "donde": "sin confirmar"})
    commits = int((_git(sitio, "rev-list", "--count", "@{u}..HEAD") or "0").strip() or 0)
    por_empujar = 0
    if commits:
        for linea in (_git(sitio, "diff", "--name-status", "@{u}..HEAD") or "").splitlines():
            partes = linea.split("\t")
            if len(partes) >= 2:
                por_empujar += 1
                if len(archivos) < tope:
                    archivos.append({"archivo": partes[-1], "estado": partes[0][:1], "donde": "por empujar"})
    return {"archivos": archivos, "total": sin_confirmar + por_empujar, "sin_confirmar": sin_confirmar, "por_empujar": por_empujar, "commits": commits}


def historial(sitio: Path, n: int = 20) -> list[dict]:
    """Los commits del remoto que tocaron la carpeta de salida: [{commit, fecha, mensaje, archivos}], el más reciente primero."""
    sitio = Path(sitio)
    salida_rel = documentos.carpeta_salida(sitio).name
    texto = _git(sitio, "log", "@{u}", f"-n{n}", "--format=\x1e%h\x1f%ci\x1f%s", "--name-only", "--", salida_rel)
    if texto is None:
        return []
    filas = []
    for bloque in texto.split("\x1e"):
        if not bloque.strip():
            continue
        cabeza, *resto = bloque.strip("\n").split("\n")
        partes = cabeza.split("\x1f")
        if len(partes) < 3:
            continue
        filas.append({"commit": partes[0], "fecha": partes[1][:16], "mensaje": partes[2], "archivos": len([r for r in resto if r.strip()])})
    return filas


def ultima(sitio: Path) -> dict:
    h = historial(sitio, 1)
    return h[0] if h else {}
