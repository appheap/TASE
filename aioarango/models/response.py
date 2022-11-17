from typing import MutableMapping, Union, Optional

from pydantic import BaseModel, Field

from aioarango.enums import MethodType
from aioarango.errors import error_ref
from aioarango.errors.error_ref import Error, empty_error


class Response(BaseModel):
    method: MethodType
    url: str
    headers: MutableMapping[str, str]
    status_code: int
    # status_text = str
    raw_body: str

    # populated later
    body: Union[str, bool, int, float, list, dict, None] = Field(default=None)
    arango_error: Error = Field(default=empty_error)
    http_error: Error = Field(default=empty_error)
    error_code: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    is_success: Optional[bool] = Field(default=None)

    def lazy_load(
        self,
        body: dict,
    ) -> None:
        http_ok = 200 <= self.status_code < 300
        self.is_success = http_ok and self.error_code is None
        self.body = body

        if body is None or not len(body) or not isinstance(body, dict):
            return

        self.error_code = body.get("errorNum", None)
        self.error_message = body.get("errorMessage", None)
        if not self.is_success:
            self.arango_error = error_ref.get_error(self.error_code)
            self.http_error = error_ref.get_error(self.status_code)
