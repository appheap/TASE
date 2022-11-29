from enum import Enum


class AQLCacheMode(Enum):
    """
    Mode the AQL query results cache operates in.
    """

    ON = "on"
    OFF = "off"
    DEMAND = "demand"
