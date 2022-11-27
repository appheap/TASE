from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel


class CollectionShardInfo(BaseModel):
    shard_id: str
    responsible_servers: Optional[List[str]]
