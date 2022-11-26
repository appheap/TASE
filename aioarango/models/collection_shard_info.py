from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel


class CollectionShardInfo(BaseModel):
    shard_id: str
    responsible_servers: Optional[List[str]]

    @classmethod
    def parse_from_dict(cls,d:dict)->Optional[CollectionShardInfo]:
        if d is None or not len(d):
            return None

        return