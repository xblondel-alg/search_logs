"""
    Module providing function to parse a date received as a parameter from the API.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple

from dateutil.relativedelta import relativedelta

STRING_REGEX_YEAR = r"(?P<year>\d\d\d\d)"
STRING_REGEX_MONTH = r"(?P<month>\d\d)"
STRING_REGEX_DAY = r"(?P<day>\d\d)"
STRING_REGEX_HOUR = r"(?P<hour>\d\d)"
STRING_REGEX_MINUTE = r"(?P<minute>\d\d)"

PREFIX_PARSER_REGEX_YEAR = re.compile(STRING_REGEX_YEAR)
PREFIX_PARSER_REGEX_MONTH = re.compile(f"{STRING_REGEX_YEAR}-{STRING_REGEX_MONTH}")
PREFIX_PARSER_REGEX_DAY = re.compile(
    f"{STRING_REGEX_YEAR}-{STRING_REGEX_MONTH}-{STRING_REGEX_DAY}"
)
PREFIX_PARSER_REGEX_HOUR = re.compile(
    f"{STRING_REGEX_YEAR}-{STRING_REGEX_MONTH}-{STRING_REGEX_DAY} {STRING_REGEX_HOUR}"
)
PREFIX_PARSER_REGEX_MINUTE = re.compile(
    f"{STRING_REGEX_YEAR}-{STRING_REGEX_MONTH}-{STRING_REGEX_DAY} {STRING_REGEX_HOUR}:{STRING_REGEX_MINUTE}"
)

def get_date_interval(date_prefix: str) -> Tuple[datetime, datetime]:
    """
    Given a date prefix in the following form:
        YYYY[-MM[-DD[ hh[:mm]]]
        Where the year is mandatory and all other component are optional.

    Return a tuple containing an open interval of dates:
    - if YYYY, returns [YYYY-01-01 00:00, YYYY+1-01-01 00:00] (full year)
    - if YYYY-MM, returns [YYYY-MM-01 00:00, YYYY-MM+1-01 00:00] (full month, deal with YYYY-12 => YYYY+1-01)
    And so on for all possible parameters.

    :param date_prefix: Date prefix to build the interval from.

    Remark: There certainly is a smarter way to do this, with a dictionary of all the regexes, but this
        make for a more readable, even though a bit tedious, code.
    """
    match = PREFIX_PARSER_REGEX_MINUTE.match(date_prefix)
    if match is not None:
        start = datetime(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
            int(match.group("hour")),
            int(match.group("minute")),
        )
        end = start + timedelta(minutes=1)
        return (start, end)
    match = PREFIX_PARSER_REGEX_HOUR.match(date_prefix)
    if match is not None:
        start = datetime(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
            int(match.group("hour")),
            0,
        )
        end = start + timedelta(hours=1)
        return (start, end)
    match = PREFIX_PARSER_REGEX_DAY.match(date_prefix)
    if match is not None:
        start = datetime(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
            0,
            0,
        )
        end = start + timedelta(days=1)
        return (start, end)
    match = PREFIX_PARSER_REGEX_MONTH.match(date_prefix)
    if match is not None:
        start = datetime(int(match.group("year")), int(match.group("month")), 1, 0, 0)
        end = start + relativedelta(months=1)
        return (start, end)
    match = PREFIX_PARSER_REGEX_YEAR.match(date_prefix)
    if match is not None:
        start = datetime(int(match.group("year")), 1, 1, 0, 0)
        end = start + relativedelta(years=1)
        return (start, end)
    raise ValueError("Invalid date prefix format - Expected YYYY[-MM[-DD[ hh[:mm]]]")

def parse_timestamp(timestamp: str) -> datetime:
    """
        Parse a timestamp in the form:
            YYYY-MM-DD hh:mm
        If the timestamp contains seconds, they are ignored.

        :param timestamp: Timestamp to parse.
    """
    match = PREFIX_PARSER_REGEX_MINUTE.match(timestamp)
    if match is None:
        raise ValueError(f"Invalid timestamp {timestamp}")
    parsed_timestamp = datetime(
        int(match.group("year")),
        int(match.group("month")),
        int(match.group("day")),
        int(match.group("hour")),
        int(match.group("minute")),
    )
    return parsed_timestamp
