from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseVertex:
    _vertex_name = 'base_vertices'

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]
    created_at: int
    modified_at: int

    def parse_for_graph(self) -> dict:
        return {
            '_id': self.id,
            '_key': self.key,
            '_rev': self.rev,
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
            'created_at': vertex.get('created_at', None),
            'modified_at': vertex.get('modified_at', None),
        }

    def update_from_metadata(self, metadata: dict):
        self.id = metadata.get('_id', None)
        self.key = metadata.get('_key', None)
        self.rev = metadata.get('_rev', None)
