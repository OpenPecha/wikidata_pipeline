import csv
import hashlib
import json
import os
import re
from datetime import datetime
from typing import Optional

import pandas as pd
import pywikibot

# Configuration: Set these before running

SITE_CODE = "mul"  # 'mul' is for multilingual Wikisource (wikisource.org)
FAMILY = "wikisource"  # Do not change unless using a non-standard Wikisource


# --- Helper Functions ---
def parse_text_file(text_file_path):
    """
    Parse the text file into a dict: {page_number: text}
    Assumes format:
        Page no: N\n<text>\n...\nPage no: M\n<text>\n...
    """
    page_texts = {}
    current_page = None
    current_lines: list[str] = []
    with open(text_file_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.strip().startswith("Page no:"):
                # Save previous page
                if current_page is not None:
                    page_texts[str(current_page)] = "\n".join(current_lines).strip()
                # Start new page
                try:
                    current_page = line.split(":", 1)[1].strip()
                except IndexError:
                    current_page = None
                current_lines = []
            else:
                # Remove text within parentheses
                line = re.sub(r"\([^)]*\)", "", line)
                current_lines.append(line)
        # Save last page
        if current_page is not None:
            page_texts[str(current_page)] = "\n".join(current_lines).strip()
    return page_texts


def get_page_titles(index_title, site):
    """
    Returns a dict of {page_number: ProofreadPage object}.
    Caches the mapping {page_number: page_title} in a local file for faster reuse.
    """
    cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "cache")
    # Use SHA256 hash of index_title for unique, safe filename
    index_hash = hashlib.sha256(index_title.encode("utf-8")).hexdigest()
    cache_file = os.path.join(cache_dir, f"Page_{index_hash}.json")

    # Try to load from cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, encoding="utf-8") as f:
                mapping = json.load(f)
            from pywikibot.proofreadpage import ProofreadPage

            page_dict = {k: ProofreadPage(site, v) for k, v in mapping.items()}
            return page_dict
        except (json.JSONDecodeError, OSError):
            print(
                f"Cache file {cache_file} is invalid or empty. Deleting and refetching."
            )
            os.remove(cache_file)

    # Otherwise, fetch from Wikisource and cache
    index = pywikibot.Page(site, index_title)
    if not index.exists():
        print(f"Index page '{index_title}' does not exist.")
        return {}
    from pywikibot.proofreadpage import IndexPage

    idx = IndexPage(index)
    page_dict = {}
    mapping = {}
    for p in idx.page_gen():
        if p._num is not None:
            page_dict[str(p._num)] = p
            mapping[str(p._num)] = p.title()
    # Save mapping to cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    return page_dict


def log_upload_result(
    index_title: str,
    page_no: str,
    page_title: str,
    status: str,
    error_message: Optional[str] = None,
    log_path: str = "upload_log.csv",
) -> None:
    """Log upload result to a CSV file"""
    csv_file_path = os.path.join(os.path.dirname(__file__), log_path)
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "index_title",
                    "page_number",
                    "page_title",
                    "status",
                    "error_message",
                ]
            )
        writer.writerow(
            [
                datetime.now().isoformat(),
                index_title,
                page_no,
                page_title,
                status,
                error_message or "",
            ]
        )


def upload_texts(site: pywikibot.Site, index_title: str, text_file_path: str) -> None:
    page_texts = parse_text_file(text_file_path)
    page_objs = get_page_titles(index_title, site)
    for page_no, text in page_texts.items():
        if page_no not in page_objs:
            print(f"Page number {page_no} not found in index.")
            log_upload_result(
                index_title, page_no, "", "failure", "Page number not found in index"
            )
            continue
        page = page_objs[page_no]
        print(f"Uploading text to {page.title()}...")
        try:
            # Wrap text in correct ProofreadPage format
            quality_tag = (
                '<noinclude><pagequality level="3" user="Ganga4364" /></noinclude>'
            )
            formatted_text = f"{quality_tag}\n{text}\n<noinclude></noinclude>"
            page.text = formatted_text
            page.proofread_page_quality = 3  # 3 = Proofread
            page.save(summary="Bot: Adding OCR/provided text and marking as proofread.")
            print(f"Success: {page.title()}")
            log_upload_result(index_title, page_no, page.title(), "success")
        except Exception as e:
            print(f"Error uploading {page.title()}: {e}")
            log_upload_result(index_title, page_no, page.title(), "failure", str(e))


def batch_upload_from_csv(
    csv_file_path: str,
    site: Optional[pywikibot.Site] = None,
    data_dir: str = "data/text",
) -> None:
    """Upload texts for all entries in a CSV file"""
    if site is None:
        site = pywikibot.Site(SITE_CODE, FAMILY)
        site.login()

    df = pd.read_csv(csv_file_path)
    for i, row in df.iterrows():
        index_title = row["Index"]
        text = row["text"]
        text_file_path = os.path.join(data_dir, text)
        print(f"Processing: {index_title} with {text_file_path}")
        if not isinstance(index_title, str) or not isinstance(text_file_path, str):
            print(f"Skipping row {i} due to missing data.")
            continue
        upload_texts(site, index_title, text_file_path)


if __name__ == "__main__":
    csv_file_path = "data/work_list.csv"  # Adjust path if needed
    batch_upload_from_csv(csv_file_path)
    print("Done.")
