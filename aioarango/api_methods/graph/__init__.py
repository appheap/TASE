from .create_graph import CreateGraph
from .drop_graph import DropGraph
from .get_graph import GetGraph
from .list_all_graphs import ListAllGraphs
from .list_edge_definitions import ListEdgeDefinitions


class GraphMethods(
    CreateGraph,
    DropGraph,
    GetGraph,
    ListAllGraphs,
    ListEdgeDefinitions,
):
    pass
