from datetime import datetime
from typing import Dict, OrderedDict, Tuple
from src.datetime_tree.node import RootNode


class SearchEngine:
    """
    Search engine that exposes the methods used the APIs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self._tree = RootNode[str]()

    def get_distinct_count(self, interval: Tuple[datetime, datetime]) -> int:
        """
        Get the count of the distinct values in an interval.

        :param interval: Interval to analyze.
        """
        dataset = self._get_dataset_from_interval(interval)
        return SearchEngine.get_count_from_dataset(dataset)

    def get_popular(
        self, interval: Tuple[datetime, datetime], size: int
    ) -> OrderedDict[str, int]:
        """
        Get the N most popular queries in the interval.

        :param interval: Interval to analyze
        :param size: Number of top elements to return
        """
        if size == 0:
            # avoid unnecessary work
            return OrderedDict()
        dataset = self._get_dataset_from_interval(interval)
        return SearchEngine.get_popular_from_dataset(dataset, size)

    #
    # Implementation
    #
    def _get_dataset_from_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Dict[str, int]:
        """
        Extract nodes from an interval, and returns a dataset: a dictionary containing the values and their count.

        :param interval: Open interval to extract from.
        """
        result: Dict[str, int] = {}
        for value in self._tree.get_values_for_interval(interval):
            if value not in result:
                result[value] = 1
            else:
                result[value] += 1
        return result

    @staticmethod
    def get_count_from_dataset(dataset: Dict[str, int]) -> int:
        """
        Given a dataset, return the total of all the counts.

        :param dataset: Dataset to analyze.
        """
        return sum(dataset.values())

    @staticmethod
    def get_popular_from_dataset(
        dataset: Dict[str, int], size: int
    ) -> OrderedDict[str, int]:
        """
        Given a dataset, return the first N values with the more occurrences.

        :param dataset: Dataset to analyze.
        :param size: Number of occurrences to return.
        """
        if size == 0 or len(dataset) == 0:
            # skip unnecessary work
            return OrderedDict()
        return OrderedDict()