"""backend/script_metadata_manager/lib/path_sync.py — metadatos derivados de la ruta del artículo y normalización de `date` a ISO.

Objetivo: mantener en cada index.qmd (y en la columna correspondiente del
  Excel) los dos metadatos que se DERIVAN de la ruta, y una sola grafía de
  fecha en todo el conjunto:
    sync-dates     → `date` desde la carpeta YYYY-MM-DD-titulo (ISO AAAA-MM-DD)
    sync-pdf-urls  → `citation.pdf-url` = <base_url_del_blog>/<ruta>/index.pdf
    fechas-iso     → `date` al formato canónico AAAA-MM-DD sin cambiar el valor
                     (lee MM/DD/YYYY, ISO, ISO con hora y date/datetime)
Método: absorbe los scripts legacy 1_sincronizar_fecha_carpeta_en_index_qmd.py
  y 3_actualizar_enlace_pdf_en_qmd.py, adaptados a la estructura actual
  (pub_* como submódulos del hub): cada blog tiene su propia URL base, que se
  resuelve por mayoría de los pdf-url ya existentes en ese blog, con override
  opcional vía blog_base_urls en metadata_config.yml. Las fechas pasan por
  lib/fechas.py. Cuando solo cambia `date`, se sustituye ESA línea del
  frontmatter y el resto del archivo queda byte a byte igual (comentarios,
  comillas y orden incluidos); el escritor YAML completo
  (qmd_updater.write_yaml_to_qmd) es el respaldo si la línea no se encuentra.
Fundamento: meta/NORMATIVA_ARCHIVOS.md §3 (toda fecha es AAAA-MM-DD; hallazgo
  H8); fase M6 (2026-09-15). Hasta v2.2 el formato canónico era MM/DD/YYYY.
Alternativa: reescribir todo el frontmatter con el escritor YAML también para
  las fechas. Se descarta: convertir 243 posts habría reordenado claves y
  borrado comentarios que el autor mantiene (`draft: true  # …`).
Límite: la parte del script legacy que reescribía enlaces a PDF dentro del
  cuerpo del documento NO se migró (ningún artículo los usa, censo 2026-07, y
  el regex era peligroso sobre el archivo completo). `duedate` no se toca.

Depende de: collector, config, excel_writer, fechas, field_mapper, qmd_updater, yaml_parser.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

import yaml

from .collector import collect_index_files
from .config import SYSTEM_EXCLUDED_FOLDERS
from .excel_writer import open_metadata_sheets
from .fechas import a_iso, fecha_de_carpeta
from .field_mapper import reorder_yaml
from .qmd_updater import write_yaml_to_qmd
from .yaml_parser import extract_yaml_only_index

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_BASE_URL_RE    = re.compile(r"^(https?://[^/]+)")
# la línea `date:` de primer nivel del frontmatter: clave, valor, comentario en línea
_DATE_LINE_RE   = re.compile(r"^(date:[ \t]*)(.*?)([ \t]+#.*)?$", re.MULTILINE)


# --- Derivación desde la ruta (funciones puras) -----------------------------

def date_from_folder(folder_name: str) -> Optional[str]:
    """'2023-05-12-titulo' → '2023-05-12' (formato canónico, NORMATIVA §3)."""
    return fecha_de_carpeta(folder_name)


def blog_dir_from_ruta(ruta: str) -> str:
    """
    Carpeta del blog dentro de ruta_archivo. Los pub_* son submódulos del hub
    ('website-achalma/_pubs/pub_chaska/…'), así que se busca el primer
    segmento con prefijo pub_; si no hay, el primer segmento ('website-achalma').
    """
    parts = Path(str(ruta)).parts
    for part in parts:
        if part.startswith("pub_"):
            return part
    return parts[0]


def expected_pdf_url(base_url: str, ruta: str) -> str:
    """
    URL canónica del PDF: base del blog + ruta interna del artículo.
    'website-achalma/_pubs/pub_chaska/operating-system/2017-.../index.qmd' con base
    'https://chaska-x.netlify.app' →
    'https://chaska-x.netlify.app/operating-system/2017-.../index.pdf'
    """
    parts = Path(str(ruta)).parts
    blog_idx = parts.index(blog_dir_from_ruta(ruta))
    inner = "/".join(parts[blog_idx + 1:-1])  # sin carpeta del blog ni index.qmd
    return f"{base_url}/{inner}/index.pdf"


def normalize_date_value(value) -> Optional[str]:
    """
    Lleva el valor actual de date a 'AAAA-MM-DD' comparable; si no se reconoce
    como fecha devuelve el texto tal cual (para que el informe lo muestre).
    yaml.safe_load devuelve date/datetime cuando la fecha iba sin comillas.
    """
    if value is None:
        return None
    return a_iso(value) or str(value).strip()


# --- Escritura de `date` sin tocar el resto del frontmatter -----------------

def sustituir_date(content: str, match, nuevo: str) -> Optional[str]:
    """
    Devuelve el archivo con la línea `date:` del frontmatter cambiada a
    `date: <nuevo>` (comentario en línea conservado), o None si el frontmatter
    no tiene una línea `date:` de primer nivel.
    """
    fm = match.group(1)
    m = _DATE_LINE_RE.search(fm)
    if not m:
        return None
    nueva_linea = f"{m.group(1)}{nuevo}{m.group(3) or ''}"
    fm_nuevo = fm[:m.start()] + nueva_linea + fm[m.end():]
    return content[:match.start(1)] + fm_nuevo + content[match.end(1):]


def _escribir_date(file_path: Path, content: str, match, yaml_data: dict, nuevo: str):
    """Escribe `date` sustituyendo su línea; si no está, reescribe el YAML entero."""
    reemplazado = sustituir_date(content, match, nuevo)
    if reemplazado is not None:
        file_path.write_text(reemplazado, encoding="utf-8")
        return
    print("   (sin línea `date:` de primer nivel: se reescribe el frontmatter completo)")
    yaml_data["date"] = nuevo
    write_yaml_to_qmd(file_path, reorder_yaml(yaml_data), content, match.end())


# --- Resolución de URL base por blog -----------------------------------------

def resolve_blog_base_urls(
    url_samples: Iterable[Tuple[str, Optional[str]]],
    configured: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Determina la URL base de cada blog.

    Prioridad: blog_base_urls del metadata_config.yml > mayoría de los
    pdf-url existentes en ese blog. El voto por mayoría hace que un
    pdf-url erróneo aislado (copy-paste de otro blog) no contamine la
    detección.

    url_samples: pares (carpeta_del_blog, pdf_url_existente_o_None).
    """
    votes: Dict[str, Counter] = defaultdict(Counter)
    for blog, url in url_samples:
        if not url:
            continue
        match = _BASE_URL_RE.match(str(url).strip())
        if match:
            votes[blog][match.group(1)] += 1

    resolved = {
        blog: counter.most_common(1)[0][0] for blog, counter in votes.items()
    }
    for blog, url in (configured or {}).items():
        resolved[blog] = url.rstrip("/")
    return resolved


