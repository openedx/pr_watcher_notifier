"""
Unit tests for the application.
"""

from .views import get_repo_watch_config
from .conftest import get_dummy_pr_with_list_of_files

URL = '/pull-requests'

REPO_CONFIG1 = {
    'patterns': ['documents/*'],
    'recipients': 'nobody@example.com',
}


def test_get_method(client):
    """
    Test a GET request.
    """
    response = client.get(URL)
    assert response.status_code == 405


def test_post_method_no_event_header(client):
    """
    Test a POST request without event header.
    """
    response = client.post(URL)
    assert response.status_code == 400


def test_event_not_pull_request(post):
    """
    Test when the event is not a pull request.
    """
    response = post(URL, headers={'X-Github-Event': 'blah'})
    assert response.status_code == 200


def test_no_signature(client):
    """
    Test when there is no signature header in the request.
    """
    response = client.post(URL, headers={'X-Github-Event': 'pull_request'})
    assert response.status_code == 400


def test_invalid_signature(client):
    """
    Test when the signature is invalid.
    """
    response = client.post(
        URL,
        headers={'X-Github-Event': 'pull_request', 'X-Hub-signature': 123},
        data={'A': 1}
    )
    assert response.status_code == 400


def test_not_json(client, mocker):
    """
    Test when the request body is not JSON.
    """
    mocker.patch('pr_watcher_notifier.views.is_signature_valid', return_value=True)
    headers = {'X-Github-Event': 'pull_request', 'X-Hub-Signature': 'abcd'}
    response = client.post(URL, data="1as2", content_type='application/x-www-form-urlencoded', headers=headers)
    assert response.status_code == 400


def test_missing_required_fields(post):
    """
    Test when the request JSON misses required fields.
    """
    response = post(json={'a': 1})
    assert response.status_code == 500


def test_pr_action_ignored(post, mocker):
    """
    Test when the request is for notifying an ignored pull request action.
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={'number': 1, 'repository': {'full_name': 'a/b', 'private': False}, 'action': 'edited'}
    )
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.notification.send_notifications')

    response = post(json={'a': 1})
    assert response.status_code == 200
    mocked_send_notifications.assert_not_called()


def test_notification_not_sent_when_unable_to_retrieve_pr_details(post, mocker):
    """
    Test when unable to retrieve the PR details, for example due to not having access to the private repository
    of the PR or when there are issues with the GitHub API.
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_pr',
        side_effect=Exception()
    )
    response = post(json={
        'repository': {
            'full_name': 'a/b',
            'private': False,
        },
        'number': 1,
        'action': 'opened',
    })
    assert response.status_code == 200


