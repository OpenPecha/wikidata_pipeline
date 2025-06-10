import unittest
from unittest.mock import MagicMock, mock_open, patch

# Import the module to test
from wiki_utils.wikisource import mainpage_extended_text_upload


class TestMainpageTextUpload(unittest.TestCase):
    def setUp(self):
        # Example minimal text file content
        self.text_content = (
            "Page no:1\nFirst page text\n" "Page no:2\nSecond page text\n"
        )
        self.page_text_dict = {"1": "First page text", "2": "Second page text"}
        self.index_title = "Index:Test.pdf"
        self.main_title = "Test Main Page"

    def test_parse_text_file(self):
        with patch("builtins.open", mock_open(read_data=self.text_content)):
            result = mainpage_extended_text_upload.parse_text_file("dummy.txt")
            self.assertEqual(result, self.page_text_dict)

    def test_prepare_wikisource_content(self):
        expected = (
            "== Page 1 ==\n{{Page:Test.pdf/1}}\nFirst page text\n\n"
            "== Page 2 ==\n{{Page:Test.pdf/2}}\nSecond page text"
        )
        result = mainpage_extended_text_upload.prepare_wikisource_content(
            self.page_text_dict, "Test.pdf"
        )
        # Remove trailing whitespace for comparison
        self.assertEqual(result.strip(), expected.strip())

    @patch("pywikibot.Page")
    @patch("pywikibot.Site")
    def test_create_main_page(self, MockSite, MockPage):
        # Mock site and page behavior
        mock_site = MockSite.return_value
        mock_page = MagicMock()
        MockPage.return_value = mock_page

        # Simulate page does not exist
        mock_page.exists.return_value = False
        mock_page.text = ""

        # Call function
        mainpage_extended_text_upload.create_main_page(
            mock_site,
            self.main_title,
            self.page_text_dict,
            self.index_title,
            overwrite=True,
        )

        # Check that the page was created and saved
        self.assertTrue(mock_page.save.called)
        self.assertIn("First page text", mock_page.text)
        self.assertIn("Second page text", mock_page.text)


if __name__ == "__main__":
    unittest.main()
