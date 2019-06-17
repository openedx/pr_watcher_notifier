"""
A web application to receive GitHub webhook payload for pull requests and send out notification
when the watched files are changed.
"""
import logging

from flask import Flask
from flask.logging import default_handler
from flask_mail import Mail

mail = Mail()


def create_app(config_obj='settings'):
    """
    Factory function for creating and configuring an application.
    """
    app = Flask(__name__)
    from .views import APP
    app.register_blueprint(APP, url_prefix='/')
    app.config.from_object(config_obj)
    app.logger.removeHandler(default_handler)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | process=%(process)d | %(name)s | %(message)s')
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    mail.init_app(app)
    return app
