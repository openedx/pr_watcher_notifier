"""
Utility functions for sending notifications.
"""

from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_email(context):
    """
    Send the notification email.
    """
    subject = context['subject'].format(**context)
    body = render_template('email_body.txt', **context)
    msg = Message(
        subject,
        recipients=context['to'],
    )
    msg.body = body
    mail.send(msg)


def send_notifications(data):
    """
    Wrapper method to send out notifications.
    """
    pr_data = data['pull_request']
    repo = data['repository']['full_name']
    watch_config = current_app.config['WATCH_CONFIG'][repo]
    context = {
        'repo': repo,
        'number': data['number'],
        'patterns': ", ".join(watch_config['patterns']),
        'action': data['action'] if data['action'] != 'synchronize' else 'updated',
        'merged': pr_data['merged'],
        'creator': pr_data['user']['login'],
        'to': watch_config['recipients'],
        'subject': watch_config['subject'],
        'pr_url': pr_data['_links']['html']['href'],
        'modified_files': data['modified_files'],
    }
    send_email(context)
