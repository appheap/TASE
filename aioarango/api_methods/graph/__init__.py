from .add_edge_definition import AddEdgeDefinition
from .create_graph import CreateGraph
from .drop_graph import DropGraph
from .get_graph import GetGraph
from .list_all_graphs import ListAllGraphs
from .list_edge_definitions import ListEdgeDefinitions
from .list_vertex_collections import ListVertexCollections


class GraphMethods(
    AddEdgeDefinition,
    CreateGraph,
    DropGraph,
    GetGraph,
    ListAllGraphs,
    ListEdgeDefinitions,
    ListVertexCollections,
):
    pass
