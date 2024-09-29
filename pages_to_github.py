import os
import time
from os.path import exists

from dotenv import load_dotenv
import requests
import json
import logging
from pathlib import Path
import html

# Load environment variables from .env file
load_dotenv()

# Get API key and base URL from environment variables
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL')

download_restricted = os.getenv('download_restricted')
upload_restricted_to_github = ('upload_restricted_to_github')

if not api_key or not base_url:
    raise ValueError("API_KEY and BASE_URL must be set in the .env file")

# Set up headers with the API key for authentication
headers = {
    'Authorization': f'Apikey {api_key}'
}

# Make a request to the API to get a list of ODS pages
response = requests.get(base_url, headers=headers)

# Check the response status and print detailed error information if needed
if response.status_code != 200:
    print(f"Failed to retrieve pages. Status code: {response.status_code}")
    print(f"Response content: {response.text}")
    raise Exception("API request failed")

# Parse the JSON response
pages = response.json()
    
# Loop through the pages and download content
for page in pages['items']:
    # TODO: Think about and discuss how restricted pages should be handled
    if page['restricted'] and not download_restricted:
        print(f"Skipping restricted entry: {page_slug}")
        continue


    page_slug = page['slug']
    print(f"Handling page: {page_slug}")

    page_title_de = page['title']['de']
    content_author = page['author']['username'].split('@')[0]

    print(f"{content_author=}: {page_title_de=}")

    # TODO: save the files somewhere somehow in some structure
    backup_dir = Path("local_backup") / page_slug
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        page_file = backup_dir / "page.json"
        with page_file.open('w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, sort_keys=True)
            #file.write(html.unescape(html_file))
        logging.info(f"Saved HTML content for {page_slug}")
    except IOError as e:
        logging.error(f"Error saving HTML content for {page_slug}: {e}")

    time.sleep(1)
    

# TODO: main method
# TODO: logging
# TODO: replace print with logging
