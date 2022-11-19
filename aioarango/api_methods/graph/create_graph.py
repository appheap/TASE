from itertools import chain
from typing import Optional, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, GraphParseError, ErrorType
from aioarango.models import Request, Response, Graph
from aioarango.typings import Result, Json, Params


class CreateGraph:
    error_codes = (
        ErrorType.ARANGO_ILLEGAL_NAME,
        ErrorType.ARANGO_DOCUMENT_KEY_BAD,
        ErrorType.GRAPH_CREATE_MALFORMED_EDGE_DEFINITION,
        ErrorType.GRAPH_DUPLICATE,
    )
    status_codes = (
        201,
        # Is returned if the graph could be created and `waitForSync` is enabled
        # for the _graphs collection, or given in the request.
        # The response body contains the graph configuration that has been stored.
        202,
        # Is returned if the graph could be created and `waitForSync` is disabled
        # for the `_graphs` collection and not given in the request.
        # The response body contains the graph configuration that has been stored.
        400,  # 1208, 1221, 1923
        # Returned if the request is in a wrong format.
        403,
        # Returned if your user has insufficient rights.
        # In order to create a graph you at least need to have the following privileges:
        #   1. `Administrate` access on the Database.
        #   2. `Read Only` access on every collection used within this graph.
        409,  # 1925
        # Returned if there is a conflict storing the graph. This can occur
        # either if a graph with this name is already stored, or if there is one
        # edge definition with a the same edge collection but a different signature
        # used in any other graph.
    )

    async def create_graph(
        self: Endpoint,
        graph: Graph,
        satellites: Optional[List[str]] = None,
        wait_for_sync: Optional[bool] = None,
    ) -> Result[Graph]:
        """
        Create a graph.

        Notes
        -----
        - The **id**, **key** and the **rev** attributes of the input graph object must should not be set.

        Parameters
        ----------
        graph : Graph
            Graph object used to create the graph in the ArangoDB.
        satellites : list of str, optional
            An array of collection names that will be used to create SatelliteCollections
            for a Hybrid (Disjoint) SmartGraph (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be modified later.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.

        Returns
        -------
        Result
            Created graph object if operation was successful.

        Raises
        ------
        aioarango.errors.GraphParseError
            If graph input object cannot be parsed.
        aioarango.errors.ArangoServerError
            If create fails.
        """
        if graph is None or graph.name is None or not len(graph.name):
            raise GraphParseError("Input graph object is not valid.")

        params: Params = {}
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        data: Json = {"name": graph.name, "options": {}}

        if graph.edge_definitions is not None and len(graph.edge_definitions):
            edge_definitions = []
            for edge_definition_obj in graph.edge_definitions:
                if edge_definition_obj is None:
                    raise GraphParseError(f"`edge_definition` is invalid!")

                if edge_definition_obj.from_ is None or not len(edge_definition_obj.from_):
                    raise GraphParseError(f"edge_definition `{edge_definition_obj.collection}` : `from` attribute of edge_definition variable is invalid!")

                if edge_definition_obj.to is None or not len(edge_definition_obj.to):
                    raise GraphParseError(f"edge_definition `{edge_definition_obj.collection}` : `to` attribute of edge_definition variable is invalid!")

                if edge_definition_obj.collection in chain(edge_definition_obj.from_, edge_definition_obj.to):
                    raise GraphParseError(
                        f"edge_definition `collection` attribute (`{edge_definition_obj.collection}`) cannot be the same as `to` or `from` collections!"
                    )

                edge_definitions.append(
                    {
                        "collection": edge_definition_obj.collection,
                        "from": edge_definition_obj.from_,
                        "to": edge_definition_obj.to,
                    }
                )

            data["edgeDefinitions"] = edge_definitions

        if satellites is not None and len(satellites):
            data["satellites"] = satellites
        if graph.orphan_collections is not None:
            data["orphanCollections"] = graph.orphan_collections
        if graph.is_smart is not None:
            data["isSmart"] = graph.is_smart
        if graph.is_disjoint is not None:
            data["isDisjoint"] = graph.is_disjoint
        if graph.smart_graph_attribute is not None:
            data["options"]["smartGraphAttribute"] = graph.smart_graph_attribute
        if graph.number_of_shards is not None:
            data["options"]["numberOfShards"] = graph.number_of_shards
        if graph.replication_factor is not None:
            data["options"]["replicationFactor"] = graph.replication_factor
        if graph.write_concern is not None:
            data["options"]["writeConcern"] = graph.write_concern

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/gharial",
            data=data,
            params=params,
        )

        def response_handler(response: Response) -> Graph:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return Graph.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
