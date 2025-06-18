import csv
import logging
import re
from urllib.parse import unquote

import pywikibot
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add this at the top of your script, after imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_mainspace_page_with_links(
    index_title: str,
    mainpage_title: str,
    site_code="mul",
    family="wikisource",
    dry_run=False,
):
    """
    Replace 'Page no: N' in a mainspace page with links to the corresponding Page:Index/N.
    """
    site = pywikibot.Site(site_code, family)
    page = pywikibot.Page(site, mainpage_title)

    if not page.exists():
        logger.info(f"Main page '{mainpage_title}' does not exist.")
        return

    original_text = page.text

    def link_replacer(match):
        num = match.group(1)
        return f"[[Page:{index_title}/{num}|Page no: {num}]]"

    updated_text = re.sub(r"Page no:\s*(\d+)", link_replacer, original_text)

    if original_text == updated_text:
        logger.info("No changes needed.")
        return

    if dry_run:
        logger.info("Dry run only — not saving changes.")
        logger.info(updated_text[:1000])  # Preview first 1000 characters
    else:
        page.text = updated_text
        try:
            page.save(summary="Bot: Converted 'Page no:' references to page links.")
        except Exception as e:
            logger.error(f"Failed to save page '{page.title()}': {e}")
            # Optionally, handle specific pywikibot exceptions here
            # For example, handle content too big error
            if hasattr(e, "args") and any(
                "contenttoobig" in str(arg) for arg in e.args
            ):
                logger.error(
                    "The content is too large to be saved. Consider splitting the page."
                )
            else:
                logger.error("An unexpected error occurred while saving the page.")
            return


def get_wikisource_links(
    sheet_id,
    creds_path,
    range="ལས་ཀ་དངོས་གཞི།!G3:J50",
    output_file="wikisource_links.csv",
):
    """
    Extracts hyperlinks from 'Text File link' (G) and 'Wikisource Link' (H) columns
    only if BOTH are present and 'Proofreading statue' (J) == 'ཞུ་དག་བྱས་ཟིན།'.
    You can change the value of range to get more or less rows.
    Doing this because of some links are set up differently. not in uniform order.

    Args:
        sheet_id (str): Google Sheet ID
        creds_path (str): Path to service account JSON credentials
        range (str): Range including G, H, J columns
        output_file (str): Where to save the extracted URLs

    Returns:
        List of tuples: [(wikisource_link, text_file_link), ...]
    """

    target_status = "ཞུ་དག་བྱས་ཟིན།"

    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.get(
        spreadsheetId=sheet_id, ranges=[range], includeGridData=True
    ).execute()

    rows = result["sheets"][0]["data"][0]["rowData"]
    links = []

    for row in rows:
        try:
            values = row["values"]
            text_file_cell = values[0]  # Column G
            wikisource_cell = values[1]  # Column H
            status_cell = values[3].get("formattedValue", "")  # Column J

            if (
                status_cell.strip() == target_status
                and "hyperlink" in text_file_cell
                and "hyperlink" in wikisource_cell
            ):
                text_file_link = text_file_cell["hyperlink"]
                wikisource_link = wikisource_cell["hyperlink"]
                links.append((wikisource_link, text_file_link))

        except (KeyError, IndexError):
            continue

    # Save to CSV. so that you can understand the output. Not much of a use in code logic
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Wikisource Link", "Text File Link"])
        for ws_link, txt_link in links:
            writer.writerow([ws_link, txt_link])

    print(f"✅ {len(links)} valid link pairs saved to '{output_file}'.")

    return links


if __name__ == "__main__":
    """
    Check for if index_title_no_ext equals with mainpage_title. if same then skip the link.

    index_title = "སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡.pdf"
    index_title_no_ext = "སྙན་བརྒྱུད་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་སྐོར། པོད། ༡"
    mainpage_title = (
        "རྒྱལ་བ་ཀཿཐོག་པའི་གྲུབ་མཆོག་རྣམས་ཀྱི་ཉམས་བཞེས་ཁྲིད་ཆེན་བཅུ་གསུམ་གྱི་པོད་དང་པོ།"
    )
    """

    SPREADSHEET_ID = "1jDZMBuGKGc9x3SXuwVo3ix60fDUccXgHPsAgFmUNCIw"
    CREDS_PATH = "my-credentials.json"

    valid_pairs = get_wikisource_links(SPREADSHEET_ID, CREDS_PATH)

    for ws_link, txt_link in valid_pairs:
        index_title = unquote(ws_link.split("Index:")[-1])
        mainpage_title = unquote(txt_link.split("/wiki/")[-1])
        # NEW: Extract only the text before '.pdf'
        index_text = index_title.rsplit(".pdf", 1)[0]

        if index_text == mainpage_title:
            logger.info(
                f"Skipping index: {index_title} and mainpage: {mainpage_title} because they are the same."
            )
            continue

        logger.info(f"Processing index: {index_title}")
        logger.info(f"Index text: {index_text}")
        logger.info(f"Mainpage title: {mainpage_title}")
        print("\n\n")

        update_mainspace_page_with_links(index_title, mainpage_title, dry_run=False)
        print("\n\n----------- ONTO NEXT ONE ------------\n\n")

    print("✅ All processes completed.")
