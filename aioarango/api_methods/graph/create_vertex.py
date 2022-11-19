from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Result, Params
from aioarango.utils.document_utils import ensure_key_from_id
from aioarango.utils.graph_utils import format_vertex


class CreateVertex:
    error_types = (
        ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED,
        ErrorType.ARANGO_DOCUMENT_KEY_BAD,
        ErrorType.GRAPH_NOT_FOUND,
        ErrorType.GRAPH_REFERENCED_VERTEX_COLLECTION_NOT_USED,
    )
    status_codes = (
        201,
        # Returned if the vertex could be added and `waitForSync` is true.
        202,
        # Returned if the request was successful but `waitForSync` is false.
        400,  # 1221
        403,
        # Returned if your user has insufficient rights.
        # In order to insert vertices into the graph you at least need to have the following privileges:
        #   1. `Read Only `access on the Database.
        #   2. `Write` access on the given collection.
        404,  # 1924, 1947
        # Returned if no graph with this name could be found.
        # Or if a graph is found but this collection is not part of the graph
        409,  # 1210
    )

    async def create_vertex(
        self: Endpoint,
        graph_name: str,
        vertex_collection_name: str,
        id_prefix: str,
        vertex: Json,
        return_new: Optional[bool] = False,
        wait_for_sync: Optional[bool] = None,
    ) -> Result[Json]:
        """
        Add a vertex to the given collection.

        Parameters
        ----------
        graph_name : str
            Name of the graph.
        vertex_collection_name : str
            Name of the vertex collection to add the vertex to.
        id_prefix : str
            ID prefix for this vertex.
        vertex : Json
            New vertex document to insert. If it has "_key" or "_id"
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
            If graph name or vertex collection name is invalid.
        aioarango.errors.DocumentParseError
            If collection name is invalid or the body is `None`.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if graph_name is None or not len(graph_name):
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        if vertex_collection_name is None or not len(vertex_collection_name):
            raise ValueError(f"`vertex_collection_name` has invalid value: `{vertex_collection_name}`")

        vertex = ensure_key_from_id(vertex, id_prefix)

        params: Params = {}
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        if return_new is not None:
            params["returnNew"] = return_new

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/gharial/{graph_name}/vertex/{vertex_collection_name}",
            data=vertex,
            params=params if len(params) else None,
            write=vertex_collection_name,
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201, 202
            return format_vertex(response.body)

        return await self.execute(request, response_handler)
