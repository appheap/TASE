from __future__ import annotations

from typing import MutableMapping

from pydantic import BaseModel, Field

from aioarango.enums import MethodType


class Response(BaseModel):
    method: MethodType
    url: str
    headers: MutableMapping[str, str]
    status_code: int
    # status_text = str
    raw_body: str

    # populated later
    body: str | bool | int | float | list | dict | None = Field(default=None)
    error_code: int | None = Field(default=None)
    error_message: str | None = Field(default=None)
    is_success: bool | None = Field(default=None)
