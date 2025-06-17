import re

import pywikibot


def update_mainspace_page_with_links(
    index_title: str,
    mainpage_title: str,
    site_code="mul",
    family="wikisource",
    dry_run=True,
):
    """
    Replace 'Page no: N' in a mainspace page with links to the corresponding Page:Index/N.
    """
    site = pywikibot.Site(site_code, family)
    page = pywikibot.Page(site, mainpage_title)

    if not page.exists():
        print(f"Main page '{mainpage_title}' does not exist.")
        return

    original_text = page.text

    def link_replacer(match):
        num = match.group(1)
        return f"[[Page:{index_title}/{num}|Page no: {num}]]"

    updated_text = re.sub(r"Page no:\s*(\d+)", link_replacer, original_text)

    if original_text == updated_text:
        print("No changes needed.")
        return

    if dry_run:
        print("Dry run only — not saving changes.")
        print(updated_text[:1000])  # Preview first 1000 characters
    else:
        page.text = updated_text
        page.save(summary="Bot: Converted 'Page no:' references to page links.")


if __name__ == "__main__":
    index_title = "སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡.pdf"
    mainpage_title = (
        "རྒྱལ་བ་ཀཿཐོག་པའི་གྲུབ་མཆོག་རྣམས་ཀྱི་ཉམས་བཞེས་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་པོད་དང་པོ།"
    )
    update_mainspace_page_with_links(
        index_title=index_title,
        mainpage_title=mainpage_title,
        dry_run=False,  # Set to False to apply changes
    )
