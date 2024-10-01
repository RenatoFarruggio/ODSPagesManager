import time
import requests
import json
import logging
from pathlib import Path
import argparse
import os
from dotenv import load_dotenv

## TODOs
# TODO: Change from Management API to Automation API
# TODO: Check rate limits and adapt wait time accordingly
# TODO: Check if page is already in repo and up to date, if so skip it
# TODO: Add error handling
# TODO: Implement progress tracking


# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

def process_page(page, debug__download_on):
    page_slug = page['slug']

    try:
        page_title_de = page['title']['de']
    except KeyError:
        page_title_de = '[Title not found]'

    try:
        content_author = page['author']['username'].split('@')[0]
    except KeyError:
        content_author = '[Author not found]'

    logging.info(f"Processing page: {page_title_de} (Author: {content_author}, Slug: {page_slug})")

    if debug__download_on:
        backup_dir = Path(Path("local_backup"), "pages", page_slug)
        backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            page_file = backup_dir / "page.json"
            with page_file.open('w', encoding='utf-8') as f:
                json.dump(page, f, indent=4, sort_keys=True)
            logging.info(f"Saved JSON content for {page_slug}")
        except IOError as e:
            logging.error(f"Error saving JSON content for {page_slug}: {e}")

    # TODO: Check rate limits and adapt wait time accordingly
    time.sleep(1)

def main(base_url, download_restricted, debug__download_on):
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY must be set in the .env file")

    # Set up headers with the API key for authentication
    headers = {
        'Authorization': f'Apikey {api_key}'
    }

    page_number = 1
    while True:
        # Make a request to the API to get a list of ODS pages
        response = requests.get(f"{base_url}?page={page_number}", headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to retrieve pages. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            raise Exception("API request failed")

        # Parse the JSON response
        pages = response.json()

        if len(pages['items']) == 0:
            break
        logging.info(f"Accessing {pages['rows']} entries from page {page_number}...")
        page_number += 1

        # Loop through the pages and download content
        for page in pages['items']:
            if page['restricted'] and not download_restricted:
                logging.info(f"Skipping restricted entry: {page['slug']}")
                continue

            process_page(page, debug__download_on)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download ODS pages from data.bs.ch")
    parser.add_argument("--base-url", default="https://data.bs.ch/api/management/v2/pages/",
                        help="Base URL for the API")
    parser.add_argument("--download-restricted", action="store_true",
                        help="Download restricted pages")
    parser.add_argument("--debug-download-on", action="store_true",
                        help="Enable debug mode and save JSON content locally")

    args = parser.parse_args()

    main(args.base_url, args.download_restricted, args.debug_download_on)