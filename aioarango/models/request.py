from typing import Optional, Dict, Any, MutableMapping

from pydantic import BaseModel, validator

from aioarango.enums import MethodType
from aioarango.typings import Headers, Params, Fields


class Request(BaseModel):
    """
    HTTP request.
    """

    method_type: MethodType
    endpoint: str  # API endpoint.
    headers: Optional[Headers]  # Request headers.
    params: Optional[Params]  # URL parameters.
    data: Optional[Dict[str, Any]]  # Request payload.
    deserialize: bool = True  # Whether the response body can be deserialized.

    read: Optional[Fields] = None  # Name(s) of collections read during transaction.
    write: Optional[Fields] = None  # Name(s) of collections written to during transaction with shared access.
    exclusive: Optional[Fields] = None  # Name(s) of collections written to during transaction with exclusive access.

    class Config:
        arbitrary_types_allowed = True

    @validator("headers")
    def norm_headers(cls, value):
        return cls.normalize_headers(value)

    @validator("params")
    def norm_params(cls, value):
        return cls.normalize_params(value)

    from typing import Optional, MutableMapping

    from aioarango.typings import Headers, Params

    @classmethod
    def normalize_headers(
        cls,
        headers: Optional[Headers],
    ) -> Headers:
        normalized_headers: Headers = {
            "charset": "utf-8",
            "content-type": "application/json",
        }
        if headers is not None:
            for key, value in headers.items():
                normalized_headers[key.lower()] = value

        return normalized_headers

    @classmethod
    def normalize_params(
        cls,
        params: Optional[Params],
    ) -> MutableMapping[str, str]:
        normalized_params: MutableMapping[str, str] = {}

        if params is not None:
            for key, value in params.items():
                if isinstance(value, bool):
                    value = int(value)

                normalized_params[key] = str(value)

        return normalized_params
