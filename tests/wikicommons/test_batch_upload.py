import unittest
from unittest.mock import MagicMock, patch

from wiki_utils.wikicommons.batch_upload import (
    assign_categories,
    assign_license,
    login_to_commons,
    upload_image_using_uploadrobot,
)


class TestBatchUpload(unittest.TestCase):
    def setUp(self):
        # Create mock site object that will be used in multiple tests
        self.mock_site = MagicMock()

    @patch("pywikibot.Site")
    def test_login_to_commons(self, mock_site_constructor):
        """Test logging into Wikimedia Commons"""
        # Setup mock
        mock_site_obj = MagicMock()
        mock_site_constructor.return_value = mock_site_obj

        # Call the function
        site = login_to_commons()

        # Verify site was created with correct parameters
        mock_site_constructor.assert_called_once_with("commons", "commons")
        # Verify login was called
        mock_site_obj.login.assert_called_once()
        # Verify correct site was returned
        self.assertEqual(site, mock_site_obj)

    @patch("pywikibot.specialbots.UploadRobot.run")
    @patch(
        "pywikibot.specialbots.UploadRobot.__init__", return_value=None
    )  # prevents constructor from doing anything
    @patch("wiki_utils.wikicommons.batch_upload.login_to_commons")
    def test_upload_image_using_uploadrobot(self, mock_login, mock_init, mock_run):
        mock_site = MagicMock()
        mock_login.return_value = mock_site

        image_path = "/path/to/test_image.jpg"
        image_title = "File:Test_Image.jpg"
        description_text = "This is a test image"

        result_site = upload_image_using_uploadrobot(
            image_path, image_title, description_text
        )

        # Check constructor args
        mock_init.assert_called_once_with(
            [image_path],
            description=description_text,
            use_filename=image_title,
            keep_filename=False,
            verify_description=True,
            target_site=mock_site,
            ignore_warning=False,
            chunk_size=0,
        )
        mock_run.assert_called_once()
        self.assertEqual(result_site, mock_site)

    @patch("pywikibot.FilePage")
    def test_assign_license(self, mock_file_page):
        """Test assigning license to a file on Commons"""
        # Setup mock
        mock_page_obj = MagicMock()
        mock_file_page.return_value = mock_page_obj
        mock_page_obj.get.return_value = "Existing page content"

        # Test parameters
        file_title = "File:Test_Image.jpg"
        license_text = "=={{int:license-header}}==\n{{PD-old-70}}\n{{PD-US-expired}}"

        # Call the function
        result = assign_license(self.mock_site, file_title, license_text)

        # Verify FilePage was created with correct parameters
        mock_file_page.assert_called_once_with(self.mock_site, file_title)
        # Verify get() was called to retrieve page content
        mock_page_obj.get.assert_called_once()
        # Verify put() was called to update the page
        self.assertTrue(mock_page_obj.put.called)
        # Verify correct return value
        self.assertTrue(result)

    @patch("pywikibot.FilePage")
    def test_assign_categories(self, mock_file_page):
        """Test assigning categories to a file on Commons"""
        # Setup mock
        mock_page_obj = MagicMock()
        mock_file_page.return_value = mock_page_obj
        mock_page_obj.get.return_value = "Existing page content"

        # Test parameters
        file_title = "File:Test_Image.jpg"
        categories = ["Tibetan manuscripts", "Buddhist texts"]

        # Call the function
        result = assign_categories(self.mock_site, file_title, categories)

        # Verify FilePage was created with correct parameters
        mock_file_page.assert_called_once_with(self.mock_site, file_title)
        # Verify get() was called to retrieve page content
        mock_page_obj.get.assert_called_once()
        # Verify put() was called with category additions
        self.assertTrue(mock_page_obj.put.called)
        # Check that the category text was in the put() call
        put_args = mock_page_obj.put.call_args[0][0]
        self.assertIn("[[Category:Tibetan manuscripts]]", put_args)
        self.assertIn("[[Category:Buddhist texts]]", put_args)
        # Verify correct return value
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
