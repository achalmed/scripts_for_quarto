# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A collection of **independent tools** (Python 3.8+ and Bash) for managing the author's Quarto blogs. Each `script_*/` directory is a self-contained tool with its own README. There is no build system, no test suite, and no linting configuration. All code comments, CLI output, and documentation are written in **Spanish** — keep new code and docs in Spanish to match.

The tools operate on Quarto blog projects that live in `~/Documents` as sibling directories: `pub_*` projects (e.g. `pub_axiomata`, `pub_chaska`) plus `website-achalma`. Posts follow the convention `<blog>/posts/YYYY-MM-DD-titulo/index.qmd`. The Bash tools autodetect the Documents directory by walking up from their own location; this can be overridden with env vars (`QBLOG_DOCS_DIR`, `PUBINDEX_DOCS_DIR`).

Python dependencies: `pyyaml`, `pandas`, `openpyxl` (typically in a conda env, e.g. `conda activate scripts_quarto`).

## The tools

| Directory                               | Language | Entry point          | Purpose                                                                                                            |
| --------------------------------------- | -------- | -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `script_blogs_manager/`                 | Bash     | `main.sh`            | Blog manager v3.0: list/render/preview/publish blogs, create posts (APAQuarto), git ops, backups, interactive menu |
| `script_metadata_manager/`              | Python   | `main.py`            | Manage YAML metadata of hundreds of articles via an Excel database                                                 |
| `script_pub_index_symlink/`             | Bash     | `main.sh`            | Maintain "04 index" symlinks (organized by year) to all publication folders                                        |
| `script_tag_manager/`                   | Python   | `qmd_tag_manager.py` | Normalize/replace/add/remove tags in `.qmd` YAML                                                                   |
| `script_format_yaml/`                   | Python   | `fix_qmd_files.py`   | Idempotent YAML block formatter for `.qmd` files                                                                   |
| `script_generador_publicacion_similar/` | Bash     | `main.sh`            | Generate publication index files (`_contenido_*.qmd`)                                                              |

The two root-level scripts (`1_sincronizar_fecha_carpeta_en_index_qmd.py`, `3_actualizar_enlace_pdf_en_qmd.py`) are legacy one-offs with hardcoded relative paths (`../tecnologia-seguridad`, `../blog`) that must be edited before running.

**Note:** the root `README.md` examples for the metadata manager still reference the old `quarto_metadata_manager.py`; the actual entry point since v2.0 is `main.py` with the same subcommands.

## Common commands

Most tools that modify files support `--dry-run` — always suggest a dry run before applying bulk changes.

```bash
# Metadata manager (run from script_metadata_manager/)
python main.py create-config ~/Documents                 # create metadata_config.yml
python main.py create-template ~/Documents --config metadata_config.yml [--incremental]
python main.py update ~/Documents excel_databases/quarto_metadata.xlsx --dry-run
python main.py update ~/Documents excel.xlsx --blog pub_axiomata --filter-path "2025-06"
python main.py find-differences ~/Documents excel.xlsx
python main.py detect-new-fields ~/Documents --config metadata_config.yml

# Blog manager
./script_blogs_manager/main.sh            # interactive menu
./script_blogs_manager/main.sh list       # list all blogs
./script_blogs_manager/main.sh help

# Publication index symlinks
./script_pub_index_symlink/main.sh [--dry-run | --check-broken | --clean-broken | --summary]

# Tag manager (run from script_tag_manager/)
python qmd_tag_manager.py --normalize --recursive --directory <path>
python qmd_tag_manager.py --replace "viejo:nuevo" --recursive

# YAML formatter
python script_format_yaml/fix_qmd_files.py --directory <path> --recursive [--dry-run]

# Publication index generator
./script_generador_publicacion_similar/main.sh <blog-dir> [--base-url <url>] [--type auto|website|blog] [--dry-run]
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

**Tag manager**: `tag_config.py` holds user-editable dictionaries (`COMMON_REPLACEMENTS`, etc.) consumed by `qmd_tag_manager.py`; tag normalization lowercases, strips accents, and converts spaces to underscores (`Gestión Empresarial` → `gestion_empresarial`).
