# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A collection of **independent tools** (Python 3.8+ and Bash) for managing the author's Quarto blogs. Each `script_*/` directory under `quarto_studio/backend/` is a self-contained tool with its own README; `quarto_studio/` is the desktop GUI that drives them. There is no build system, no test suite, and no linting configuration. All code comments, CLI output, and documentation are written in **Spanish** — keep new code and docs in Spanish to match.

The tools operate on Quarto blog projects that live in `~/Documents` as sibling directories: `pub_*` projects (e.g. `pub_axiomata`, `pub_chaska`) plus `website-achalma`. Posts follow the convention `<blog>/posts/YYYY-MM-DD-titulo/index.qmd`. The Bash tools autodetect the Documents directory by walking up from their own location; this can be overridden with env vars (`QBLOG_DOCS_DIR`, `PUBINDEX_DOCS_DIR`).

Python dependencies: `pyyaml`, `pandas`, `openpyxl` (typically in a conda env, e.g. `conda activate scripts_quarto`).

## The tools

The backend scripts live in `quarto_studio/backend/`:

| Directory                                               | Language | Entry point          | Purpose                                                                                                            |
| -------------------------------------------------------- | -------- | -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `quarto_studio/backend/script_blogs_manager/`                 | Bash     | `main.sh`            | Blog manager v3.0: list/render/preview/publish blogs, create posts (APAQuarto), git ops, backups, interactive menu |
| `quarto_studio/backend/script_metadata_manager/`              | Python   | `main.py`            | Manage YAML metadata AND tags of hundreds of articles via an Excel database (v2.1 absorbed the old tag manager)    |
| `quarto_studio/backend/script_pub_index_symlink/`             | Bash     | `main.sh`            | Maintain "04 index" symlinks (organized by year) to all publication folders                                        |
| `quarto_studio/backend/script_format_yaml/`                   | Python   | `fix_qmd_files.py`   | Idempotent YAML block formatter for `.qmd` files                                                                   |
| `quarto_studio/backend/script_generador_publicacion_similar/` | Bash     | `main.sh`            | Generate publication index files (`_contenido_*.qmd`)                                                              |
| `quarto_studio/`                                          | Python   | `main.py`            | Quarto Studio: desktop GUI (PySide6/Qt6) that unifies all the tools above; the scripts are its backend (see its README) |

The GUI resolves every backend entry point through `quarto_studio/app/services/paths.py` — if a script moves, update only that file.

The old root-level one-off scripts (`1_sincronizar_fecha_carpeta_en_index_qmd.py`, `3_actualizar_enlace_pdf_en_qmd.py`) were absorbed into the metadata manager as `sync-dates` and `sync-pdf-urls` (v2.2) and deleted.

**Note:** the old standalone `script_tag_manager/` was removed in favor of the tag commands inside `script_metadata_manager/` (v2.1); if docs or scripts mention `qmd_tag_manager.py`, they are stale.

## Common commands

Most tools that modify files support `--dry-run` — always suggest a dry run before applying bulk changes.

