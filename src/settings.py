import os
import yaml

from dotenv import load_dotenv

SCAN_INTERVAL_SEC = 60 * 20
WORKING_HOURS = (8, 23)
OUT_FILE = '../found_offers.json'
DB_FILE = '../db.file'
LOG_LEVEL = 3  # 3 - Debug, 2 - Normal, 1 - No output

# Load data as environment variables from .envconfig file.
load_dotenv('../.envconfig')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
MESSENGER_APP_TOKEN = os.getenv('MESSENGER_APP_TOKEN')

# Load search data from YAML file
with open('../searchconfig.yaml', 'r') as yaml_file:
    yaml_data = yaml.load(yaml_file)
    OLX_SITES_TO_MONITOR = yaml_data['olx_urls']
    RECIPIENT_EMAILS = yaml_data['recipient_emails']
    MESSENGER_RECIPIENTS = yaml_data['messenger_users_psids']
