from typing import Optional, MutableMapping

from aioarango.typings import Headers, Params


def normalize_headers(headers: Optional[Headers]) -> Headers:
    normalized_headers: Headers = {
        "charset": "utf-8",
        "content-type": "application/json",
    }
    if headers is not None:
        for key, value in headers.items():
            normalized_headers[key.lower()] = value

    return normalized_headers


def normalize_params(params: Optional[Params]) -> MutableMapping[str, str]:
    normalized_params: MutableMapping[str, str] = {}

    if params is not None:
        for key, value in params.items():
            if isinstance(value, bool):
                value = int(value)

            normalized_params[key] = str(value)

    return normalized_params
