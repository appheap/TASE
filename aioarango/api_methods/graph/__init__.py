from .add_edge_definition import AddEdgeDefinition
from .add_vertex_collection import AddVertexCollection
from .create_graph import CreateGraph
from .drop_graph import DropGraph
from .get_graph import GetGraph
from .list_all_graphs import ListAllGraphs
from .list_edge_definitions import ListEdgeDefinitions
from .list_vertex_collections import ListVertexCollections
from .remove_vertex_collection import RemoveVertexCollection


class GraphMethods(
    AddEdgeDefinition,
    AddVertexCollection,
    CreateGraph,
    DropGraph,
    GetGraph,
    ListAllGraphs,
    ListEdgeDefinitions,
    ListVertexCollections,
    RemoveVertexCollection,
):
    pass
