# search_logs

This repository search timestamped logs on a period of time.

## Setup

You need Python 3.9.5.

Once the repository is cloned, you can proceed as follows:

```
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

## Commands

A Makefile provides you with the following commands:

- `make black`: Apply black linter to the source and test trees
- `make mypy`: Apply mypy type checking to the source and test trees (rules defined in mypy.ini)
- `make pytest`: Execute tests stored in the tests directory, and calculate coverage (rules defined in pytest.ini)
- `make start`: Start the application - See below

Starting the application requires you to set the environment variable `DATASET_PATH` to the path of the data set, that is the path of the TSV file containing the logs:

```
DATASET_PATH=~/hn_logs.tsv make start
```

Failing to set this value will result in an error.

## API

The API uses Flask and Werkzeug. Werkzeug being a development platform, additional deployment options would be needed to ship to production, to use a production-ready web server (such as nginx).

We expose the two requested routes:

- `GET /1/queries/count/<DATE_PREFIX>`
- `GET /1/queries/popular/<DATE_PREFIX>?size=<SIZE>`

In this version, we did not pay much attention to the route structure. Most notably, versions are hardcoded in the route names.

## Date prefix parsing

Date prefixes are parsed using the `get_date_interval` function of the `src/date_prefix_parsing/date_prefix_parser.py` module.

Given a date prefix, it returns the matching interval. For instance:

    - if YYYY, returns [YYYY-01-01 00:00, YYYY+1-01-01 00:00] (full year)
    - if YYYY-MM, returns [YYYY-MM-01 00:00, YYYY-MM+1-01 00:00] (full month, deal with YYYY-12 => YYYY+1-01)
    And so on for all possible parameters.

It tackles the `datetime` and `dateutils` modules to handle date arithmetic.

It is tested in `tests/unit/src/date_prefix_parsing/test_date_prefix_parser.py`.

## Search tree

The `src/search_tree/search_tree.py` module contains the gist of the data structure used to store and search the dataset. It is tested in `tests/unit/src/datetime_tree/test_search_tree.py`.

It is a search tree, whose keys are `datetime`, and whose values are generic with the type variable `TDataType`. It stores the values in memory.

It exposes two APIs:

- `def add_value(self, key: datetime, value: TDataType) -> None`: Inserts the key/value pair in the search tree. This is used to load the data. Note that adding a value actually inserts it in the tree, so the data is not expected to be loaded sequentially (actually, the data is not sequential in the example file).
- `def get_values_for_interval(self, interval: Tuple[datetime, datetime]) -> Generator[TDataType, None, None]:` For a given open interval of two `datetime`, it returns a generator of the values found. Note that the interval is in the form `(start, end)`, but `end` is excluded from the interval (it acts as a range in Python).

I initially started with a binary search tree, aiming to convert it to an n-ary search tree (more than 2 child nodes for each node), but I thought it more interesting to tackle the underlying data structure. Namely:

- We have a root node that contains years. There is no limit to the number of years contained, besides the min and max of the datetime type.
- We have year nodes, that contains months. Each year node contains up to 12 months.
- We have month nodes, that contain days. Each month node contains up to 31 days at most.
- We have day nodes, that contain hours. Each day node contains up to 24 hours.
- We have hour nodes, that contain minutes. Each hour node contains up to 60 minutes node.
- We have minute nodes, that contain the values. Each minute node can contain an unlimited number of values, as we may have several values at the same minute.

In terms of data structure organization, all nodes in the search tree inherits from the abstract `Node` class, and may belong to three categories:

- `SearchTree` is the root node, that contains years.
- `NonDataNode` is an abstract class, from which we derive all the intermediate nodes in the tree: `YearNode`, `MonthNode`, `DayNode`, `HourNode`.
- `MinuteNode` is a leaf node, that contain values.

The `Node` class actually contains a start and end value for the key, which constitutes an interval where end is excluded. It provides us with an `_overlaps_interval` method, that checks whether a given interval matches the start and end of the node, and that is used for searching in the tree.

The `SearchTree` node actually contains a dictionary, associating a year to a `YearNode` instance.

Adding a value to a `SearchTree` node is simply implemented by finding or creating the matching year node, then adding to this node.

Getting a value from a `SearchTree` node simply iterates on the dictionary keys between the start and end year (this latter excluded), and calling the search method of each year node.

The `MinuteNode` contains the data in an unordered list, as we systematically return the whole data set if the interval is matched when searching.

Adding a value to the minute node simply adds it to the list. Searching returns the whole list, as we already are at the last level of the interval.

A minute node may contain duplicate values, as the same query may appear multiple times in the same minute, and this information is necessary to count the most popular queries.

The `NonDataNode` derived classes are built around a fixed-size list, that contains enough room for the expected number of elements (e.g. 12 slots for the 12 months of a year, 24 slots for the 24 hours of the day). For months, we systematically reserve 31 days, independently of the actual number of days in the month.

Inserting a node in a `NonDataNode` is implemented by finding the index of the node in the list of elements (which implies dealing with 0-based values, such as hours or minutes, and 1-based values, such as months or days), and either fetching the existing node in the list, or creating a new one if it does not exists.

The derived class of `NonDataNode` basically deal with index calculation, and providing a factory for nodes at the next level.

Searching in `NonDataNode` uses a brute force approach: It is implemented in the `get_values_for_interval` method of `NonDataNode`, and first check if we have an interval overlap. If yes, it strolls the whole list, spawning a search if the node exists at the index (i.e. if it is not `None`).

This could be improved, for instance by targeting the exact indices matching the searched interval, but this would require normalizing the interval: Let us say an interval spans two months, such as `(2015-01-15, 2015-02-15)`. When examining January, we would need to normalize the interval to `(2015-01-15, 2015-02-01)`(remember that the last element is excluded), and extract the indices 15, 16... up to 31.

This adds complexity in handling edge cases, and the performance benefit is disputable, compared to strolling a list that can only contain a maximum of 60 elements (number of minutes in an hour). For lack of time, I have not been able to implement the normalizing version to compare the actual performance to the brute force approach performance.

## Implementing the API

The `src/search_engine/search_engine.py` module implements the API by using the search tree just described. It is tested in `tests/unit/src/search_engine/test_search_engine.py`.

It exposes a `get_dataset_from_interval` method that, for a given interval, returns a dictionary associating a query to the number of its occurrences in the given interval (the _dataset_). As such, we create a data structure in memory containing all the results, which is the only way to count them properly.

The implementation for getting the count is implemented in the `get_distinct_count_from_dataset` method, that simply counts the key of the dataset.

The implementation for getting the most popular relies on generating a sorted list of tuples (query, count) from the dataset, sorted on the count, from which we extract the number of elements that we want.

I used the `sorted` method of the standard Python library. If I had to reimplement it, I would implement a standard sorting algorithm, such as quicksort.

## Memory consumption of the search tree

The search tree stores all data in memory. This could be improved in two ways, than I did not have time to explore.

First, rather than storing the queries as string, we could store an index in a dataset file, and fetch the data from the file. We could then use an LRU cache to keep only a fraction of the values in memory. Note that the values in the search tree being of a generic `TDataType` type, we could change this behavior without changing the `search_tree` module itself.

Second, the whole index is in memory (even if we can flush out the values, as discussed just above), which does not scale well. To address this problem, we would need to:

- Add a persistence scheme to the nodes of the search tree, to be able to write them to and read them from disk.
- Have a `Node` class with multiple states, i.e. loaded and unloaded, and implement an LRU cache to only keep a subset of the node in memory. Upon accessing an unloaded node, it is automatically loaded.

Some heuristics would need to be devised to correctly implement this approach. Most notably:

- How do we store data for efficient insertion and retrieval in the file?
- When loading a node, shouldn't we load all of its subnodes immediately, as we know we will stroll them soon? If yes, what depth of subnodes do we load? For instance, when loading a year, do we load all the months or all the days?
