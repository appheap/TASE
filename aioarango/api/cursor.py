from __future__ import annotations

from collections import deque
from types import TracebackType
from typing import Any, Deque, Optional, Sequence, Type

from ..api_methods import CursorsMethods
from ..connection import Connection
from ..errors import CursorCountError, CursorEmptyError, CursorStateError, ArangoServerError
from ..executor import API_Executor
from ..models import CursorStats
from ..typings import Json


class Cursor:
    """
    Cursor API wrapper.

    Cursors fetch query results from ArangoDB server in batches. Cursor objects
    are *stateful* as they store the fetched items in-memory. They must not be
    shared across threads without proper locking mechanism.

    """

    __slots__ = [
        "_api",
        "_type",
        "_id",
        "_count",
        "_cached",
        "_stats",
        "_profile",
        "_warnings",
        "_has_more",
        "_batch",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
        init_data: Json,
        cursor_type: str = "cursor",
    ):
        self._api = CursorsMethods(connection, executor)

        self._type = cursor_type
        self._batch: Deque[Any] = deque()
        self._id = None
        self._count: Optional[int] = None
        self._cached = None
        self._stats: Optional[CursorStats] = None
        self._profile = None
        self._warnings = None
        self._update(init_data)

    def _update(
        self,
        data: Json,
    ) -> Json:
        """
        Update the cursor using data from ArangoDB server.

        Parameters
        ----------
        data : Json
            Cursor data from ArangoDB server (e.g. results).

        Returns
        -------
        Json
            Cursor data from ArangoDB server (e.g. results), but slightly modified.

        """
        result: Json = {}

        if "id" in data:
            self._id = data["id"]
            result["id"] = data["id"]
        if "count" in data:
            self._count = data["count"]
            result["count"] = data["count"]
        if "cached" in data:
            self._cached = data["cached"]
            result["cached"] = data["cached"]

        self._has_more = bool(data["hasMore"])
        result["has_more"] = data["hasMore"]

        self._batch.extend(data["result"])
        result["batch"] = data["result"]

        if "extra" in data:
            extra = data["extra"]

            if "profile" in extra:
                self._profile = extra["profile"]
                result["profile"] = extra["profile"]

            if "warnings" in extra:
                self._warnings = extra["warnings"]
                result["warnings"] = extra["warnings"]

            if "stats" in extra:
                self._stats = CursorStats.parse_from_dict(extra["stats"])
                result["statistics"] = self._stats

        return result

    def __aiter__(self) -> Cursor:
        return self

    async def __anext__(self) -> Any:
        return await self.next()

    async def __aenter__(self) -> Cursor:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        return await self.close(ignore_missing=True)

    def __len__(self) -> int:
        """
        Return the number of documents in the result.

        Returns
        -------
        int
            Number of documents in the result.

        Raises
        ------
        aioarango.errors.CursorCountError
            If cursor count is not enabled.

        """
        if self._count is None:
            raise CursorCountError("cursor count not enable")

        return self._count

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def type(self) -> Optional[str]:
        return self._type

    def empty(self) -> bool:
        """
        Check if the current batch is empty.

        Returns
        -------
        bool
            True if current batch is empty, False otherwise.

        """
        return len(self._batch) == 0

    def has_more(self) -> Optional[bool]:
        """
        Check if more results are available on the server.

        Returns
        -------
        bool, optional
            `True` if more results are available on the server.
        """
        return self._has_more

    def count(self) -> Optional[int]:
        """
        Return the total number of documents in the entire result set.

        Returns
        -------
        int, optional
            Total number of documents, or None if the count option was not enabled during cursor initialization.

        """
        return self._count

    def cached(self) -> Optional[bool]:
        """
        Check if the results are cached.

        Returns
        -------
        bool, optional
            True if results are cached.

        """
        return self._cached

    def statistics(self) -> Optional[CursorStats]:
        """
        Return cursor statistics.

        Returns
        -------
        CursorStats, optional
            Cursor statistics.
        """
        return self._stats

    def profile(self) -> Optional[Json]:
        """
        Return cursor performance profile.

        Returns
        -------
        Json, optional
            Cursor performance profile.
        """
        return self._profile

    def warnings(self) -> Optional[Sequence[Json]]:
        """
        Return any warnings from the query execution.

        Returns
        -------
        list, optional
            Warnings, or None if there are none.

        """
        return self._warnings

    async def next(self) -> Any:
        """
        Pop the next item from the current batch.

        Notes
        -----
        If current batch is empty/depleted, an API request is automatically
        sent to ArangoDB server to fetch the next batch and update the cursor.


        Returns
        -------
        Any
            Next item in current batch.

        Raises
        ------
        StopAsyncIteration
            If the result set is depleted.
        ValueError
            If the cursor ID or cursor type are not set. (This must not be raised, because it is checked beforehand!)
        aioarango.errors.client.CursorStateError
            If cursor ID is not set.
        aioarango.errors.ArangoServerError
            If batch retrieval fails.

        """
        if self.empty():
            if not self.has_more():
                raise StopAsyncIteration

            await self.fetch()

        return self.pop()

    def pop(self) -> Any:
        """
        Pop the next item from current batch.

        If current batch is empty/depleted, an exception is raised. You must
        call :meth:`aioarango.api.cursor.Cursor.fetch` to manually fetch the next
        batch from server.

        Returns
        -------
        Any
            Next item in current batch.

        Raises
        ------
        aioarango.errors.client.CursorEmptyError
            If current batch is empty.

        """
        if len(self._batch) == 0:
            raise CursorEmptyError("current batch is empty")

        return self._batch.popleft()

    async def fetch(self) -> Json:
        """
        Fetch the next batch from server and update the cursor.

        Returns
        -------
        Json
            New batch details.

        Raises
        ------
        ValueError
            If the cursor ID or cursor type are not set. (This must not be raised, because it is checked beforehand!)
        aioarango.errors.client.CursorStateError
            If cursor ID is not set.
        aioarango.errors.ArangoServerError
            If batch retrieval fails.
        """
        if self._id is None:
            raise CursorStateError("cursor ID not set")

        response = await self._api.read_cursor_next_batch(self._id, self._type)

        return self._update(response)

    async def close(
        self,
        ignore_missing: bool = False,
    ) -> Optional[bool]:
        """
        Close the cursor and free any server resources tied to it.

        Parameters
        ----------
        ignore_missing : bool, default : False
            Do not raise exception on missing cursors.

        Returns
        -------
        bool, optional
            `True` if cursor was closed successfully, `False` if cursor was
            missing on the server and **ignore_missing** was set to `True`, `None`
            if there are no cursors to close server-side (e.g. result set is
            smaller than the batch size).

        Raises
        ------
        ValueError
            If the cursor ID or cursor type are not set.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if self._id is None:
            return None

        try:
            response = await self._api.delete_cursor(self._id, self._type)
        except ArangoServerError as e:
            if e.response.status_code == 404 and ignore_missing:
                return False
            else:
                raise e
        else:
            return response
