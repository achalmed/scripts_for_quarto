"""tests/test_post_service.py — el post nuevo sin la ventana (2026-11-17, posts desde Qillqa).

`studio/quarto_app/services/post_service.py` es la única lógica del asistente de posts portada a Python. Lo prueba sin Qt
y sin `quarto_app` (se carga por su ruta, como lo corre Yachay): sin los campos nuevos, el `index.qmd` es el de siempre;
con ellos, lleva `description`, `draft`, `csl`, `citation` y `fuentes`; la orden `crear` simula salvo `--aplicar`, no pisa
un post que ya existe y rechaza un campo desconocido. Todo en el temporal de pytest: nunca el hub ni los pubs.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

RUTA = Path(__file__).resolve().parents[1] / "studio" / "quarto_app" / "services" / "post_service.py"
_spec = importlib.util.spec_from_file_location("post_service_solo", RUTA)
ps = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ps
_spec.loader.exec_module(ps)


def _frontmatter(texto: str) -> dict:
    assert texto.startswith("---\n")
    return yaml.safe_load(texto[4:texto.index("\n---\n", 4)])


def _blog(tmp_path: Path) -> Path:
    blog = tmp_path / "pub"
    (blog / "posts").mkdir(parents=True)
    (blog / "_quarto.yml").write_text("project:\n  type: website\n", encoding="utf-8")
    return blog


def test_sin_campos_nuevos_el_index_es_el_de_siempre():
    texto = ps.generar_index_qmd(ps.DatosPost(titulo="Mi post", tags=["a"], categorias=["B"]))
    fm = _frontmatter(texto)
    assert fm["title"] == "Mi post" and fm["shorttitle"] == "Mi post" and fm["tags"] == ["a"]
    for clave in ("description", "draft", "csl", "citation", "fuentes"):
        assert clave not in fm
    assert "## Introducción" in texto and texto.endswith("references.bib\n")


def test_los_campos_nuevos_salen_en_yaml_valido():
    d = ps.DatosPost(titulo='Un "título" con: dos puntos', descripcion="Resumen de la tarjeta, con coma.", borrador=True,
                     bibliography="referencias.bib", csl="../../_extensions/wjschne/apaquarto/apa.csl",
                     pdf_url="https://x.netlify.app/posts/2026-11-17-a/index.pdf", autor_cita="Edison Achalma",
                     fuentes=[{"calibre_id": 530, "zotero": "mariategui2007", "uso": "p. 129: «el problema»"}],
                     cuerpo="Primer párrafo.\n\n## Una sección\n\nTexto.")
    texto = ps.generar_index_qmd(d)
    fm = _frontmatter(texto)
    assert fm["title"] == 'Un "título" con: dos puntos'
    assert fm["description"] == "Resumen de la tarjeta, con coma." and fm["draft"] is True
    assert fm["csl"].endswith("apa.csl") and fm["bibliography"] == "referencias.bib"
    assert fm["citation"] == {"type": "article-journal", "author": ["Edison Achalma"], "pdf-url": d.pdf_url}
    assert fm["fuentes"] == [{"calibre_id": 530, "zotero": "mariategui2007", "uso": "p. 129: «el problema»"}]
    assert texto.endswith("---\n\nPrimer párrafo.\n\n## Una sección\n\nTexto.\n")


def _crear(blog: Path, datos: dict, *extra: str) -> tuple[int, dict]:
    r = subprocess.run([sys.executable, str(RUTA), "crear", "--blog", str(blog), "--datos", "-", *extra],
                       input=json.dumps(datos), capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)


def test_crear_simula_por_defecto_y_crea_con_aplicar(tmp_path):
    blog = _blog(tmp_path)
    rc, r = _crear(blog, {"titulo": "Hola mundo", "borrador": True})
    carpeta = blog / "posts" / f"{date.today().isoformat()}-hola-mundo"
    assert rc == 0 and r["ok"] and not r["aplicado"] and r["carpeta"] == str(carpeta)
    assert not carpeta.exists()
    assert _frontmatter(r["index_qmd"])["draft"] is True
    rc, r = _crear(blog, {"titulo": "Hola mundo", "borrador": True}, "--aplicar")
    assert rc == 0 and r["aplicado"]
    assert (carpeta / "index.qmd").read_text(encoding="utf-8") == r["index_qmd"]
    assert (carpeta / "references.bib").exists()
    rc, r = _crear(blog, {"titulo": "Hola mundo"}, "--aplicar")
    assert rc == 1 and "Ya existe" in r["error"]


def test_crear_rechaza_lo_que_no_sirve(tmp_path):
    blog = _blog(tmp_path)
    assert _crear(blog, {"titulo": "x", "otro": 1})[0] == 2
    assert _crear(blog, {"titulo": "  "})[0] == 2
    assert _crear(blog, {"titulo": "x", "carpeta_posts": "no-existe"})[0] == 1
    assert _crear(blog, {"titulo": "x", "carpeta_posts": "../posts"})[0] == 1
    assert _crear(tmp_path / "no-es-blog", {"titulo": "x"})[0] == 1


def test_sin_jupyter_el_post_no_declara_motor():
    """Un post sin código no lleva `jupyter: python3` (2026-11-16: desde Qillqa nacía con él y la regla lo marcaba)."""
    assert _frontmatter(ps.generar_index_qmd(ps.DatosPost(titulo="Mi post")))["jupyter"] == "python3"
    assert "jupyter" not in _frontmatter(ps.generar_index_qmd(ps.DatosPost(titulo="Mi post", jupyter=False)))


def test_el_generador_toma_la_url_del_blog_sin_base_url(tmp_path):
    """Sin --base-url, los índices enlazan al `site-url` del blog, no al del hub (2026-11-16)."""
    raiz = Path(__file__).resolve().parents[1] / "backend" / "script_generador_publicacion_similar"
    blog = tmp_path / "pub"
    (blog / "posts" / "2026-01-01-uno").mkdir(parents=True)
    (blog / "_quarto.yml").write_text('project:\n  type: website\nwebsite:\n  site-url: "https://pub.example.app/"\n', encoding="utf-8")
    (blog / "posts" / "2026-01-01-uno" / "index.qmd").write_text("---\ntitle: Uno\n---\n\nTexto.\n", encoding="utf-8")
    for extra, url in (([], "https://pub.example.app"), (["-u", "https://otra.example"], "https://otra.example")):
        r = subprocess.run(["bash", str(raiz / "main.sh"), str(blog), "--dry-run", *extra], capture_output=True, text=True, timeout=60)
        assert f"URL base configurada: {url}" in r.stdout + r.stderr
