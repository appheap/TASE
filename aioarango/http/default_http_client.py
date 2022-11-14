from typing import Optional, MutableMapping, Union

import aiohttp
from pydantic import Field
from requests_toolbelt import MultipartEncoder

from aioarango.enums import MethodType
from aioarango.http import BaseHTTPClient
from aioarango.models import Response
from aioarango.typings import Headers


class DefaultHTTPClient(BaseHTTPClient):
    """Default HTTP client implementation."""

    request_timeout: int = Field(default=60)

    def create_session(
        self,
        host: str,
    ) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def send_request(
        self,
        session: aiohttp.ClientSession,
        method_type: MethodType,
        url: str,
        headers: Optional[Headers] = None,
        params: Optional[MutableMapping[str, str]] = None,
        data: Union[str, MultipartEncoder, None] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
    ) -> Response:
        raw_response = await session.request(
            method=method_type.value,
            url=url,
            params=params,
            data=data,
            headers=headers,
            auth=auth,
            timeout=self.request_timeout,
        )

        return Response(
            method=method_type,
            url=url,
            headers=headers,
            status_code=raw_response.status,
            raw_body=await raw_response.text(),
        )
