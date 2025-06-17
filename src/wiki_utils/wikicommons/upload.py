import json
import os
from typing import Any, Dict, List, Optional

import pywikibot
from pywikibot.specialbots import UploadRobot


def login_to_commons() -> pywikibot.Site:
    """
    Logs in to Wikimedia Commons using Pywikibot.
    Returns:
    - site: Pywikibot Site object for Wikimedia Commons.
    """
    site = pywikibot.Site("commons", "commons")
    site.login()  # Log into Wikimedia Commons
    return site


def upload_image_using_uploadrobot(
    image_path: str,
    image_title: str,
    description_text: str,
    site: Optional[pywikibot.Site] = None,
) -> pywikibot.Site:
    """
    Uploads the image to Wikimedia Commons using UploadRobot, with description verification.

    Parameters:
    - image_path: Path to the image file.
    - image_title: Title for the image on Commons (e.g., "File:YourImage.jpg").
    - description_text: The description to be added to the image page.
    - site: Optional pywikibot Site object. If None, a new login will be performed.

    Returns:
    - site: The pywikibot Site object used for the upload.
    """
    # Use provided site or login to commons
    if site is None:
        site = login_to_commons()

    # UploadRobot expects the first argument as a LIST of file paths or URLs
    bot = UploadRobot(
        [image_path],  # List of local file paths or URLs
        description=description_text,  # Description for the image
        use_filename=image_title,  # Custom title for the image file on Commons
        keep_filename=False,  # Do not keep original filename
        verify_description=True,  # Verify description before upload
        target_site=site,  # Target site (Commons)
        ignore_warning=False,  # Do not ignore warnings during upload
        chunk_size=0,  # Default chunk size
    )

    try:
        bot.run()
    except Exception as e:
        import sys

        print(f"ERROR: Upload error: {e}", file=sys.stderr)

    return site


def assign_caption(
    site: pywikibot.Site, file_title: str, captions: Dict[str, str]
) -> bool:
    """
    Assigns captions to a file on Wikimedia Commons in multiple languages by editing the Wikibase item.

    Parameters:
    - site: Pywikibot Site object for Wikimedia Commons.
    - file_title: Title of the file on Commons (with or without 'File:' prefix).
    - captions: Dictionary mapping language codes to caption text
        (e.g., {"en": "English caption", "bo": "བོད་ཡིག caption"})

    Returns:
    - Success status (True if caption was set successfully)
    """
    # Ensure the file title has the 'File:' prefix
    if not file_title.startswith("File:"):
        file_title = f"File:{file_title}"

    try:
        # Get the file page object
        file_page = pywikibot.FilePage(site, file_title)

        # Get the associated Wikibase item
        item = file_page.data_item()

        # Edit the labels (captions) in the specified languages
        item.editLabels(captions)

        print(f"Caption successfully added in {len(captions)} language(s)")
        return True
    except Exception as e:
        print(f"Failed to assign caption: {e}")
        return False


def assign_license(
    site: pywikibot.Site,
    file_title: str,
    license_text: str,
    summary: str = "Script: Setting license",
) -> bool:
    """
    Assigns the license to a file page on Wikimedia Commons by editing the page content.

    Parameters:
    - site: Pywikibot Site object for Wikimedia Commons.
    - file_title: Title of the file on Commons (with or without 'File:' prefix).
    - license_text (str): The full wikitext of the license section
        (e.g., '=={{int:license-header}}==\n{{PD-old-70}}\n{{PD-US-expired}}\n').
    - summary (str): The edit summary for the change.

    Returns:
    - Success status (True if license was set successfully)
    """
    # Ensure the file title has the 'File:' prefix
    if not file_title.startswith("File:"):
        file_title = f"File:{file_title}"

    try:
        # Get the file page object
        file_page = pywikibot.FilePage(site, file_title)
        text = file_page.get()

        # Identify the license section
        license_start = text.find("=={{int:license-header}}==")
        license_end = -1
        if license_start != -1:
            license_end = text.find("\n\n", license_start)
            if license_end == -1:
                license_end = len(text)

        new_text = ""
        if license_start != -1:
            new_text = text[:license_start] + license_text + text[license_end:]
        else:
            # If no license header is found, append it (might need adjustment based on page structure)
            new_text = text + "\n" + license_text

        if new_text != text:
            file_page.put(new_text, summary=summary)
            print(f"License successfully set for {file_title}")
            return True
        else:
            print(f"License for {file_title} is already set as provided.")
            return True

    except Exception as e:
        print(f"Failed to assign license for {file_title}: {e}")
        return False


