from abc import ABC, abstractmethod
from typing import Dict, Generator, Generic, Iterable, List, Optional, Tuple, TypeVar
from datetime import datetime

# type variable for the data type at the leaf of the tree
TDataType = TypeVar("TDataType")


class Node(ABC, Generic[TDataType]):
    """
    Base class for all types of nodes in the datetime tree.
    """

    def __init__(
        self, level_value: int, max_children_number: int, children_index_base: int
    ) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        :param children_number: Max number of children (0 for unlimited, else e.g. max is 12 for months, 31 for days, 23 for hours...)
        :param children_index_base: Indexing base for children (e.g. months and days start at 1, hours and minutes start at 0)
        """
        self._level_value = level_value
        self._max_children_number = max_children_number
        self._children_index_base = children_index_base

    @abstractmethod
    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a key/value pair to the tree.

        :param key: Key to insert at
        :param value: Value to insert
        """
        pass

    @abstractmethod
    def get_values_for_exact_key(self, key: datetime) -> Iterable[TDataType]:
        """
        Get the values exactly matching a key.
        May return an empty iterable if nothing found.

        :param key: Key to find the values for.

        This method is mostly used in tests.
        """
        pass

    @abstractmethod
    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.
        """
        pass


class NonDataNode(Node[TDataType]):
    """
    Intermediate node that contains no data, and are not the root.
    """

    def __init__(
        self, level_value: int, max_children_number: int, children_index_base: int
    ) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        :param children_number: Max number of children (0 for unlimited, else e.g. max is 12 for months, 31 for days, 23 for hours...)
        :param children_index_base: Indexing base for children (e.g. months and days start at 1, hours and minutes start at 0)
        """
        super().__init__(level_value, max_children_number, children_index_base)

        self._children: List[Optional[Node[TDataType]]] = [
            None for _ in range(self._max_children_number)
        ]

    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a key/value pair to the tree.

        :param key: Key to insert at
        :param value: Value to insert
        """
        key_part = self._extract_next_level_key_part(key)
        index = self._get_index_from_key_part(key_part)
        if self._children[index] is None:
            node = self._create_next_level_instance(key_part)
            self._children[index] = node
        else:
            node = self._children[index]
        # this is to prevent type checks from complaining that node may be None
        # which is guaranteed by the logic above
        assert node is not None
        node.add_value(key, value)

    def get_values_for_exact_key(self, key: datetime) -> Iterable[TDataType]:
        """
        Get the values exactly matching a key.
        May return an empty iterable if nothing found.

        :param key: Key to find the values for.
        """
        key_part = self._extract_next_level_key_part(key)
        index = self._get_index_from_key_part(key_part)
        node = self._children[index]
        if node is None:
            return []
        return node.get_values_for_exact_key(key)

    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.
        """
        start, end = interval
        start_index = self._get_index_from_key_part(
            self._extract_next_level_key_part(start)
        )
        end_index = self._get_index_from_key_part(
            self._extract_next_level_key_part(end)
        )
        # we do not want to exclude the end index, as both start and end index could
        # have the same value
        for index in range(start_index, end_index + 1):
            child = self._children[index]
            if child is not None:
                yield from child.get_values_for_interval(interval)

    def _get_index_from_key_part(self, key_part: int) -> int:
        """
        Given a key part, rebase from the children index base to get an index
            in the children list.

        :param key_part: Key part to rebase
        """
        return key_part - self._children_index_base

    @abstractmethod
    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the key part for the next level

        :param key: Key to extract from
        """
        pass

    @abstractmethod
    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a next level object.

        :param key_part: Key part for the next level
        """
        pass


class MinuteNode(Node[TDataType]):
    """
    Node modelling a minute.
    It is a leaf node, as it also contains the data.
    """

    def __init__(self, level_value: int) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        """
        super().__init__(level_value, 0, 0)
        # since we are at a leaf node, we add the values in heap, as we will always return them all
        self._values: List[TDataType] = []

    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a value to this given minute.

        :param key: Insertion key.
        :param value: Value to insert.
        """
        if key.minute != self._level_value:
            raise ValueError(
                f"Trying to insert key {key} at minute {self._level_value}"
            )
        self._values.append(value)

    def get_values_for_exact_key(self, key: datetime) -> Iterable[TDataType]:
        """
        Get the values exactly matching a key.
        May return an empty iterable if nothing found.

        :param key: Key to find the values for.
        """
        if self._level_value == key.minute:
            return self._values
        return []

    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.
        """
        start, end = interval
        if start.minute <= self._level_value < end.minute:
            yield from self._values


class HourNode(NonDataNode[TDataType]):
    """
    Node modelling an hour.
    """

    def __init__(self, level_value: int) -> None:
        # 60 minutes in an hour, base 0
        super().__init__(level_value, 60, 0)

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a minute object.

        :param key_part: Key part for the minute.
        """
        return MinuteNode[TDataType](level_value=key_part)

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the minute part from the key.

        :param key: Key to extract from
        """
        return key.minute


class DayNode(NonDataNode[TDataType]):
    """
    Node modelling an day.
    """

    def __init__(self, level_value: int) -> None:
        # 24 hours in a day, base 0
        super().__init__(level_value, 24, 0)

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of an hour object.

        :param key_part: Key part for the minute.
        """
        return HourNode[TDataType](level_value=key_part)

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the hour part from the key.

        :param key: Key to extract from
        """
        return key.hour


class MonthNode(NonDataNode[TDataType]):
    """
    Node modelling a month.
    """

    def __init__(self, level_value: int) -> None:
        # we handle the maximum possible number of days, independently of the
        # actual number of days in a given month
        # days are numbered with a base 1
        super().__init__(level_value, 31, 1)

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of an hour object.

        :param key_part: Key part for the minute.
        """
        return DayNode[TDataType](level_value=key_part)

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the day part from the key.

        :param key: Key to extract from
        """
        return key.day


class YearNode(NonDataNode[TDataType]):
    """
    Node modelling a year.
    """

    def __init__(self, level_value: int) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        """
        # 12 months, starting at 1
        super().__init__(level_value, 12, 1)

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a month object.

        :param key_part: Key part for the month.
        """
        return MonthNode[TDataType](level_value=key_part)

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the month part from the key.

        :param key: Key to extract from
        """
        return key.month


class RootNode(Node[TDataType]):
    """
    Specific class for the root node, that has a specific behavior, as it has an unlimited number of children (the number of years).
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__(level_value=-1, max_children_number=0, children_index_base=0)
        # as we have an unlimited number of child nodes, we use a dictionary
        self._children: Dict[int, Node[TDataType]] = {}

    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a key/value pair to the tree.

        :param key: Key to insert at
        :param value: Value to insert
        """
        if key.year not in self._children:
            node = YearNode[TDataType](level_value=key.year)
            self._children[key.year] = node
        else:
            node = self._children[key.year]
        node.add_value(key, value)

    def get_values_for_exact_key(self, key: datetime) -> Iterable[TDataType]:
        if key.year in self._children:
            return self._children[key.year].get_values_for_exact_key(key)
        return []

    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.
        """
        start, end = interval
        for year in sorted(self._children.keys()):
            if year > end.year:
                break
            if year >= start.year:
                yield from self._children[year].get_values_for_interval(interval)
