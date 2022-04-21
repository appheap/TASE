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
