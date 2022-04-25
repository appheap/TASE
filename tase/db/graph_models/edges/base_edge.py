from typing import Optional, Tuple

from arango import DocumentInsertError, DocumentUpdateError, DocumentRevisionError
from arango.collection import EdgeCollection
from pydantic import BaseModel, Field

from tase.my_logger import logger
from tase.utils import get_timestamp
from ..vertices import BaseVertex


class BaseEdge(BaseModel):
    _collection_edge_name = 'base_edge_collection'

    _from_graph_db_mapping = {
        '_id': 'id',
        '_key': 'key',
        '_rev': 'rev',
    }
    _from_graph_db_mapping_rel = {
        '_from': 'from_node',
        '_to': 'to_node',
    }

    _to_graph_db_mapping = {
        'id': '_id',
        'key': '_key',
        'rev': '_rev',
    }
    _to_graph_db_mapping_rel = {
        'from_node': '_from',
        'to_node': '_to',
    }
    _do_not_update = ['created_at']

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]
    from_node: 'BaseVertex'
    to_node: 'BaseVertex'
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

        for k, v in self._to_graph_db_mapping_rel.items():
            if temp_dict.get(k, None):
                temp_dict[v] = temp_dict[k]['id']
                del temp_dict[k]
            else:
                del temp_dict[k]
                temp_dict[v] = None

        return temp_dict

    @classmethod
    def _from_graph(cls, vertex: dict) -> Optional['dict']:
        if not len(vertex):
            return None

        for k, v in BaseEdge._from_graph_db_mapping.items():
            if vertex.get(k, None):
                vertex[v] = vertex[k]
                del vertex[k]
            else:
                vertex[v] = None

        for k, v in BaseEdge._from_graph_db_mapping_rel.items():
            if vertex.get(k, None):
                vertex[v] = BaseVertex.parse_from_graph({'_id': vertex.get(vertex[k], None)})
                del vertex[k]
            else:
                vertex[v] = None

        return vertex

    def parse_for_graph(self) -> dict:
        return self._to_graph()

    @classmethod
    def parse_from_graph(cls, vertex: dict):
        if vertex is None or not len(vertex):
            return None

        return cls(**cls._from_graph(vertex))

    def _update_from_metadata(self, metadata: dict):
        for k, v in self._from_graph_db_mapping.items():
            setattr(self, v, metadata.get(k, None))

    def _update_metadata_from_old_edge(self, old_edge: 'BaseEdge'):
        """
        Updates the metadata of this edge from another edge metadata
        :param old_edge: The edge to get the metadata from
        :return: self
        """
        for k in self._to_graph_db_mapping.keys():
            setattr(self, k, getattr(old_edge, k, None))

        for k in self._do_not_update:
            setattr(self, k, getattr(old_edge, k, None))

        return self

    @classmethod
    def create(cls, db: 'EdgeCollection', edge: 'BaseEdge'):
        """
        Insert an object into the database

        :param db: The EdgeCollection to use for inserting the object
        :param edge: The edge to insert into the database
        :return: self, successful
        """

        if db is None or edge is None:
            return None, False

        successful = False
        try:
            metadata = db.insert(edge.parse_for_graph())
            edge._update_from_metadata(metadata)
            successful = True
        except DocumentInsertError as e:
            # Failed to insert the document
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        return edge, successful

    @classmethod
    def update(cls, db: 'EdgeCollection', old_edge: 'BaseEdge', edge: 'BaseEdge'):
        """
        Update an object in the database

        :param db: The EdgeCollection to use for updating the object
        :param old_edge: The edge that is already in the database
        :param edge: The edge used for updating the object in the database
        :return: self, successful
        """
        if db is None or old_edge is None or edge is None:
            return None, False

        if not isinstance(edge, BaseEdge):
            raise Exception(f'`edge` is not an instance of {BaseEdge.__class__.__name__} class')

        successful = False
        try:
            metadata = db.update(edge._update_metadata_from_old_edge(old_edge).parse_for_graph())
            edge._update_from_metadata(metadata)
            successful = True
        except DocumentUpdateError as e:
            # Failed to update document.
            logger.exception(e)
        except DocumentRevisionError as e:
            # The expected and actual document revisions mismatched.
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        return edge, successful
