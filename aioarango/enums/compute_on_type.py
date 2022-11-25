from enum import Enum


class ComputeOnType(Enum):
    """
    Define on which write operations the value shall be computed.
    """

    INSERT = "insert"
    UPDATE = "update"
    REPLACE = "replace"
