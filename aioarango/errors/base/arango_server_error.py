from typing import Optional

from aioarango.enums import ErrorSource, MethodType
from aioarango.models import Response, Request
from aioarango.typings import Headers
from .arango_error import ArangoError


class ArangoServerError(ArangoError):
    """Base class for errors originating from ArangoDB server."""

    source: ErrorSource = ErrorSource.SERVER

    def __init__(
        self,
        resp: Response,
        request: Request,
        msg: Optional[str] = None,
    ):
        msg = msg or resp.error_message or str(resp.status_code)  # fixme
        self.error_message: Optional[str] = resp.error_message
        self.error_code: Optional[int] = resp.error_code
        if self.error_code is not None:
            msg = f"[HTTP {resp.status_code}][ERR {self.error_code}] {msg}"
        else:
            msg = f"[HTTP {resp.status_code}] {msg}"
            self.error_code = resp.status_code
        super().__init__(msg)

        self.message: str = msg
        self.url: str = resp.url
        self.response: Response = resp
        self.request: Request = request
        self.http_method: MethodType = resp.method
        self.http_code: int = resp.status_code
        self.http_headers: Headers = resp.headers
