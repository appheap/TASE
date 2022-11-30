from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Result, Params
from aioarango.utils.document_utils import prep_from_body
from aioarango.utils.graph_utils import format_vertex


class UpdateVertex((Endpoint)):
    error_codes = (
        ErrorType.ARANGO_CONFLICT,
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.GRAPH_NOT_FOUND,
    )
    status_codes = (
        200,
        # Returned if the vertex could be updated, and `waitForSync` is true.
        202,
        # Returned if the request was successful, and `waitForSync` is false.
        403,
        # Returned if your user has insufficient rights.
        # In order to update vertices in the graph you at least need to have the following privileges:
        #   1. `Read Only` access on the Database.
        #   2. `Write` access on the given collection.
        404,  # 1202, 1203, 1924
        # Returned in the following cases:
        #   - No graph with this name could be found.
        #   - This collection is not part of the graph.
        #   - The vertex to update does not exist.
        412,  # 1200
        # Returned if if-match header is given, but the stored documents revision is different.
    )

    async def update_vertex(
        self,
        graph_name: str,
        vertex_collection_name: str,
        id_prefix: str,
        vertex: Json,
        check_for_revisions_match: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
        keep_none: bool = True,
        return_old: bool = False,
        return_new: bool = False,
    ) -> Result[Json]:
        """
        Update the data of the specific vertex in the collection.


        Parameters
        ----------
        graph_name : str
            Name of the graph.
        vertex_collection_name : str
            Name of the vertex collection the vertex belongs to.
        id_prefix : str
            ID prefix for this vertex document.
        vertex : Json
            Partial or full vertex document with updated values. It must contain the "_key" or "_id" field.
        check_for_revisions_match : bool, optional
            Whether the revisions must match or not
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        keep_none : bool, default : True
            If set to `True`, fields with value None are retained
            in the document. If set to False, they are removed completely.
        return_old : bool, default : False
            Include body of the new document in the returned metadata.
        return_new : bool, default : False
            Include body of the new document in the returned metadata.


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
            If update fails.

        """
        if graph_name is None or not len(graph_name):
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        if vertex_collection_name is None or not len(vertex_collection_name):
            raise ValueError(f"`vertex_collection_name` has invalid value: `{vertex_collection_name}`")

        vertex_id, headers = prep_from_body(
            vertex,
            id_prefix,
            check_for_revisions_match=check_for_revisions_match,
        )

        params: Params = {
            "keepNull": keep_none,
            "returnNew": return_new,
            "returnOld": return_old,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        request = Request(
            method_type=MethodType.PATCH,
            endpoint=f"/_api/gharial/{graph_name}/vertex/{vertex_id}",
            headers=headers,
            params=params,
            data=vertex,
            write=vertex_collection_name,
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 202
            return format_vertex(response.body)

        return await self.execute(request, response_handler)
