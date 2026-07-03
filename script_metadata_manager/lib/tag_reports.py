"""
lib/tag_reports.py
==================
Estadísticas y auditoría de la taxonomía de tags.

Comandos cubiertos:
  tag-stats   → frecuencias, top N, huérfanos, distribución por blog/año
  audit-tags  → variantes, typos probables, singular/plural, problemas de
                formato, con comandos replace-tags listos para ejecutar

Ambos aceptan como fuente los archivos .qmd (vía collector, la verdad en
disco) o un Excel (columna tags de METADATOS).

Depende de: collector, yaml_parser, tag_utils.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from .collector import collect_index_files
from .tag_utils import (
    find_similar_pairs,
    is_plural_pair,
    normalize_tag,
    tags_from_cell,
    tags_from_yaml_value,
)
from .yaml_parser import extract_yaml_only_index


# =============================================================================
# RECOLECCIÓN DE DATOS (archivos o Excel)
# =============================================================================

def collect_tag_data_from_files(
    base_path: Path,
    allowed_blogs: Set[str],
    user_excluded_folders: Set[str],
    blog_filter: Optional[str] = None,
) -> pd.DataFrame:
    """
    Recorre la colección y devuelve un DataFrame con una fila por artículo:
    ruta_archivo, blog_nombre, tags (lista, posiblemente vacía).
    """
    df_files = collect_index_files(
        base_path, allowed_blogs, user_excluded_folders,
        blog_name=blog_filter, verbose=False,
    )

    rows = []
    for _, row in df_files.iterrows():
        file_path = base_path / row["ruta_archivo"]
        yaml_data = extract_yaml_only_index(file_path) or {}
        tags = tags_from_yaml_value(yaml_data.get("tags")) or []
        rows.append({
            "ruta_archivo": row["ruta_archivo"],
            "blog_nombre":  row["blog_nombre"],
            "tags":         tags,
        })
    return pd.DataFrame(rows)


def collect_tag_data_from_excel(
    excel_path: str, blog_filter: Optional[str] = None
) -> pd.DataFrame:
    """Lee METADATOS y devuelve el mismo formato que la versión de archivos."""
    df = pd.read_excel(excel_path, sheet_name="METADATOS")
    if blog_filter:
        df = df[df["blog_nombre"] == blog_filter]

    rows = []
    for _, row in df.iterrows():
        if pd.isna(row.get("ruta_archivo")):
            continue
        raw = row.get("tags")
        tags = tags_from_cell(None if pd.isna(raw) else raw)
        rows.append({
            "ruta_archivo": row["ruta_archivo"],
            "blog_nombre":  row["blog_nombre"],
            "tags":         tags,
        })
    return pd.DataFrame(rows)


def _year_from_path(ruta: str) -> Optional[str]:
    """Extrae el año de la carpeta con fecha (…/YYYY-MM-DD-titulo/index.qmd)."""
    match = re.search(r"(\d{4})-\d{2}-\d{2}", str(ruta))
    return match.group(1) if match else None


# =============================================================================
# ESTADÍSTICAS (tag-stats)
# =============================================================================

def print_tag_stats(df: pd.DataFrame, top: int = 20):
    """Imprime el reporte de estadísticas de tags de la colección."""
    print("\n📊 ESTADÍSTICAS DE TAGS")
    print("=" * 70)

    if df.empty:
        print("⚠️  No hay artículos para analizar")
        return

    all_tags: List[str] = [t for tags in df["tags"] for t in tags]
    counter = Counter(all_tags)
    with_tags = df[df["tags"].apply(bool)]

    print(f"\n📈 GENERALES")
    print(f"   Total artículos:            {len(df)}")
    print(f"   Artículos con tags:         {len(with_tags)}")
    print(f"   Artículos sin tags:         {len(df) - len(with_tags)}")
    print(f"   Total de tags (con repet.): {len(all_tags)}")
    print(f"   Tags únicos:                {len(counter)}")
    if len(with_tags) > 0:
        avg = len(all_tags) / len(with_tags)
        print(f"   Promedio tags/artículo:     {avg:.2f}")

    if counter:
        print(f"\n🏆 TOP {min(top, len(counter))} TAGS MÁS USADOS")
        width = max(len(t) for t, _ in counter.most_common(top))
        for tag, count in counter.most_common(top):
            bar = "█" * min(count, 40)
            print(f"   {tag:<{width}}  {count:>4}  {bar}")

        orphans = sorted(t for t, c in counter.items() if c == 1)
        print(f"\n🥀 TAGS HUÉRFANOS (usados 1 sola vez): {len(orphans)}")
        for i in range(0, min(len(orphans), 30), 6):
            print(f"   {', '.join(orphans[i:i + 6])}")
        if len(orphans) > 30:
            print(f"   ... y {len(orphans) - 30} más")

    print(f"\n📚 DISTRIBUCIÓN POR BLOG")
    by_blog = df.groupby("blog_nombre")["tags"].agg(
        articulos="count",
        tags_unicos=lambda s: len({t for tags in s for t in tags}),
    )
    for blog, row in by_blog.iterrows():
        print(f"   {blog:<32} {row['articulos']:>4} artículos, "
              f"{row['tags_unicos']:>4} tags únicos")

    print(f"\n📅 DISTRIBUCIÓN POR AÑO")
    year_counter: Dict[str, int] = defaultdict(int)
    for ruta in df["ruta_archivo"]:
        year = _year_from_path(ruta)
        if year:
            year_counter[year] += 1
    for year in sorted(year_counter):
        print(f"   {year}: {year_counter[year]:>4} artículos")

    print("\n" + "=" * 70 + "\n")


# =============================================================================
# AUDITORÍA (audit-tags)
# =============================================================================

def _find_normalization_variants(counter: Counter) -> Dict[str, List[str]]:
    """
    Agrupa tags crudos que colapsan a la misma forma normalizada
    (mayúsculas, tildes, espacios, guiones): son inconsistencias seguras.
    """
    groups: Dict[str, List[str]] = defaultdict(list)
    for tag in counter:
        groups[normalize_tag(tag)].append(tag)
    return {k: sorted(v) for k, v in groups.items() if len(v) > 1}


def _find_format_issues(counter: Counter) -> Dict[str, List[str]]:
    """Clasifica tags cuyo formato se aparta del snake_case canónico."""
    issues: Dict[str, List[str]] = defaultdict(list)
    for tag in sorted(counter):
        if tag != tag.lower():
            issues["mayúsculas"].append(tag)
        if re.search(r"[áéíóúüñÁÉÍÓÚÜÑ]", tag):
            issues["tildes/ñ"].append(tag)
        if " " in tag:
            issues["espacios"].append(tag)
        if "-" in tag:
            issues["kebab-case (guiones)"].append(tag)
        if len(tag) > 30:
            issues["muy largos (>30)"].append(tag)
    return issues


def print_tag_audit(df: pd.DataFrame, threshold: float = 0.8):
    """
    Audita la taxonomía: variantes, formato, singular/plural y typos
    probables. Emite recomendaciones como comandos listos para ejecutar.
    """
    print("\n🔬 AUDITORÍA DE TAXONOMÍA DE TAGS")
    print("=" * 70)

    if df.empty:
        print("⚠️  No hay artículos para analizar")
        return

    counter = Counter(t for tags in df["tags"] for t in tags)
    if not counter:
        print("⚠️  No hay tags en la colección")
        return

    recommendations: List[Tuple[str, str]] = []  # (viejo, nuevo)

    # --- 1. Variantes que colapsan al normalizar --------------------------------
    variants = _find_normalization_variants(counter)
    print(f"\n1️⃣  VARIANTES DE ESCRITURA (colapsan al normalizar): {len(variants)}")
    for normalized, forms in sorted(variants.items()):
        print(f"   {' | '.join(forms)}  →  {normalized}")
        recommendations.extend(
            (form, normalized) for form in forms if form != normalized
        )

    # --- 2. Problemas de formato -------------------------------------------------
    issues = _find_format_issues(counter)
    print(f"\n2️⃣  PROBLEMAS DE FORMATO")
    if issues:
        for kind, tags in issues.items():
            shown = ", ".join(tags[:8])
            extra = f" ... (+{len(tags) - 8})" if len(tags) > 8 else ""
            print(f"   • {kind} ({len(tags)}): {shown}{extra}")
            recommendations.extend(
                (t, normalize_tag(t)) for t in tags if normalize_tag(t) != t
            )
    else:
        print("   ✅ Todos los tags siguen el formato snake_case")

    # --- 3. Singular / plural ----------------------------------------------------
    normalized_unique = sorted({normalize_tag(t) for t in counter})
    plural_pairs = [
        (a, b) for a, b, _ in find_similar_pairs(normalized_unique, 0.75)
        if is_plural_pair(a, b)
    ]
    print(f"\n3️⃣  POSIBLES PARES SINGULAR/PLURAL: {len(plural_pairs)}")
    for a, b in plural_pairs:
        # Recomendar consolidar en la forma más frecuente
        freq_a = sum(c for t, c in counter.items() if normalize_tag(t) == a)
        freq_b = sum(c for t, c in counter.items() if normalize_tag(t) == b)
        keep, drop = (a, b) if freq_a >= freq_b else (b, a)
        print(f"   {a} ({freq_a}) / {b} ({freq_b})  →  sugerido: {keep}")
        recommendations.append((drop, keep))

    # --- 4. Tags casi iguales (typos probables) ---------------------------------
    similar = [
        (a, b, r) for a, b, r in find_similar_pairs(normalized_unique, threshold)
        if not is_plural_pair(a, b)
    ]
    print(f"\n4️⃣  TAGS CASI IGUALES (similitud ≥ {threshold:.0%}): {len(similar)}")
    for a, b, ratio in similar[:25]:
        print(f"   {a}  ~  {b}  ({ratio:.0%})")
    if len(similar) > 25:
        print(f"   ... y {len(similar) - 25} pares más")
    if similar:
        print("   💡 Revisar manualmente: pueden ser typos o conceptos distintos")

    # --- Recomendaciones ejecutables ---------------------------------------------
    unique_recs = sorted(set(recommendations))
    print(f"\n{'=' * 70}")
    print(f"💡 RECOMENDACIONES ({len(unique_recs)} correcciones automáticas)")
    if unique_recs:
        print("\n   La mayoría se resuelve normalizando toda la colección:")
        print("      python main.py normalize-tags <destino> --dry-run")
        pending = [(o, n) for o, n in unique_recs if normalize_tag(o) != n]
        if pending:
            print("\n   Consolidaciones que requieren replace-tags:")
            args = " ".join(f'"{o}:{n}"' for o, n in pending[:10])
            print(f"      python main.py replace-tags <destino> {args} --dry-run")
            if len(pending) > 10:
                print(f"      ... y {len(pending) - 10} reemplazos más")
    else:
        print("   ✅ Taxonomía consistente: sin correcciones automáticas pendientes")
    print("=" * 70 + "\n")
