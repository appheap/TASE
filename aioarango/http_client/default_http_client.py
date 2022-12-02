from typing import Optional, MutableMapping, Union, Any

import aiohttp

from aioarango.enums import MethodType
from aioarango.http_client import BaseHTTPClient
from aioarango.models import Response
from aioarango.typings import Headers


class DefaultHTTPClient(BaseHTTPClient):
    """Default HTTP client implementation."""

    def create_session(
        self,
        host: str,
        request_timeout: int = 60,
    ) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=request_timeout))

    async def send_request(
        self,
        session: aiohttp.ClientSession,
        method_type: MethodType,
        url: str,
        headers: Optional[Headers] = None,
        params: Optional[MutableMapping[str, str]] = None,
        data: Union[str, Any, None] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
    ) -> Response:
        raw_response = await session.request(
            method=str(method_type.value),
            url=url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
        )

        return Response(
            method=method_type,
            url=url,
            headers=dict(raw_response.headers),
            status_code=raw_response.status,
            raw_body=await raw_response.text(),
        )
