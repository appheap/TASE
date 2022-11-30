from typing import List, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, GraphInfo
from aioarango.typings import Result


class AddVertexCollection(Endpoint):
    error_codes = (
        ErrorType.ARANGO_ILLEGAL_NAME,
        ErrorType.GRAPH_NOT_FOUND,
    )
    status_codes = (
        201,
        # Is returned if the collection could be created and `waitForSync` is enabled
        # for the `_graphs` collection, or given in the request.
        # The response body contains the graph configuration that has been stored.
        202,
        # Is returned if the collection could be created and `waitForSync` is disabled
        # for the `_graphs` collection, or given in the request.
        # The response body contains the graph configuration that has been stored.
        400,  # 1200
        # Returned if the request is in an invalid format.
        403,
        # Returned if your user has insufficient rights.
        # In order to modify a graph you at least need to have the following privileges:
        #   1. `Administrate` access on the Database.
        #   2. `Read Only` access on every collection used within this graph.
        404,  # 1924
        # Returned if no graph with this name could be found.
    )

    async def add_vertex_collection(
        self,
        graph_name: str,
        name: str,
        satellites: Optional[List[str]] = None,
    ) -> Result[GraphInfo]:
        """
        Adds a vertex collection to the set of orphan collections of the graph.
        If the collection does not exist, it will be created.

        Parameters
        ----------
        graph_name : str
            Name of the graph.
        name : str
            Name of the vertex collection to create.
        satellites :  list of str, optional
            An array of collection names that will be used to create SatelliteCollections
            for a `Hybrid` (Disjoint) `SmartGraph` (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be
            modified later.

        Returns
        -------
        Result
            Graph object description if the vertex creation was successful.

        Raises
        ------
        ValueError
            If graph name or the vertex collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if graph_name is None or not len(graph_name):
            raise ValueError("`graph_name` is invalid!")

        if name is None or not len(name):
            raise ValueError("`name` is invalid!")

        data = {
            "collection": name,
        }
        if satellites is not None and len(satellites):  # todo: check if this works correctly
            data["options"] = {}
            data["options"]["satellites"] = satellites

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/gharial/{graph_name}/vertex",
            data=data,
            write=name,
        )

        def response_handler(response: Response):
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return GraphInfo.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
