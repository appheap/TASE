from abc import ABC, abstractmethod
from typing import Optional, MutableMapping, Union, Tuple

import aiohttp
from pydantic import BaseModel
from requests_toolbelt import MultipartEncoder

from aioarango.enums import MethodType
from aioarango.models import Response
from aioarango.typings import Headers


class BaseHTTPClient(BaseModel, ABC):
    """Abstract base class for HTTP clients."""

    @abstractmethod
    def create_session(
        self,
        host: str,
    ) -> aiohttp.ClientSession:
        """
        Return a new aiohttp client session given the host URL.

        This method must be overridden by the user.

        Parameters
        ----------
        host : str
            ArangoDB host URL

        Returns
        -------
        aiohttp.ClientSession
            aiohttp client session object
        """
        raise NotImplementedError

    @abstractmethod
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
        """
        Send an HTTP request.

        This method must be overridden by the user.

        Parameters
        ----------
        session : aiohttp.ClientSession
            aiohttp client session object
        method_type : MethodType
            HTTP method type
        url : str
            Request URL
        headers : Headers, optional
            Request headers
        params : MutableMapping[str, str], optional
            URL (query) parameters
        data :str or MultipartEncoder, optional
            Request payload
        auth : aiohttp.BasicAuth
            Username and password

        Returns
        -------
        Response
            HTTP Response
        """
        raise NotImplementedError
