from .create_graph import CreateGraph
from .drop_graph import DropGraph
from .get_graph import GetGraph
from .list_all_graphs import ListAllGraphs


class GraphMethods(
    ListAllGraphs,
    DropGraph,
    GetGraph,
    CreateGraph,
):
    pass
