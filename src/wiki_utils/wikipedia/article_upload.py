import pywikibot

from wiki_utils.wikidata import login_to_wikidata


def login_to_wikipedia(lang: str = "en") -> pywikibot.Site:
    """
    Logs in to Wikipedia using Pywikibot.

    Parameters:
    - lang: Language code for the Wikipedia site (default: "en" for English)

    Returns:
    - site: Pywikibot Site object for Wikipedia.
    """
    site = pywikibot.Site(lang, "wikipedia")
    site.login()  # Log into Wikipedia
    print(f"Logged in to {lang} Wikipedia as {site.username()}")
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


def create_or_edit_article(
    site: pywikibot.Site,
    title: str,
    content: str,
    summary: str = "Edit via script",
    minor: bool = False,
    overwrite_existing: bool = True,
) -> bool:
    """
    Creates or edits a Wikipedia article.

    Parameters:
    - site: Pywikibot Site object for Wikipedia.
    - title: Article title
    - content: Article content (wikitext)
    - summary: Edit summary
    - minor: Whether this is a minor edit
    - overwrite_existing: Whether to overwrite if the page already exists

    Returns:
    - success: Boolean indicating success
    """
    try:
        page = get_article(site, title)
        text = page.text
        print(f"Current content of page '{title}': {text}")

        with open("article_content.txt", "w") as f:
            f.write(text)

        # Check if the page exists
        if page.exists() and not overwrite_existing:
            print(
                f"Page '{title}' already exists and overwrite_existing is False. Skipping."
            )
            return False

        page.text = content
        # page.save(summary=summary, minor=minor)  # Uncomment this to actually save
        print(f"Successfully saved page: {title}")
        return True
    except Exception as e:
        print(f"Error saving page {title}: {e}")
        return False


if __name__ == "__main__":
    # Login to Wikipedia
    site = login_to_wikipedia("en")
    # Login to Wikidata
    login_to_wikidata()
    title = "Heart Sutra"
    content = """
    {{
    }}
    """
    create_or_edit_article(
        site,
        title,
        content,
        summary="Created via script",
        minor=True,
        overwrite_existing=False,
    )  # noqa: E501
    print(f"Successfully created or edited article: {title}")
