from __future__ import annotations

from typing import Dict, List, Type, Optional, Tuple, Any, Callable

from arango import DocumentInsertError
from arango.collection import EdgeCollection

from tase.db.arangodb.base import (
    BaseCollectionDocument,
    ToGraphBaseProcessor,
    FromGraphBaseProcessor,
)
from tase.db.arangodb.graph.vertices import BaseVertex
from tase.errors import InvalidFromVertex, InvalidToVertex
from tase.my_logger import logger


class ToVertexMapper(ToGraphBaseProcessor):
    @classmethod
    def process(
        cls,
        document: BaseEdge,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for k, v in document._to_graph_db_mapping_rel.items():
            attr_value = attr_value_dict.get(k, None)
            if attr_value is not None:
                attr_value_dict[v] = attr_value["_id"]
                del attr_value_dict[k]
            else:
                del attr_value_dict[k]
                attr_value_dict[v] = None


class FromVertexMapper(FromGraphBaseProcessor):
    @classmethod
    def process(
        cls,
        document_class: Type[BaseEdge],
        graph_doc: Dict[str, Any],
    ) -> None:
        for (
            graph_doc_attr,
            obj_attr,
        ) in document_class._from_graph_db_mapping_rel.items():
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


class EdgeEndsValidator:
    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, *args, **kwargs):
        cls = args[0]
        from_vertex: BaseVertex = args[1]
        to_vertex: BaseVertex = args[2]

        if not isinstance(from_vertex, cls._from_vertex_collections):
            e = InvalidFromVertex(from_vertex.__class__.__name__, cls.__name__)
            logger.error(e)
            raise e
        if not isinstance(to_vertex, cls._to_vertex_collections):
            e = InvalidToVertex(to_vertex.__class__.__name__, cls.__name__)
            logger.error(e)
            raise e

        return self.func(*args, **kwargs)


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

    _from_vertex_collections: Tuple[Type[BaseVertex]] = (BaseVertex,)
    _to_vertex_collections: Tuple[Type[BaseVertex]] = (BaseVertex,)

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
        return cls._get_vertices_collection_names(list(cls._to_vertex_collections))

    @classmethod
    def from_vertex_collections(cls) -> List[str]:
        return cls._get_vertices_collection_names(list(cls._from_vertex_collections))

    @classmethod
    def link(
        cls,
        from_vertex: BaseVertex,
        to_vertex: BaseVertex,
        *args,
        **kwargs,
    ) -> Tuple[Optional[BaseEdge], bool]:
        """
        Insert a new edge document linking the given vertices.

        Parameters
        ----------
        from_vertex : BaseVertex
            Vertex at the start of the link
        to_vertex : BaseVertex
            Vertex at the end of the link

        Returns
        -------
        tuple
            Updated edge with returned metadata from ArangoDB and `True` if the operation was successful,
            old object and `False` otherwise.

        Raises
        ------
        ValueError
            When the start or the end vertex provided to the function does not match the edge definition in the
            database.
        """

        if from_vertex is None or to_vertex is None or from_vertex.id is None or to_vertex.id is None:
            return None, False

        successful = False
        edge = None
        try:
            edge = cls.parse(from_vertex, to_vertex, *args, **kwargs)
            if edge is None:
                return None, False

            graph_doc = edge.to_collection()
            if graph_doc is None:
                return None, False

            metadata = cls._collection.link(
                from_vertex=from_vertex.id,
                to_vertex=to_vertex.id,
                data=graph_doc,
            )
            edge._update_metadata(metadata)
            successful = True
        except DocumentInsertError as e:
            # Failed to insert the document
            logger.exception(f"{cls.__name__} : {e}")
        except NotImplementedError as e:
            logger.exception(f"{cls.__name__} : {e}")
        except Exception as e:
            logger.exception(f"{cls.__name__} : {e}")
        return edge, successful

    ####################################################################
    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: BaseVertex,
        to_vertex: BaseVertex,
        *args,
        **kwargs,
    ) -> Optional[BaseEdge]:
        """
        Create an `Edge` object with the arguments provided

        Parameters
        ----------
        from_vertex : BaseVertex
            Start of the edge
        to_vertex : BaseVertex
            End of the edge
        args : tuple
            Arguments provided to this function
        kwargs : dict, optional
            Keyword arguments provided to this function

        Returns
        -------
        BaseEdge
            Edge object if given arguments are valid, otherwise return `None`

        Raises
        ------
        InvalidFromVertex
            If the start vertex provided to the function does not match the edge definition in the database.
        InvalidToVertex
            If the end vertex provided to the function does not match the edge definition in the database.
        """
        raise NotImplementedError

    @classmethod
    def parse_key(
        cls,
        from_vertex: BaseVertex,
        to_vertex: BaseVertex,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def create_edge(
        cls,
        from_vertex: BaseVertex,
        to_vertex: BaseVertex,
        *args,
        **kwargs,
    ) -> Tuple[Optional[BaseEdge], bool]:
        """
        Create a new edge from `from_vertex` vertex to `to_vertex` vertex with given arguments and return it if
        successful.

        Parameters
        ----------
        from_vertex : BaseVertex
            Start of the edge
        to_vertex : BaseVertex
            End of the edge
        args : tuple
            Arguments passed to this function
        kwargs : dict, optional
            Keyword arguments passed to this function

        Returns
        -------
        tuple
            Created edge and whether the creation was successful.

        Raises
        ------
        InvalidFromVertex
            If the start vertex provided to the function does not match the edge definition in the database.
        InvalidToVertex
            If the end vertex provided to the function does not match the edge definition in the database.
        """
        if from_vertex is None or to_vertex is None:
            return None, False

        return cls.insert(cls.parse(from_vertex, to_vertex, *args, **kwargs))

    @classmethod
    def get_or_create_edge(
        cls,
        from_vertex: Optional[BaseVertex],
        to_vertex: Optional[BaseVertex],
        *args,
        **kwargs,
    ) -> Optional[BaseEdge]:
        """
        Get an Edge if it exists in the database, and create it otherwise.

        Parameters
        ----------
        from_vertex : BaseVertex, optional
            Start of the edge
        to_vertex : BaseVertex, optional
            End of the edge
        args
            Arguments passed to the function
        kwargs
            Keywords passed to the function

        Returns
        --------
        BaseEdge, optional
            The created/existing Edge if successful, otherwise, return `None`.

        Raises
        ------
        InvalidFromVertex
            If the start vertex provided to the function does not match the edge definition in the database.
        InvalidToVertex
            If the end vertex provided to the function does not match the edge definition in the database.

        """
        if from_vertex is None or to_vertex is None:
            return None

        edge = cls.get(cls.parse_key(from_vertex, to_vertex, *args, **kwargs))
        if not edge:
            # edge does not exist in the database, create it
            edge, successful = cls.create_edge(from_vertex, to_vertex, *args, **kwargs)

        return edge

    @classmethod
    def update_or_create_edge(
        cls,
        from_vertex: BaseVertex,
        to_vertex: BaseVertex,
        *args,
        **kwargs,
    ) -> Optional[BaseEdge]:
        """
        Update an Edge if it exists in the database, and create it otherwise. Return the created/updated if
        successful and return `None` otherwise

        Parameters
        ----------
        from_vertex : BaseVertex
            Start of the edge
        to_vertex : BaseVertex
            End of the edge
        args
            Arguments passed to the function
        kwargs
            Keywords passed to the function

        Returns
        -------
        BaseEdge, optional
            The created/updated if successful, otherwise, return `None`.

        Raises
        ------
        InvalidFromVertex
            If the start vertex provided to the function does not match the edge definition in the database.
        InvalidToVertex
            If the end vertex provided to the function does not match the edge definition in the database.

        """
        if from_vertex is None or to_vertex is None:
            return None

        edge = cls.get(cls.parse_key(from_vertex, to_vertex, *args, **kwargs))
        if edge is not None:
            # edge exists in the database, update it
            edge, successful = edge.update(cls.parse(from_vertex, to_vertex, *args, **kwargs))
        else:
            # edge does not exist in the database, create it
            edge, successful = cls.create_edge(from_vertex, to_vertex, *args, **kwargs)

        return edge
