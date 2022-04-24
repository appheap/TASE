from typing import Optional

from pydantic import BaseModel, Field

from tase.utils import get_timestamp


class BaseVertex(BaseModel):
    _vertex_name = 'base_vertices'
    _from_graph_db_mapping = {
        '_id': 'id',
        '_key': 'key',
        '_rev': 'rev',
    }
    _to_graph_db_mapping = {
        'id': '_id',
        'key': '_key',
        'rev': '_rev',
    }

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]
    created_at: int = Field(default_factory=get_timestamp)
    modified_at: int = Field(default_factory=get_timestamp)

    def _to_graph(self) -> dict:
        temp_dict = self.dict()
        for k, v in self._to_graph_db_mapping.items():
            if temp_dict.get(k, None):
                temp_dict[v] = temp_dict[k]
                del temp_dict[k]
            else:
                del temp_dict[k]
                temp_dict[v] = None

        return temp_dict

    @classmethod
    def _from_graph(cls, vertex: dict) -> Optional['dict']:
        if not len(vertex):
            return None

        for k, v in BaseVertex._from_graph_db_mapping.items():
            if vertex.get(k, None):
                vertex[v] = vertex[k]
                del vertex[k]
            else:
                vertex[v] = None

        return vertex

    def parse_for_graph(self) -> dict:
        return self._to_graph()

    @classmethod
    def parse_from_graph(cls, vertex: dict):
        return cls(**cls._from_graph(vertex))

    def update_from_metadata(self, metadata: dict):
        for k, v in self._from_graph_db_mapping.items():
            setattr(self, v, metadata.get(k, None))

    def update_metadata_from_vertex(self, vertex: 'BaseVertex'):
        for k in self._to_graph_db_mapping.keys():
            setattr(self, k, getattr(vertex, k, None))

        return self