def assign_categories(
    site: pywikibot.Site,
    file_title: str,
    categories: List[str],
    summary: str = "Script: Adding categories",
) -> bool:
    """
    Assigns categories to a file page on Wikimedia Commons.

    Parameters:
    - site: Pywikibot Site object for Wikimedia Commons.
    - file_title: Title of the file on Commons (with or without 'File:' prefix).
    - categories: List of category names without the 'Category:' prefix
        (e.g., ['Tibetan manuscripts', 'Buddhist texts'])
    - summary: Edit summary for the category addition.

    Returns:
    - Success status (True if categories were added successfully)
    """
    # Ensure the file title has the 'File:' prefix
    if not file_title.startswith("File:"):
        file_title = f"File:{file_title}"

    try:
        # Get the file page object
        file_page = pywikibot.FilePage(site, file_title)
        text = file_page.get()

        # Process each category
        categories_to_add = []
        for category in categories:
            category_link = f"[[Category:{category}]]"
            if category_link not in text:
                categories_to_add.append(category_link)

        if categories_to_add:
            # Add categories at the end of the page
            if text.strip().endswith("]]"):
                # If the file already has some categories (ends with a category link)
                new_text = text + "\n" + "\n".join(categories_to_add)
            else:
                # If the file has no categories yet
                new_text = text + "\n\n" + "\n".join(categories_to_add)

            file_page.put(new_text, summary=summary)
            print(f"Added {len(categories_to_add)} categories to {file_title}")
            return True
        else:
            print(f"No new categories to add for {file_title}")
            return True

    except Exception as e:
        print(f"Failed to assign categories for {file_title}: {e}")
        return False


def batch_upload_images(images_to_upload: List[Dict[str, Any]]) -> None:
    """
    Uploads multiple images to Wikimedia Commons with individual metadata.

    Parameters:
    - images_to_upload: List of dictionaries, each with keys:
        - image_path: Local path to the image file
        - image_title: Desired title for the image on Commons
        - description: Wikitext for the Information template
        - captions: Dict of language codes to captions
        - license_text: Wikitext for the license section
        - categories: List of category names (no 'Category:' prefix)
    """
    site = login_to_commons()
    for idx, img in enumerate(images_to_upload, 1):
        print(
            f"\n=== Processing image {idx}/{len(images_to_upload)}: {img['image_title']} ==="
        )
        try:
            # Upload the image
            upload_image_using_uploadrobot(
                image_path=img["image_path"],
                image_title=img["image_title"],
                description_text=img["description"],
                site=site,
            )

            # Assign license
            assign_license(
                site=site,
                file_title=img["image_title"],
                license_text=img["license_text"],
                summary="Script: Setting license",
            )

            # Assign captions
            assign_caption(
                site=site, file_title=img["image_title"], captions=img["captions"]
            )

            # Assign categories
            assign_categories(
                site=site,
                file_title=img["image_title"],
                categories=img["categories"],
                summary="Script: Adding categories",
            )
        except Exception as e:
            print(f"Failed to process {img['image_title']}: {e}")


def load_images_from_json(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Load image upload configurations from a JSON file.

    Parameters:
    - json_file_path: Path to the JSON file containing image configurations

    Returns:
    - List of dictionaries with image upload configurations formatted for upload
    """

    if not os.path.exists(json_file_path):
        print(f"Error: JSON file not found: {json_file_path}")
        return []

    with open(json_file_path, encoding="utf-8") as f:
        try:
            config = json.load(f)
            processed_config = []

            for item in config:
                # Process the new JSON structure into the format needed for upload
                processed_item = {
                    "image_path": item["image_path"],
                    "image_title": item["image_title"],
                    "captions": item["captions"],
                    "categories": item["categories"],
                }

                # Build the description from the info_template
                if "info_template" in item:
                    info = item["info_template"]
                    desc = "=={{int:filedesc}}==\n{{Information\n"

                    # Add multilingual descriptions
                    if "description" in info:
                        desc += "|description="
                        for lang, text in info["description"].items():
                            desc += (
                                f"{{{{bo|1={text}}}}}\n"
                                if lang == "bo"
                                else f"{{{{en|1={text}}}}}\n"
                            )

                    # Add other info fields
                    for field in ["date", "source", "author"]:
                        if field in info:
                            desc += f"|{field}={info[field]}\n"

                    desc += "}}"
                    processed_item["description"] = desc

                # Build the license text from license_templates
                if "license_templates" in item:
                    license_text = "=={{int:license-header}}==\n"
                    for template in item["license_templates"]:
                        license_text += f"{{{{{template}}}}}\n"
                    processed_item["license_text"] = license_text

                processed_config.append(processed_item)

            return processed_config
        except json.JSONDecodeError as e:
            print(f"Error loading JSON: {e}")
            return []
        except KeyError as e:
            print(f"Error processing JSON structure: Missing key {e}")
            return []


# Main script execution
if __name__ == "__main__":
    # Use a hardcoded path to the JSON configuration file
    json_file = "data/commons_upload_config.json"

    # Load the image configurations from the JSON file
    images_to_upload = load_images_from_json(json_file)

    if images_to_upload:
        print(f"Loaded {len(images_to_upload)} image configurations from {json_file}")
        batch_upload_images(images_to_upload)
    else:
        print(f"No valid image configurations found in {json_file}")
