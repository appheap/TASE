from aioarango.api_methods import GraphMethods
from aioarango.connection import Connection
from aioarango.executor import API_Executor


class Graph:
    """
    Graph API wrapper.
    """

    __slots__ = [
        "_connection",
        "_executor",
        "_graph_api",
        "_name",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
        name: str,
    ):
        if not name:
            raise ValueError(f"`name` has invalid value: `{name}`")

        self._connection = connection
        self._executor = executor

        self._name = name
        self._graph_api = GraphMethods(connection, executor)

    def __repr__(self) -> str:
        return f"<Graph {self._name}>"

    @property
    def name(self) -> str:
        """
        Return the graph name.

        Returns
        -------
        str
            Graph name.
        """
        return self._name
