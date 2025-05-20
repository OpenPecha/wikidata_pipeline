<h1 align="center">
  <br>
  <a href="https://openpecha.org"><img src="https://avatars.githubusercontent.com/u/82142807?s=400&u=19e108a15566f3a1449bafb03b8dd706a72aebcd&v=4" alt="OpenPecha" width="150"></a>
  <br>
</h1>

# Wiki Utils

**A comprehensive toolkit for uploading and managing Tibetan Buddhist texts and resources across Wikimedia platforms.**

With Wiki Utils, you can automate uploads to Wikimedia Commons, add rich metadata to Wikidata, and upload text content to Wikisource with full language support for Tibetan texts.

## Table of Contents

- [Overview](#overview)
- [Project Dependencies](#project-dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Components](#components)
  - [WikiCommons Batch Upload](#wikicommons-batch-upload)
  - [Wikidata BDRC Utilities](#wikidata-bdrc-utilities)
  - [Wikisource Text Upload](#wikisource-text-upload)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

Wiki Utils is designed for content maintainers and librarians working with Tibetan Buddhist texts who want to make these resources available on Wikimedia platforms. The package provides three main components:

1. **WikiCommons Batch Upload**: Upload PDFs and other media files to Wikimedia Commons with rich metadata, captions, and proper licensing.
2. **Wikidata BDRC Utilities**: Query and retrieve information from Wikidata for Buddhist Digital Resource Center (BDRC) resources.
3. **Wikisource Text Upload**: Upload and manage text content on Wikisource with page-by-page organization.

## Project Dependencies

Before using Wiki Utils, ensure you have:

* Python 3.8 or higher
* pywikibot (core library for interacting with Wikimedia APIs)
* pandas (for CSV data handling)
* requests (for API interactions)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/OpenPecha/wikidata_pipeline.git
   cd wikidata_pipeline
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -U pip
   pip install -e .
   pip install .[dev]
   pre-commit install
   ```

## Configuration

### Pywikibot Configuration

Wiki Utils uses pywikibot for authentication and API interactions. You need to configure pywikibot before using the scripts:

1. Create a `user-config.py` file in the project root directory with the following content:
   ```python
   family = 'commons'
   mylang = 'commons'

   # Configuration for Wikimedia Commons
   usernames['commons']['commons'] = 'YourUsername'

   # Configuration for multilingual Wikisource
   usernames['wikisource']['mul'] = 'YourUsername'

   password_file = "user-password.py"
   ```

2. Obtain a bot password from Wikimedia:
   - Log in to your Wikimedia account on [Wikimedia Commons](https://commons.wikimedia.org) or [Wikisource](https://wikisource.org)
   - Go to Special:BotPasswords page: `Special:BotPasswords` (e.g., https://commons.wikimedia.org/wiki/Special:BotPasswords)
   - Create a new bot password with an appropriate name (e.g., "WikiUtils")
   - Select the required permissions (minimum required: `Edit pages`, `Upload new files`, `Upload by URL`)
   - Click "Create" and save the generated credentials

3. Create a `user-password.py` file in the project root directory with your bot password:
   ```python
   # This is an automatically generated file used to store BotPasswords.
   # See https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords for more information.

   ('YourUsername', BotPassword('BotName', 'your-bot-password-token'))
   ```
   Replace `YourUsername` with your Wikimedia username, `BotName` with the name you gave your bot,
   and `your-bot-password-token` with the token provided by Wikimedia.

4. Set appropriate file permissions to protect your credentials:
   ```
   chmod 600 user-password.py
   ```

## Components

### WikiCommons Batch Upload

The WikiCommons component allows you to upload images and PDFs to Wikimedia Commons with proper metadata, captions in multiple languages, licensing information, and categories.

#### Input Format

Prepare a JSON configuration file with the following structure (example in `data/commons_upload_config.json`):

```json
[
  {
    "image_path": "/path/to/your/file.pdf",
    "image_title": "TibetanText_Title.pdf",
    "info_template": {
      "description": {
        "bo": "བོད་ཀྱི་རྒྱལ་རབས།",
        "en": "Tibetan Historical Text"
      },
      "date": "2024",
      "source": "BDRC",
      "author": "Traditional"
    },
    "captions": {
      "bo": "བོད་ཀྱི་རྒྱལ་རབས།",
      "en": "Tibetan Historical Text"
    },
    "license_templates": [
      "PD-old-70",
      "PD-US-expired"
    ],
    "categories": [
      "Tibetan manuscripts",
      "Buddhist texts",
      "Tibetan history"
    ]
  }
]
```

Each entry in the array represents one file to upload with its metadata.

#### Running WikiCommons Upload

To upload files to WikiCommons:

```bash
python -m wiki_utils.wikicommons.batch_upload
```

By default, the script looks for the configuration file at `data/commons_upload_config.json`. You can modify the path in the script if needed.

### Wikidata BDRC Utilities

The Wikidata component provides utilities for querying and retrieving information from Wikidata related to BDRC (Buddhist Digital Resource Center) resources.

#### Usage Examples

```python
from wiki_utils.wikidata.bdrc_utils import get_wikidata_metadata

# Get metadata for a BDRC work
work_id = "WA0RK0529"
metadata = get_wikidata_metadata(
    work_id,
    language="en",
    properties=["P31", "P4969", "P1476"]
)
print(metadata)
```

### Wikisource Text Upload

The Wikisource component allows you to upload text content to Wikisource pages, organized by page numbers.

#### Input Format

1. **Text Files**: Place your text files in the `data/text/` directory. Each file should follow this format:

   ```
   Page no: 1
   ལེའུ་དང་པོ། བོད་ཀྱི་སྔ་རབས་ལོ་རྒྱུས།
   འདི་ནི་བོད་ཀྱི་སྔ་རབས་ཀྱི་ལོ་རྒྱུས་ཡིན།

   Page no: 2
   ལེའུ་གཉིས་པ། ...
   ```

2. **Work List CSV**: Create a CSV file (`data/work_list.csv`) with the following columns:
   - `Index`: The Wikisource index page title (e.g., "Index:My_Tibetan_Book.pdf")
   - `text`: Name of the text file in `data/text/` directory

   Example:
   ```csv
   Index,text
   Index:TibetanHistory_Vol1.pdf,tibetan_history_vol1.txt
   Index:TibetanDharma_Vol1.pdf,tibetan_dharma_vol1.txt
   ```

#### Running Wikisource Upload

To upload texts to Wikisource:

```bash
python -m wiki_utils.wikisource.etext_upload
```

By default, the script looks for the work list at `data/work_list.csv`. You can modify the path in the script if needed.

## Logging

Wiki Utils implements comprehensive logging mechanisms to track upload activities and results:

1. **Wikisource Upload Logs**:
   - Location: `src/wiki_utils/wikisource/upload_log.csv`
   - Format: CSV with timestamp, index_title, page_number, page_title, status, and error_message

2. **Console Output**:
   - All scripts provide detailed console output during execution
   - Shows progress, successes, and errors in real-time

## Troubleshooting

### Common Issues

<table>
  <tr>
   <td><strong>Issue</strong></td>
   <td><strong>Solution</strong></td>
  </tr>
  <tr>
   <td>Authentication failures</td>
   <td>Ensure pywikibot is correctly configured with valid credentials. Run <code>python -m pywikibot login</code> to reset and update credentials.</td>
  </tr>
  <tr>
   <td>File upload errors</td>
   <td>Check that your file paths in the JSON configuration are correct and absolute. Ensure file formats are supported by Commons (PDF, JPG, PNG, etc.).</td>
  </tr>
  <tr>
   <td>Text parsing issues</td>
   <td>Verify text files follow the correct format with "Page no: X" headers. Check encoding is UTF-8.</td>
  </tr>
  <tr>
   <td>API throttling/limits</td>
   <td>Reduce batch size or add delays between uploads if hitting API rate limits.</td>
  </tr>
</table>

### Pywikibot Cache

Wikisource text upload creates and uses cache files in the `cache/` directory to optimize page lookups. If you encounter stale data issues, delete the cache files to force fresh fetching.

## Contributing

Contributions to Wiki Utils are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
  </tr>
  <tr>
   <td>
    _Describe the issue here_
   </td>
   <td>
    _Write solution here_
   </td>
  </tr>
  <tr>
   <td>
    _Describe the issue here_
   </td>
   <td>
    _Write solution here_
   </td>
  </tr>
</table>


Other troubleshooting supports:
* _Link to FAQs_
* _Link to runbooks_
* _Link to other relevant support information_


## Contributing guidelines
If you'd like to help out, check out our [contributing guidelines](/CONTRIBUTING.md).


## Additional documentation
_Include links and brief descriptions to additional documentation._

For more information:
* [Reference link 1](#)
* [Reference link 2](#)
* [Reference link 3](#)


## How to get help
* File an issue.
* Email us at openpecha[at]gmail.com.
* Join our [discord](https://discord.com/invite/7GFpPFSTeA).


## Terms of use
_Project Name_ is licensed under the [MIT License](/LICENSE.md).
