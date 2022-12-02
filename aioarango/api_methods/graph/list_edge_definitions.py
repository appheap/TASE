from typing import List, Dict

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, EdgeDefinition
from aioarango.typings import Result


class ListEdgeDefinitions(Endpoint):
    error_codes = (ErrorType.GRAPH_NOT_FOUND,)
    status_codes = (
        200,
        # Is returned if the edge definitions could be listed.
        404,  # 1924
        # Returned if no graph with this name could be found.
    )

    async def list_edge_definitions(
        self,
        name: str,
    ) -> Result[List[EdgeDefinition]]:
        """
        List all edge collections within this graph.


        Parameters
        ----------
        name : str
            Name of the graph.

        Returns
        -------
        Result
            Edge definitions of the graph.

        Raises
        ------
        ValueError
            If graph name is invalid.
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        if name is None or not len(name):
            raise ValueError("`name` has invalid value!")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/gharial/{name}",
        )

        def response_handler(response: Response) -> List[EdgeDefinition]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            if "graph" not in response.body:
                raise ValueError("`name` has invalid value!")

            body: Dict = response.body["graph"]
            return [EdgeDefinition.parse_edge_definition_dict(edge_definition) for edge_definition in body["edgeDefinitions"]]

        return await self.execute(request, response_handler)
