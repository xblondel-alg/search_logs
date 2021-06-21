import pytest
from src.date_prefix_parsing.date_prefix_parser import get_date_interval

from datetime import datetime


class TestDatePrefixParser:
    """
    Tests of the date_prefix_parser module.
    """

    def test_get_date_interval_empty_value(self) -> None:
        """
        It should raise an error if we pass an empty value.
        """
        with pytest.raises(ValueError):
            get_date_interval("")

    def test_get_date_interval_year_level_date(self) -> None:
        """
        It should return an open interval covering a year
        """
        target = "2015"
        expected = (datetime(2015, 1, 1, 0, 0), datetime(2016, 1, 1, 0, 0))
        actual = get_date_interval(target)
        assert expected == actual
