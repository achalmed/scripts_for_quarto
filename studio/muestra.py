#!/usr/bin/env python3
"""studio/muestra.py — una familia de sitios de muestra para las pruebas y las capturas de Quarto Studio.

Nunca el hub `web` ni los pubs reales (Netlify despliega con cada push). En una carpeta temporal crea un espacio de
trabajo de juguete: `core/` enlazado al real (solo se lee), un hub `web/` con el registro `_pubs/pubs.yml`, una copia
de la puerta R6, `_indice/` con un enlace bueno y otro roto, y tres pubs con git y un remoto «bare» local en cada
uno de los estados de la ventana (al día, con cambios sin render, con render sin publicar) más el hub con problemas
(sin `_site/`); un fragmento `_contenido_posts.qmd`; y, si `openpyxl` está, un Excel de metadatos con la hoja
`METADATOS`. Devuelve las variables de entorno con las que `core/env` y los backends ven la muestra. Ojo: Quarto omite los
archivos de un proyecto cuya ruta pasa por una carpeta oculta (`~/.cache/…`): para un `quarto render` real la muestra va
en una ruta sin componentes `.x` (las pruebas usan /var/tmp; las capturas, /tmp).

    from muestra import crear
    m = crear(Path(carpeta))      # m.entorno: DOCS_ROOT, INDEX_DIR, HOME, XDG_*, GIT_CONFIG_GLOBAL…
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
FECHA_PASADA = "2026-01-10T10:00:00+00:00"
FECHA_RENDER = "2026-01-12T10:00:00+00:00"
FECHA_DESPUES = "2026-01-20T10:00:00+00:00"

PUBS = [("aequilibria", "Macroeconomía", "Política monetaria y fiscal, crecimiento y ciclos."),
        ("axiomata", "Matemática", "Cálculo, álgebra lineal y estadística aplicada a la economía."),
        ("chaska", "Tecnología y seguridad", "Ciberseguridad, privacidad y herramientas.")]
ENTRADAS = {
    "aequilibria": [("2026-01-05-curva-de-phillips", "Curva de Phillips y expectativas", "macroeconomía, inflación"),
                    ("2025-11-20-multiplicador-fiscal", "El multiplicador fiscal", "política fiscal")],
    "axiomata": [("2026-01-08-matrices-y-determinantes", "Matrices y determinantes", "álgebra lineal"),
                 ("2025-12-02-limites-y-continuidad", "Límites y continuidad", "cálculo"),
                 ("2025-10-14-regresion-lineal-simple", "Regresión lineal simple", "estadística, econometría")],
    "chaska": [("2026-01-02-configuracion-de-quarto", "Configuración de Quarto", "quarto, herramientas")],
}


@dataclass
class Muestra:
    raiz: Path
    hub: Path
    pubs: Path
    remotos: Path
    excel: Path | None
    entorno: dict = field(default_factory=dict)


def _core_real() -> Path | None:
    d = REPO
    while d != d.parent and not (d / "core" / "env.py").is_file():
        d = d.parent
    return d / "core" if (d / "core" / "env.py").is_file() else None


def _git(env: dict, cwd: Path, *args: str, fecha: str | None = None) -> str:
    e = dict(env)
    if fecha:
        e["GIT_AUTHOR_DATE"] = e["GIT_COMMITTER_DATE"] = fecha
    r = subprocess.run(["git", "-C", str(cwd), *args], env=e, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} en {cwd}: {r.stderr}")
    return r.stdout.strip()


def _entrada(sitio: Path, carpeta: str, titulo: str, tags: str, seccion: str = "posts") -> Path:
    d = sitio / seccion / carpeta
    d.mkdir(parents=True, exist_ok=True)
    fecha = carpeta[:10]
    lista = "".join(f"  - {t.strip()}\n" for t in tags.split(","))
    (d / "index.qmd").write_text(f'---\ntitle: "{titulo}"\ndate: "{fecha}"\ntags:\n{lista}categories: [Muestra]\n---\n\n## Introducción\n\nTexto de muestra de «{titulo}».\n', encoding="utf-8")
    return d


def _html(titulo: str, cuerpo: str, lista: bool = False) -> str:
    """Una página como las que deja `quarto render`, mínima y sin recursos externos."""
    contenido = f"<ul>{cuerpo}</ul>" if lista else cuerpo
    return (f'<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
            '<style>body{font-family:sans-serif;max-width:42em;margin:2em auto;line-height:1.5;padding:0 1em}</style></head>'
            f"<body><h1>{titulo}</h1>{contenido}</body></html>\n")


def _sitio(ruta: Path, nombre: str, titulo: str, con_site: bool = True) -> None:
    ruta.mkdir(parents=True, exist_ok=True)
    (ruta / "_quarto.yml").write_text(f'project:\n  type: website\n  output-dir: _site\nwebsite:\n  title: "{titulo}"\n  site-url: https://{nombre}.netlify.app/\nformat:\n  html:\n    theme: cosmo\n', encoding="utf-8")
    (ruta / "index.qmd").write_text(f'---\ntitle: "{titulo}"\nlisting:\n  contents: posts\n---\n\nSitio de muestra.\n', encoding="utf-8")
    if con_site:
        (ruta / "_site").mkdir(exist_ok=True)
        (ruta / "_site" / "index.html").write_text(f"<html><body>{titulo} v1</body></html>\n", encoding="utf-8")
    (ruta / ".gitignore").write_text(".quarto/\n/_freeze/\n", encoding="utf-8")


def crear(raiz: Path) -> Muestra:
    raiz = Path(raiz)
    raiz.mkdir(parents=True, exist_ok=True)
    core = _core_real()
    if core is not None and not (raiz / "core").exists():
        (raiz / "core").symlink_to(core, target_is_directory=True)
    hub, pubs, remotos, hogar = raiz / "web", raiz / "web" / "_pubs", raiz / "remotos", raiz / "hogar"
    pubs.mkdir(parents=True, exist_ok=True)
    remotos.mkdir(exist_ok=True)
    hogar.mkdir(exist_ok=True)
    gitconfig = raiz / "gitconfig"
    gitconfig.write_text("[user]\n\tname = Muestra\n\temail = muestra@example.invalid\n[init]\n\tdefaultBranch = main\n[advice]\n\tdetachedHead = false\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"HOME": str(hogar), "GIT_CONFIG_GLOBAL": str(gitconfig), "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C.UTF-8"})

    # el hub: registro, puerta, _indice, una entrada; sin _site (con problemas)
    _sitio(hub, "achalmaedison", "Hub de muestra", con_site=False)
    (hub / "_pubs" / "pubs.yml").write_text(
        "actualizado: 2026-11-02\nhub:\n  carpeta: web\n  repo: website-muestra\n  url: https://achalmaedison.netlify.app/\n"
        "autor:\n  nombre: Muestra\npubs:\n" + "".join(f"  - carpeta: {n}\n    repo: {n}\n    url: https://{n}.netlify.app/\n    tema: {t}\n    descripcion: {d}\n" for n, t, d in PUBS),
        encoding="utf-8")
    (hub / "scripts").mkdir(exist_ok=True)
    puerta = (core.parent / "web" / "scripts" / "puerta-r6.sh") if core else None
    if puerta and puerta.is_file():
        shutil.copy2(puerta, hub / "scripts" / "puerta-r6.sh")
    _entrada(hub, "2026-01-03-bienvenida-al-hub", "Bienvenida al hub", "hub", seccion="blog/posts")
    _git(env, hub, "init", "-q", "-b", "main")
    _git(env, hub, "add", "-A")
    _git(env, hub, "commit", "-q", "-m", "hub de muestra", fecha=FECHA_PASADA)

    # los pubs, cada uno en un estado
    for nombre, tema, _d in PUBS:
        sitio = pubs / nombre
        _sitio(sitio, nombre, f"{tema} (muestra)")
        for carpeta, titulo, tags in ENTRADAS[nombre]:
            _entrada(sitio, carpeta, titulo, tags)
        if nombre == "axiomata":
            (sitio / "posts" / "_contenido_posts.qmd").write_text("<!-- fragmento de inclusión — índice de posts (muestra) -->\n\n"
                                                                    + "".join(f"- [{t}]({c}/index.qmd)\n" for c, t, _ in ENTRADAS[nombre]), encoding="utf-8")
        _git(env, sitio, "init", "-q", "-b", "main")
        _git(env, sitio, "add", "-A")
        _git(env, sitio, "commit", "-q", "-m", "fuentes", fecha=FECHA_PASADA)
        (sitio / "_site" / "index.html").write_text(_html(f"{tema} (muestra)", "".join(
            f'<li><a href="posts/{c}/index.html">{t}</a> · {c[:10]}</li>' for c, t, _ in ENTRADAS[nombre]), lista=True), encoding="utf-8")
        for carpeta, titulo, tags in ENTRADAS[nombre]:      # una página por entrada: lo que la vista previa muestra
            pagina = sitio / "_site" / "posts" / carpeta / "index.html"
            pagina.parent.mkdir(parents=True, exist_ok=True)
            pagina.write_text(_html(titulo, f"<p><em>{carpeta[:10]} · {tags}</em></p><p>Una entrada de muestra de {tema.lower()}: "
                                            "el texto que Quarto renderiza a partir de su <code>index.qmd</code>.</p>"
                                            '<p><a href="../../index.html">← Volver a la portada</a></p>'), encoding="utf-8")
        _git(env, sitio, "add", "-A")
        _git(env, sitio, "commit", "-q", "-m", "render", fecha=FECHA_RENDER)
        remoto = remotos / f"{nombre}.git"
        _git(env, raiz, "init", "-q", "--bare", str(remoto))
        _git(env, sitio, "remote", "add", "origin", str(remoto))
        _git(env, sitio, "push", "-q", "-u", "origin", "main")
        if nombre == "axiomata":            # con cambios sin render: una fuente confirmada después del render y otra sin confirmar
            (sitio / "posts" / "2026-01-08-matrices-y-determinantes" / "index.qmd").write_text(
                '---\ntitle: "Matrices y determinantes"\ndate: "2026-01-08"\ntags:\n  - álgebra lineal\ncategories: [Muestra]\n---\n\n## Introducción\n\nTexto corregido.\n', encoding="utf-8")
            _git(env, sitio, "add", "-A")
            _git(env, sitio, "commit", "-q", "-m", "corrección", fecha=FECHA_DESPUES)
            _git(env, sitio, "push", "-q")
            (sitio / "posts" / "2025-12-02-limites-y-continuidad" / "index.qmd").write_text(
                '---\ntitle: "Límites y continuidad"\ndate: "2025-12-02"\ntags:\n  - cálculo\n---\n\nAmpliado sin confirmar.\n', encoding="utf-8")
        if nombre == "chaska":              # con render sin publicar: _site confirmado después de las fuentes, sin empujar
            (sitio / "_site" / "index.html").write_text(f"<html><body>{tema} v3</body></html>\n", encoding="utf-8")
            _git(env, sitio, "add", "-A")
            _git(env, sitio, "commit", "-q", "-m", "render nuevo", fecha=FECHA_DESPUES)

    # el índice del vault: un enlace bueno y otro roto
    (hub / "_indice" / "2026").mkdir(parents=True, exist_ok=True)
    (hub / "_indice" / "2026" / "2026-01-05-curva-de-phillips").symlink_to(pubs / "aequilibria" / "posts" / "2026-01-05-curva-de-phillips")
    (hub / "_indice" / "2026" / "2026-01-01-borrado").symlink_to(pubs / "no-existe")

    # el Excel de metadatos (con openpyxl)
    excel = None
    try:
        import openpyxl
        libro = openpyxl.Workbook()
        hoja = libro.active
        hoja.title = "INSTRUCCIONES"
        hoja["A1"] = "Excel de metadatos de muestra"
        ws = libro.create_sheet("METADATOS")
        ws.append(["ruta_archivo", "blog_nombre", "title", "date", "tags", "categories"])
        ws.append(["pub_aequilibria/posts/2026-01-05-curva-de-phillips/index.qmd", "aequilibria", "Curva de Phillips y expectativas", "2026-01-05", "macroeconomía, inflación", "Muestra"])
        ws.append(["axiomata/posts/2026-01-08-matrices-y-determinantes/index.qmd", "axiomata", "Matrices, determinantes y sistemas", "2026-01-08", "álgebra lineal", "Muestra"])
        excel = raiz / "quarto_metadata.xlsx"
        libro.save(excel)
    except ImportError:
        pass

    entorno = {"DOCS_ROOT": str(raiz), "INDEX_DIR": str(hub), "HOME": str(hogar), "XDG_CONFIG_HOME": str(hogar / ".config"),
               "XDG_CACHE_HOME": str(hogar / ".cache"), "XDG_STATE_HOME": str(hogar / ".local" / "state"), "RESPALDOS_DIR": str(raiz / "respaldos"),
               "GIT_CONFIG_GLOBAL": str(gitconfig), "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C.UTF-8", "QUARTO_STUDIO_SIN_VENV": "1"}
    for k in ("QBLOG_WEBSITE_DIR", "QBLOG_PUBS_SUBDIR", "PUBINDEX_PUBS_SUBDIR", "PUBS_SUBDIR", "QBLOG_BACKUP_DIR"):
        entorno.pop(k, None)
    return Muestra(raiz, hub, pubs, remotos, excel, entorno)


if __name__ == "__main__":
    import json
    import tempfile
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="quarto-muestra-"))
    m = crear(destino)
    print(json.dumps({"raiz": str(m.raiz), "excel": str(m.excel), "entorno": m.entorno}, indent=1, ensure_ascii=False))
