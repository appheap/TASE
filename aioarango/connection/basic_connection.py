from __future__ import annotations

from typing import Any

import aiohttp

from aioarango.connection import BaseConnection
from aioarango.models import Response, Request


class BasicConnection(BaseConnection):
    """
    Connection to specific ArangoDB database using basic authentication.
    """

    _auth: aiohttp.BasicAuth | None

    class Config:
        underscore_attrs_are_private = True

    def __init__(
        self,
        username: str,
        password: str,
        **data: Any,
    ):
        super().__init__(**data)

        self._username = username
        self.auth = aiohttp.BasicAuth(
            username,
            password,
            encoding="utf-8",
        )

    async def send_request(
        self,
        request: Request,
    ) -> Response:
        return await self.process_request(
            self.host_resolver.get_host_index(),
            request,
            auth=self._auth,
        )
