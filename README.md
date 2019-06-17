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
* Setup the watch configuration YAML file and configure the `WATCH_CONFIG_FILE` environment variable to point to it. The format is documented in `settings.py`.
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
