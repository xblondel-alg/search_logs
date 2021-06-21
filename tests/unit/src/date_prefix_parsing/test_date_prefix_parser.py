import pytest
from src.date_prefix_parsing.date_prefix_parser import get_date_interval


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
