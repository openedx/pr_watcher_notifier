import json
import textwrap
from pathlib import Path

import yaml

from .conftest import get_dummy_pr_with_list_of_files
from .notification import make_email
from .views import combine_data


TEST_DATA = Path(__file__).parent.parent / "test_data"

def test_email_rendering(app, client, mocker):
    """
    Test the rendering of email notifications.
    """
    fake_names = ["oeps/some-oep.rst", "some-other-file", "oeps/another.rst"]
    dummy_pr_object = get_dummy_pr_with_list_of_files(names=fake_names)
    mocker.patch('pr_watcher_notifier.views.get_pr', return_value=dummy_pr_object)

    with open(TEST_DATA / "pr_145_merged.json") as fdata:
        data = json.load(fdata)
    with open(TEST_DATA / "edx_config.yml") as fconfig:
        config = yaml.safe_load(fconfig)
    combine_data(data, config)
    msg = make_email(data)
    assert msg.subject == "Change in edx/open-edx-proposals: Describe the 'maybe' key."
    assert msg.body == textwrap.dedent("""\
        A pull request has files you might be interested in.

        "Describe the 'maybe' key." (https://github.com/edx/open-edx-proposals/pull/145
        by nedbat)
        against the edx/open-edx-proposals
        repository (branch master)
        has been merged.

        Changed files matching the filter:

          * oeps/some-oep.rst

          * oeps/another.rst


        --
        PR Watcher Notifier
        """).strip()
