from typing import Optional

from aioarango.enums import ErrorSource, MethodType
from aioarango.errors.base.arango_error import ArangoError
from aioarango.typings import Headers


class ArangoClientError(ArangoError):
    """
    Base class for errors originating from aioarango client.
    """

    source: ErrorSource = ErrorSource.CLIENT  # source of the error

    def __init__(
        self,
        msg: str,
    ) -> None:
        super(ArangoClientError, self).__init__(msg)

        from aioarango.models import Response
        from aioarango.models import Request

        self.message: str = msg
        self.error_message: Optional[str] = None
        self.error_code: Optional[int] = None
        self.url: Optional[str] = None
        self.response: Optional[Response] = None
        self.request: Optional[Request] = None
        self.http_method: Optional[MethodType] = None
        self.http_code: Optional[int] = None
        self.http_headers: Optional[Headers] = None
