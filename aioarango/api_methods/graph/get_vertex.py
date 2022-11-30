from typing import Optional, Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Json
from aioarango.utils.document_utils import prep_from_doc


class GetVertex(Endpoint):
    error_codes = (
        ErrorType.ARANGO_CONFLICT,
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.GRAPH_NOT_FOUND,
    )
    status_codes = (
        200,
        # Returned if the vertex could be found.
        304,
        # Returned if the if-none-match header is given and the
        # currently stored vertex still has this revision value.
        # So there was no update between the last time the vertex
        # was fetched by the caller.
        403,
        # Returned if your user has insufficient rights.
        # In order to update vertices in the graph you at least need to have the following privileges:
        #   1. `Read Only` access on the Database.
        #   2. `Read Only` access on the given collection.
        404,  # 1202, 1203, 1924
        # Returned in the following cases:
        #   - No graph with this name could be found.
        #   - This collection is not part of the graph.
        #   - The vertex does not exist.
        412,  # 1200
        # Returned if if-match header is given, but the stored documents revision is different.
    )

    async def get_vertex(
        self,
        graph_name: str,
        vertex_collection_name,
        id_prefix: str,
        vertex: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        check_for_revisions_mismatch: Optional[bool] = None,
    ) -> Result[Json]:
        """
        Get a vertex from the given collection.


        Parameters
        ----------
        graph_name : str
            Name of the graph.
        vertex_collection_name : str
            Name of the vertex collection to retrieve this vertex from.
        id_prefix : str
            ID prefix for this vertex document.
        vertex : str or Json
            Vertex document ID, key or body. Document body must contain the "_id" or "_key" field.
        revision : str, optional
            Expected document revision. Overrides the value of "_rev" field in **vertex** if present.
        check_for_revisions_match : bool, default : None
            Whether the revisions must match or not
        check_for_revisions_mismatch : bool, default : None
            Whether the revisions must mismatch or not

        Returns
        -------
        Result
            Vertex document.

        Raises
        ------
        ValueError
            If graph name or vertex collection name is invalid.
        aioarango.errors.DocumentParseError
            If collection name is invalid or the body is `None`.
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        if graph_name is None or not len(graph_name):
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        if vertex_collection_name is None or not len(vertex_collection_name):
            raise ValueError(f"`vertex_collection_name` has invalid value: `{vertex_collection_name}`")

        handle, _, headers = prep_from_doc(
            vertex,
            id_prefix,
            revision,
            check_for_revisions_match=check_for_revisions_match,
            check_for_revisions_mismatch=check_for_revisions_mismatch,
        )

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/gharial/{graph_name}/vertex/{handle}",
            headers=headers,
            read=vertex_collection_name,
        )

        def response_handler(resp: Response) -> Optional[Json]:
            if not resp.is_success:
                raise ArangoServerError(resp, request)

            # status_code 200
            return resp.body["vertex"]

        return await self.execute(request, response_handler)
