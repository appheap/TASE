from typing import Callable

from aioarango.connection import Connection
from aioarango.enums import APIContextType
from aioarango.executor import BaseAPIExecutor
from aioarango.models import Request, Response
from aioarango.typings import T


class DefaultAPIExecutor(BaseAPIExecutor):
    """Default API executor."""

    def __init__(
        self,
        connection: Connection,
    ):
        self.connection = connection
        self.context = APIContextType.DEFAULT

    async def execute(
        self,
        request: Request,
        response_handler: Callable[[Response], T],
    ) -> T:
        return response_handler(await self.connection.send_request(request))
