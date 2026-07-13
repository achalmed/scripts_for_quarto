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
from .field_mapper import extract_value, apply_row_to_yaml, reorder_yaml
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
from .tag_utils import (
    normalize_tag,
    normalize_tag_list,
    transform_tags,
    parse_replacement_args,
    find_similar_pairs,
)
from .tag_operations import apply_tag_ops_to_files, apply_tag_ops_to_excel
from .path_sync import (
    sync_dates_files,
    sync_dates_excel,
    sync_pdf_urls_files,
    sync_pdf_urls_excel,
    resolve_blog_base_urls,
)
from .tag_reports import (
    collect_tag_data_from_files,
    collect_tag_data_from_excel,
    print_tag_stats,
    print_tag_audit,
)
