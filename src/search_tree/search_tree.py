from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Generator, Generic, List, Optional, Tuple, TypeVar, cast

from dateutil.relativedelta import relativedelta

# type variable for the data type at the leaf of the tree
TDataType = TypeVar("TDataType")


class Node(ABC, Generic[TDataType]):
    """
    Base class for all types of nodes in the datetime tree.
    """

    def __init__(
        self,
        max_children_number: int,
        children_index_base: int,
        start: datetime,
        end: datetime,
    ) -> None:
        """
        Constructor.

        :param children_number: Max number of children (0 for unlimited, else e.g. max is 12 for months, 31 for days, 23 for hours...)
        :param children_index_base: Indexing base for children (e.g. months and days start at 1, hours and minutes start at 0)
        :param start: Start of the interval contained in the node.
        :param end: End of the interval contained in the node (excluded).
        """
        self._key_part = self._get_keypart(start)
        self._max_children_number = max_children_number
        self._children_index_base = children_index_base
        self._start = start
        self._end = end

    #
    # Abstract interface
    #
    @abstractmethod
    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a key/value pair to the tree.

        :param key: Key to insert at
        :param value: Value to insert
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

    #
    # Protected methods
    #
    def _overlaps_interval(self, interval: Tuple[datetime, datetime]) -> bool:
        """
        Check that this object interval and the interval passed in parameter overlap.

        :param interval: Interval to check.
        """
        start, end = interval
        start_matches = self._start < end
        end_matches = start < self._end
        return start_matches and end_matches

    @abstractmethod
    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        pass


class NonDataNode(Node[TDataType]):
    """
    Intermediate node that contains no data, and are not the root.
    """

    def __init__(
        self,
        max_children_number: int,
        children_index_base: int,
        start: datetime,
        end: datetime,
    ) -> None:
        """
        Constructor.

        :param children_number: Max number of children (0 for unlimited, else e.g. max is 12 for months, 31 for days, 23 for hours...)
        :param children_index_base: Indexing base for children (e.g. months and days start at 1, hours and minutes start at 0)
        :param start: Start of the interval contained in the node.
        :param end: End of the interval contained in the node (excluded).
        """
        super().__init__(max_children_number, children_index_base, start, end)

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
            # this cast is here to prevent from assuming that
            # self._children[index] is None, which is verified by the current logic
            node = cast(Node[TDataType], self._children[index])
        node.add_value(key, value)

    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.
        """
        matches = self._overlaps_interval(interval)
        if matches:
            for child in [c for c in self._children if c is not None]:
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

    def __init__(self, start: datetime) -> None:
        """
        Constructor.

        :param start: Start of the range.
        """
        super().__init__(
            max_children_number=0,
            children_index_base=0,
            start=start,
            end=start + timedelta(minutes=1),
        )
        # since we are at a leaf node, we add the values in heap, as we will always return them all
        self._values: List[TDataType] = []

    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a value to this given minute.

        :param key: Insertion key.
        :param value: Value to insert.
        """
        if key.minute != self._key_part:
            raise ValueError(f"Trying to insert key {key} at minute {self._key_part}")
        self._values.append(value)

    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.

        Since the minute is at the leaf, matching a minute returns all its contents.
        """
        if self._overlaps_interval(interval):
            yield from self._values

    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        return timestamp.minute


class HourNode(NonDataNode[TDataType]):
    """
    Node modelling an hour.
    """

    def __init__(self, start: datetime) -> None:
        """
        Constructor.

        :param start: Start of the range.
        """
        # 60 minutes in an hour, base 0
        super().__init__(
            max_children_number=60,
            children_index_base=0,
            start=start,
            end=start + timedelta(hours=1),
        )

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a minute object.

        :param key_part: Key part for the minute.
        """
        return MinuteNode[TDataType](
            start=datetime(
                self._start.year,
                self._start.month,
                self._start.day,
                self._start.hour,
                key_part,
                0,
            ),
        )

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the minute part from the key.

        :param key: Key to extract from
        """
        return key.minute

    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        return timestamp.hour


class DayNode(NonDataNode[TDataType]):
    """
    Node modelling an day.
    """

    def __init__(self, start: datetime) -> None:
        """
        Constructor.

        :param start: Start of the range.
        """
        # 24 hours in a day, base 0
        super().__init__(
            max_children_number=24,
            children_index_base=0,
            start=start,
            end=start + timedelta(days=1),
        )

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of an hour object.

        :param key_part: Key part for the hour.
        """
        return HourNode[TDataType](
            start=datetime(
                self._start.year, self._start.month, self._start.day, key_part, 0, 0
            ),
        )

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the hour part from the key.

        :param key: Key to extract from
        """
        return key.hour

    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        return timestamp.day


class MonthNode(NonDataNode[TDataType]):
    """
    Node modelling a month.
    """

    def __init__(self, key_part: int, start: datetime) -> None:
        """
        Constructor.

        :param key_part: Key part of the level.
        :param start: Start of the range.
        """
        # we handle the maximum possible number of days, independently of the
        # actual number of days in a given month
        # days are numbered with a base 1
        super().__init__(
            max_children_number=31,
            children_index_base=1,
            start=start,
            end=start + relativedelta(months=1),
        )

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of an day object.

        :param key_part: Key part for the day.
        """
        return DayNode[TDataType](
            start=datetime(self._start.year, self._start.month, key_part, 0, 0, 0),
        )

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the day part from the key.

        :param key: Key to extract from
        """
        return key.day

    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        return timestamp.month


class YearNode(NonDataNode[TDataType]):
    """
    Node modelling a year.
    """

    def __init__(self, start: datetime) -> None:
        """
        Constructor.

        :param start: Start of the range.
        """
        # 12 months, starting at 1
        super().__init__(
            max_children_number=12,
            children_index_base=1,
            start=start,
            end=start + relativedelta(years=1),
        )

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a month object.

        :param key_part: Key part for the month.
        """
        return MonthNode[TDataType](
            key_part=key_part, start=datetime(self._start.year, key_part, 1, 0, 0, 0)
        )

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the month part from the key.

        :param key: Key to extract from
        """
        return key.month

    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        return timestamp.year


class SearchTree(Node[TDataType]):
    """
    Specific class for the root node, that has a specific behavior, as it has an unlimited number of children (the number of years).
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__(
            max_children_number=0,
            children_index_base=0,
            start=datetime.min,
            end=datetime.max,
        )
        # as we have an unlimited number of child nodes, we use a dictionary
        self._children: Dict[int, Node[TDataType]] = {}

    def add_value(self, key: datetime, value: TDataType) -> None:
        """
        Add a key/value pair to the tree.

        :param key: Key to insert at
        :param value: Value to insert
        """
        if key.year not in self._children or self._children[key.year] is None:
            node: Node[TDataType] = YearNode[TDataType](
                start=datetime(key.year, 1, 1, 0, 0, 0)
            )
            self._children[key.year] = node
        else:
            node = self._children[key.year]
        node.add_value(key, value)

    def get_values_for_interval(
        self, interval: Tuple[datetime, datetime]
    ) -> Generator[TDataType, None, None]:
        """
        Find all values contained in the passed interval.

        :param interval: Open interval for the start and end.
        """
        start, end = interval
        for year in range(start.year, end.year + 1):
            if year in self._children:
                yield from self._children[year].get_values_for_interval(interval)

    def _get_keypart(self, timestamp: datetime) -> int:
        """
        Extract the key part from the timestamp.

        :param timestamp: Timestamp to extract the key part from.
        """
        # there actually is not key part at this level
        return -1
