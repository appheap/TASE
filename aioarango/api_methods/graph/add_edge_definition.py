from itertools import chain
from typing import Optional, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, EdgeDefinition, Graph
from aioarango.typings import Result


class AddEdgeDefinition:
    error_codes = (
        ErrorType.ARANGO_ILLEGAL_NAME,
        ErrorType.GRAPH_COLLECTION_MULTI_USE,
    )
    status_codes = (
        201,
        # Returned if the definition could be added successfully and
        # `waitForSync` is enabled for the `_graphs` collection.
        # The response body contains the graph configuration that has been stored.
        202,
        # Returned if the definition could be added successfully and
        # `waitForSync` is disabled for the `_graphs` collection.
        # The response body contains the graph configuration that has been stored.
        400,  # 1208, 1920
        # Returned if the definition could not be added.
        # This could be because it is ill-formed, or
        # if the definition is used in an other graph with a different signature.
        403,
        # Returned if your user has insufficient rights.
        # In order to modify a graph you at least need to have the following privileges:
        #   1. `Administrate` access on the Database.
        404,
        # Returned if no graph with this name could be found.
    )

    async def add_edge_definition(
        self: Endpoint,
        graph_name: str,
        edge_definition: EdgeDefinition,
        satellites: Optional[List[str]] = None,
    ) -> Result:
        """
        Add an additional edge definition to the graph.

        Notes
        -----
        This edge definition has to contain a collection and an array of
        each from and to vertex collections. An edge definition can only
        be added if this definition is either not used in any other graph, or
        it is used with exactly the same definition. It is not possible to
        store a definition "e" from "v1" to "v2" in the one graph, and "e"
        from "v2" to "v1" in the other graph.

        Additionally, collection creation options can be set.



        Parameters
        ----------
        graph_name : str
            Name of the graph.
        edge_definition : EdgeDefinition
            Edge definition to add to the graph.
        satellites : list of str, optional
             An array of collection names that will be used to create SatelliteCollections
            for a `Hybrid` (Disjoint) `SmartGraph` (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be
            modified later.

        Returns
        -------
        Result
            Graph object if adding edge definition was successful.

        Raises
        ------
        ValueError
            If graph name is invalid or edge definition object has invalid attributes.
        aioarango.errors.ArangoServerError
            If add operation fails.

        """
        if graph_name is None or not len(graph_name):
            raise ValueError("`graph_name` is invalid!")

        if edge_definition is None:
            raise ValueError("`edge_definition` is invalid!")

        if edge_definition.from_ is None or not len(edge_definition.from_):
            raise ValueError("`from` attribute of edge_definition variable is invalid!")

        if edge_definition.to is None or not len(edge_definition.to):
            raise ValueError("`to` attribute of edge_definition variable is invalid!")

        if edge_definition.collection in chain(edge_definition.from_, edge_definition.to):
            raise ValueError("edge_definition `collection` attribute cannot be the same as `to` or `from` collections!")

        data = {
            "collection": edge_definition.collection,
            "from": edge_definition.from_,
            "to": edge_definition.to,
        }
        if satellites is not None and len(satellites):  # todo: check if this works correctly
            data["options"] = {}
            data["options"]["satellites"] = satellites

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/gharial/{graph_name}/edge",
            data=data,
        )

        def response_handler(response: Response) -> Graph:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return Graph.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
