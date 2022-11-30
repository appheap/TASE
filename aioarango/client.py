from __future__ import annotations

from json import dumps, loads
from typing import Callable, Union, Sequence, List, Optional

import aiohttp

from aioarango.api import StandardDatabase
from aioarango.connection import BasicConnection
from aioarango.enums import HostResolverType, ConnectionType
from aioarango.errors import ServerConnectionError
from aioarango.http_client import HTTPClient, DefaultHTTPClient
from aioarango.resolver import HostResolver, SingleHostResolver, RandomHostResolver, RoundRobinHostResolver


class ArangoClient:
    def __init__(
        self,
        hosts: Union[str, Sequence[str]] = "http://127.0.0.1:8529",
        host_resolver_type: HostResolverType = HostResolverType.ROUND_ROBIN,
        resolver_max_tries: Optional[int] = None,
        http_client: Optional[HTTPClient] = None,
        serializer: Callable[..., str] = lambda x: dumps(x),
        deserializer: Callable[[str], str] = lambda x: loads(x),
        request_timeout: int = 60,
    ):
        if isinstance(hosts, str):
            self.hosts = [host.strip("/") for host in hosts.split(",")]
        else:
            self.hosts = [host.strip("/") for host in hosts]

        self.host_resolver_type = host_resolver_type
        self.serializer = serializer
        self.deserializer = deserializer
        self.request_timeout = request_timeout

        # Initializes the http_client client
        self.http_client: Optional[HTTPClient] = http_client or DefaultHTTPClient()
        self._sessions: List[aiohttp.ClientSession] = [
            self.http_client.create_session(
                host,
                request_timeout,
            )
            for host in self.hosts
        ]

        self._host_resolver: Optional[HostResolver] = None
        host_count = len(self.hosts)
        if host_count == 1:
            self._host_resolver = SingleHostResolver(
                host_count=1,
                max_tries=resolver_max_tries,
            )
        elif self.host_resolver_type == HostResolverType.RANDOM:
            self._host_resolver = RandomHostResolver(
                host_count=host_count,
                max_tries=resolver_max_tries,
            )
        else:
            self._host_resolver = RoundRobinHostResolver(
                host_count=host_count,
                max_tries=resolver_max_tries,
            )

    def __repr__(self) -> str:
        return f"<ArangoClient {','.join(self.hosts)}>"

    @property
    def host_resolver(self) -> Optional[HostResolver]:
        return self._host_resolver

    @property
    def sessions(self) -> List[aiohttp.ClientSession]:
        return self._sessions

    def close(self):
        """
        Close HTTP sessions.
        """
        for session in self.sessions:
            session.close()

    async def db(
        self,
        name: str = "_system",
        username: str = "root",
        password: str = "",
        connection_type: ConnectionType = ConnectionType.BASIC,
        verify: bool = True,
        superuser_token: Optional[str] = None,
    ) -> StandardDatabase:
        if connection_type == ConnectionType.BASIC:
            connection = BasicConnection(
                hosts=self.hosts,
                host_resolver=self.host_resolver,
                sessions=self.sessions,
                http_client=self.http_client,
                db_name=name,
                serializer=self.serializer,
                deserializer=self.deserializer,
                username=username,
                password=password,
            )
        else:
            raise NotImplementedError  # fixme

        if verify:
            try:
                await connection.ping()
            except ServerConnectionError as err:
                raise err
            except Exception as err:
                raise ServerConnectionError(f"bad connection: {err}")

        return StandardDatabase(connection=connection)
