from .add_edge_definition import AddEdgeDefinition
from .add_vertex_collection import AddVertexCollection
from .create_edge import CreateEdge
from .create_graph import CreateGraph
from .create_vertex import CreateVertex
from .drop_graph import DropGraph
from .get_graph import GetGraph
from .get_vertex import GetVertex
from .list_all_graphs import ListAllGraphs
from .list_edge_definitions import ListEdgeDefinitions
from .list_vertex_collections import ListVertexCollections
from .remove_edge_definition import RemoveEdgeDefinition
from .remove_vertex import RemoveVertex
from .remove_vertex_collection import RemoveVertexCollection
from .replace_vertex import ReplaceVertex
from .update_vertex import UpdateVertex


class GraphMethods(
    AddEdgeDefinition,
    AddVertexCollection,
    CreateEdge,
    CreateGraph,
    CreateVertex,
    DropGraph,
    GetGraph,
    GetVertex,
    ListAllGraphs,
    ListEdgeDefinitions,
    ListVertexCollections,
    RemoveEdgeDefinition,
    RemoveVertex,
    RemoveVertexCollection,
    ReplaceVertex,
    UpdateVertex,
):
    pass
