from abc import ABC, abstractmethod
from typing import Optional, MutableMapping, Union, Any

from aiohttp import ClientSession, BasicAuth

from aioarango.enums import MethodType
from aioarango.models import Response
from aioarango.typings import Headers


class BaseHTTPClient(ABC):
    """Abstract base class for HTTP clients."""

    @abstractmethod
    def create_session(
        self,
        host: str,
    ) -> ClientSession:
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
        session: ClientSession,
        method_type: MethodType,
        url: str,
        headers: Optional[Headers] = None,
        params: Optional[MutableMapping[str, str]] = None,
        data: Union[str, Any, None] = None,
        auth: Optional[BasicAuth] = None,
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
        data :str or Any, optional
            Request payload
        auth : aiohttp.BasicAuth
            Username and password

        Returns
        -------
        Response
            HTTP Response
        """
        raise NotImplementedError