def _print_base_urls(base_urls: Dict[str, str]):
    print("\n🌐 URL base por blog (config > mayoría de pdf-url existentes):")
    for blog in sorted(base_urls):
        print(f"   {blog:<28} → {base_urls[blog]}")


def _current_pdf_url(yaml_data: dict) -> Optional[str]:
    citation = yaml_data.get("citation")
    if isinstance(citation, dict):
        return citation.get("pdf-url")
    return None


# --- Infraestructura común de recorrido --------------------------------------

def _leer_articulo(file_path: Path, ruta: str):
    """(content, match, yaml_data) de un .qmd con frontmatter legible; None si no."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ No se pudo leer {ruta}: {e}")
        return None
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None
    try:
        yaml_data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"⚠️  YAML inválido en {ruta}: {e}")
        return None
    return content, match, yaml_data


def _iter_article_yaml(base_path: Path, df_files, path_filter: Optional[str]):
    """
    Genera (ruta_relativa, file_path, content, match, yaml_data) por artículo
    legible. Centraliza lectura + parseo para los comandos de sync.
    """
    for _, row in df_files.iterrows():
        ruta = row["ruta_archivo"]
        if path_filter and path_filter.lower() not in str(ruta).lower():
            continue
        file_path = base_path / ruta
        if not file_path.exists():
            continue
        leido = _leer_articulo(file_path, str(ruta))
        if leido is None:
            continue
        content, match, yaml_data = leido
        yield str(ruta), file_path, content, match, yaml_data


def _iter_todos_los_qmd(base_path: Path, path_filter: Optional[str]):
    """
    Todo .qmd bajo base_path (no solo los index.qmd con carpeta datada), fuera
    de las carpetas del sistema. Es el recorrido de fechas-iso: la norma de
    fechas rige todo el sitio, no solo los posts. No aplica `excluded_folders`
    de la configuración: esa lista nombra carpetas de ~/Documents (`latex`,
    `stata`, `ofimatica`…) que coinciden con secciones de pub_numerus-scriptum,
    y quien pasa un directorio explícito quiere normalizarlo entero.
    """
    excluidas = set(SYSTEM_EXCLUDED_FOLDERS)
    for file_path in sorted(base_path.rglob("*.qmd")):
        rel = file_path.relative_to(base_path)
        if any(parte in excluidas for parte in rel.parts[:-1]):
            continue
        if path_filter and path_filter.lower() not in str(rel).lower():
            continue
        leido = _leer_articulo(file_path, str(rel))
        if leido is None:
            continue
        content, match, yaml_data = leido
        yield str(rel), file_path, content, match, yaml_data


def _print_sync_summary(changed: int, unchanged: int, skipped: int,
                        skipped_label: str, dry_run: bool):
    print(f"\n{'=' * 70}")
    print(f"{'🔍 RESUMEN DE SIMULACIÓN' if dry_run else '✅ RESUMEN'}")
    print(f"   ✅ Actualizados:           {changed}")
    print(f"   ⏭️  Ya sincronizados:       {unchanged}")
    print(f"   ⚠️  Omitidos ({skipped_label}): {skipped}")
    print(f"{'=' * 70}\n")
    if dry_run and changed > 0:
        print("💡 Para aplicar cambios, ejecuta sin --dry-run\n")


# --- sync-dates sobre archivos -----------------------------------------------

def sync_dates_files(
    base_path: Path,
    allowed_blogs: Set[str],
    user_excluded_folders: Set[str],
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """Sincroniza el campo date de cada index.qmd con su carpeta (escribe ISO)."""
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '📅 SINCRONIZANDO'} FECHAS DESDE CARPETAS (ISO AAAA-MM-DD)\n")
    print("=" * 70)

    df_files = collect_index_files(
        base_path, allowed_blogs, user_excluded_folders,
        blog_name=blog_filter, verbose=False,
    )
    if df_files.empty:
        print("⚠️  No se encontraron artículos")
        return

    changed = unchanged = skipped = 0
    for ruta, file_path, content, match, yaml_data in _iter_article_yaml(
        base_path, df_files, path_filter
    ):
        expected = date_from_folder(file_path.parent.name)
        if expected is None:
            skipped += 1
            continue

        current = normalize_date_value(yaml_data.get("date"))
        if current == expected and _date_ya_iso(match):
            unchanged += 1
            continue

        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} {ruta}")
        print(f"   date: {_date_literal(match)!r} → {expected!r}")

        if not dry_run:
            _escribir_date(file_path, content, match, yaml_data, expected)

    _print_sync_summary(changed, unchanged, skipped, "sin fecha en carpeta", dry_run)


def _date_literal(match) -> Optional[str]:
    """El texto literal de la línea `date:` del frontmatter (con comillas si las lleva)."""
    m = _DATE_LINE_RE.search(match.group(1))
    return m.group(2) if m else None


def _date_ya_iso(match) -> bool:
    """True si la línea `date:` ya está escrita como AAAA-MM-DD sin comillas ni hora."""
    literal = _date_literal(match)
    return bool(literal) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", literal))


# --- fechas-iso sobre archivos -----------------------------------------------

def fechas_iso_files(
    base_path: Path,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Normaliza el campo date de todo .qmd a AAAA-MM-DD sin cambiar la fecha:
    '05/16/2023' → 2023-05-16 · '"2021-06-01T10:00:00+00:00"' → 2021-06-01 ·
    '"2026-01-02"' → 2026-01-02. Un valor irreconocible se informa y se deja.
    """
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '📅 NORMALIZANDO'} FECHAS A ISO AAAA-MM-DD\n")
    print("=" * 70)

    changed = unchanged = skipped = 0
    for ruta, file_path, content, match, yaml_data in _iter_todos_los_qmd(
        base_path, path_filter
    ):
        if "date" not in yaml_data:
            continue
        literal = _date_literal(match)
        if literal is None or literal == "":
            skipped += 1
            continue
        nuevo = a_iso(yaml_data.get("date")) or a_iso(literal)
        if nuevo is None:
            skipped += 1
            print(f"\n⚠️  {ruta}\n   date: {literal!r} no se reconoce como fecha; no se toca")
            continue
        if literal == nuevo:
            unchanged += 1
            continue

        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} {ruta}")
        print(f"   date: {literal!r} → {nuevo!r}")
        if not dry_run:
            _escribir_date(file_path, content, match, yaml_data, nuevo)

    _print_sync_summary(changed, unchanged, skipped, "sin fecha reconocible", dry_run)


