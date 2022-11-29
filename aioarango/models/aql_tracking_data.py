from typing import Optional

from pydantic import BaseModel


class AQLTrackingData(BaseModel):
    """
    AQL Tracking Data.

    Attributes
    ----------
    enabled : bool, optional
        If set to `true`, then queries will be tracked. If set to
        `false`, neither queries nor slow queries will be tracked.

    track_slow_queries : bool, optional
        if set to `true`, then slow queries will be tracked
        in the list of slow queries if their runtime exceeds the value set in
        slowQueryThreshold. In order for slow queries to be tracked, the enabled
        property must also be set to true.

    track_bind_vars : bool, optional
        If set to `true`, then bind variables used in queries will be tracked.

    max_slow_queries : int, optional
        Maximum number of slow queries to keep in the list
        of slow queries. If the list of slow queries is full, the oldest entry in
        it will be discarded when additional slow queries occur.

    slow_query_threshold : float, optional
        Threshold value for treating a query as slow. A
        query with a runtime greater or equal to this threshold value will be
        put into the list of slow queries when slow query tracking is enabled.
        The value for slowQueryThreshold is specified in seconds.

    max_query_string_length : int, optional
        Maximum query string length to keep in the
        list of queries. Query strings can have arbitrary lengths, and this property
        can be used to save memory in case very long query strings are used. The
        value is specified in bytes.
    """

    enabled: Optional[bool]
    track_slow_queries: Optional[bool]
    track_bind_vars: Optional[bool]
    max_slow_queries: Optional[int]
    slow_query_threshold: Optional[float]
    max_query_string_length: Optional[int]
    slow_streaming_query_threshold: Optional[float]
