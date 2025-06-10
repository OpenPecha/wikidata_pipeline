from typing import Dict, List

import pywikibot

from wiki_utils.utils.logger import get_logger

# Initialize the logger
logger = get_logger(__name__)

# Configuration
SITE_CODE = "mul"  # 'mul' is for multilingual Wikisource (wikisource.org)
FAMILY = "wikisource"


def login_to_wikisource() -> pywikibot.Site:
    """Login to Wikisource and return the site object."""
    site = pywikibot.Site(SITE_CODE, FAMILY)
    site.login()
    return site


def parse_text_file(text_file_path: str) -> Dict[str, str]:
    """
    Parse a text file into a dict: {page_number: text}.
    Assumes format:
        Page no: N\n<text>\n...\nPage no: M\n<text>\n...
    """
    page_texts = {}
    current_page = None
    current_lines: List[str] = []
    with open(text_file_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.strip().startswith("Page no:"):
                if current_page is not None:
                    page_texts[str(current_page)] = "\n".join(current_lines).strip()
                try:
                    current_page = line.split(":", 1)[1].strip()
                except IndexError:
                    current_page = None
                current_lines = []
            else:
                current_lines.append(line)
        if current_page is not None:
            page_texts[str(current_page)] = "\n".join(current_lines).strip()
    return page_texts


def prepare_wikisource_content(
    page_text_dict: Dict[str, str], wikisource_file_name: str
) -> str:
    """
    Combine text from the dictionary into a single string,
    adding == Page N == and {{Page:...}} annotations at the start of each page's content.
    """
    content_lines = []
    for page_num in sorted(page_text_dict, key=lambda x: int(x)):
        text = page_text_dict[page_num].strip()
        if not text:
            logger.warning(f"Page {page_num} has no text content in the dictionary.")
            continue
        annotation = (
            f"== Page {page_num} ==\n{{{{Page:{wikisource_file_name}/{page_num}}}}}"
        )
        content_lines.append(f"{annotation}\n{text}\n")
    return "\n".join(content_lines).strip()


def create_main_page(
    site: pywikibot.Site,
    main_title: str,
    page_text_dict: Dict[str, str],
    index_title: str,
    summary: str = "Bot: Creating main page with transclusion of text pages",
    overwrite: bool = False,
) -> None:
    """
    Create or update the main page that transcludes all the individual pages using {{Page:}} annotations.
    """
    wikisource_file_name = index_title.replace("Index:", "")
    content = prepare_wikisource_content(page_text_dict, wikisource_file_name)
    main_page = pywikibot.Page(site, main_title)
    if not main_page.exists() or not main_page.text.strip() or overwrite:
        main_page.text = content
        main_page.save(summary=summary)
        logger.info(
            f"{'Updated' if main_page.exists() and overwrite else 'Created'} main page: {main_title}"
        )
    else:
        logger.warning(f"Main page {main_title} already exists. Not overwriting.")


if __name__ == "__main__":
    text_file_path = "data/text/katok-Vol-1.txt"
    page_text_dict = parse_text_file(text_file_path)
    site = login_to_wikisource()
    index_title = "Index:སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡.pdf"
    main_title = "སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡"
    create_main_page(site, main_title, page_text_dict, index_title, overwrite=True)