# --- sync-pdf-urls sobre archivos --------------------------------------------

def sync_pdf_urls_files(
    base_path: Path,
    allowed_blogs: Set[str],
    user_excluded_folders: Set[str],
    configured_urls: Optional[Dict[str, str]] = None,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Sincroniza citation.pdf-url de cada index.qmd con su ruta real.
    Solo actualiza artículos que YA tienen bloque citation (no lo crea).
    """
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '🔗 SINCRONIZANDO'} PDF-URLS DESDE RUTAS\n")
    print("=" * 70)

    df_files = collect_index_files(
        base_path, allowed_blogs, user_excluded_folders,
        blog_name=blog_filter, verbose=False,
    )
    if df_files.empty:
        print("⚠️  No se encontraron artículos")
        return

    # Pre-pase: censo de pdf-urls existentes para el voto por mayoría
    samples = []
    for _, row in df_files.iterrows():
        yaml_data = extract_yaml_only_index(base_path / row["ruta_archivo"]) or {}
        samples.append(
            (blog_dir_from_ruta(row["ruta_archivo"]), _current_pdf_url(yaml_data))
        )
    base_urls = resolve_blog_base_urls(samples, configured_urls)
    _print_base_urls(base_urls)

    changed = unchanged = skipped = 0
    for ruta, file_path, content, match, yaml_data in _iter_article_yaml(
        base_path, df_files, path_filter
    ):
        blog = blog_dir_from_ruta(ruta)
        base_url = base_urls.get(blog)
        citation = yaml_data.get("citation")

        # Sin citation o sin URL base conocida no hay nada que sincronizar
        if base_url is None or not isinstance(citation, dict):
            skipped += 1
            continue

        expected = expected_pdf_url(base_url, ruta)
        current = citation.get("pdf-url")
        if current == expected:
            unchanged += 1
            continue

        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} {ruta}")
        print(f"   pdf-url: {current}")
        print(f"        →   {expected}")

        if not dry_run:
            citation["pdf-url"] = expected
            write_yaml_to_qmd(
                file_path, reorder_yaml(yaml_data), content, match.end()
            )

    _print_sync_summary(
        changed, unchanged, skipped, "sin citation o sin URL base", dry_run
    )


# --- Sync sobre Excel (solo columnas date / citation_pdf_url) ----------------

def _iter_excel_rows(ws, ws_values, headers, blog_filter, path_filter):
    """Genera (row_idx, ruta) de las filas que pasan los filtros."""
    ruta_col = headers["ruta_archivo"]
    blog_col = headers["blog_nombre"]
    for row_idx in range(2, ws.max_row + 1):
        ruta = ws_values.cell(row_idx, ruta_col).value
        if not ruta:
            continue
        if blog_filter and ws_values.cell(row_idx, blog_col).value != blog_filter:
            continue
        if path_filter and path_filter.lower() not in str(ruta).lower():
            continue
        yield row_idx, str(ruta)


def _escribir_celda_texto(ws, row_idx: int, col: int, valor: str):
    """Escribe texto y fija el formato de celda a texto: Excel no lo convierte en fecha serial."""
    celda = ws.cell(row_idx, col, valor)
    celda.number_format = "@"


def _sync_excel_column(
    excel_path: str,
    column: str,
    expected_for_ruta,
    blog_filter: Optional[str],
    path_filter: Optional[str],
    dry_run: bool,
    normalize_current=lambda v: None if v is None else str(v).strip(),
    como_texto: bool = False,
):
    """
    Motor común de sync sobre Excel: recorre filas, calcula el valor
    esperado desde ruta_archivo (callback expected_for_ruta) y actualiza
    la columna indicada. Los .qmd no se tocan (eso lo hace 'update').
    """
    try:
        wb, ws, ws_values = open_metadata_sheets(excel_path)
    except Exception as e:
        print(f"❌ Error abriendo Excel: {e}")
        return

    headers = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1)}
    for required in ("ruta_archivo", "blog_nombre", column):
        if required not in headers:
            print(f"❌ El Excel no tiene columna '{required}' en METADATOS")
            return

    target_col = headers[column]
    changed = unchanged = skipped = 0

    for row_idx, ruta in _iter_excel_rows(
        ws, ws_values, headers, blog_filter, path_filter
    ):
        expected = expected_for_ruta(ruta)
        if expected is None:
            skipped += 1
            continue
        actual = ws.cell(row_idx, target_col).value
        es_formula = isinstance(actual, str) and actual.startswith("=")
        current = normalize_current(ws_values.cell(row_idx, target_col).value)
        if current == expected and not es_formula:
            unchanged += 1
            continue

        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} Fila {row_idx}: {ruta}")
        mostrado = actual if es_formula else current
        print(f"   {column}: {mostrado!r} → {expected!r}")
        if not dry_run:
            if como_texto:
                _escribir_celda_texto(ws, row_idx, target_col, expected)
            else:
                ws.cell(row_idx, target_col, expected)

    _print_sync_summary(changed, unchanged, skipped, "sin valor derivable", dry_run)

    if not dry_run and changed > 0:
        wb.save(excel_path)
        print(f"✅ Excel guardado: {excel_path}")
        print("💡 Los archivos .qmd NO fueron modificados. Para aplicar:")
        print(f"   python main.py update ~/Documents {excel_path}\n")


def sync_dates_excel(
    excel_path: str,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """Sincroniza la columna date del Excel con la carpeta de cada ruta (texto ISO; sustituye fórmulas)."""
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '📅 SINCRONIZANDO'} FECHAS EN EXCEL (ISO AAAA-MM-DD)\n")
    print("=" * 70)
    _sync_excel_column(
        excel_path, "date",
        expected_for_ruta=lambda ruta: date_from_folder(Path(ruta).parts[-2]),
        blog_filter=blog_filter, path_filter=path_filter, dry_run=dry_run,
        normalize_current=normalize_date_value, como_texto=True,
    )


def fechas_iso_excel(
    excel_path: str,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """
    Normaliza la columna date del Excel a texto AAAA-MM-DD sin cambiar la fecha.
    Una fórmula (=TEXT(DATE(…),"mm/dd/yyyy")) se sustituye por su valor
    calculado; si el archivo no guarda el valor calculado, por la fecha de la
    carpeta de ruta_archivo, que es lo que la fórmula calculaba.
    """
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '📅 NORMALIZANDO'} FECHAS DEL EXCEL A ISO AAAA-MM-DD\n")
    print("=" * 70)

    try:
        wb, ws, ws_values = open_metadata_sheets(excel_path)
    except Exception as e:
        print(f"❌ Error abriendo Excel: {e}")
        return
    headers = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1)}
    for required in ("ruta_archivo", "blog_nombre", "date"):
        if required not in headers:
            print(f"❌ El Excel no tiene columna '{required}' en METADATOS")
            return
    col = headers["date"]
    changed = unchanged = skipped = 0

    for row_idx, ruta in _iter_excel_rows(ws, ws_values, headers, blog_filter, path_filter):
        actual = ws.cell(row_idx, col).value
        if actual is None or (isinstance(actual, str) and not actual.strip()):
            continue
        if isinstance(actual, str) and actual.startswith("="):
            base = ws_values.cell(row_idx, col).value
            nuevo = a_iso(base) if base is not None else date_from_folder(Path(ruta).parts[-2])
        else:
            nuevo = a_iso(actual)
        if nuevo is None:
            skipped += 1
            print(f"\n⚠️  Fila {row_idx}: {ruta}\n   date: {actual!r} no se reconoce como fecha; no se toca")
            continue
        if actual == nuevo:
            unchanged += 1
            continue
        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} Fila {row_idx}: {ruta}")
        print(f"   date: {actual!r} → {nuevo!r}")
        if not dry_run:
            _escribir_celda_texto(ws, row_idx, col, nuevo)

    _print_sync_summary(changed, unchanged, skipped, "sin fecha reconocible", dry_run)
    if not dry_run and changed > 0:
        wb.save(excel_path)
        print(f"✅ Excel guardado: {excel_path}\n")


def sync_pdf_urls_excel(
    excel_path: str,
    configured_urls: Optional[Dict[str, str]] = None,
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """Sincroniza la columna citation_pdf_url del Excel con cada ruta."""
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '🔗 SINCRONIZANDO'} PDF-URLS EN EXCEL\n")
    print("=" * 70)

    # Censo para voto por mayoría a partir de la propia columna del Excel
    try:
        wb, ws, ws_values = open_metadata_sheets(excel_path)
    except Exception as e:
        print(f"❌ Error abriendo Excel: {e}")
        return
    headers = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1)}
    if "citation_pdf_url" not in headers:
        print("❌ El Excel no tiene columna 'citation_pdf_url' en METADATOS")
        return

    samples = [
        (blog_dir_from_ruta(ruta),
         ws_values.cell(row_idx, headers["citation_pdf_url"]).value)
        for row_idx, ruta in _iter_excel_rows(ws, ws_values, headers, None, None)
    ]
    base_urls = resolve_blog_base_urls(samples, configured_urls)
    _print_base_urls(base_urls)

    def expected(ruta: str) -> Optional[str]:
        base = base_urls.get(blog_dir_from_ruta(ruta))
        return expected_pdf_url(base, ruta) if base else None

    _sync_excel_column(
        excel_path, "citation_pdf_url", expected_for_ruta=expected,
        blog_filter=blog_filter, path_filter=path_filter, dry_run=dry_run,
    )
