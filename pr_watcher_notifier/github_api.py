"""
Utility functions for interacting with the GitHub API.
"""
import hashlib
import hmac

from flask import current_app
from github import Github


def is_signature_valid(request_obj):
    """
    Check the HMAC signature and return if it is valid or not.
    """
    signature = request_obj.headers.get('X-Hub-Signature')
    if signature is not None:
        secret = current_app.config['GITHUB_WEBHOOK_SECRET'].encode('utf-8')
        mac = hmac.new(secret, msg=request_obj.data, digestmod=hashlib.sha1)
        return hmac.compare_digest('sha1={}'.format(mac.hexdigest()), signature)
    return False


def get_client():
    """
    Return the GitHub client.
    """
    return Github(current_app.config['GITHUB_ACCESS_TOKEN'])


def get_pr(repo, pr_number):
    """
    Return the pull request object for the given repository and pull request number.
    """
    try:
        return get_client().get_repo(repo).get_pull(pr_number)
    except Exception:
        current_app.logger.error('Failed to retrieve the details of {}: #{}'.format(repo, pr_number))
        raise


def get_file_names(files):
    """
    Returns a list of file names from an iterable containing the 'File' object.
    """
    return [f.filename for f in files]


def get_comparison_file_names(repo, base, head):
    """
    Return the file names of the file names modified in the given comparison.
    """
    files = []
    try:
        files = get_client().get_repo(repo).compare(base, head).files
    except Exception:
        current_app.logger.error('Failed to retrieve the files changed in the most recent update to the PR')
    return get_file_names(files)


def get_target_branch(pr):
    """
    Return the target branch name of a pull request.
    """
    return pr.base.ref
