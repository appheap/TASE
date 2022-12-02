from enum import Enum


class IndexType(Enum):
    UNKNOWN = "unknown"
    PRIMARY = "primary"
    EDGE = "edge"
    GEO = "geo"
    TTL = "ttl"
    HASH = "hash"
    FULL_TEXT = "fulltext"
    INVERTED = "inverted"
    PERSISTENT = "persistent"
    SKIPLIST = "skiplist"
    MULTI_DIMENSIONAL = "zkd"
