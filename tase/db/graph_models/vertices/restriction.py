from typing import Optional, List

import pyrogram
from pydantic import BaseModel


class Restriction(BaseModel):
    platform: Optional["str"]
    reason: Optional["str"]
    text: Optional["str"]

    @staticmethod
    def parse_from_restriction(
        restriction: "pyrogram.types.Restriction",
    ) -> Optional["Restriction"]:
        if restriction is None:
            return None

        return Restriction(
            platform=restriction.platform,
            reason=restriction.reason,
            text=restriction.text,
        )

    @staticmethod
    def parse_from_restrictions(
        restrictions: List["pyrogram.types.Restriction"],
    ) -> Optional[List["Restriction"]]:
        if restrictions is None:
            return None

        l = []
        for restriction in restrictions:
            l.append(Restriction.parse_from_restriction(restriction))
        return l
