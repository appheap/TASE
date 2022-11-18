from .create_graph import CreateGraph
from .get_graph import GetGraph
from .list_all_graphs import ListAllGraphs


class GraphMethods(
    ListAllGraphs,
    GetGraph,
    CreateGraph,
):
    pass
