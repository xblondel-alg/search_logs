from abc import ABC, abstractmethod
from typing import Dict, Generator, Generic, Iterable, List, Optional, Tuple, TypeVar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# type variable for the data type at the leaf of the tree
TDataType = TypeVar("TDataType")


class Node(ABC, Generic[TDataType]):
    """
    Base class for all types of nodes in the datetime tree.
    """

    def __init__(
        self,
        level_value: int,
        max_children_number: int,
        children_index_base: int,
        start: datetime,
        end: datetime,
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
        self._start = start
        self._end = end

    def matches_interval(self, interval: Tuple[datetime, datetime]) -> bool:
        start, end = interval
        start_matches = self._start < end
        end_matches = start < self._end
        return start_matches and end_matches

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
        self,
        level_value: int,
        max_children_number: int,
        children_index_base: int,
        start: datetime,
        end: datetime,
    ) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        :param children_number: Max number of children (0 for unlimited, else e.g. max is 12 for months, 31 for days, 23 for hours...)
        :param children_index_base: Indexing base for children (e.g. months and days start at 1, hours and minutes start at 0)
        """
        super().__init__(
            level_value, max_children_number, children_index_base, start, end
        )

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
        matches = self.matches_interval(interval)
        if matches:
            for child in self._children:
                if child is not None:
                    yield from child.get_values_for_interval(interval)

    @abstractmethod
    def _normalize_interval(
        self, key_part: int, interval: Tuple[datetime, datetime]
    ) -> Tuple[datetime, datetime]:
        """
        Normalize the interval, to limit it to the current level.

        :param key_part: Normalization base
        :param interval: Interval to normalize
        """
        pass

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

    def __init__(self, level_value: int, start: datetime) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        """
        super().__init__(level_value, 0, 0, start, start + timedelta(minutes=1))
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
        if self.matches_interval(interval):
            yield from self._values


class HourNode(NonDataNode[TDataType]):
    """
    Node modelling an hour.
    """

    def __init__(self, level_value: int, start: datetime) -> None:
        # 60 minutes in an hour, base 0
        super().__init__(level_value, 60, 0, start, start + timedelta(hours=1))

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a minute object.

        :param key_part: Key part for the minute.
        """
        return MinuteNode[TDataType](
            level_value=key_part,
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

    def _normalize_interval(
        self, key_part: int, interval: Tuple[datetime, datetime]
    ) -> Tuple[datetime, datetime]:
        """
        Normalize the interval, by focusing it on the current minute.

        :param key_part: Targeted minute
        :param interval: Original interval
        """
        start, end = interval
        candidate_start = datetime(
            start.year, start.month, start.day, start.hour, key_part, 0
        )
        candidate_end = candidate_start + timedelta(minutes=1)
        actual_start = max(start, candidate_start)
        actual_end = min(end, candidate_end)
        return actual_start, actual_end


class DayNode(NonDataNode[TDataType]):
    """
    Node modelling an day.
    """

    def __init__(self, level_value: int, start: datetime) -> None:
        # 24 hours in a day, base 0
        super().__init__(level_value, 24, 0, start, start + timedelta(days=1))

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of an hour object.

        :param key_part: Key part for the hour.
        """
        return HourNode[TDataType](
            level_value=key_part,
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

    def _normalize_interval(
        self, key_part: int, interval: Tuple[datetime, datetime]
    ) -> Tuple[datetime, datetime]:
        """
        Normalize the interval, by focusing it on the current hour.

        :param key_part: Targeted hour
        :param interval: Original interval
        """
        start, end = interval
        candidate_start = datetime(start.year, start.month, start.day, key_part, 0, 0)
        candidate_end = datetime(start.year, start.month, start.day, key_part, 23, 59)
        actual_start = max(start, candidate_start)
        actual_end = min(end, candidate_end)
        return actual_start, actual_end


class MonthNode(NonDataNode[TDataType]):
    """
    Node modelling a month.
    """

    def __init__(self, level_value: int, start: datetime) -> None:
        # we handle the maximum possible number of days, independently of the
        # actual number of days in a given month
        # days are numbered with a base 1
        super().__init__(level_value, 31, 1, start, start + relativedelta(months=1))

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of an day object.

        :param key_part: Key part for the day.
        """
        return DayNode[TDataType](
            level_value=key_part,
            start=datetime(self._start.year, self._start.month, key_part, 0, 0, 0),
        )

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the day part from the key.

        :param key: Key to extract from
        """
        return key.day

    def _normalize_interval(
        self, key_part: int, interval: Tuple[datetime, datetime]
    ) -> Tuple[datetime, datetime]:
        """
        Normalize the interval, by focusing it on the current day.

        :param key_part: Targeted day
        :param interval: Original interval
        """
        start, end = interval
        candidate_start = datetime(start.year, start.month, key_part, 0, 0, 0)
        candidate_end = candidate_start + relativedelta(days=1)
        actual_start = max(start, candidate_start)
        actual_end = min(end, candidate_end)
        return actual_start, actual_end


class YearNode(NonDataNode[TDataType]):
    """
    Node modelling a year.
    """

    def __init__(self, level_value: int, start: datetime) -> None:
        """
        Constructor.

        :param level_value: Value at the given level (e.g. the year, the month etc.)
        """
        # 12 months, starting at 1
        super().__init__(
            level_value, 12, 1, start=start, end=start + relativedelta(years=1)
        )

    def _create_next_level_instance(self, key_part: int) -> Node[TDataType]:
        """
        Create an instance of a month object.

        :param key_part: Key part for the month.
        """
        return MonthNode[TDataType](
            level_value=key_part, start=datetime(self._start.year, key_part, 1, 0, 0, 0)
        )

    def _extract_next_level_key_part(self, key: datetime) -> int:
        """
        Extract the month part from the key.

        :param key: Key to extract from
        """
        return key.month

    def _normalize_interval(
        self, key_part: int, interval: Tuple[datetime, datetime]
    ) -> Tuple[datetime, datetime]:
        """
        Normalize the interval, by focusing it on the current month.

        :param key_part: Targeted month
        :param interval: Original interval
        """
        start, end = interval
        candidate_start = datetime(start.year, key_part, 1, 0, 0, 0)
        candidate_end = candidate_start + relativedelta(months=1)
        actual_start = max(start, candidate_start)
        actual_end = min(end, candidate_end)
        return actual_start, actual_end


class RootNode(Node[TDataType]):
    """
    Specific class for the root node, that has a specific behavior, as it has an unlimited number of children (the number of years).
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__(
            level_value=-1,
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
        if key.year not in self._children:
            node = YearNode[TDataType](
                level_value=key.year, start=datetime(key.year, 1, 1, 0, 0, 0)
            )
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
        for year in range(start.year, end.year + 1):
            if year in self._children:
                yield from self._children[year].get_values_for_interval(interval)

    def _normalize_interval(self, year: int, interval: Tuple[datetime, datetime]):
        """
        Normalize the interval, by focusing it on the current year.

        :param year: Targeted year
        :param interval: Original interval
        """
        start, end = interval
        candidate_start = datetime(year, 1, 1, 0, 0, 0)
        candidate_end = datetime(year + 1, 1, 1, 0, 0, 0)
        actual_start = max(start, candidate_start)
        actual_end = min(end, candidate_end)
        return actual_start, actual_end
