"""
    Module providing function to parse a date received as a parameter from the API.
"""

from typing import Tuple
from datetime import datetime

import re

PREFIX_PARSER_REGEX = re.compile(r"(?P<year>\d\d\d\d)")


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
    """
    match = PREFIX_PARSER_REGEX.match(date_prefix)
    if match is None:
        raise ValueError(
            "Invalid date prefix format - Expected YYYY[-MM[-DD[ hh[:mm]]]"
        )
    if not match.group("year"):
        raise ValueError("The YYYY part is mandatory")
    year = int(match.group("year"))
    return (datetime(year, 1, 1, 0, 0, 0), datetime(year + 1, 1, 1, 0, 0, 0))
