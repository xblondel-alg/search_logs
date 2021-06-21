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

    def test_get_date_interval_month_level_date(self) -> None:
        """
        It should return an open interval covering a month
        """
        target = "2015-03"
        expected = (datetime(2015, 3, 1, 0, 0), datetime(2015, 4, 1, 0, 0))
        actual = get_date_interval(target)
        assert expected == actual

    def test_get_date_interval_day_level_date(self) -> None:
        """
        It should return an open interval covering a day
        """
        target = "2015-03-15"
        expected = (datetime(2015, 3, 15, 0, 0), datetime(2015, 3, 16, 0, 0))
        actual = get_date_interval(target)
        assert expected == actual

    def test_get_date_interval_hour_level_date(self) -> None:
        """
        It should return an open interval covering an hour
        """
        target = "2015-03-15 11"
        expected = (datetime(2015, 3, 15, 11, 0), datetime(2015, 3, 15, 12, 0))
        actual = get_date_interval(target)
        assert expected == actual

    def test_get_date_interval_minute_level_date(self) -> None:
        """
        It should return an open interval covering a minute
        """
        target = "2015-03-15 11:07"
        expected = (datetime(2015, 3, 15, 11, 7), datetime(2015, 3, 15, 11, 8))
        actual = get_date_interval(target)
        assert expected == actual
