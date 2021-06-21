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

We expose the two requested routes:

- `GET /1/queries/count/<DATE_PREFIX>`
- `GET /1/queries/popular/<DATE_PREFIX>?size=<SIZE>`

In this version, we did not pay much attention to the route structure. Most notably, versions are hardcoded in the route names.

## Date prefix parsing

Date prefixes are parsed using the `get_date_interval` function of the `src/date_prefix_parsing/date_prefix_parser.py` module.

Given a date prefix, it returns the matching interval. For instance:

    - if YYYY, returns [YYYY-01-01 00:00, YYYY+1-01-01 00:00] (full year)
    - if YYYY-MM, returns [YYYY-MM-01 00:00, YYYY-MM+1-01 00:00] (full month, deal with YYYY-12 => YYYY+1-01)
    And so on for all possible parameters.

It tackles the `datetime` and `dateutils` modules to handle date arithmetic.

It is tested in `tests/unit/src/date_prefix_parsing/test_date_prefix_parser.py`.
