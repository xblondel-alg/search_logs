"""
    Startup file of the application, that set up Flask and its routes.

    The API is quite simple. Most notably, versioning is hardcoded in the routes.
"""
from os import getenv

from flask import Flask, jsonify, request
from flask.wrappers import Response

from src.application.setup import setup_application
from src.date_prefix_parsing.date_prefix_parser import get_date_interval
from src.search_engine.search_engine import SearchEngine

search_engine = SearchEngine()
setup_application(dataset_path=getenv("DATASET_PATH", ""), search_engine=search_engine)


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
    # parse parameter
    date_interval = get_date_interval(date_prefix)

    # get value
    count = search_engine.get_distinct_count(date_interval)

    # format result
    return jsonify({"count": count})


@app.route("/1/queries/popular/<date_prefix>")  # type: ignore
def popular_handler(date_prefix: str) -> Response:
    """
    Handler of the popular route.

    :param date_prefix: Extracted from teh query string, date prefix to apply restrictions.

    Query string param:
    - size: Optional number of requested elements, defaults to 3.

    Raises if the date prefix is in an invalid format or the size is not a strictly positive integer.

    """
    # parse parameters
    size = int(request.args.get("size", "-1"))
    if size <= 0:
        raise ValueError(f"Invalid or missing size {size}")
    date_interval = get_date_interval(date_prefix)

    # get results
    popular_list = search_engine.get_popular(date_interval, size)

    # format the result
    return jsonify(
        {"queries": [{"query": query, "count": count} for query, count in popular_list]}
    )
