import os
import yaml

from dotenv import load_dotenv

SCAN_INTERVAL_SEC = 60 * 15
OUT_FILE = '../found_offers.json'
DB_FILE = '../db.file'
LOG_LEVEL = 3  # 3 - Debug, 2 - Normal, 1 - No output

# This is for simulating that requests comes from web-browser.
BROWSER_REQUEST_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,pl;q=0.7",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/66.0.3359.139 Safari/537.36"
}

# Load data as environment variables from .envconfig file.
load_dotenv('../.envconfig')
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Load search data from YAML file
with open("../searchconfig.yaml", "r") as yaml_file:
    yaml_data = yaml.load(yaml_file)
    OLX_SITES_TO_MONITOR = yaml_data['olx_urls']
    RECIPIENT_EMAILS = yaml_data['recipient_emails']
