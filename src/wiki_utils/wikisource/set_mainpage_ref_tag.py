import re

import pywikibot


def replace_braces_with_ref_tag(text):
    """
    Replaces (word1,word2) with word2<ref>word1</ref> in the text.
    Handles Tibetan and standard punctuation/spacing.
    """

    # Pattern: (word1,word2) with optional spaces and Tibetan punctuation
    pattern = r"\(([^,\)]+),([^\)]+)\)"

    def replacer(match):
        word1 = match.group(1).strip()
        word2 = match.group(2).strip()
        return f"{word2}<ref>བྲིས་མར། {word1}</ref>"

    return re.sub(pattern, replacer, text)


def update_mainspace_page_with_ref_tag(
    mainpage_title: str,
    site_code="mul",
    family="wikisource",
    dry_run=True,
    save_to_files=False,
):
    """
    Replace 'Page no: N' in a mainspace page with links to the corresponding Page:Index/N.

    Args:
        mainpage_title: Title of the mainspace page
        site_code: Site code for pywikibot
        family: Family for pywikibot
        dry_run: If True, only preview changes without saving
        save_to_files: If True, save original and updated text to files
    """
    site = pywikibot.Site(site_code, family)
    page = pywikibot.Page(site, mainpage_title)

    if not page.exists():
        print(f"Main page '{mainpage_title}' does not exist.")
        return

    original_text = page.text
    updated_text = replace_braces_with_ref_tag(original_text)

    if original_text == updated_text:
        print("No changes needed.")
        return

    # Save texts to files if requested
    if save_to_files:
        # Create safe filename from title
        safe_title = mainpage_title.replace("/", "_").replace("\\", "_")[
            :50
        ]  # Limit length and replace slashes

        # Save original text
        with open(f"{safe_title}_original.txt", "w", encoding="utf-8") as f:
            f.write(original_text)
        print(f"Original text saved to {safe_title}_original.txt")

        # Save updated text
        with open(f"{safe_title}_updated.txt", "w", encoding="utf-8") as f:
            f.write(updated_text)
        print(f"Updated text saved to {safe_title}_updated.txt")

    if dry_run:
        print("Dry run only — not saving changes.")
        print(updated_text[:1000])  # Preview first 1000 characters
    else:
        page.text = updated_text
        page.save(summary="Bot: Converted 'Page no:' references to page links.")


if __name__ == "__main__":
    # Test example for ref tag replacement
    mainpage_title = (
        "རྒྱལ་བ་ཀཿཐོག་པའི་གྲུབ་མཆོག་རྣམས་ཀྱི་ཉམས་བཞེས་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་པོད་དང་པོ།"
    )
    update_mainspace_page_with_ref_tag(
        mainpage_title=mainpage_title,
        dry_run=True,  # Set to True to prevent changes
        save_to_files=True,  # Save text to files for review
    )
