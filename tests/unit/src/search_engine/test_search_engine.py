from typing import Dict, OrderedDict
import pytest

from src.search_engine.search_engine import SearchEngine


@pytest.fixture
def empty_dataset() -> Dict[str, int]:
    return {}


@pytest.fixture
def non_empty_dataset() -> Dict[str, int]:
    return {
        "value1": 3,
        "value2": 5,
        "value3": 7,
        "value4": 11,
    }


class TestSearchEngineGetCountFromDataSet:
    """
    Test of the SearchEngine.get_count_from_dataset method.
    """

    def test_empty_dataset(self, empty_dataset: Dict[str, int]) -> None:
        """
        Should return a value of 0 for an empty dataset.
        """
        expected = 0
        actual = SearchEngine.get_count_from_dataset(empty_dataset)
        assert expected == actual

    def test_non_empty_dataset(self, non_empty_dataset: Dict[str, int]) -> None:
        """
        It should return the actual sum when the dataset contains data.
        """
        expected = 26
        actual = SearchEngine.get_count_from_dataset(non_empty_dataset)
        assert expected == actual


class TestSearchEngineGetPopularFromDataset:
    """
    Test of the SearchEngine.get_popular_from_dataset method.
    """

    def test_empty_dataset_and_zero_size(self, empty_dataset: Dict[str, int]):
        """
        It should return an empty result with an empty dataset and a size of zero.
        """
        size = 0
        expected: OrderedDict[str, int] = OrderedDict()
        actual = SearchEngine.get_popular_from_dataset(empty_dataset, size)
        assert expected == actual

    def test_empty_dataset_and_non_zero_size(self, empty_dataset: Dict[str, int]):
        """
        It should return an empty result with an empty dataset and a non-zero size.
        """
        size = 3
        expected: OrderedDict[str, int] = OrderedDict()
        actual = SearchEngine.get_popular_from_dataset(empty_dataset, size)
        assert expected == actual

    def test_non_empty_dataset_and_zero_size(self, non_empty_dataset: Dict[str, int]):
        """
        It should return an empty result with a non-empty dataset and a zero size.
        """
        size = 3
        expected: OrderedDict[str, int] = OrderedDict()
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert expected == actual
