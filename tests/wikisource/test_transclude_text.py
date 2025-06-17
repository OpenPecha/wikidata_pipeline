import unittest
from unittest.mock import MagicMock, patch

from wiki_utils.wikisource import transclude_text


class TestTranscludeText(unittest.TestCase):
    def setUp(self):
        self.index_title = "Index:SomeBook.pdf"
        self.page1 = "Page:somebook.pdf/2"
        self.page2 = "Page:somebook.pdf/abc"
        self.page_text = "This is page 2 of somebook.pdf"
        self.main_title = "SomeBook"
        self.base_title = "SomeBook.pdf"
        self.base_title_no_ext = "SomeBook"

    def test_extract_page_number(self):
        self.assertEqual(transclude_text.extract_page_number(self.page1), 2)
        self.assertEqual(transclude_text.extract_page_number(self.page2), float("inf"))

    def test_get_base_info(self):
        class DummySite:
            def namespace(self, ns_id):
                return {106: "Index", 104: "Page"}[ns_id]

        site = DummySite()
        (
            base_title,
            base_title_no_ext,
            index_ns,
            page_ns,
            page_prefix,
        ) = transclude_text.get_base_info(site, self.index_title)
        self.assertEqual(base_title, self.base_title)
        self.assertEqual(base_title_no_ext, self.base_title_no_ext)
        self.assertEqual(index_ns, "Index")
        self.assertEqual(page_ns, "Page")
        self.assertEqual(page_prefix, f"{page_ns}:{self.base_title_no_ext}/")

    @patch("wiki_utils.wikisource.transclude_text.extract_page_number")
    def test_get_pages_sorted(self, mock_extract_page_number):
        mock_site = MagicMock()

        # Create mock Page objects with title() methods
        mock_page1 = MagicMock()
        mock_page1.title.return_value = "Page:SomeBook/1"
        mock_page2 = MagicMock()
        mock_page2.title.return_value = "Page:SomeBook/2"
        mock_page3 = MagicMock()
        mock_page3.title.return_value = "Page:SomeBook/3"

        # Site.allpages returns unsorted mock pages
        mock_site.allpages.return_value = [mock_page1, mock_page2, mock_page3]

        # Fake extract_page_number based on title endings
        def fake_extract(p):
            return int(p.title().split("/")[-1])

        mock_extract_page_number.side_effect = fake_extract

        result = transclude_text.get_pages(mock_site, self.index_title)

        # Expect the pages in order: 1, 2, 3
        self.assertEqual(result, [mock_page1, mock_page2, mock_page3])
        mock_site.allpages.assert_called_once_with(
            prefix=self.base_title_no_ext, namespace=104
        )

    # Optionally, add test for no pages case
    def test_get_pages_empty(self):
        mock_site = MagicMock()

        # No pages returned
        mock_site.allpages.return_value = []

        result = transclude_text.get_pages(mock_site, self.index_title)
        self.assertEqual(result, [])

    @patch("wiki_utils.wikisource.transclude_text.pywikibot.Page")
    @patch("wiki_utils.wikisource.transclude_text.get_pages")
    def test_format_page_orientation_main_page_exists(self, mock_get_pages, mock_Page):
        # Setup dummy site and mock return values
        mock_site = MagicMock()
        mock_page_obj = MagicMock()
        mock_page_obj.exists.return_value = True

        mock_Page.return_value = mock_page_obj

        # Call the function
        transclude_text.format_page_orientation(
            index_title=self.index_title, site=mock_site, dry_run=True
        )

        # Ensure it checked the main page and exited early
        mock_Page.assert_called_with(mock_site, self.main_title)
        self.assertFalse(
            mock_get_pages.called, "Should not call get_pages when main page exists"
        )
