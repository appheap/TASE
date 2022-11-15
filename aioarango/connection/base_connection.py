from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Sequence, Callable, Any, Optional, Set, Union

from aiohttp import ClientSession, BasicAuth
from requests_toolbelt import MultipartEncoder

from aioarango.enums import MethodType
from aioarango.http_client import HTTPClient
from aioarango.models import Response, Request
from aioarango.resolver import HostResolver
from aioarango.typings import Fields, Json


class BaseConnection:
    """Base connection to a specific ArangoDB database."""

    def __init__(
        self,
        hosts: Fields,
        host_resolver: HostResolver,
        sessions: Sequence[ClientSession],
        db_name: str,
        http_client: HTTPClient,
        serializer: Callable[..., str],
        deserializer: Callable[[str], Any],
    ):

        self._url_prefixes = [f"{host}/_db/{db_name}" for host in hosts]
        self.host_resolver = host_resolver
        self.sessions = sessions
        self.db_name = db_name
        self.http_client = http_client
        self.serializer = serializer
        self.deserializer = deserializer
        self._username: Optional[str] = None

    @property
    def username(self) -> str | None:
        """
        Return the username.

        Returns
        -------
        str, optional
            Username

        """
        return self._username

    def serialize(
        self,
        obj: Any,
    ) -> str:
        """
        Serialize the given object.

        Parameters
        ----------
        obj : Any
            JSON object to serialize

        Returns
        -------
        str
            Serialized string

        """
        return self.serializer(obj)

    def deserialize(
        self,
        string: str,
    ) -> Any:
        """
        Deserialize the string and return the object.

        Parameters
        ----------
        string : str
            String to deserialize

        Returns
        -------
        Any
            Deserialized object

        """
        try:
            return self.deserializer(string)
        except (ValueError, TypeError):
            return string

    def prep_response(
        self,
        response: Response,
        deserialize: bool = True,
    ) -> Response:
        """
        Populate the response with details and return it.

        Parameters
        ----------
        response : Response
            HTTP response
        deserialize : bool, default : True
            Whether to deserialize the response body or not. default set to True.

        Returns
        -------
        Response
            HTTP response

        """
        if deserialize:
            response.body = self.deserialize(response.raw_body)
            if isinstance(response.body, dict):
                response.error_code = response.body.get("errorNum")
                response.error_message = response.body.get("errorMessage")
                if response.status_code == response.error_code == 503:
                    raise ConnectionError  # Fallback to another host
        else:
            response.body = response.raw_body

        http_ok = 200 <= response.status_code < 300
        response.is_success = http_ok and response.error_code is None
        return response

    async def process_request(
        self,
        host_index: int,
        request: Request,
        auth: Optional[BasicAuth] = None,
    ) -> Response:
        """
        Execute a request until a valid response has been returned.

        Parameters
        ----------
        host_index : int
            The index of the first host to try
        request : Request
            HTTP request
        auth : aiohttp.BasicAuth, optional
            Username and password

        Returns
        -------

        """
        tries = 0
        indexes_to_filter: Set[int] = set()
        while tries < self.host_resolver.max_tries:
            try:
                resp = await self.http_client.send_request(
                    session=self.sessions[host_index],
                    method_type=request.method_type,
                    url=self._url_prefixes[host_index] + request.endpoint,
                    params=request.params,
                    data=self.normalize_data(request.data),
                    headers=request.headers,
                    auth=auth,
                )

                return self.prep_response(resp, request.deserialize)
            except ConnectionError:
                url = self._url_prefixes[host_index] + request.endpoint
                logging.debug(f"ConnectionError: {url}")

                if len(indexes_to_filter) == self.host_resolver.host_count - 1:
                    indexes_to_filter.clear()
                indexes_to_filter.add(host_index)

                host_index = self.host_resolver.get_host_index(indexes_to_filter)
                tries += 1

        raise ConnectionAbortedError(f"Can't connect to host(s) within limit ({self.host_resolver.max_tries})")

    def prep_bulk_err_response(
        self,
        parent_response: Response,
        body: Json,
    ) -> Response:
        """
        Build and return a bulk error response.

        Parameters
        ----------
        parent_response : Response
            Parent response
        body : Json
            Error response body

        Returns
        -------
        Response
            Child bulk error response.

        """
        resp = Response(
            method=parent_response.method,
            url=parent_response.url,
            headers=parent_response.headers,
            status_code=parent_response.status_code,
            # status_text=parent_response.status_text,
            raw_body=self.serialize(body),
        )
        resp.body = body
        resp.error_code = body["errorNum"]
        resp.error_message = body["errorMessage"]
        resp.is_success = False
        return resp

    def normalize_data(
        self,
        data: Any,
    ) -> Union[str, MultipartEncoder, None]:
        """
        Normalize request data.

        Parameters
        ----------
        data : Any
            Request data

        Returns
        -------
        str | MultipartEncoder | None
            Normalized data

        """
        if data is None:
            return None
        elif isinstance(data, (str, MultipartEncoder)):
            return data
        else:
            return self.serialize(data)

    async def ping(self) -> int:
        """
        Ping the next host to check if connection is established.

        Returns
        -------
        int
            Response status code

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/collection",
        )
        resp = await self.send_request(request)
        if resp.status_code in {401, 403}:
            # raise ServerConnectionError("bad username and/or password") # fixme
            raise Exception("bad username and/or password")
        if not resp.is_success:  # pragma: no cover
            # raise ServerConnectionError(resp.error_message or "bad server response") # fixme
            raise Exception(resp.error_message or "bad server response")
        return resp.status_code

    @abstractmethod
    async def send_request(
        self,
        request: Request,
    ) -> Response:
        """
        Send an HTTP request to ArangoDB server.

        Parameters
        ----------
        request : Request
            HTTP request

        Returns
        -------
        Response
            HTTP response
        """
        raise NotImplementedError
