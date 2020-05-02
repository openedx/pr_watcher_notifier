"""
Fixtures for the tests.
"""

from unittest.mock import MagicMock

import pytest

from pr_watcher_notifier import create_app

URL = '/pull-requests'


def get_dummy_pr_with_list_of_files(count):
    """
    Return a dummy list of files in a PR.
    """
    dummy_pr_object = MagicMock()
    dummy_list_of_files = MagicMock(return_value=[MagicMock() for _ in range(count)])
    dummy_pr_object.get_files = dummy_list_of_files
    return dummy_pr_object


@pytest.fixture
def app():
    """
    Fixture that returns an app.
    """
    app = create_app('test_settings')
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = False
    return app


@pytest.fixture
def client(app):
    """
    Fixture that returns a test client.
    """
    return app.test_client()


@pytest.fixture
def post(client, mocker):
    """
    Fixture that allows making a customized post request.
    """
    mocker.patch('pr_watcher_notifier.views.is_signature_valid', return_value=True)

    def _inner(json, headers=None):
        request_headers = {
            'X-Github-Event': 'pull_request', 'X-Hub-Signature': '123'
        }
        if headers:
            request_headers.update(headers)
        return client.post(
            URL,
            json=json,
            headers=request_headers,
            content_type='application/json',
        )
    return _inner
