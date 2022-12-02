from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from aioarango.enums import KeyOptionsType


class KeyOptions(BaseModel):
    type: KeyOptionsType

    allow_user_keys: bool
    """
     if set to `true`, then it is allowed to supply own key values in the
    `_key` attribute of a document. If set to `false`, then the key generator
    will solely be responsible for generating keys and supplying own key values
    in the _key attribute of documents is considered an error.
    """

    last_value: Optional[int]

    @classmethod
    def parse_from_dict(cls, d: dict) -> Optional[KeyOptions]:
        if d is None or not len(d):
            return None

        return KeyOptions(
            type=d["type"],
            allow_user_keys=d["allowUserKeys"],
            last_value=d["lastValue"],
        )
