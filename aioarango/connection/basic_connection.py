from __future__ import annotations

from typing import Optional, Sequence, Callable, Any

from aiohttp import ClientSession

from aioarango.connection import BaseConnection
from aioarango.http_client import HTTPClient
from aioarango.models import Response, Request
from aioarango.resolver import HostResolver
from aioarango.typings import Fields


class BasicConnection(BaseConnection):
    """
    Connection to specific ArangoDB database using basic authentication.
    """

    def __init__(
        self,
        hosts: Fields,
        host_resolver: HostResolver,
        sessions: Sequence[ClientSession],
        db_name: str,
        http_client: HTTPClient,
        serializer: Callable[..., str],
        deserializer: Callable[[str], Any],
        username: str,
        password: str,
    ):
        super().__init__(
            hosts,
            host_resolver,
            sessions,
            db_name,
            http_client,
            serializer,
            deserializer,
        )

        self._url_prefixes = [f"{host}/_db/{db_name}" for host in hosts]
        self.host_resolver = host_resolver
        self.sessions = sessions
        self.db_name = db_name
        self.http_client = http_client
        self.serializer = serializer
        self.deserializer = deserializer
        self._username: Optional[str] = None

        from aiohttp import BasicAuth

        self._username = username
        self._auth: Optional[BasicAuth] = BasicAuth(
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
