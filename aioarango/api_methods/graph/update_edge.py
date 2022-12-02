from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Result, Params
from aioarango.utils.document_utils import prep_from_body
from aioarango.utils.graph_utils import format_edge


class UpdateEdge(Endpoint):
    error_codes = (
        ErrorType.ARANGO_CONFLICT,
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.GRAPH_NOT_FOUND,
    )
    status_codes = (
        200,
        # Returned if the edge could be updated, and `waitForSync` is true.
        202,
        # Returned if the request was successful, and `waitForSync` is false.
        403,
        # Returned if your user has insufficient rights.
        # In order to update edges in the graph you at least need to have the following privileges:
        #   1. `Read Only` access on the Database.
        #   2. `Write` access on the given collection.
        404,  # 1202, 1203, 1924
        # Returned in the following cases:
        #   - No graph with this name could be found.
        #   - This collection is not part of the graph.
        #   - The edge to update does not exist.
        #   - either `_from` or `_to` vertex does not exist (if updated).
        412,  # 1200
        # Returned if if-match header is given, but the stored documents revision is different.
    )

    async def update_edge(
        self,
        graph_name: str,
        edge_collection_name: str,
        id_prefix: str,
        edge: Json,
        check_for_revisions_match: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
        keep_none: bool = True,
        return_old: bool = False,
        return_new: bool = False,
    ) -> Result[Json]:
        """
        Update the data of the specific edge in the collection.


        Parameters
        ----------
        graph_name : str
            Name of the graph.
        edge_collection_name : str
            Name of the edge collection the edge belongs to.
        id_prefix : str
            ID prefix for this edge document.
        edge : Json
            Edge document ID, key or body. Document body must contain the "_id" or "_key" field.
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
            If graph name or edge collection name is invalid.
        aioarango.errors.DocumentParseError
            If collection name is invalid or the body is `None`.
        aioarango.errors.ArangoServerError
            If update fails.

        """
        if graph_name is None or not len(graph_name):
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        if edge_collection_name is None or not len(edge_collection_name):
            raise ValueError(f"`edge_collection_name` has invalid value: `{edge_collection_name}`")

        edge_id, headers = prep_from_body(
            edge,
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
            endpoint=f"/_api/gharial/{graph_name}/edge/{edge_id}",
            headers=headers,
            params=params,
            data=edge,
            write=edge_collection_name,
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 202
            return format_edge(response.body)

        return await self.execute(request, response_handler)
