"""
lib/__init__.py
Paquete de módulos del metadata-manager.
"""
from .config import (
    load_config,
    create_default_config,
    ALL_FIELDS,
    VERSION,
    AUTHOR,
    EMAIL,
)
from .collector import collect_index_files
from .yaml_parser import (
    extract_yaml_only_index,
    extract_yaml_merged,
    detect_document_mode,
    is_article_index,
    flatten_yaml_keys,
)
from .field_mapper import extract_value, apply_row_to_yaml
from .excel_writer import (
    build_metadata_sheet,
    build_instructions_sheet,
    append_new_articles,
    add_columns_to_excel,
)
from .qmd_updater import update_from_excel
from .sync import (
    find_differences,
    sync_single_interactive,
    sync_batch_interactive,
    detect_new_fields,
)