```bash
# Metadata manager (run from quarto_studio/backend/script_metadata_manager/)
python main.py create-config ~/Documents                 # create metadata_config.yml
python main.py create-template ~/Documents --config metadata_config.yml [--incremental]
python main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run
python main.py update ~/Documents excel.xlsx --blog pub_axiomata --filter-path "2025-06"
python main.py find-differences ~/Documents excel.xlsx
python main.py detect-new-fields ~/Documents --config metadata_config.yml

# Tag management (target = .xlsx file → edits only the Excel; directory → edits .qmd files directly)
python main.py normalize-tags <excel.xlsx | ~/Documents> [--dry-run]
python main.py replace-tags <target> "viejo:nuevo" ["otro:nuevo2" ...]
python main.py remove-tags <target> tag1 [tag2 ...]      # alias: remove-tag
python main.py add-tags <target> tag1 [tag2 ...]         # only adds to articles that already have tags
python main.py tag-stats <target> [--top N]
python main.py audit-tags <target> [--threshold 0.8]

# Path-derived sync (same dual target; absorbed the old root scripts 1_ and 3_)
python main.py sync-dates <target> [--dry-run]        # date ← YYYY-MM-DD folder name (as MM/DD/YYYY)
python main.py sync-pdf-urls <target> [--dry-run]     # citation.pdf-url ← per-blog base URL + article path

# Blog manager
./quarto_studio/backend/script_blogs_manager/main.sh            # interactive menu
./quarto_studio/backend/script_blogs_manager/main.sh list       # list all blogs
./quarto_studio/backend/script_blogs_manager/main.sh help

# Publication index symlinks
./quarto_studio/backend/script_pub_index_symlink/main.sh [--dry-run | --check-broken | --clean-broken | --summary]

# YAML formatter
python quarto_studio/backend/script_format_yaml/fix_qmd_files.py --directory <path> --recursive [--dry-run]

# Publication index generator
./quarto_studio/backend/script_generador_publicacion_similar/main.sh <blog-dir> [--base-url <url>] [--type auto|website|blog] [--dry-run]
```

## Architecture

**Modular Bash pattern** (`script_blogs_manager`, `script_pub_index_symlink`, `script_generador_publicacion_similar`): a thin `main.sh` sources numbered modules from `lib/` in order (`00-config.sh`, `01-...`). Conventions:

- `00-config.sh` centralizes all paths, colors, excluded dirs, and defaults — other modules must not hardcode these values.
- Each tool namespaces its globals with a prefix (`QBLOG_`, `PUBINDEX_`, `GENIDX_`) and guards against double-sourcing with a `*_CONFIG_LOADED` variable.
- Modules load in numeric order because later modules depend on earlier ones.
- `script_pub_index_symlink` writes daily logs to its `logs/` directory.

**Metadata manager** (`script_metadata_manager/`): `main.py` is only argparse + command dispatch; all logic lives in `lib/`:

- `config.py` — loads `metadata_config.yml` (`allowed_blogs`, `excluded_folders`, output dir)
- `collector.py` — finds `index.qmd` files (only in date-named folders)
- `yaml_parser.py` / `field_mapper.py` — YAML frontmatter parsing and Excel-column ↔ YAML-field mapping
- `excel_writer.py` — builds/appends the Excel template (METADATOS + INSTRUCCIONES sheets)
- `qmd_updater.py` — applies Excel rows back to `.qmd` files (only when values differ)
- `sync.py` — diff detection and interactive per-article/batch sync

The Excel file is the source of truth for bulk edits: generate template → edit in Excel → `update` applies changes back to the `.qmd` files.

**Path-derived sync** (inside `script_metadata_manager/`, since v2.2): `path_sync.py` derives `date` from the article's `YYYY-MM-DD-titulo` folder and `citation.pdf-url` from the per-blog base URL + article path. Base URLs are resolved by majority vote over each blog's existing pdf-urls (so one bad copy-pasted URL can't poison detection — note `pub_chaska` → `chaska-x.netlify.app`, not derivable from the folder name), overridable via `blog_base_urls` in `metadata_config.yml`. It never creates a `citation` block, only updates existing ones.

**Tag management** (inside `script_metadata_manager/`, since v2.1): `tag_utils.py` has the pure functions (normalization lowercases, strips accents, converts spaces to underscores: `Gestión Empresarial` → `gestion_empresarial`; dedup, string similarity); `tag_operations.py` applies operations to either the Excel `tags` column or directly to `.qmd` files (through the same `collector` + `write_yaml_to_qmd` used by `update`); `tag_reports.py` builds `tag-stats` and `audit-tags` reports. Every tag operation normalizes the full list, and articles without a `tags` field are always skipped. There is exactly ONE YAML writer (`qmd_updater.write_yaml_to_qmd`) and ONE field reorderer (`field_mapper.reorder_yaml`) — do not introduce parallel implementations.
