from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Params


class DropGraph:
    error_codes = (
        ErrorType.HTTP_METHOD_NOT_ALLOWED,
        ErrorType.GRAPH_NOT_FOUND,
    )

    status_codes = (
        201,
        # Is returned if the graph could be dropped and `waitForSync` is enabled
        # for the `_graphs` collection, or given in the request.
        202,
        # Is returned if the graph could be dropped and `waitForSync` is disabled
        # for the `_graphs` collection and not given in the request.
        403,
        # Returned if your user has insufficient rights.
        # In order to drop a graph you at least need to have the following privileges
        #   1. `Administrate` access on the Database.
        404,  # 1924
        # Returned if no graph with this name could be found.
        500,  # 405
    )

    async def drop_graph(
        self: Endpoint,
        name: str,
        drop_collections: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Drops an existing graph object by name. Optionally all collections not used by other graphs
        can be dropped as well.

        Parameters
        ----------
        name : str
            Name of the graph.
        drop_collections : bool, optional
            Drop collections of this graph as well. Collections will only be dropped if they are not used in other graphs.

        Returns
        -------
        Result
            True if the graph was deleted successfully.

        Raises
        ------
        ValueError
            If the input graph name is invalid.
        aioarango.errors.ArangoServerError
            If drop fails.

        """
        if name is None or not len(name):
            raise ValueError("`name` has invalid value!")

        params: Params = {}
        if drop_collections is not None:
            params["dropCollections"] = drop_collections

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/gharial/{name}",
            params=params,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return True

        return await self.execute(request, response_handler)
