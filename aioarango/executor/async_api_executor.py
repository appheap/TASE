from typing import Callable

from aioarango.enums import APIContextType
from aioarango.models import Request, Response
from aioarango.typings import T
from .base_api_executor import BaseAPIExecutor
from ..connection import Connection


class AsyncAPIExecutor(BaseAPIExecutor):
    """Async API Executor."""

    def __init__(
        self,
        connection: Connection,
        return_result: bool,
    ):
        self.connection = connection
        self.context = APIContextType.ASYNC
        self.return_result = return_result

    async def execute(
        self,
        request: Request,
        response_handler: Callable[[Response], T],
        # ) -> Optional[AsyncJob[T]]: # fixme
    ) -> T:
        """
        Execute an API request asynchronously.

        Parameters
        ----------
        request : Request
            HTTP request
        response_handler : Callable
            HTTP response handler

        Returns
        -------
        AsyncJob[T], optional
            Async job or None if `return_result` parameter was set to False during initialization.
        """
        pass
