import re

import pywikibot

from wiki_utils.utils.logger import get_logger

# Initialize the logger
logger = get_logger(__name__)


def extract_page_number(page):
    # Extracts the number after the last '/' in the title, returns as int if possible
    m = re.search(r"/(\d+)$", page.title())
    return int(m.group(1)) if m else float("inf")


def get_base_info(site, index_title):
    """
    Extract base title components and namespace information from an Index title

    :param site: pywikibot.Site object
    :param index_title: Title of the Index page, e.g., "Index:SomeBook.pdf"
    :return: Tuple of (base_title, base_title_no_ext, index_ns, page_ns, page_prefix)
    """
    # Get the base name for constructing page titles
    if index_title.startswith("Index:"):
        index_prefix_len = len("Index:")
        base_title = index_title[index_prefix_len:]
    else:
        base_title = index_title

    if "." in base_title:
        base_title_no_ext = ".".join(base_title.split(".")[:-1])
    else:
        base_title_no_ext = base_title

    # Get namespace IDs
    index_ns = site.namespace(106)  # Index namespace
    page_ns = site.namespace(104)  # Page namespace

    # Generate query for pages in Page namespace that belong to this index
    page_prefix = f"{page_ns}:{base_title_no_ext}/"

    return base_title, base_title_no_ext, index_ns, page_ns, page_prefix


def get_pages(site, index_title):
    """
    Get all Page: namespace pages associated with an Index
    :param site: pywikibot.Site object
    :param index_title: Title of the Index page, e.g., "Index:SomeBook.pdf"
    :return: List of pywikibot.Page objects sorted by page number
    """
    # Get base info using the new function
    _, base_title_no_ext, _, _, page_prefix = get_base_info(site, index_title)

    logger.info(f"Looking for pages with prefix: {page_prefix}")

    # Get all pages that belong to this index
    pages = list(site.allpages(prefix=base_title_no_ext, namespace=104))

    # Sort pages by page number
    pages = sorted(pages, key=extract_page_number)

    if not pages:
        logger.warning(f"No pages found for index: {index_title}")
    else:
        logger.info(f"Found {len(pages)} pages to process")

    return pages


def format_page_orientation(index_title, site=None, dry_run=False):
    """
    Create a mainspace page for a given Index page by transcluding its text.
    Also, wrap each page in the Index with a styled div if it exists.
    :param index_title: Title of the Index page, e.g., "Index:SomeBook.pdf"
    :param site: pywikibot.Site object for bo.wikisource
    :param dry_run: If True, do not actually save the page
    """
    if site is None:
        site = pywikibot.Site("mul", "wikisource")

    # --- Step 1: Check if Index page exists and process each page ---
    index_page = pywikibot.Page(site, index_title)
    if not index_page.exists():
        print(f"Index page '{index_title}' does not exist!")
        return

    # Get pages using the new get_pages function
    pages = get_pages(site, index_title)

    # Process each page
    for page in pages:
        logger.info(f"Processing page: {page.title()}")
        try:
            if page.exists():
                orig_text = page.text.strip()
                # Remove any other HTML tags from the main content
                # (This preserves the actual text while removing formatting tags)
                main_text = re.sub(r"<[^>]+>", "", orig_text).strip()

                if main_text:  # Apply our styling to the clean text
                    styled_content = (
                        '<div style="margin-left: 3em; margin-right: 3em;">'
                        f"{main_text}"
                        "</div>"
                        "<noinclude></noinclude>"
                    )

                else:
                    styled_content = (
                        '<div style="margin-left: 3em; margin-right: 3em;">'
                        "&nbsp;"
                        "</div>"
                        "<noinclude></noinclude>"
                    )

                # Set proofread status to level 3 with specific user
                user = site.username()
                quality_tag = (
                    f'<noinclude><pagequality level="3" user="{user}" /></noinclude>'
                )

                logger.info(
                    f"Setting proofread status to level 3 for page: {page.title()}"
                )

                # Format text in the correct ProofreadPage format with newlines
                new_text = f"{quality_tag}\n{styled_content}"

                logger.info(f"Updating page: {page.title()}")
                if not dry_run:
                    page.text = new_text
                    # Set the proofread_page_quality property
                    page.proofread_page_quality = 3  # 3 = Proofread
                    # Use the same summary as in etext_upload.py
                    page.save(
                        summary="Bot: Adding margin styling and marking as proofread."
                    )
                else:
                    logger.info("Dry run: not saving page.")
        except Exception as e:
            logger.error(f"Error processing page {page.title()}: {e}")


def create_main_page(
    index_title, main_title=None, from_page=1, to_page=None, site=None, dry_run=False
):
    """
    Create a mainspace page for a given Index page using <pages> tag for transclusion.

    :param index_title: Title of the Index page, e.g., "Index:SomeBook.pdf"
    :param main_title: Title for the main namespace page. If None, derived from index_title
    :param from_page: First page to include (default: 1)
    :param to_page: Last page to include (default: None, will use last available page)
    :param site: pywikibot.Site object for wikisource
    :param dry_run: If True, do not actually save the page
    :return: The created main page object
    """
    if site is None:
        site = pywikibot.Site("mul", "wikisource")

    # Check if Index page exists
    index_page = pywikibot.Page(site, index_title)
    if not index_page.exists():
        logger.error(f"Index page '{index_title}' does not exist!")
        return None

    # Use the get_base_info function to extract title components
    base_title, base_title_no_ext, _, _, _ = get_base_info(site, index_title)

    # Get pages using the get_pages function
    pages = get_pages(site, index_title)

    if not pages:
        logger.warning(f"No pages found for index: {index_title}")
        return None

    # If no main_title provided, derive it from base_title_no_ext
    if main_title is None:
        main_title = base_title_no_ext

    # If to_page not specified, use the last available page
    if to_page is None and pages:
        last_page = pages[-1]
        to_page = extract_page_number(last_page)

    # Create the actual content with <pages> tag
    # The index attribute should not include the "Index:" prefix
    content = f'<pages index="{base_title}" from={from_page} to={to_page} />'

    # Create or update the main page
    main_page = pywikibot.Page(site, main_title)

    if not dry_run:
        main_page.text = content
        main_page.save(summary="Bot: Creating mainspace transclusion of Index pages")
        logger.info(f"Mainspace page created: {main_title}")

    return main_page


if __name__ == "__main__":
    index_title = "Index:སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡.pdf"
    format_page_orientation(index_title)
    main_title = "སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡"
    create_main_page(main_title)
