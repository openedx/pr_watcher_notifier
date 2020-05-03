"""
Utility functions for sending notifications.
"""

from flask import current_app, render_template, render_template_string
from flask_mail import Message

from . import mail


def make_email(data):
    """
    Make the notification email.
    """
    context = make_notification_context(data)
    current_app.logger.debug('Sending email with context: {}'.format(context))
    # Jinja assumes HTML output, but subjects are plain text, so disable
    # the html autoescaping.
    subject = render_template_string(
        "{{% autoescape false %}}{}{{% endautoescape %}}".format(context['subject']),
        **context
    )
    body = render_template(context['body'], **context)
    msg = Message(
        subject,
        recipients=context['to'],
    )
    msg.body = body
    return msg


def make_notification_context(data):
    """
    Create the rendering context with information useful for templates.
    """
    pr_data = data['pull_request']
    repo = data['repository']['full_name']
    watch_config = data['watch_config']

    action = data['action']
    if action == 'synchronize':
        action = 'updated'
    elif action == 'closed' and pr_data['merged'] is True:
        action = 'merged'

    context = {
        'repo': repo,
        'number': data['number'],
        'patterns': ", ".join(watch_config['patterns']),
        'action': action,
        'merged': pr_data['merged'],
        'creator': pr_data['user']['login'],
        'to': watch_config['recipients'],
        'subject': watch_config['subject'],
        'body': watch_config['body'] if 'body' in watch_config else 'email_body.txt',
        'pr_url': pr_data['_links']['html']['href'],
        'modified_files': data['modified_files'],
        'pr': pr_data,
    }
    return context


def send_notifications(data):
    """
    Send email notifications.
    """
    mail = make_email(data)
    current_app.logger.info('Sending email to {!r} with subject {!r}'.format(
        context['to'], subject,
        ))
    mail.send(msg)
