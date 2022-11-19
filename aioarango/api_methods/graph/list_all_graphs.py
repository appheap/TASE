import collections
from typing import List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, Graph
from aioarango.typings import Result


class ListAllGraphs:
    error_codes = ()
    status_codes = (
        200,
        # Is returned if the module is available and the graphs could be listed.
    )

    async def list_all_graphs(self: Endpoint) -> Result[List[Graph]]:
        """
        List all graphs stored in this database.

        Returns
        -------
        Result
            List of all graph stored in the database if successful.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/gharial",
        )

        def response_handler(response: Response) -> List[Graph]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            graphs = collections.deque()
            for graph_body in response.body["graphs"]:
                graphs.append(Graph.parse_graph_dict(graph_body))

            return list(graphs)

        return await self.execute(request, response_handler)
