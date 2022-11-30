from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, GraphInfo
from aioarango.typings import Result, Params


class RemoveEdgeDefinition(Endpoint):
    error_codes = (
        ErrorType.GRAPH_NOT_FOUND,
        ErrorType.GRAPH_EDGE_COLLECTION_NOT_USED,
    )
    status_codes = (
        201,
        # Returned if the edge definition could be removed from the graph and `waitForSync` is true.
        202,
        # Returned if the edge definition could be removed from the graph and `waitForSync` is false.
        403,
        # Returned if your user has insufficient rights.
        # In order to drop a vertex you at least need to have the following privileges:
        #   1. `Administrate` access on the Database.
        404,  # 1924, 1930
        # Returned if no graph with this name could be found,
        # or if no edge definition with this name is found in the graph.
    )

    async def remove_edge_definition(
        self,
        graph_name: str,
        name: str,
        drop_collections: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
    ) -> Result[GraphInfo]:
        """
        Remove one edge definition from the graph. This will only remove the
        edge collection, the vertex collections remain untouched and can still
        be used in your queries.

        Parameters
        ----------
        graph_name : str
            Name of the graph the edge definition belongs to.
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
        Result
            Graph object description if operation was successful.

        Raises
        ------
        ValueError
            If graph name or the edge collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if graph_name is None or not len(graph_name):
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        params: Params = {}
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync
        if drop_collections is not None:
            params["dropCollections"] = drop_collections

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/gharial/{graph_name}/edge/{name}",
            params=params if len(params) else None,
            write=name,
        )

        def response_handler(response: Response) -> GraphInfo:
            if not response.is_success:
                raise ArangoServerError(response, request)

            return GraphInfo.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
