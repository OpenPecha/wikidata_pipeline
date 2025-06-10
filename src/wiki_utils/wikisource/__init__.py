# Import key functions from etext_upload for backward compatibility
from .etext_upload import (
    batch_upload_from_csv,
    get_page_titles,
    parse_text_file,
    upload_texts,
)
from .mainpage_extended_text_upload import create_main_page, prepare_wikisource_content
