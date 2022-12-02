from typing import List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Response, Request
from aioarango.typings import Result


class ListVertexCollections(Endpoint):
    error_codes = (ErrorType.GRAPH_NOT_FOUND,)
    status_codes = (
        200,
        # Is returned if the collections could be listed.
        404,  # 1924
        # Returned if no graph with this name could be found.
    )

    async def list_vertex_collections(
        self,
        graph_name: str,
    ) -> Result[List[str]]:
        """
        List all vertex collections within this graph.


        Parameters
        ----------
        graph_name : str
            Name of the graph

        Returns
        -------
        Result
            List of all vertex collections if operation was successful.

        Raises
        ------
        ValueError
            If graph name is invalid.
        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        if graph_name is None or not len(graph_name):
            raise ValueError("`graph_name` is invalid!")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/gharial/{graph_name}/vertex",
        )

        def response_handler(response: Response) -> List[str]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body["collections"]

        return await self.execute(request, response_handler)
