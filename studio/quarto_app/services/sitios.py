"""quarto_app/services/sitios.py — el estado de cada sitio de la familia, leído del disco y de git (sin Qt; se prueba solo).

La regla es la de la puerta R6 del hub (`web/scripts/puerta-r6.sh`): un sitio está «al día» cuando su `_site/index.html`
está confirmado después del último commit de sus fuentes (los mismos pathspecs de la puerta), sin fuentes sin
confirmar, sin `_site/` sin confirmar y sin commits por empujar. De ahí salen los cuatro estados: `problemas` (sin
`_quarto.yml`, sin git o sin `_site/index.html`), `sin_render` (fuentes sin confirmar o confirmadas después del último
render), `sin_publicar` (`_site/` sin confirmar o commits sin empujar) y `al_dia`. Solo lee: `git status`, `git log`,
`git rev-list`.
"""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

# los pathspecs de fuentes de la puerta R6 (web/scripts/puerta-r6.sh, FUENTES); _site/ y _freeze/ nunca lo son
FUENTES = [":(glob)**/*.qmd", ":(glob)**/_quarto.yml", ":(glob)**/_metadata.yml", "_extensions/", "_filters/", "_partials/",
           "assets/scss/", "assets/js/", "assets/css/", "_brand.yml",
           ":(exclude)_site/", ":(exclude)_freeze/", ":(exclude)_vitrina/", ":(exclude)_ediciones/", ":(exclude,glob)**/README.md"]
ESTADOS = (("al_dia", "Al día", "positivo"), ("sin_render", "Cambios sin render", "neutro"),
           ("sin_publicar", "Render sin publicar", "activo"), ("problemas", "Con problemas", "negativo"))
TEXTO_ESTADO = {e: t for e, t, _n in ESTADOS}
NIVEL_ESTADO = {e: n for e, _t, n in ESTADOS}


def _git(ruta: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(ruta), *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _fecha(ts: int | None) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "—"


def estado_sitio(ruta: Path) -> dict:
    """Todo lo que la tabla y el Resumen dicen de un sitio; `estado` y `motivo` explican por qué."""
    ruta = Path(ruta)
    d = {"quarto_yml": (ruta / "_quarto.yml").is_file(), "git": (ruta / ".git").exists(),
         "site": (ruta / "_site" / "index.html").is_file(), "rama": "", "cambios": 0, "site_sin_confirmar": False,
         "por_empujar": 0, "sin_remoto": False, "ts_fuentes": 0, "ts_render": 0}
    if d["git"]:
        d["rama"] = _git(ruta, "rev-parse", "--abbrev-ref", "HEAD") or ""
        cambios = _git(ruta, "status", "--porcelain", "--untracked-files=all", "--", *FUENTES)
        d["cambios"] = len([l for l in (cambios or "").splitlines() if l.strip()])
        site = _git(ruta, "status", "--porcelain", "--", "_site")
        d["site_sin_confirmar"] = bool((site or "").strip())
        adelante = _git(ruta, "rev-list", "--count", "@{u}..HEAD")
        if adelante is None:
            d["sin_remoto"] = True
        else:
            d["por_empujar"] = int(adelante or 0)
        tf = _git(ruta, "log", "-1", "--format=%ct", "--", *FUENTES)
        tr = _git(ruta, "log", "-1", "--format=%ct", "--", "_site/index.html")
        d["ts_fuentes"] = int(tf) if tf and tf.isdigit() else 0
        d["ts_render"] = int(tr) if tr and tr.isdigit() else 0
    d["fecha_fuentes"], d["fecha_render"] = _fecha(d["ts_fuentes"]), _fecha(d["ts_render"])
    d["estado"], d["motivo"] = clasificar(d)
    d["texto_estado"], d["nivel"] = TEXTO_ESTADO[d["estado"]], NIVEL_ESTADO[d["estado"]]
    return d


def clasificar(d: dict) -> tuple[str, str]:
    """El estado y su motivo, con la regla de la puerta R6."""
    if not d["quarto_yml"]:
        return "problemas", "no tiene _quarto.yml: no es un proyecto de Quarto"
    if not d["git"]:
        return "problemas", "no es un repositorio git: no se puede publicar"
    if not d["site"]:
        return "problemas", "no hay _site/index.html: nunca se renderizó (o se limpió)"
    if d["cambios"]:
        return "sin_render", f"{d['cambios']} fuente(s) sin confirmar: hay que renderizar y confirmar"
    if d["ts_fuentes"] and d["ts_render"] and d["ts_fuentes"] > d["ts_render"]:
        return "sin_render", f"las fuentes se confirmaron el {_fecha(d['ts_fuentes'])}, después del render del {_fecha(d['ts_render'])}"
    if d["site_sin_confirmar"]:
        return "sin_publicar", "_site/ cambió y no está confirmado: commit y push lo publican"
    if d["sin_remoto"]:
        return "sin_publicar", "la rama no sigue a ningún remoto: nada se publica"
    if d["por_empujar"]:
        return "sin_publicar", f"{d['por_empujar']} commit(s) sin empujar: el push publica en Netlify"
    return "al_dia", f"render confirmado el {_fecha(d['ts_render'])}, al día con las fuentes y con el remoto"


def contar(estados: list[dict]) -> dict:
    c = {e: 0 for e, _t, _n in ESTADOS}
    for d in estados:
        c[d["estado"]] = c.get(d["estado"], 0) + 1
    c["todos"] = len(estados)
    return c


def resumen(c: dict) -> str:
    n = c.get("todos", 0)
    partes = [f"{n} sitio" + ("" if n == 1 else "s")]
    for clave, texto in (("al_dia", "al día"), ("sin_render", "sin render"), ("sin_publicar", "sin publicar"), ("problemas", "con problemas")):
        if c.get(clave):
            partes.append(f"{c[clave]} {texto}")
    return " · ".join(partes)
