import unittest
from unittest.mock import patch, MagicMock, mock_open
import pages_to_github
import json

class TestPagesToGitHub(unittest.TestCase):
    @patch('pages_to_github.logging')
    @patch('pages_to_github.Path')
    def test_process_page(self, mock_path, mock_logging):
        # Arrange
        mock_page = {
            'slug': 'test-page',
            'title': {'de': 'Test Page'},
            'author': {'username': 'test@example.com'},
            'restricted': False
        }

        # Mock the Path object and file operations
        mock_backup_dir = MagicMock()
        mock_path.return_value = mock_backup_dir
        mock_backup_dir.__truediv__.return_value.__truediv__.return_value = mock_backup_dir
        mock_file = MagicMock()
        mock_file.open.return_value.__enter__.return_value = mock_open()()
        mock_backup_dir.__truediv__.return_value = mock_file

        # Act
        pages_to_github.process_page(mock_page)

        # Assert
        mock_logging.info.assert_any_call(
            f"Processing page: {mock_page['title']['de']} "
            f"(Author: test, Slug: {mock_page['slug']})"
        )
        mock_backup_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.open.assert_called_once_with('w', encoding='utf-8')
        mock_logging.info.assert_any_call(f"Saved JSON content for {mock_page['slug']}")

    @patch('pages_to_github.logging')
    @patch('pages_to_github.Path')
    @patch('pages_to_github.json.dump')
    def test_process_page_error_handling(self, mock_json_dump, mock_path, mock_logging):
        # Arrange
        mock_page = {
            'slug': 'test-page',
            'title': {'de': 'Test Page'},
            'author': {'username': 'test@example.com'},
            'restricted': False
        }

        # Mock the Path object and file operations
        mock_backup_dir = MagicMock()
        mock_path.return_value = mock_backup_dir
        mock_backup_dir.__truediv__.return_value.__truediv__.return_value = mock_backup_dir
        
        # Create a mock file object with an open method that raises an IOError
        mock_file = MagicMock()
        mock_file.open.side_effect = IOError("Failed to write file")
        mock_backup_dir.__truediv__.return_value = mock_file

        # Act
        pages_to_github.process_page(mock_page)

        # Assert
        mock_logging.error.assert_called_once_with(
            f"Error saving JSON content for {mock_page['slug']}: Failed to write file"
        )

    @patch('pages_to_github.requests.get')
    @patch('pages_to_github.process_page')
    @patch('pages_to_github.logging')
    @patch('pages_to_github.os.getenv')
    def test_main_success(self, mock_getenv, mock_logging, mock_process_page, mock_requests_get):
        # Arrange
        mock_getenv.return_value = 'fake_api_key'
        base_url = 'https://data.bs.ch/api/management/v2/pages/'
        download_restricted = False

        # Mock API responses for two pages and then an empty list to terminate
        mock_response_page1 = MagicMock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            'items': [
                {
                    'slug': 'test-page-1',
                    'title': {'de': 'Test Page 1'},
                    'author': {'username': 'test1@example.com'},
                    'restricted': False
                },
                {
                    'slug': 'test-page-2',
                    'title': {'de': 'Test Page 2'},
                    'author': {'username': 'test2@example.com'},
                    'restricted': True
                }
            ],
            'rows': 2
        }

        mock_response_page2 = MagicMock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            'items': [],
            'rows': 0
        }

        mock_requests_get.side_effect = [mock_response_page1, mock_response_page2]

        # Act
        pages_to_github.main(base_url, download_restricted)

        # Assert
        self.assertEqual(mock_requests_get.call_count, 2)
        mock_process_page.assert_called_once_with(mock_response_page1.json()['items'][0])
        mock_logging.info.assert_any_call("Accessing 2 entries from page 1...")
        mock_logging.info.assert_any_call("Skipping restricted entry: test-page-2")

    @patch('pages_to_github.requests.get')
    @patch('pages_to_github.process_page')
    @patch('pages_to_github.logging')
    @patch('pages_to_github.os.getenv')
    def test_main_api_failure(self, mock_getenv, mock_logging, mock_process_page, mock_requests_get):
        # Arrange
        mock_getenv.return_value = 'fake_api_key'
        base_url = 'https://data.bs.ch/api/management/v2/pages/'
        download_restricted = False

        # Mock API response with failure status code
        mock_response_failure = MagicMock()
        mock_response_failure.status_code = 500
        mock_response_failure.text = 'Internal Server Error'

        mock_requests_get.return_value = mock_response_failure

        # Act & Assert
        with self.assertRaises(Exception) as context:
            pages_to_github.main(base_url, download_restricted)

        self.assertIn("API request failed", str(context.exception))
        mock_logging.error.assert_any_call("Failed to retrieve pages. Status code: 500")
        mock_logging.error.assert_any_call("Response content: Internal Server Error")
        mock_process_page.assert_not_called()

    @patch('pages_to_github.os.getenv')
    def test_main_missing_api_key(self, mock_getenv):
        # Arrange
        mock_getenv.return_value = None
        base_url = 'https://data.bs.ch/api/management/v2/pages/'
        download_restricted = False

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            pages_to_github.main(base_url, download_restricted)

        self.assertIn("API_KEY must be set in the .env file", str(context.exception))

if __name__ == '__main__':
    unittest.main()
