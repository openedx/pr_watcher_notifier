"""
views for the application.
"""
from flask import abort, request, current_app, Blueprint

from .github_api import is_signature_valid, should_send_notification
from .notification import send_notifications

APP = Blueprint('app.views', __name__, template_folder='templates')


def get_request_json(req):
    """
    Return the parsed request body JSON.
    """
    data = req.get_json(silent=True)
    if data is None:
        current_app.logger.error('Invalid JSON in the request body')
        abort(400)
    return data


@APP.route('/pull-requests', methods=['POST', ])
def handler():
    """
    View to handle the webhook notifications.
    """
    event_type = request.headers.get('X-Github-Event')
    status_code = 200
    if event_type is None:
        current_app.logger.error('No event type specified')
        abort(400)
    if event_type == 'pull_request':
        if not is_signature_valid(request):
            current_app.logger.error('Invalid request signature')
            abort(400)
        data = get_request_json(request)
        repo = data['repository']['full_name']
        pr_number = data['number']
        notify, modified_files = should_send_notification(data)
        if notify:
            data['modified_files'] = modified_files
            current_app.logger.info('Match: {} #{}'.format(repo, pr_number))
            send_notifications(data)
            status_code = 201
        else:
            current_app.logger.info('Ignored: {} #{}'.format(repo, pr_number))
    else:
        current_app.logger.info('Ignored: Not a pull request')

    return '', status_code
