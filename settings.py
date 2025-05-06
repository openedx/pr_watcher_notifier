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
    with open(config_file, encoding='utf-8') as yaml_file:
        return yaml.safe_load(yaml_file)


GITHUB_WEBHOOK_SECRET = os.environ['GITHUB_WEBHOOK_SECRET']
GITHUB_ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']

WATCH_CONFIG = get_watch_config()

MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']

if os.environ.get('MAIL_SERVER'):
    MAIL_SERVER = os.environ.get('MAIL_SERVER')

if os.environ.get('MAIL_PORT'):
    MAIL_PORT = os.environ.get('MAIL_PORT')

if os.environ.get('MAIL_USE_TLS'):
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')

if os.environ.get('MAIL_USERNAME'):
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')

if os.environ.get('MAIL_PASSWORD'):
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
