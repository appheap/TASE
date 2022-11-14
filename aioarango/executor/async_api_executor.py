from typing import Callable

from aioarango.enums import APIContextType
from aioarango.executor import BaseAPIExecutor
from aioarango.models import Request, Response
from aioarango.typings import T


class AsyncAPIExecutor(BaseAPIExecutor):
    """Async API Executor."""

    context = APIContextType.ASYNC
    return_result: bool

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
