from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Graph, Request, Response
from aioarango.typings import Result


class GetGraph(Endpoint):
    error_codes = (ErrorType.GRAPH_NOT_FOUND,)
    status_codes = (
        200,
        # Returns the graph if it could be found.
        404,  # 1924
        # Returned if no graph with this name could be found.
    )

    async def get_graph(
        self,
        name: str,
    ) -> Result[Graph]:
        """
        Get a graph from the ArangoDB.

        Parameters
        ----------
        name : str
            Name of the graph.

        Returns
        -------
        Result
            Graph object if the operation was successful.

        Raises
        ------
        ValueError
            If the input graph name is invalid.
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        if name is None or not len(name):
            raise ValueError("`name` has invalid value!")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/gharial/{name}",
        )

        def response_handler(response: Response) -> Graph:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            if "graph" not in response.body:
                raise ValueError("`name` has invalid value!")

            return Graph.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
