from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Json, Params
from aioarango.utils.document_utils import ensure_key_from_id
from aioarango.utils.graph_utils import format_edge


class CreateEdge(Endpoint):
    error_codes = (
        ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED,
        ErrorType.ARANGO_INVALID_EDGE_ATTRIBUTE,
        ErrorType.GRAPH_NOT_FOUND,
        ErrorType.GRAPH_EDGE_COLLECTION_NOT_USED,
    )
    status_codes = (
        201,
        # Returned if the edge could be created and `waitForSync` is true.
        202,
        # Returned if the request was successful but `waitForSync` is false.
        400,  # 1233
        # Returned if the input document is invalid.
        # This can for instance be the case if the `_from` or `_to` attribute is missing
        # or malformed, or if the referenced vertex collection is not part of the graph.
        403,
        # Returned if your user has insufficient rights.
        # In order to insert edges into the graph you at least need to have the following privileges:
        #   1. `Read Only` access on the Database.
        #   2. `Write` access on the given collection.
        404,  # 1924, 1930
        # Returned in any of the following cases:
        #   - no graph with this name could be found.
        #   - the edge collection is not part of the graph.
        #   - the vertex collection is part of the graph, but does not exist.
        #   - `_from` or `_to` vertex does not exist.
        409,  # 1210
    )

    async def create_edge(
        self,
        graph_name: str,
        edge_collection_name: str,
        id_prefix: str,
        edge: Json,
        return_new: Optional[bool] = False,
        wait_for_sync: Optional[bool] = None,
    ) -> Result[Json]:
        """
        Create a new edge in the collection.

        Notes
        -----
        Within the body the edge has to contain a **_from** and **_to** value referencing to valid vertices in the graph.
        Furthermore, the edge has to be valid in the definition of the used edge collection.


        Parameters
        ----------
        graph_name : str
            Name of the graph.
        edge_collection_name : str
            Name of the edge collection to add the edge to.
        id_prefix : str
            ID prefix for this vertex.
        edge : Json
            New edge document to insert. If it has "_key" or "_id"
            field, its value is used as key of the new vertex (otherwise it is
            auto-generated). Any "_rev" field is ignored.
        return_new : bool, default : False
            Include body of the new document in the returned metadata.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.

        Returns
        -------
        Result
            Document metadata (e.g. document key, revision).

        Raises
        ------
        ValueError
            If graph name or edge collection name is invalid.
        aioarango.errors.DocumentParseError
            If collection name is invalid or the body is `None`.
        aioarango.errors.ArangoServerError
            If edge creation fails.

        """
        if graph_name is None or not len(graph_name):
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        if edge_collection_name is None or not len(edge_collection_name):
            raise ValueError(f"`edge_collection_name` has invalid value: `{edge_collection_name}`")

        edge = ensure_key_from_id(edge, id_prefix)

        params: Params = {
            "returnNew": return_new,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/gharial/{graph_name}/edge/{edge_collection_name}",
            data=edge,
            params=params,
            write=edge_collection_name,
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return format_edge(response.body)

        return await self.execute(request, response_handler)
