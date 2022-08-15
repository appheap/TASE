from typing import Dict, Any

from arango.collection import EdgeCollection
from pydantic.typing import List, Type, Optional

from tase.db.arangodb.models.base import (
    BaseCollectionDocument,
    ToGraphBaseProcessor,
    FromGraphBaseProcessor,
)
from tase.db.arangodb.models.graph.vertices import BaseVertex


class ToVertexMapper(ToGraphBaseProcessor):
    @classmethod
    def process(
        cls,
        document: "BaseEdge",
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for k, v in document._to_graph_db_mapping_rel.items():
            attr_value = attr_value_dict.get(k, None)
            if attr_value is not None:
                attr_value_dict[v] = attr_value["id"]
                del attr_value_dict[k]
            else:
                del attr_value_dict[k]
                attr_value_dict[v] = None


class FromVertexMapper(FromGraphBaseProcessor):
    @classmethod
    def process(
        cls,
        document_class: Type["BaseEdge"],
        graph_doc: Dict[str, Any],
    ) -> None:
        for graph_doc_attr, obj_attr in document_class._from_graph_db_mapping_rel.items():
            attr_value = graph_doc.get(graph_doc_attr, None)
            if attr_value is not None:
                obj = BaseVertex.from_collection({"_id": graph_doc.get(attr_value, None)})
                if obj is None:
                    raise Exception(f"`obj` cannot be `None`")
                graph_doc[obj_attr] = obj
                del graph_doc[graph_doc_attr]
            else:
                graph_doc[obj_attr] = None


##############################################################################


class BaseEdge(BaseCollectionDocument):
    _collection_name = "base_edges"
    _collection: Optional[EdgeCollection]

    _from_graph_db_mapping_rel = {
        "_from": "from_node",
        "_to": "to_node",
    }
    _to_graph_db_mapping_rel = {
        "from_node": "_from",
        "to_node": "_to",
    }

    _from_vertex_collections = [BaseVertex]
    _to_vertex_collections = [BaseVertex]

    _to_graph_db_extra_processors = [
        ToVertexMapper,
    ]
    _from_graph_db_extra_processors = [
        FromVertexMapper,
    ]

    from_node: BaseVertex
    to_node: BaseVertex

    @classmethod
    def _get_vertices_collection_names(
        cls,
        lst: List[Type[BaseVertex]],
    ) -> List[str]:
        return [v._collection_name for v in lst if v._collection_name != BaseVertex._collection_name]

    @classmethod
    def to_vertex_collections(cls) -> List[str]:
        return cls._get_vertices_collection_names(cls._to_vertex_collections)

    @classmethod
    def from_vertex_collections(cls) -> List[str]:
        return cls._get_vertices_collection_names(cls._to_vertex_collections)
