from typing import Optional, Dict, Any

from pydantic import BaseModel, validator

from aioarango.enums import MethodType
from aioarango.typings import Fields
from aioarango.utils import normalize_headers, normalize_params


class Request(BaseModel):
    method: MethodType
    endpoint: str
    headers: Optional[Fields]
    params: Optional[Fields]
    data: Optional[Dict[str, Any]]
    deserialize: bool = True

    @validator("headers")
    def norm_headers(cls, value):
        return normalize_headers(value)

    @validator("params")
    def norm_params(cls, value):
        return normalize_params(value)
