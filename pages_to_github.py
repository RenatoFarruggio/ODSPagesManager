import os
import time
from dotenv import load_dotenv
import requests
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
api_key = os.getenv('API_KEY')

base_url = f"https://data.bs.ch/api/management/v2/pages/"

download_restricted = os.getenv('download_restricted')
upload_restricted_to_github = os.getenv('upload_restricted_to_github')
debug__download_on = False

# Path structure:
#
# local_backup
# - pages
# - custom_views
#

if not api_key or not base_url:
    raise ValueError("API_KEY and BASE_URL must be set in the .env file")

# Set up headers with the API key for authentication
headers = {
    'Authorization': f'Apikey {api_key}'
}

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

    if debug__download_on:
        backup_dir = Path(os.path.join(Path("local_backup"), "pages", page_slug))
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

def main():
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

            process_page(page)

if __name__ == "__main__":
    main()