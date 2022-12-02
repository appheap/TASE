from typing import Optional, MutableMapping

from pydantic import BaseModel

from aioarango.enums import AQLQueryState


class AQLQuery(BaseModel):
    """
    Represents an AQL query.

    Attributes
    ----------
    id: str
        ID of the query.
    database: str
        Name of the database the query runs in.
    user: str
        Name of the user that started the query.
    query: str
        Query string (potentially truncated).
    bind_vars: MutableMapping, optional
        Bind parameter values used by the query.
    started: str, optional
        Date and time when the query was started.
    runtime: float, optional
        Query's total run time (in seconds).
    state: AQLQueryState, optional
        Query's current execution state (will always be "finished" for the list of slow queries).
    stream: bool, optional
        Whether the query uses a streaming cursor or not.

    """

    id: str
    query: str
    database: Optional[str]
    bind_vars: Optional[MutableMapping[str, str]]
    runtime: Optional[float]
    started: Optional[str]
    state: Optional[AQLQueryState]
    stream: Optional[bool]
    user: Optional[str]
