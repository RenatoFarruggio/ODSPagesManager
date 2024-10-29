# ODS Pages Manager for data.bs.ch
This is a script that downloads opendatasoft (ODS) pages.

## Setup with venv (recommended)
- Create virtual environment: `python -m venv .venv`
- Activate virtual environment: `.venv\Scripts\activate`
- Install requirements: `pip install -r requirements.txt`
- Create .env file from .env.template and insert API key from the [Back-Office](https://data.bs.ch/account/api-keys/). It needs two permissions: "Alle Seiten durchsuchen" and "Alle Seiten bearbeiten"

## Setup without venv
- Install requirements: `pip install -r requirements.txt`
- Create .env file from .env.template and insert API key from the [Back-Office](https://data.bs.ch/account/api-keys/). It needs two permissions: "Alle Seiten durchsuchen" and "Alle Seiten bearbeiten"

## Usage
Run script with `python pages_to_github.py`. This will download a json file of the entire page, and also the separate 
html and css files for all pages.

## TODO
- Version control with git
- Upload pages to github
- Automatically translate pages
