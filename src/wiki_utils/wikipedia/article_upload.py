import pywikibot

from wiki_utils.utils.logger import get_logger

# Initialize the logger
logger = get_logger(__name__)


def login_to_wikipedia(lang: str = "bo") -> pywikibot.Site:
    """
    Logs in to Wikipedia using Pywikibot.

    Parameters:
    - lang: Language code for the Wikipedia site (default: "en" for English)

    Returns:
    - site: Pywikibot Site object for Wikipedia.
    """
    site = pywikibot.Site(lang, "wikipedia")
    site.login()  # Log into Wikipedia
    logger.info(f"Logged in to {lang} Wikipedia as {site.username()}")
    return site


def login_to_wikidata() -> pywikibot.Site:
    """
    Logs in to Wikidata using Pywikibot.

    Returns:
    - site: Pywikibot Site object for Wikidata.
    """
    site = pywikibot.Site("wikidata", "wikidata")
    site.login()  # Log into Wikidata
    logger.info(f"Logged in to Wikidata as {site.username()}")
    return site


def get_article(site: pywikibot.Site, title: str) -> pywikibot.Page:
    """
    Gets a Wikipedia article by title.

    Parameters:
    - site: Pywikibot Site object for Wikipedia.
    - title: Article title

    Returns:
    - page: Pywikibot Page object for the article.
    """
    page = pywikibot.Page(site, title)
    return page


def create_article(
    site: pywikibot.Site,
    title: str,
    content: str,
    summary: str = "Created via script",
    minor: bool = False,
) -> bool:
    """
    Creates a new Wikipedia article.

    Parameters:
    - site: Pywikibot Site object for Wikipedia.
    - title: Article title
    - content: Article content (wikitext)
    - summary: Edit summary
    - minor: Whether this is a minor edit

    Returns:
    - success: Boolean indicating success
    """
    try:
        page = get_article(site, title)

        # Check if the page already exists
        if page.exists():
            logger.warning(
                f"Page '{title}' already exists. Use edit_article to modify it."
            )
            return False

        page.text = content
        page.save(summary=summary, minor=minor)
        logger.info(f"Successfully created page: {title}")
        return True
    except Exception as e:
        logger.error(f"Error creating page {title}: {e}")
        return False


def edit_article(
    site: pywikibot.Site,
    title: str,
    content: str,
    summary: str = "Edit via script",
    minor: bool = False,
) -> bool:
    """
    Edits an existing Wikipedia article.

    Parameters:
    - site: Pywikibot Site object for Wikipedia.
    - title: Article title
    - content: Article content (wikitext)
    - summary: Edit summary
    - minor: Whether this is a minor edit

    Returns:
    - success: Boolean indicating success
    """
    try:
        page = get_article(site, title)

        # Check if the page exists
        if not page.exists():
            logger.warning(
                f"Page '{title}' does not exist. Use create_article to create it."
            )
            return False

        text = page.text
        logger.info(f"Current content of page '{title}': {text}")

        with open("article_content.txt", "w") as f:
            f.write(text)

        page.text = content
        page.save(summary=summary, minor=minor)
        logger.info(f"Successfully edited page: {title}")
        return True
    except Exception as e:
        logger.error(f"Error editing page {title}: {e}")
        return False


if __name__ == "__main__":
    # Login to Wikipedia
    site = login_to_wikipedia("bo")
    # Login to Wikidata
    login_to_wikidata()
    title = "ཨོཾ་ནི 123"
    content = """
    ཨོཾ་ནི་ eited
    """
    # Check if the article exists and decide whether to create or edit
    page = get_article(site, title)
    if page.exists():
        edit_article(
            site,
            title,
            content,
            summary="Edited via script",
            minor=True,
        )
    else:
        create_article(
            site,
            title,
            content,
            summary="Created via script",
            minor=True,
        )
    logger.info(f"Successfully created or edited article: {title}")
