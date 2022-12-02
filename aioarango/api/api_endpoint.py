from typing import Optional, Callable

from aioarango.connection import Connection
from aioarango.enums import APIContextType
from aioarango.executor import API_Executor
from aioarango.models import Request, Response
from aioarango.typings import T, Result


class Endpoint:
    __slots__ = [
        "_connection",
        "_executor",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
    ):
        self._connection = connection
        self._executor = executor

    @property
    def db_name(self) -> str:
        """
        Return the name of the current database.

        Returns
        -------
        str
            Database name

        """
        return self._connection.db_name

    @property
    def username(self) -> Optional[str]:
        """
        Return the username.

        Returns
        -------
        str
            Username

        """
        return self._connection.username

    @property
    def context(self) -> APIContextType:
        """
        Return the API execution context.

        Returns
        -------
        APIContextType
            API execution context

        """
        return self._executor.context

    async def execute(
        self,
        request: Request,
        response_handler: Callable[[Response], T],
    ) -> Result[T]:
        """
        Execute an API

        Parameters
        ----------
        request : Request
            HTTP request
        response_handler : callable
            HTTP response handler

        Returns
        -------
        Result
            API execution result

        """
        return await self._executor.execute(
            request,
            response_handler,
        )
