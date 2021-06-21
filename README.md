# search_logs

This repository search timestamped logs on a period of time.

## Setup

You need Python 3.9.5.

Once the repository is cloned, you can proceed as follows:

```
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

## Commands

A Makefile provides you with the following commands:

- `make black`: Apply black linter to the source and test trees
- `make mypy`: Apply mypy type checking to the source and test trees (rules defined in mypy.ini)
- `make pytest`: Execute tests stored in the tests directory, and calculate coverage (rules defined in pytest.ini)

## API

The API uses Flask and Werkzeug. Werkzeug being a development platform, additional deployment options would be needed to ship to production, to use a production-ready web server (such as nginx).
