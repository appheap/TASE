from itertools import chain
from typing import Optional, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, EdgeDefinition, GraphInfo
from aioarango.typings import Result, Params


class ReplaceEdgeDefinition(Endpoint):
    error_codes = (
        ErrorType.ARANGO_ILLEGAL_NAME,
        ErrorType.GRAPH_COLLECTION_MULTI_USE,
        ErrorType.GRAPH_NOT_FOUND,
        ErrorType.GRAPH_EDGE_COLLECTION_NOT_USED,
    )
    status_codes = (
        201,
        # Returned if the request was successful and `waitForSync` is true.
        202,
        # Returned if the request was successful but `waitForSync` is false.
        400,  # 1208, 1920
        # Returned if the new edge definition is ill-formed and cannot be used.
        403,
        # Returned if your user has insufficient rights.
        # In order to drop a vertex you at least need to have the following privileges:
        #   1. `Administrate` access on the Database.
        404,  # 1924, 1930
        # Returned if no graph with this name could be found, or if no edge definition
        # with this name is found in the graph.
    )

    async def replace_edge_definition(
        self,
        graph_name: str,
        edge_definition: EdgeDefinition,
        satellites: Optional[List[str]] = None,
        wait_for_sync: Optional[bool] = None,
        drop_collections: Optional[bool] = None,
    ) -> Result:
        """
        Change one specific edge definition.
        This will modify all occurrences of this definition in all graphs known to your database.

        Parameters
        ----------
        graph_name : str
            Name of the graph.
        edge_definition : EdgeDefinition
            Edge definition to replace the existing edge definition in the graph.
        satellites : list of str, optional
             An array of collection names that will be used to create SatelliteCollections
            for a `Hybrid` (Disjoint) `SmartGraph` (Enterprise Edition only). Each array element
            must be a string and a valid collection name. The collection type cannot be
            modified later.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        drop_collections: bool, optional
            Drop the collection as well.
            Collection will only be dropped if it is not used in other graphs.

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

        params: Params = {}
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        if drop_collections is not None:
            params["dropCollections"] = drop_collections

        data = {
            "collection": edge_definition.collection,
            "from": edge_definition.from_,
            "to": edge_definition.to,
        }
        if satellites is not None and len(satellites):  # todo: check if this works correctly
            data["options"] = {}
            data["options"]["satellites"] = satellites

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/gharial/{graph_name}/edge/{edge_definition.collection}",
            data=data,
            params=params if len(params) else None,
            write=edge_definition.collection,
        )

        def response_handler(response: Response) -> GraphInfo:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return GraphInfo.parse_graph_dict(response.body["graph"])

        return await self.execute(request, response_handler)
