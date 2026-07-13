"""
lib/path_sync.py
================
Sincroniza metadatos que se DERIVAN de la ruta del artículo:

  sync-dates     → campo date desde la carpeta YYYY-MM-DD-titulo
                   (formato canónico MM/DD/YYYY)
  sync-pdf-urls  → citation.pdf-url = <base_url_del_blog>/<ruta>/index.pdf

Absorbe los scripts legacy 1_sincronizar_fecha_carpeta_en_index_qmd.py y
3_actualizar_enlace_pdf_en_qmd.py, adaptados a la estructura actual
(pub_* + website-achalma): cada blog tiene su propia URL base, que se
resuelve por mayoría de los pdf-url ya existentes en ese blog, con
override opcional vía blog_base_urls en metadata_config.yml.

Nota: la parte del script legacy que reescribía enlaces a PDF dentro del
cuerpo del documento NO se migró: ningún artículo actual los usa (censo
2026-07) y el regex original era peligroso sobre el archivo completo.

Depende de: collector, yaml_parser, field_mapper, qmd_updater, excel_writer.
"""

import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

import yaml

from .collector import collect_index_files
from .excel_writer import open_metadata_sheets
from .field_mapper import reorder_yaml
from .qmd_updater import write_yaml_to_qmd
from .yaml_parser import extract_yaml_only_index

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_FOLDER_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
_BASE_URL_RE    = re.compile(r"^(https?://[^/]+)")


# =============================================================================
# DERIVACIÓN DESDE LA RUTA (funciones puras)
# =============================================================================

def date_from_folder(folder_name: str) -> Optional[str]:
    """'2023-05-12-titulo' → '05/12/2023' (formato canónico del proyecto)."""
    match = _FOLDER_DATE_RE.match(folder_name)
    if not match:
        return None
    year, month, day = match.groups()
    return f"{month}/{day}/{year}"


def blog_dir_from_ruta(ruta: str) -> str:
    """Primer segmento de ruta_archivo: 'pub_chaska', 'website-achalma'…"""
    return Path(str(ruta)).parts[0]


def expected_pdf_url(base_url: str, ruta: str) -> str:
    """
    URL canónica del PDF: base del blog + ruta interna del artículo.
    'pub_chaska/operating-system/2017-.../index.qmd' con base
    'https://chaska-x.netlify.app' →
    'https://chaska-x.netlify.app/operating-system/2017-.../index.pdf'
    """
    parts = Path(str(ruta)).parts
    inner = "/".join(parts[1:-1])  # sin carpeta del blog ni index.qmd
    return f"{base_url}/{inner}/index.pdf"


def normalize_date_value(value) -> Optional[str]:
    """
    Lleva el valor actual de date a string comparable MM/DD/YYYY.
    yaml.safe_load puede devolver date/datetime si la fecha iba sin comillas.
    """
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.strftime("%m/%d/%Y")
    return str(value).strip()


# =============================================================================
# RESOLUCIÓN DE URL BASE POR BLOG
# =============================================================================

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


# =============================================================================
# INFRAESTRUCTURA COMÚN DE RECORRIDO
# =============================================================================

def _iter_article_yaml(base_path: Path, df_files, path_filter: Optional[str]):
    """
    Genera (ruta_relativa, file_path, content, match, yaml_data) por artículo
    legible. Centraliza lectura + parseo para los dos comandos de sync.
    """
    for _, row in df_files.iterrows():
        ruta = row["ruta_archivo"]
        if path_filter and path_filter.lower() not in str(ruta).lower():
            continue
        file_path = base_path / ruta
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ No se pudo leer {ruta}: {e}")
            continue
        match = _FRONTMATTER_RE.match(content)
        if not match:
            continue
        try:
            yaml_data = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as e:
            print(f"⚠️  YAML inválido en {ruta}: {e}")
            continue
        yield str(ruta), file_path, content, match, yaml_data


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


# =============================================================================
# SYNC-DATES SOBRE ARCHIVOS
# =============================================================================

def sync_dates_files(
    base_path: Path,
    allowed_blogs: Set[str],
    user_excluded_folders: Set[str],
    blog_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    dry_run: bool = False,
):
    """Sincroniza el campo date de cada index.qmd con su carpeta."""
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '📅 SINCRONIZANDO'} FECHAS DESDE CARPETAS\n")
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
        if current == expected:
            unchanged += 1
            continue

        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} {ruta}")
        print(f"   date: {current!r} → {expected!r}")

        if not dry_run:
            yaml_data["date"] = expected
            write_yaml_to_qmd(
                file_path, reorder_yaml(yaml_data), content, match.end()
            )

    _print_sync_summary(changed, unchanged, skipped, "sin fecha en carpeta", dry_run)


# =============================================================================
# SYNC-PDF-URLS SOBRE ARCHIVOS
# =============================================================================

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


# =============================================================================
# SYNC SOBRE EXCEL (solo columnas date / citation_pdf_url)
# =============================================================================

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


def _sync_excel_column(
    excel_path: str,
    column: str,
    expected_for_ruta,
    blog_filter: Optional[str],
    path_filter: Optional[str],
    dry_run: bool,
    normalize_current=lambda v: None if v is None else str(v).strip(),
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
        current = normalize_current(ws_values.cell(row_idx, target_col).value)
        if current == expected:
            unchanged += 1
            continue

        changed += 1
        icon = "🔍" if dry_run else "✅"
        print(f"\n{icon} Fila {row_idx}: {ruta}")
        print(f"   {column}: {current!r} → {expected!r}")
        if not dry_run:
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
    """Sincroniza la columna date del Excel con la carpeta de cada ruta."""
    print(f"\n{'🔍 SIMULACIÓN' if dry_run else '📅 SINCRONIZANDO'} FECHAS EN EXCEL\n")
    print("=" * 70)
    _sync_excel_column(
        excel_path, "date",
        expected_for_ruta=lambda ruta: date_from_folder(Path(ruta).parts[-2]),
        blog_filter=blog_filter, path_filter=path_filter, dry_run=dry_run,
        normalize_current=normalize_date_value,
    )


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
