from __future__ import annotations

from json import dumps, loads
from typing import ClassVar, Callable, Union, Sequence, List

import aiohttp
from arango.resolver import RandomHostResolver, SingleHostResolver, RoundRobinHostResolver, HostResolver
from pydantic import BaseModel, Field, validator

from aioarango.enums import HostResolverType
from aioarango.http import HTTPClient, DefaultHTTPClient
from aioarango.methods import Methods


class ArangoClient(
    BaseModel,
    Methods,
):
    version: ClassVar[str] = "0.1"

    hosts: Union[str, Sequence[str]] = Field(default="http://127.0.0.1:8529")
    host_resolver_type: HostResolverType = Field(default=HostResolverType.ROUND_ROBIN)
    http_client: HTTPClient | None
    resolver_max_tries: int | None
    serializer: Callable[..., str] = Field(default=lambda x: dumps(x))
    deserializer: Callable[[str], str] = Field(default=lambda x: loads(x))
    request_timeout: int = Field(default=60)

    _host_resolver: HostResolver | None
    _sessions: List[aiohttp.ClientSession] | None

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

        host_count = len(self.hosts)

        if host_count == 1:
            self._host_resolver = SingleHostResolver(1, self.resolver_max_tries)
        elif self.host_resolver_type == HostResolverType.RANDOM:
            self._host_resolver = RandomHostResolver(host_count, self.resolver_max_tries)
        else:
            self._host_resolver = RoundRobinHostResolver(host_count, self.resolver_max_tries)

        # Initializes the http client
        self.http_client = self.http_client or DefaultHTTPClient()

        self._sessions = [self.http_client.create_session(host) for host in self.hosts]

    @validator("hosts")
    def validate_hosts(cls, value):
        if isinstance(value, str):
            return [host.strip("/") for host in value.split(",")]
        else:
            return [host.strip("/") for host in value]

    def __repr__(self) -> str:
        return f"<ArangoClient {','.join(self.hosts)}>"

    def close(self):
        """
        Close HTTP sessions.
        """
        for session in self.sessions:
            session.close()

    @property
    def sessions(self) -> List[aiohttp.ClientSession]:
        return self._sessions
