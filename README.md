PR Watcher Notifier
===================

A flask web application that handles webhook notifications for pull request changes and sends out notifications
when there are changes to files matched by the configured patterns for each repository


Pre-requisites
==============

Python 3.6 or newer


GitHub Webhook setup
====================

* The application has to be run on a internet-accessible URL in production. During development, a tool like
  `ngrok` can be used to expose the local development server on the internet.
* Create a webhook on the repository to be watched by following [these instructions](https://developer.github.com/webhooks/creating/).
This requires administrator-level access to the repository.
* Use the `<Internet-accessible URL of the app>/pull-requests` as the payload URL and set the `Content Type` to `application/json`.
* Remember to set a secret and to select only the 'Pull request' event.
* Create a GitHub access token. No particular permissions are required for a public repository. The `repo` scope permissions are needed for private repositories.


Development Setup
=================

* Clone this repository and navigate into the cloned directory.
* Create a virtualenv environment and install the requirements.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt -r requirements-dev.txt
```

* Verify that the unit tests run without errors and pass.

```bash
$ pytest --cov=pr_watcher_notifier
```

* Configure the environment variables used in the `settings.py` file.
* Setup the watch configuration YAML file and configure the `WATCH_CONFIG_FILE` environment variable to point to it. The
  file format is documented in `watch_config.yml.sample`.
* Set the `FLASK_APP` environment variable to point to the `run.py` file.
* Set the `FLASK_DEBUG` environment variable to `1` and run the development server.

```bash
$ export FLASK_APP=run.py
$ export FLASK_DEBUG=1
$ flask run
```

The development server should now be available at http://127.0.0.1:5000 and listening for the webhook notifications.
To modify the IP address or the port used by the development server, use the `-h` and `-p` flags of the `flask run`
command respectively.

```bash
$ flask run -h 0.0.0.0 -p 8000
```

Configuration
=============

The app gets its configuration settings from the following environment variables.

* `GITHUB_ACCESS_TOKEN` - The GitHub access token which has the appropriate permissions to access the repositories
  the app will be configured to watch.
  Get this from https://github.com/settings/tokens.
* `GITHUB_WEBHOOK_SECRET` - The webhook secret token used to create the GitHub webhook.
  This is a random string you make up, and will use when configuring the webhook.
  ``uuid.uuid4()`` could be a good source.

* `WATCH_CONFIG_FILE` - The file containing the watch configuration to be used by the app.
* `CUSTOM_CONFIG_REPO` - Optional. Required only when deploying to Heroku. URL of a git repository containing
  the watch configuration file, which must be named config.yml. More details in the section about deploying to Heroku.
* `LOG_LEVEL` - the log level to use: "debug", "info", "warning", or "error".

The following settings related to email accept values as documented in
the [Flask-Mail documentation](https://pythonhosted.org/Flask-Mail/#configuring-flask-mail).

* `MAIL_DEFAULT_SENDER`
* `MAIL_SERVER`
* `MAIL_PORT`
* `MAIL_USE_TLS`
* `MAIL_USERNAME`
* `MAIL_PASSWORD`

Deploying to Heroku
===================

An example `Procfile` which deploys this app to Heroku using `gunicorn` is provided. Since Heroku doesn't provide an easy
way to deploy custom configuration files, the `do_pre_release_steps.sh` script is run before starting the app.
The script downloads the watch configuration file named `config.yml` from an external git repository specified in
the `CUSTOM_CONFIG_REPO` environment variable to the location specified in the `WATCH_CONFIG_FILE` environment variable.
If the repository also contains a `templates` sub-directory containing the custom email templates, those are copied to
the app templates directory and can be used in the watch configuration file.

[Here](https://github.com/lgp171188/custom_templates) is an example repo that can be used as the `CUSTOM_CONFIG_REPO`.


Setting the webhook
===================

To use this as a GitHub webhook, you configure either a per-repo or per-organization webhook:

* For payload URL, use https://<HOST>/pull-requests .
* For Content type, use application/json .
* For Secret, use whatever you set for `GITHUB_WEBHOOK_SECRET` above.
* For Events, choose Pull requests.
