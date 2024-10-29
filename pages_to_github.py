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
# TODO: Add script to scripts folder
# TODO: Add test to test folder


# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

def process_page(page):
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

    backup_dir = Path(Path("local_backup"), "pages", page_slug)
    backup_dir.mkdir(parents=True, exist_ok=True)

    try:
        page_file = backup_dir / "page.json"
        with page_file.open('w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, sort_keys=True)
        logging.info(f"Saved JSON content for {page_slug}")
    except IOError as e:
        logging.error(f"Error saving JSON content for {page_slug}: {e}")

    try:
        page_file = backup_dir / f"{page.get('template', 'index.html')}"
        with page_file.open('w', encoding='utf-8') as f:
            json.dump(page['content']['html']['de'], f, indent=4, sort_keys=True)
        logging.info(f"Saved HTML content for {page_slug}")
    except IOError as e:
        logging.error(f"Error saving HTML content for {page_slug}: {e}")

    try:
        page_file = backup_dir / "page.css"
        with page_file.open('w', encoding='utf-8') as f:
            json.dump(page['content']['css']['de'], f, indent=4, sort_keys=True)
        logging.info(f"Saved CSS content for {page_slug}")
    except IOError as e:
        logging.error(f"Error saving CSS content for {page_slug}: {e}")

    # TODO: Check rate limits and adapt wait time accordingly
    time.sleep(1)

def list_studio_pages(api_key, domain):
    url = f"https://{domain}/api/automation/v1.0/studio_pages/"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def retrieve_studio_page(api_key, domain, page_slug):
    url = f"https://{domain}/api/automation/v1.0/studio_pages/{page_slug}/"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main(base_url, download_restricted):
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
            if not page['restricted'] or download_restricted:
                process_page(page)
            else:
                logging.info(f"Skipping restricted entry: {page['slug']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download ODS pages from data.bs.ch")
    parser.add_argument("--base-url", default="https://data.bs.ch/api/management/v2/pages/",
                        help="Base URL for the API")
    parser.add_argument("--download-restricted", type=bool, default=True,
                        help="Download restricted pages")

    args = parser.parse_args()

    main(args.base_url, args.download_restricted)