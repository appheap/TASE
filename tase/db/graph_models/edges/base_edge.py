from dataclasses import dataclass
from typing import Optional

from ..vertices import BaseVertex


@dataclass
class BaseEdge:
    _collection_edge_name = 'base_edge_collection'

    id: Optional[str]
    key: Optional[str]
    from_node: 'BaseVertex'
    to_node: 'BaseVertex'
    created_at: int
    modified_at: int

    def parse_for_graph(self) -> dict:
        return {
            '_id': self.id,
            '_key': self.key,
            '_from': self.from_node.id,
            '_to': self.to_node.id,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
        }
