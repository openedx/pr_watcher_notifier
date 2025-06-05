"""
views for the application.
"""

from fnmatch import fnmatch

from flask import abort, request, current_app, Blueprint

from .github_api import get_comparison_file_names, get_target_branch, get_pr, is_signature_valid
from .notification import send_notifications

APP = Blueprint('views', __name__, template_folder='templates')


def get_request_json(req):
    """
    Return the parsed request body JSON.
    """
    data = req.get_json(silent=True)
    if data is None:
        current_app.logger.error('Invalid JSON in the request body')
        abort(400)
    return data


def get_repo_watch_config(watch_config, repo):
    """
    Return the watch configuration for a given repository.
    """
    repo_config = {}
    wildcard_match = False
    for watched_repo_name, config in watch_config.items():
        if fnmatch(repo, watched_repo_name):
            excludes = config.get("exclude", ())
            if any(fnmatch(repo, exclude) for exclude in excludes):
                continue
            repo_config = config
            if '/*' not in watched_repo_name:
                wildcard_match = False
                break
            wildcard_match = True
    return repo_config, wildcard_match


def should_send_notification(data):
    """
    Return whether the notification should be sent for the given request data or not.
    """
    action = data['action']
    notify = False
    matching_modified_files = []
    if action in ('opened', 'closed', 'synchronize', 'reopened'):  # pylint:disable=too-many-nested-blocks
        repo = data['repository']['full_name']
        is_private = data['repository']['private']
        pr_number = data['number']
        try:
            pr = get_pr(repo, pr_number)
        except Exception:
            return notify, matching_modified_files
        matched = False
        config = data['watch_config']
        wildcard_match = data['wildcard_match']
        if is_private and wildcard_match and not config.get('notify_for_private_repos', False):
            current_app.logger.info(
                f'{repo} is a private repo for which notifications have not been explicitly enabled'
            )
            return False, []
        if config:
            for modified_file in pr.get_files():
                for pattern in config['patterns']:
                    current_app.logger.debug(f"fnmatch({modified_file.filename!r}, {pattern!r})")
                    if fnmatch(modified_file.filename, pattern):
                        matched = True
                        matching_modified_files.append(modified_file.filename)
        if matched:
            notify = True

            # To avoid duplicate notifications for the same PR when its source branch is updated,
            # check if the modifications to the watched patterns are first added by the changes
            # in the update. This can be done by comparing the previous HEAD of the PR branch against
            # the target branch and verifying that no files matching the patterns were modified.
            if action == 'synchronize':
                target = get_target_branch(pr)
                previous_head = data['before']
                for modified_file in get_comparison_file_names(repo, target, previous_head):
                    for pattern in config['patterns']:
                        if fnmatch(modified_file, pattern):
                            notify = False
                            break
    return notify, matching_modified_files


def combine_data(data, watch_config):
    repo = data['repository']['full_name']
    data['watch_config'], data['wildcard_match'] = get_repo_watch_config(watch_config, repo)
    notify, modified_files = should_send_notification(data)
    data['notify'] = notify
    data['modified_files'] = modified_files


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
        combine_data(data, current_app.config['WATCH_CONFIG'])
        repo = data['repository']['full_name']
        pr_number = data['number']
        if data['notify']:
            current_app.logger.info(f'Match: {repo} #{pr_number}')
            send_notifications(data)
            status_code = 201
        else:
            current_app.logger.info(f'Ignored: {repo} #{pr_number}')
    else:
        current_app.logger.info('Ignored: Not a pull request')

    return '', status_code
