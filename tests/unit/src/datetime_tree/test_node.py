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
