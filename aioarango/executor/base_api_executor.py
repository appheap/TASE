from abc import abstractmethod
from typing import Callable

from aioarango.models import Request, Response
from aioarango.typings import T


class BaseAPIExecutor:
    @abstractmethod
    async def execute(
        self,
        request: Request,
        response_handler: Callable[[Response], T],
    ) -> T:
        """
        Execute an API request and return the result.

        Parameters
        ----------
        request : Request
            HTTP request
        response_handler : Callable
            HTTP response handler

        Returns
        -------
        T
            API execution result
        """
        raise NotImplementedError
