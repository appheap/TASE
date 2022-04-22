from dataclasses import dataclass
from typing import Optional

from ..vertices import BaseVertex


@dataclass
class BaseEdge:
    _collection_edge_name = 'base_edge_collection'

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]
    from_node: 'BaseVertex'
    to_node: 'BaseVertex'
    created_at: int
    modified_at: int

    def parse_for_graph(self) -> dict:
        return {
            '_id': self.id,
            '_key': self.key,
            '_rev': self.rev,
            '_from': self.from_node.id,
            '_to': self.to_node.id,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
        }

    @staticmethod
    def parse_from_graph(vertex: dict) -> Optional['dict']:
        if not len(vertex):
            return None

        return {
            'id': vertex.get('_id', None),
            'key': vertex.get('_key', None),
            'rev': vertex.get('_rev', None),
            'from_node': BaseVertex.parse_from_graph({'_id': vertex.get('_from', None)}),
            'to_node': BaseVertex.parse_from_graph({'_id': vertex.get('_to', None)}),
            'created_at': vertex.get('created_at', None),
            'modified_at': vertex.get('modified_at', None),
        }

    def update_from_metadata(self, metadata: dict):
        self.id = metadata.get('_id', None)
        self.key = metadata.get('_key', None)
        self.rev = metadata.get('_rev', None)
