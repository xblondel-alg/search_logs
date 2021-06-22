"""
    Startup file of the application, that set up Flask and its routes.

    The API is quite simple. Most notably, versioning is hardcoded in the routes.
"""
from flask import Flask, jsonify, request
from flask.wrappers import Response

from src.date_prefix_parsing.date_prefix_parser import get_date_interval
from src.search_engine.search_engine import SearchEngine
from os import getenv

engine = SearchEngine()
with open(getenv("DATASET_PATH", ""), "r") as f:
    engine.bulk_load_dataset(f)

app = Flask(__name__)


@app.route("/")  # type: ignore
def home_handler() -> str:
    """
    Home handler, used to check if the Flask application is running.
    """
    return "Ready"


@app.route("/1/queries/count/<date_prefix>")  # type: ignore
def count_handler(date_prefix: str) -> Response:
    """
    Handler of the count route.

    :param date_prefix: Extracted from the query string, date prefix to apply restrictions.

    Raises if the date prefix is in an invalid format.
    """
    app.logger.debug(f"Date prefix: {date_prefix}")
    date_interval = get_date_interval(date_prefix)
    return jsonify({"count": engine.get_distinct_count(date_interval)})


@app.route("/1/queries/popular/<date_prefix>")  # type: ignore
def popular_handler(date_prefix: str) -> Response:
    """
    Handler of the popular route.

    :param date_prefix: Extracted from teh query string, date prefix to apply restrictions.

    Query string param:
    - size: Optional number of requested elements, defaults to 3.

    Raises if the date prefix is in an invalid format or the size is not a strictly positive integer.

    """
    size = int(request.args.get("size", "3"))
    app.logger.debug(f"Date prefix: {date_prefix}")
    app.logger.debug(f"Size: {size}")
    if size <= 0:
        raise ValueError(f"Invalid size value {size}")
    date_interval = get_date_interval(date_prefix)
    popular_list = engine.get_popular(date_interval, size)
    return jsonify({"queries": [{"query": query, "count": count} for query, count in popular_list]})
