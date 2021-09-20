# appdcon
A Django application to test Discourse Connect connectivity.

Accepts Discourse Connect requests when a user tries to log into a Discourse site.

See [this page](https://meta.discourse.org/t/discourseconnect-official-single-sign-on-for-discourse-sso/13045)
for more details on Discourse Connect.

Configure **Discourse Connect** to send a request to this app at
`http://IP:PORT/discourse`. Where IP is the IP address of the computer
running this app, and PORT is the port number used by the app.

The code that handles the Discourse Connect request can be found in `appdcon/discourse/views.py`.

This app can handle connections from multiple Discourse sites. Each
site must have a hostname and secret. This information is stored in
the SITE table (see `appdcon/discourse/models.py`).

The `appdata\fixtures\discourse_sites.json` file contains the information for a Discourse test site.


## Development

This project uses [Poetry](https://python-poetry.org/) for dependency
management. See [Dependencies](#Dependencies) for instructions on how to install it.

Use the following commands to install the project dependencies:

```sh
poetry config virtualenvs.in-project true
poetry install
```

To start a shell using the virtual environment:

```sh
poetry shell
```

### Dependencies

Install poetry on Linux or OSX with the following command:

```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3
```

Refer to this documentation at https://python-poetry.org/docs/ for more details on how to install Poetry.
