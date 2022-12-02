from pydantic import BaseModel

from aioarango.enums import AQLCacheMode


class AQLCacheProperties(BaseModel):
    """
    AQL query results cache configuration.

    Attributes
    ----------
    mode : AQLCacheMode
        Mode the AQL query results cache operates in. The mode is one of the following values: `off`, `on` or `demand`.
    max_results : int
        Maximum number of query results that will be stored per database-specific cache.
    max_results_size : int
        Maximum cumulated size of query results that will be stored per database-specific cache.
    max_entry_size : int
        Maximum individual result size of queries that will be stored per database-specific cache.
    include_system: bool
        Whether results of queries that involve system collections will be stored in the query results cache or not.
    """

    mode: AQLCacheMode
    max_results: int
    max_results_size: int
    max_entry_size: int
    include_system: bool
