from dataclasses import dataclass
from typing import Optional, List

import pyrogram


@dataclass
class Restriction:
    platform: Optional['str']
    reason: Optional['str']
    text: Optional['str']

    def parse_for_graph(self) -> dict:
        return {
            'platform': self.platform,
            'reason': self.reason,
            'text': self.reason,
        }

    @staticmethod
    def parse_from_restriction(restriction: 'pyrogram.types.Restriction') -> Optional['Restriction']:
        if restriction is None:
            return None

        return Restriction(
            platform=restriction.platform,
            reason=restriction.reason,
            text=restriction.text,
        )

    @staticmethod
    def parse_from_restrictions(restrictions: List['pyrogram.types.Restriction']) -> Optional[List['Restriction']]:
        if restrictions is None:
            return None

        l = []
        for restriction in restrictions:
            l.append(Restriction.parse_from_restriction(restriction))
        return l

    @staticmethod
    def parse_all_for_graph(restrictions: List['Restriction']) -> Optional[List[dict]]:
        if restrictions is None or not len(restrictions):
            return None
        l = []
        for restriction in restrictions:
            l.append(restriction.parse_for_graph())
        return l
