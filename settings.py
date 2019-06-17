"""
Configuration for the application.
"""
import os

import yaml

def get_watch_config():
    """
    Load the watch configuration from the YAML file specified in
    the WATCH_CONFIG_FILE environment variable.
    """
    config_file = os.environ['WATCH_CONFIG_FILE']
    with open(config_file) as yaml_file:
        return yaml.safe_load(yaml_file)


GITHUB_WEBHOOK_SECRET = os.environ['GITHUB_WEBHOOK_SECRET']
GITHUB_ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']

# Expected format of values in the YAML configuration file.
# Repeat the same block for configuring multiple repositories.
#
# ---
# <repo owner>/<repo name>:
#   patterns:
#     - "pattern1"
#     - "pattern2"
#   recipients:
#     - "nobody@example.com"
#   subject: "Subject text, see code for available format strings"

WATCH_CONFIG = get_watch_config()

MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
