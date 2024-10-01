# ODS Pages Manager for data.bs.ch
This is a script that downloads opendatasoft (ODS) pages.

## Usage
Install requirements from the requirements.txt: `pip install -r requirements.txt`. Then, create .env file from .env.template and insert API key from the [Back-Office](https://data.bs.ch/account/api-keys/). It needs two permissions: "Alle Seiten durchsuchen" and "Alle Seiten bearbeiten". Run script with `python pages_to_github.py`.

## TODO
- Version control with git
- Upload pages to github
- Automatically translate pages
