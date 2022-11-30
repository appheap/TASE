from typing import List, Optional

from aioarango.api import VertexCollection, EdgeCollection
from aioarango.api_methods import GraphMethods
from aioarango.connection import Connection
from aioarango.executor import API_Executor
from aioarango.models import GraphInfo, EdgeDefinition
from aioarango.typings import Result


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

    async def properties(self) -> Result[GraphInfo]:
        """
        Return graph properties.

        Returns
        -------
        GraphInfo
            Graph properties.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._graph_api.get_graph(name=self.name)

    ################################
    # Vertex Collection Management #
    ################################

    async def has_vertex_collection(
        self,
        name: str,
    ) -> Result[bool]:
        """
        Check if the graph has the given vertex collection.

        Parameters
        ----------
        name : str
            Vertex collection name.

        Returns
        -------
        bool
            True if vertex collection exists, False otherwise.

        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        return name in await self._graph_api.list_vertex_collections(graph_name=self.name)

    async def vertex_collections(self) -> Result[List[str]]:
        """
        Return vertex collections in the graph that are not orphaned.

        Returns
        -------
        list
            Names of vertex collections that are not orphaned.

        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        return await self._graph_api.list_vertex_collections(graph_name=self.name)

    def vertex_collection(
        self,
        name: str,
    ) -> Result[VertexCollection]:
        """
        Return the vertex collection API wrapper.

        Parameters
        ----------
        name : str
            Vertex collection name.

        Returns
        -------
        VertexCollection
            Vertex collection API wrapper.

        Raises
        ------
        ValueError
            If `name` has invalid value.
        """
        return VertexCollection(
            connection=self._connection,
            executor=self._executor,
            name=name,
            graph_name=self._name,
        )

    async def create_vertex_collection(
        self,
        name: str,
        satellites: Optional[List[str]] = None,
    ) -> Result[VertexCollection]:
        """
        Create a vertex collection in the graph.

        Parameters
        ----------
        name : str
            Name of the vertex collection to create.
        satellites :  list of str, optional
            An array of collection names that will be used to create SatelliteCollections
            for a `Hybrid` (Disjoint) `SmartGraph` (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be
            modified later.

        Returns
        -------
        VertexCollection
            Vertex collection API wrapper.

        Raises
        ------
        ValueError
            If vertex collection name is invalid.
        aioarango.errors.ArangoServerError
            If create fails.
        """
        _ = await self._graph_api.add_vertex_collection(
            graph_name=self.name,
            name=name,
            satellites=satellites,
        )

        return VertexCollection(
            connection=self._connection,
            executor=self._executor,
            name=name,
            graph_name=self._name,
        )

    async def delete_vertex_collection(
        self,
        name: str,
        drop_collection: Optional[bool],
    ) -> Result[bool]:
        """
        Remove a vertex collection from the graph.

        Parameters
        ----------
        name : str
            Name of the vertex collection to remove from the graph.
        drop_collection : bool, optional
            If set to `True`, the vertex collection is not just deleted
            from the graph but also from the database completely.

        Returns
        -------
        bool
            True if vertex collection was deleted successfully.

        Raises
        ------
        ValueError
            If the vertex collection name is invalid.
        aioarango.errors.ArangoServerError
            If delete fails.

        """
        _ = await self._graph_api.remove_vertex_collection(
            graph_name=self._name,
            name=name,
            drop_collection=drop_collection,
        )
        return True

    ##############################
    # Edge Collection Management #
    ##############################

    async def has_edge_definition(
        self,
        name: str,
    ) -> Result[bool]:
        """
        Check if the graph has the given edge definition.

        Parameters
        ----------
        name : str
            Edge collection name.

        Returns
        -------
        bool
            True if edge definition exists, False otherwise.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        return any(edge_def.collection == name for edge_def in await self._graph_api.list_edge_definitions(name=self.name))

    def edge_collection(
        self,
        name: str,
    ) -> EdgeCollection:
        """
        Return the edge collection API wrapper.

        Parameters
        ----------
        name : str
            Edge collection name.

        Returns
        -------
        EdgeCollection
            Edge collection API wrapper.

        Raises
        ------
        ValueError
            If edge collection name has invalid value.
        """
        return EdgeCollection(
            connection=self._connection,
            executor=self._executor,
            name=name,
            graph_name=self.name,
        )

    async def edge_definitions(self) -> Result[List[EdgeCollection]]:
        """
        Return the edge definitions of the graph.

        Returns
        -------
        list
            Edge definitions of the graph.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        return await self._graph_api.list_edge_definitions(name=self.name)

    async def create_edge_definition(
        self,
        edge_definition: EdgeDefinition,
        satellites: Optional[List[str]] = None,
    ) -> Result[EdgeCollection]:
        """
        Create a new edge definition.

        Parameters
        ----------
        edge_definition : EdgeDefinition
            Edge definition to add to the graph.
        satellites : list of str, optional
             An array of collection names that will be used to create SatelliteCollections
            for a `Hybrid` (Disjoint) `SmartGraph` (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be
            modified later.

        Returns
        -------
        EdgeCollection
            Edge collection API wrapper.

        Raises
        ------
        ValueError
            If edge definition object has invalid attributes.
        aioarango.errors.ArangoServerError
            If create fails.
        """
        _ = await self._graph_api.add_edge_definition(
            graph_name=self.name,
            edge_definition=edge_definition,
            satellites=satellites,
        )

        return EdgeCollection(
            connection=self._connection,
            executor=self._executor,
            name=edge_definition.collection,
            graph_name=self.name,
        )

    async def replace_edge_definition(
        self,
        edge_definition: EdgeDefinition,
        satellites: Optional[List[str]] = None,
        wait_for_sync: Optional[bool] = None,
        drop_collections: Optional[bool] = None,
    ) -> Result[EdgeCollection]:
        """
        Replace an edge definition.

        Parameters
        ----------
        edge_definition : EdgeDefinition
            Edge definition to replace the existing edge definition in the graph.
        satellites : list of str, optional
             An array of collection names that will be used to create SatelliteCollections
            for a `Hybrid` (Disjoint) `SmartGraph` (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be
            modified later.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        drop_collections: bool, optional
            Drop the collection as well.
            Collection will only be dropped if it is not used in other graphs.

        Returns
        -------
        EdgeCollection
            Edge collection API wrapper.

        Raises
        ------
        ValueError
            If edge definition object has invalid attributes.
        aioarango.errors.ArangoServerError
            If replace fails.
        """
        _ = await self._graph_api.replace_edge_definition(
            graph_name=self.name,
            edge_definition=edge_definition,
            satellites=satellites,
            wait_for_sync=wait_for_sync,
            drop_collections=drop_collections,
        )

        return EdgeCollection(
            connection=self._connection,
            executor=self._executor,
            name=edge_definition.collection,
            graph_name=self.name,
        )

    async def delete_edge_definition(
        self,
        name: str,
        drop_collections: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Delete an edge definition from the graph. This will only remove the
        edge collection, the vertex collections remain untouched and can still
        be used in your queries.

        Parameters
        ----------
        name : str
            Name of the edge definition to remove.
        drop_collections : bool, optional
            If set to `True`, the edge definition is not just removed
            from the graph but the edge collection is also deleted completely
            from the database.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.

        Returns
        -------
        bool
            True if edge definition was deleted successfully.

        Raises
        ------
        ValueError
            If edge collection name is invalid.
        aioarango.errors.ArangoServerError
            If delete fails.
        """
        return bool(
            await self._graph_api.remove_edge_definition(
                graph_name=self.name,
                name=name,
                drop_collections=drop_collections,
                wait_for_sync=wait_for_sync,
            )
        )

    ###################
    # Graph Functions #
    ###################

    #####################
    # Vertex Management #
    #####################

    ###################
    # Edge Management #
    ###################
