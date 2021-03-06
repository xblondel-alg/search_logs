from typing import Dict, Iterable, OrderedDict, Tuple
import pytest

from src.search_engine.search_engine import SearchEngine


@pytest.fixture
def empty_dataset() -> Dict[str, int]:
    return {}


@pytest.fixture
def non_empty_dataset() -> Dict[str, int]:
    return {
        "value2": 5,
        "value1": 11,
        "value4": 3,
        "value3": 7,
    }


@pytest.fixture
def popular_query_1() -> Iterable[Tuple[str, int]]:
    """
    One most popular query
    """
    return [("value1", 11)]


@pytest.fixture
def popular_queries_2() -> Iterable[Tuple[str, int]]:
    """
    Two most popular queries
    """
    return [("value1", 11), ("value3", 7)]


@pytest.fixture
def popular_queries_3() -> Iterable[Tuple[str, int]]:
    """
    Three most popular queries
    """
    return [("value1", 11), ("value3", 7), ("value2", 5)]


@pytest.fixture
def popular_queries_4() -> Iterable[Tuple[str, int]]:
    """
    Four most popular queries
    """
    return [("value1", 11), ("value3", 7), ("value2", 5), ("value4", 3)]


@pytest.fixture
def dataset_with_ties() -> Dict[str, int]:
    return {
        "value1": 11,
        "value3": 11,
        "value4": 3,
        "value2": 3,
    }


@pytest.fixture
def popular_queries_with_ties_2() -> Iterable[Tuple[str, int]]:
    """
    Two most popular queries with ties
    """
    return [("value1", 11), ("value3", 11)]


@pytest.fixture
def popular_queries_with_ties_3() -> Iterable[Tuple[str, int]]:
    """
    Three most popular queries with ties
    """
    return [("value1", 11), ("value3", 11), ("value4", 3)]


class TestSearchEngineGetCountFromDataSet:
    """
    Test of the SearchEngine.get_count_from_dataset method.
    """

    def test_empty_dataset(self, empty_dataset: Dict[str, int]) -> None:
        """
        Should return a value of 0 for an empty dataset.
        """
        expected = 0
        actual = SearchEngine.get_distinct_count_from_dataset(empty_dataset)
        assert expected == actual

    def test_non_empty_dataset(self, non_empty_dataset: Dict[str, int]) -> None:
        """
        It should return the distinct count of data, without regards to the number of elements.
        """
        expected = 4
        actual = SearchEngine.get_distinct_count_from_dataset(non_empty_dataset)
        assert expected == actual


class TestSearchEngineGetPopularFromDataset:
    """
    Test of the SearchEngine.get_popular_from_dataset method.
    """

    def test_empty_dataset_and_zero_size(self, empty_dataset: Dict[str, int]) -> None:
        """
        It should return an empty result with an empty dataset and a size of zero.
        """
        size = 0
        expected: Iterable[Tuple[str, int]] = []
        actual = SearchEngine.get_popular_from_dataset(empty_dataset, size)
        assert expected == actual

    def test_empty_dataset_and_non_zero_size(
        self, empty_dataset: Dict[str, int]
    ) -> None:
        """
        It should return an empty result with an empty dataset and a non-zero size.
        """
        size = 3
        expected: Iterable[Tuple[str, int]] = []
        actual = SearchEngine.get_popular_from_dataset(empty_dataset, size)
        assert expected == actual

    def test_non_empty_dataset_and_zero_size(
        self, non_empty_dataset: Dict[str, int]
    ) -> None:
        """
        It should return an empty result with a non-empty dataset and a zero size.
        """
        size = 0
        expected: Iterable[Tuple[str, int]] = []
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert expected == actual

    def test_non_empty_dataset_and_1_size(
        self, non_empty_dataset: Dict[str, int], popular_query_1: OrderedDict[str, int]
    ) -> None:
        """
        It should return the most popular query with a size of 1.
        """
        size = 1
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert popular_query_1 == actual

    def test_non_empty_dataset_and_2_size(
        self,
        non_empty_dataset: Dict[str, int],
        popular_queries_2: OrderedDict[str, int],
    ) -> None:
        """
        It should return the two most popular queries with a size of 2.
        """
        size = 2
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert popular_queries_2 == actual

    def test_non_empty_dataset_and_3_size(
        self,
        non_empty_dataset: Dict[str, int],
        popular_queries_3: OrderedDict[str, int],
    ) -> None:
        """
        It should return the three most popular queries with a size of 3.
        """
        size = 3
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert popular_queries_3 == actual

    def test_non_empty_dataset_and_4_size(
        self,
        non_empty_dataset: Dict[str, int],
        popular_queries_4: OrderedDict[str, int],
    ) -> None:
        """
        It should return the four most popular queries with a size of 4.
        """
        size = 4
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert popular_queries_4 == actual

    def test_non_empty_dataset_and_large_size(
        self,
        non_empty_dataset: Dict[str, int],
        popular_queries_4: OrderedDict[str, int],
    ) -> None:
        """
        It should return all the most popular queries with a size larger than the dataset.
        """
        size = len(non_empty_dataset) * 10
        actual = SearchEngine.get_popular_from_dataset(non_empty_dataset, size)
        assert popular_queries_4 == actual

    def test_dataset_with_ties_and_size_2(
        self,
        dataset_with_ties: Dict[str, int],
        popular_queries_with_ties_2: OrderedDict[str, int],
    ) -> None:
        """
        It should return the two most popular queries with ties sorted in their order in the dataset.
        """
        size = 2
        actual = SearchEngine.get_popular_from_dataset(dataset_with_ties, size)
        assert popular_queries_with_ties_2 == actual

    def test_dataset_with_ties_and_size_3(
        self,
        dataset_with_ties: Dict[str, int],
        popular_queries_with_ties_3: OrderedDict[str, int],
    ) -> None:
        """
        It should return the three most popular queries with ties sorted in their order in the dataset.
        """
        size = 3
        actual = SearchEngine.get_popular_from_dataset(dataset_with_ties, size)
        assert popular_queries_with_ties_3 == actual
