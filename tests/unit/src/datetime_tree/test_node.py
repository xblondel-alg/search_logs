from datetime import datetime
import pytest
from src.datetime_tree.node import RootNode


@pytest.fixture
def tree() -> RootNode[str]:
    return RootNode[str]()


class TestNode:
    """
    Test of the node module.
    """

    def test_find_minute_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in a minute interval.
        """
        # we fill 3 consecutive minutes, and we look for the middle one
        key1 = datetime(2015, 10, 1, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 1, 12, 23)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 10, 1, 12, 24)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)

        # we expect to find the values for key2, but not for key3 (as the interval is open)
        expected = [value2_1, value2_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key3,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_multiple_minutes_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in an interval containing multiple minutes
        """
        # we fill 4 consecutive minutes, and we look for the two middle ones
        key1 = datetime(2015, 10, 1, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 1, 12, 23)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 10, 1, 12, 24)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)
        key4 = datetime(2015, 10, 1, 12, 25)
        value4_1 = "test4_1"
        value4_2 = "test4_2"
        tree.add_value(key4, value4_1)
        tree.add_value(key4, value4_2)

        # we expect to find the values for key2 and key3, but not for key4 (as the interval is open)
        expected = [value2_1, value2_2, value3_1, value3_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key4,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_hour_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in an hour interval.
        """
        # we fill 3 consecutive hours, and we look for the middle one
        # note that all other values are identical, to avoid false positives
        key1 = datetime(2015, 10, 1, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 1, 13, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 10, 1, 14, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)

        # we expect to find the values for key2, but not for key3 (as the interval is open)
        expected = [value2_1, value2_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key3,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_multiple_hours_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in an interval containing multiple hours
        """
        # we fill 4 consecutive hours, and we look for the two middle ones
        # note that all other values are identical, to avoid false positives

        key1 = datetime(2015, 10, 1, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 1, 13, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 10, 1, 14, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)
        key4 = datetime(2015, 10, 1, 15, 22)
        value4_1 = "test4_1"
        value4_2 = "test4_2"
        tree.add_value(key4, value4_1)
        tree.add_value(key4, value4_2)

        # we expect to find the values for key2 and key3, but not for key4 (as the interval is open)
        expected = [value2_1, value2_2, value3_1, value3_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key4,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_day_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in a day interval.
        """
        # we fill 3 consecutive days, and we look for the middle one
        # note that all other values are identical, to avoid false positives
        key1 = datetime(2015, 10, 1, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 2, 12, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 10, 3, 12, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)

        # we expect to find the values for key2, but not for key3 (as the interval is open)
        expected = [value2_1, value2_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key3,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_multiple_days_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in an interval containing multiple days
        """
        # we fill 4 consecutive days, and we look for the two middle ones
        # note that all other values are identical, to avoid false positives

        key1 = datetime(2015, 10, 1, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 2, 12, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 10, 3, 12, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)
        key4 = datetime(2015, 10, 4, 12, 22)
        value4_1 = "test4_1"
        value4_2 = "test4_2"
        tree.add_value(key4, value4_1)
        tree.add_value(key4, value4_2)

        # we expect to find the values for key2 and key3, but not for key4 (as the interval is open)
        expected = [value2_1, value2_2, value3_1, value3_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key4,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_month_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in a month interval.
        """
        # we fill 3 consecutive months, and we look for the middle one
        # note that all other values are identical, to avoid false positives
        key1 = datetime(2015, 10, 2, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 11, 2, 12, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 12, 2, 12, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)

        # we expect to find the values for key2, but not for key3 (as the interval is open)
        expected = [value2_1, value2_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key3,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_multiple_months_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in an interval containing multiple months.
        """
        # we fill 4 consecutive months, and we look for the two middle ones
        # note that all other values are identical, to avoid false positives

        key1 = datetime(2015, 9, 2, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2015, 10, 2, 12, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2015, 11, 2, 12, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)
        key4 = datetime(2015, 12, 2, 12, 22)
        value4_1 = "test4_1"
        value4_2 = "test4_2"
        tree.add_value(key4, value4_1)
        tree.add_value(key4, value4_2)

        # we expect to find the values for key2 and key3, but not for key4 (as the interval is open)
        expected = [value2_1, value2_2, value3_1, value3_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key4,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_year_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in a year interval.
        """
        # we fill 3 consecutive years, and we look for the middle one
        # note that all other values are identical, to avoid false positives
        key1 = datetime(2015, 10, 2, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2016, 10, 2, 12, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2017, 10, 2, 12, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)

        # we expect to find the values for key2, but not for key3 (as the interval is open)
        expected = [value2_1, value2_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key3,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual

    def test_find_multiple_years_interval(self, tree: RootNode[str]) -> None:
        """
        Should find all data in an interval containing multiple years.
        """
        # we fill 4 consecutive years, and we look for the two middle ones
        # note that all other values are identical, to avoid false positives

        key1 = datetime(2015, 10, 2, 12, 22)
        value1_1 = "test1_1"
        value1_2 = "test1_2"
        tree.add_value(key1, value1_1)
        tree.add_value(key1, value1_2)
        key2 = datetime(2016, 10, 2, 12, 22)
        value2_1 = "test2_1"
        value2_2 = "test2_2"
        tree.add_value(key2, value2_1)
        tree.add_value(key2, value2_2)
        key3 = datetime(2017, 10, 2, 12, 22)
        value3_1 = "test3_1"
        value3_2 = "test3_2"
        tree.add_value(key3, value3_1)
        tree.add_value(key3, value3_2)
        key4 = datetime(2018, 10, 2, 12, 22)
        value4_1 = "test4_1"
        value4_2 = "test4_2"
        tree.add_value(key4, value4_1)
        tree.add_value(key4, value4_2)

        # we expect to find the values for key2 and key3, but not for key4 (as the interval is open)
        expected = [value2_1, value2_2, value3_1, value3_2]
        actual_generator = tree.get_values_for_interval(
            (
                key2,
                key4,
            )
        )
        # resolve the generator
        actual = list(actual_generator)

        assert expected == actual