def test_no_files_matching_condition(post, mocker):
    """
    Test if no files in the opened PR match the watch pattern.
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={'number': 1, 'repository': {'full_name': 'a/b', 'private': False}, 'action': 'opened'}
    )
    dummy_pr_object = get_dummy_pr_with_list_of_files(["code/module.py"])
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    response = post(json={'a': '1'})
    assert response.status_code == 200
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.notification.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 200
    mocked_send_notifications.assert_not_called()


def test_files_matching_condition(post, mocker):
    """
    Test when the files in the opened PR match the watch pattern.
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={'number': 1, 'repository': {'full_name': 'a/b', 'private': False}, 'action': 'opened'}
    )
    this_commit_file_names = ["documents/file1.rst", "elsewhere/file2.py"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(this_commit_file_names)
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.views.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 201
    mocked_send_notifications.assert_called_once()


def test_pr_synchronized_but_already_notified(post, mocker):
    """
    Test when the files in the synchronized PR match the watch pattern,
    but weren't first added in the recent change.
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={
            'number': 1,
            'repository': {'full_name': 'a/b', 'private': False},
            'action': 'synchronize', 'before': '123'
        }
    )
    this_commit_file_names = ["documents/file1.rst", "elsewhere/file2.py"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(this_commit_file_names)
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    mocker.patch('pr_watcher_notifier.views.get_target_branch', return_value='master')
    mocker.patch('pr_watcher_notifier.views.get_comparison_file_names', return_value=this_commit_file_names)
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.views.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 200
    mocked_send_notifications.assert_not_called()


def test_pr_synchronized_but_not_already_notified(post, mocker):
    """
    Test when the files in the synchronized PR match the watch pattern,
    and are added in the recent change.
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={
            'number': 1,
            'repository': {'full_name': 'a/b', 'private': False},
            'action': 'synchronize',
            'before': '123'
        }
    )
    this_commit_file_names = ["documents/file1.rst", "elsewhere/file2.py"]
    last_commit_file_names = ["a", "b"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(this_commit_file_names)

    mocker.patch('pr_watcher_notifier.views.get_repo_watch_config', return_value=(REPO_CONFIG1, False))
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    mocker.patch('pr_watcher_notifier.views.get_target_branch', return_value='master')
    mocker.patch('pr_watcher_notifier.views.get_comparison_file_names', return_value=last_commit_file_names)
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.views.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 201
    mocked_send_notifications.assert_called_once()


def test_get_repo_watch_config_when_a_matching_org_wildcard_pattern_is_present():
    """
    Test the get_repo_watch_config function when a matching wildcard pattern is present
    """
    repo_config, wildcard_match = get_repo_watch_config(
        {
            'a/*': {
                'patterns': ['documents/*'],
                'recipients': 'nobody@example.com',
            }
        },
        'a/abcd'
    )
    assert repo_config
    assert wildcard_match


def test_get_repo_watch_config_when_excluding():
    """
    Test the get_repo_watch_config function when excluding a pattern
    """
    repo_config, wildcard_match = get_repo_watch_config(
        {
            'a/*': {
                'patterns': ['documents/*'],
                'recipients': 'nobody@example.com',
                'exclude': ['a/xyz', 'a/*bc*'],
            }
        },
        'a/abcd'
    )
    assert not repo_config


def test_get_repo_watch_config_when_excluding_doesnt_exclude():
    """
    Test the get_repo_watch_config function when excluding a pattern that doesn't match.
    """
    repo_config, wildcard_match = get_repo_watch_config(
        {
            'a/*': {
                'patterns': ['documents/*'],
                'recipients': 'nobody@example.com',
                'exclude': ['a/xyz', 'a/*qq*'],
            }
        },
        'a/abcd'
    )
    assert repo_config
    assert wildcard_match


def test_get_repo_watch_config_when_an_exact_match_and_a_matching_org_wildcard_pattern_present():
    """
    Test the get_repo_watch_config function when a wildcard pattern and an exact match are present
    """
    repo_config, wildcard_match = get_repo_watch_config(
        {
            'a/*': {
                'patterns': ['documents/*'],
                'recipients': 'nobody@example.com',
            },
            'a/abcd': {
                'patterns': ['documents/*'],
                'recipients': 'specific@example.com',
            }
        },
        'a/abcd'
    )
    assert repo_config
    assert repo_config['recipients'] == 'specific@example.com'
    assert wildcard_match is False


def test_notifications_not_sent_for_private_repo_with_only_a_matching_org_wildcard_pattern(post, mocker):
    """
    Test and verify that notifications are not sent by default for private repositories with a matching
    organization wildcard pattern in configuration
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={
            'number': 1,
            'repository': {'full_name': 'b/c', 'private': True},
            'action': 'synchronize',
            'before': '123'
        }
    )
    this_commit_file_names = ["documents/file1.rst", "elsewhere/file2.py"]
    last_commit_file_names = ["a", "b"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(this_commit_file_names)
    wildcard_match = True

    mocker.patch('pr_watcher_notifier.views.get_repo_watch_config', return_value=(REPO_CONFIG1, wildcard_match))
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    mocker.patch('pr_watcher_notifier.views.get_target_branch', return_value='master')
    mocker.patch('pr_watcher_notifier.views.get_comparison_file_names', return_value=last_commit_file_names)
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.views.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 200
    mocked_send_notifications.assert_not_called()


def test_notifications_sent_for_private_repo_with_an_exact_match(post, mocker):
    """
    Test and verify that notifications are sent for private repositories with an exactly matching
    repo name in the watch configuration
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={
            'number': 1,
            'repository': {'full_name': 'a/b', 'private': True},
            'action': 'synchronize',
            'before': '123'
        }
    )
    wildcard_match = False
    this_commit_file_names = ["documents/file1.rst", "elsewhere/file2.py"]
    last_commit_file_names = ["a", "b"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(this_commit_file_names)
    mocker.patch('pr_watcher_notifier.views.get_repo_watch_config', return_value=(REPO_CONFIG1, wildcard_match))
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    mocker.patch('pr_watcher_notifier.views.get_target_branch', return_value='master')
    mocker.patch('pr_watcher_notifier.views.get_comparison_file_names', return_value=last_commit_file_names)
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.views.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 201
    mocked_send_notifications.assert_called_once()


def test_notifications_sent_for_private_repo_with_matching_org_wildcard_pattern_when_enabled_explicitly(post, mocker):
    """
    Test and verify that notifications are sent for private repositories with an exactly matching
    repo name in the watch configuration
    """
    mocker.patch(
        'pr_watcher_notifier.views.get_request_json',
        return_value={
            'number': 1,
            'repository': {'full_name': 'b/c', 'private': True},
            'action': 'synchronize',
            'before': '123'
        }
    )
    this_commit_file_names = ["documents/file1.rst", "elsewhere/file2.py"]
    last_commit_file_names = ["a", "b"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(this_commit_file_names)
    wildcard_match = True
    repo_config = {
        'patterns': ['documents/*'],
        'recipients': 'nobody@example.com',
        'notify_for_private_repos': True,
    }
    mocker.patch('pr_watcher_notifier.views.get_repo_watch_config', return_value=(repo_config, wildcard_match))
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)
    mocker.patch('pr_watcher_notifier.views.get_target_branch', return_value='master')
    mocker.patch('pr_watcher_notifier.views.get_comparison_file_names', return_value=last_commit_file_names)
    mocked_send_notifications = mocker.patch('pr_watcher_notifier.views.send_notifications')
    response = post(json={'a': 1})
    assert response.status_code == 201
    mocked_send_notifications.assert_called_once()
