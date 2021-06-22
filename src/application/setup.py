from src.search_engine.search_engine import SearchEngine


def setup_application(dataset_path: str, search_engine: SearchEngine) -> None:
    """
    Setup the application, by loading data into the search engine.

    :param dataset_path: Path to load the dataset from.
    :param search_engine: Search engine to load the data into.
    """
    with open(dataset_path, "r") as f:
        search_engine.bulk_load_dataset(f)
