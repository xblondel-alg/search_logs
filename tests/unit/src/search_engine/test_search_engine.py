from typing import Dict

from src.search_engine.search_engine import SearchEngine


class TestSearchEngineGetCountFromDataSet:
    """
    Test of the SearchEngine.get_count_from_dataset method.
    """

    def test_empty_dataset(self) -> None:
        """
        Should return a value of 0 for an empty dataset.
        """
        dataset: Dict[str, int] = {}
        expected = 0
        actual = SearchEngine.get_count_from_dataset(dataset)
        assert expected == actual

    def test_dataset(self) -> None:
        """
        It should return the actual sum when the dataset contains data.
        """
        dataset = {
            "value1": 3,
            "value2": 5,
            "value3": 7,
            "value4": 11,
        }
        expected = 26
        actual = SearchEngine.get_count_from_dataset(dataset)
        assert expected == actual
