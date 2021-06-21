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

    def test_empty_tree(self, tree: RootNode[str]) -> None:
        """
        Should not return a value from an empty tree
        """
        key = datetime(2015, 10, 1, 12, 22)
        expected = []
        actual = tree.get_values_for_exact_key(key)

        assert expected == actual

    def test_single_element_tree_success(self, tree: RootNode[str]) -> None:
        """
        Should find the only inserted value.
        """
        key = datetime(2015, 10, 1, 12, 22)
        value = "test"
        tree.add_value(key, value)
        expected = [value]
        actual = tree.get_values_for_exact_key(key)

        assert expected == actual

    def test_single_element_tree_failure(self, tree: RootNode[str]) -> None:
        """
        Should not another key than the only inserted one.
        """
        key = datetime(2015, 10, 1, 12, 22)
        target = datetime(2016, 10, 1, 12, 22)

        value = "test"
        tree.add_value(key, value)
        expected = []
        actual = tree.get_values_for_exact_key(target)

        assert expected == actual

    def test_multiple_elements_tree_success(self, tree: RootNode[str]) -> None:
        """
        Should find all the elements matching a given minute.
        """
        key = datetime(2015, 10, 1, 12, 22)
        value1 = "test1"
        value2 = "test2"
        value3 = "test3"
        tree.add_value(key, value1)
        tree.add_value(key, value2)
        tree.add_value(key, value3)
        expected = [value1, value2, value3]
        actual = tree.get_values_for_exact_key(key)

        assert expected == actual

    def test_duplicate_elements_tree_success(self, tree: RootNode[str]) -> None:
        """
        Duplicate values for the same key should be found.
        """
        key = datetime(2015, 10, 1, 12, 22)
        value1 = "test1"
        tree.add_value(key, value1)
        tree.add_value(key, value1)
        tree.add_value(key, value1)
        # we expect to the duplicate value three times
        expected = [value1, value1, value1]
        actual = tree.get_values_for_exact_key(key)

        assert expected == actual

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
