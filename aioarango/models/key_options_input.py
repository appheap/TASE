from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from aioarango.enums import KeyOptionsType
from aioarango.typings import Json


class KeyOptionsInput(BaseModel):
    type: KeyOptionsType
    """
    specifies the type of the key generator.
    """

    allow_user_keys: bool
    """
     if set to `true`, then it is allowed to supply own key values in the
    `_key` attribute of a document. If set to `false`, then the key generator
    will solely be responsible for generating keys and supplying own key values
    in the _key attribute of documents is considered an error.
    """

    increment: Optional[int]
    """
     increment value for `autoincrement` key generator. Not used for other key generator types.
    """

    offset: Optional[int]
    """
    Initial offset value for `autoincrement` key generator. Not used for other key generator types.
    """

    def parse_for_arangodb(self) -> Json:
        """
        Parse the Key options object for using in ArangoDB API.

        Returns
        -------
        Json
            A dictionary containing the values of the key options object.

        """
        key_options_d: Json = {
            "type": self.type.value,
            "allowUserKeys": self.allow_user_keys,
        }

        if self.increment is not None:
            key_options_d["increment"] = self.increment
        if self.offset is not None:
            key_options_d["offset"] = self.offset

        return key_options_d
