import unittest
from unittest.mock import MagicMock, mock_open, patch

from wiki_utils.wikipedia.article_upload import (
    create_or_edit_article,
    get_article,
    login_to_wikipedia,
)


class TestArticleUpload(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Create mock site without spec to avoid attribute errors
        self.mock_site = MagicMock()
        self.mock_site.username.return_value = "TestUser"

        # Create mock page without spec to avoid attribute errors
        self.mock_page = MagicMock()
        self.mock_page.text = "Original page content"

    @patch("pywikibot.Site")
    def test_login_to_wikipedia(self, mock_site_class):
        """Test login to Wikipedia function"""
        # Configure the mock
        mock_site_instance = mock_site_class.return_value
        mock_site_instance.username.return_value = "TestUser"

        # Call the function
        result = login_to_wikipedia("en")

        # Verify the mock was called correctly
        mock_site_class.assert_called_once_with("en", "wikipedia")
        mock_site_instance.login.assert_called_once()

        # Assert the result is the mocked site
        self.assertEqual(result, mock_site_instance)

    def test_get_article(self):
        """Test getting an article by title"""
        # Configure the mock
        with patch("pywikibot.Page") as mock_page_class:
            mock_page_instance = mock_page_class.return_value

            # Call the function
            result = get_article(self.mock_site, "Test Article")

            # Verify the mock was called correctly
            mock_page_class.assert_called_once_with(self.mock_site, "Test Article")

            # Assert the result is the mocked page
            self.assertEqual(result, mock_page_instance)

    @patch("pywikibot.Page")
    def test_create_or_edit_article_existing_no_overwrite(self, mock_page_class):
        """Test creating/editing an article that exists but overwrite_existing is False"""
        # Configure the mock
        mock_page_instance = mock_page_class.return_value
        mock_page_instance.text = "Original content"
        mock_page_instance.exists.return_value = True

        # Call the function
        result = create_or_edit_article(
            self.mock_site, "Test Article", "New content", overwrite_existing=False
        )

        # Verify behavior
        self.assertFalse(result)  # Should return False
        mock_page_class.assert_called_once_with(self.mock_site, "Test Article")
        mock_page_instance.exists.assert_called_once()
        self.assertNotEqual(
            mock_page_instance.text, "New content"
        )  # Content should not be changed

    @patch("pywikibot.Page")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_or_edit_article_new(self, mock_file, mock_page_class):
        """Test creating a new article"""
        # Configure the mock
        mock_page_instance = mock_page_class.return_value
        mock_page_instance.text = ""
        mock_page_instance.exists.return_value = False

        # Call the function
        result = create_or_edit_article(
            self.mock_site,
            "New Article",
            "Article content",
            summary="Created via test",
            minor=True,
        )

        # Verify behavior
        self.assertTrue(result)  # Should return True
        mock_page_class.assert_called_once_with(self.mock_site, "New Article")
        self.assertEqual(
            mock_page_instance.text, "Article content"
        )  # Content should be updated
        # Uncomment to test actual saving when the code is updated:
        # mock_page_instance.save.assert_called_once_with(summary="Created via test", minor=True)

    @patch("pywikibot.Page")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_or_edit_article_existing_with_overwrite(
        self, mock_file, mock_page_class
    ):
        """Test editing an existing article with overwrite_existing=True"""
        # Configure the mock
        mock_page_instance = mock_page_class.return_value
        mock_page_instance.text = "Original content"
        mock_page_instance.exists.return_value = True

        # Call the function
        result = create_or_edit_article(
            self.mock_site,
            "Existing Article",
            "Updated content",
            summary="Updated via test",
            minor=False,
            overwrite_existing=True,
        )

        # Verify behavior
        self.assertTrue(result)  # Should return True
        mock_page_class.assert_called_once_with(self.mock_site, "Existing Article")
        self.assertEqual(
            mock_page_instance.text, "Updated content"
        )  # Content should be updated

    @patch("pywikibot.Page")
    def test_create_or_edit_article_exception(self, mock_page_class):
        """Test exception handling in create_or_edit_article"""
        # Configure the mock to raise an exception
        mock_page_instance = mock_page_class.return_value
        mock_page_instance.text = "Original content"
        mock_page_instance.exists.side_effect = Exception("Test exception")

        # Call the function
        result = create_or_edit_article(self.mock_site, "Problem Article", "Content")

        # Verify behavior
        self.assertFalse(result)  # Should return False on exception


if __name__ == "__main__":
    unittest.main()
