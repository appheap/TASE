from typing import Optional, TYPE_CHECKING

from aioarango.enums import ErrorSource, MethodType
from aioarango.errors import error_ref
from aioarango.errors.base.arango_error import ArangoError
from aioarango.typings import Headers

if TYPE_CHECKING:
    from aioarango.models import Response, Request  # fixme


class ArangoServerError(ArangoError):
    """Base class for errors originating from ArangoDB server."""

    source: ErrorSource = ErrorSource.SERVER

    def __init__(
        self,
        response: "Response",
        request: "Request",
        msg: Optional[str] = None,
    ):
        msg = msg or response.error_message or str(response.status_code)  # fixme

        self.error_message: Optional[str] = response.error_message
        self.error_code: Optional[int] = response.error_code
        self.url: str = response.url
        self.response: Response = response
        self.request: Request = request
        self.http_method: MethodType = response.method
        self.http_code: int = response.status_code
        self.http_headers: Headers = response.headers

        self.arango_error: error_ref.Error = error_ref.get_error(self.error_code)
        self.http_error: error_ref.Error = error_ref.get_error(self.http_code)

        if self.error_code is not None:
            msg = (
                f"[HTTP {response.status_code}][ERR {self.error_code} : `{self.arango_error.title}` -> `{self.arango_error.description}`] ArangoDB says: {msg}"
            )
        else:
            from aioarango.errors import ErrorType

            if self.http_error.type in (ErrorType.EMPTY_PLACEHOLDER, ErrorType.UNKNOWN):
                msg = f"[HTTP {response.status_code}] ArangoDB says: {msg}`"
            else:
                msg = f"[HTTP {response.status_code} : `{self.http_error.title}` -> `{self.http_error.description}`] ArangoDB says: {msg}"
            self.error_code = response.status_code
        super().__init__(msg)

        self.message: str = msg
