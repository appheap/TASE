from .add_edge_definition import AddEdgeDefinition
from .add_vertex_collection import AddVertexCollection
from .create_edge import CreateEdge
from .create_graph import CreateGraph
from .create_vertex import CreateVertex
from .drop_graph import DropGraph
from .get_edge import GetEdge
from .get_graph import GetGraph
from .get_vertex import GetVertex
from .list_all_graphs import ListAllGraphs
from .list_edge_definitions import ListEdgeDefinitions
from .list_vertex_collections import ListVertexCollections
from .remove_edge import RemoveEdge
from .remove_edge_definition import RemoveEdgeDefinition
from .remove_vertex import RemoveVertex
from .remove_vertex_collection import RemoveVertexCollection
from .replace_edge import ReplaceEdge
from .replace_vertex import ReplaceVertex
from .update_edge import UpdateEdge
from .update_vertex import UpdateVertex


class GraphMethods(
    AddEdgeDefinition,
    AddVertexCollection,
    CreateEdge,
    CreateGraph,
    CreateVertex,
    DropGraph,
    GetEdge,
    GetGraph,
    GetVertex,
    ListAllGraphs,
    ListEdgeDefinitions,
    ListVertexCollections,
    RemoveEdge,
    RemoveEdgeDefinition,
    RemoveVertex,
    RemoveVertexCollection,
    ReplaceEdge,
    ReplaceVertex,
    UpdateEdge,
    UpdateVertex,
):
    pass
