from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Graph, Response, Request
from aioarango.typings import Result


class RemoveVertexCollection:
    error_codes = (
        ErrorType.GRAPH_NOT_IN_ORPHAN_COLLECTION,
        ErrorType.GRAPH_NOT_FOUND,
    )
    status_codes = (
        200,
        # Returned if the vertex collection was removed from the graph successfully and `waitForSync` is true.
        202,
        # Returned if the request was successful but `waitForSync` is false.
        400,  # 1928
        # Returned if the vertex collection is still used in an edge definition.
        # In this case it cannot be removed from the graph yet, it has to be
        # removed from the edge definition first.
        403,
        # Returned if your user has insufficient rights.
        # In order to drop a vertex you at least need to have the following privileges:
        #   1. `Administrate` access on the Database.
        404,  # 1924
        # Returned if no graph with this name could be found.
    )

    async def remove_vertex_collection(
        self: Endpoint,
        graph_name: str,
        name: str,
        drop_collection: Optional[bool] = None,
    ) -> Result[Graph]:
        """
        Remove a vertex collection from the graph and optionally **delete** the collection, if it is not used in any other graph.
        It can only remove vertex collections that are no longer part of edge definitions,
        **if they are used in edge definitions you are required to modify those first.**

        Parameters
        ----------
        graph_name : str
            Name of the graph the vertex collection belongs to.
        name : str
            Name of the vertex collection to remove from the graph.
        drop_collection : bool, optional
            If set to `True`, the vertex collection is not just deleted
            from the graph but also from the database completely.

        Returns
        -------
        Result
            Graph object description if the operation was successful.

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

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/gharial/{graph_name}/vertex/{name}",
            params={"dropCollection": drop_collection} if drop_collection is not None else None,
            write=name,
        )

        def response_handler(response: Response) -> Graph:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 202
            return Graph.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
