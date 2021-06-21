from enum import Enum

class Levels(Enum):
    """
        All possible levels of a node in the tree.
    """
    ROOT=0
    YEAR=1
    MONTH=2
    DAY=3
    HOUR=4
    MINUTE=5