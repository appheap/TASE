from typing import Optional, Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Json, Params
from aioarango.utils.document_utils import prep_from_doc


class RemoveVertex(Endpoint):
    error_codes = (
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_CONFLICT,
        ErrorType.GRAPH_NOT_FOUND,
    )
    status_codes = (
        200,
        # Returned if the vertex could be removed.
        202,
        # Returned if the request was successful but `waitForSync` is false.
        403,
        # Returned if your user has insufficient rights.
        # In order to delete vertices in the graph you at least need to have the following privileges:
        #   1. `Read Only` access on the Database.
        #   2. `Write` access on the given collection.
        404,  # 1202, 1203, 1924
        # Returned in the following cases:
        #   - No graph with this name could be found.
        #   - This collection is not part of the graph.
        #   - The vertex to remove does not exist.
        412,  # 1200
        # Returned if if-match header is given, but the stored documents revision is different.
    )

    async def remove_vertex(
        self,
        graph_name: str,
        vertex_collection_name: str,
        id_prefix: str,
        vertex: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
        return_old: bool = False,
    ) -> Result[Union[bool, Json]]:
        """
        Remove a vertex from the collection.


        Parameters
        ----------
        graph_name : str
            Name of the graph.
        vertex_collection_name : str
            Name of the vertex collection to remove the vertex from.
        id_prefix : str
            ID prefix for this vertex document.
        vertex : str or Json
            Vertex document ID, key or body. Document body must contain the "_id" or "_key" field.
        revision : str, optional
            Expected document revision. Overrides the value of "_rev" field in **vertex** if present.
        check_for_revisions_match : bool, default : True
            If set to `True`, revision of **vertex** (if given) is compared against the revision of target vertex document.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        return_old : bool, default : False
            Return body of the old document in the result.

        Returns
        -------
        Result
            `True` if vertex was deleted successfully, `False` if vertex was
            not deleted. (does not apply in transactions).
            Old document is returned if **return_old** is set to
            True.

        Raises
        ------
        ValueError
            If graph name or vertex collection name is invalid.
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or the document is `None` or if collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
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
        )

        params: Params = {"returnOld": return_old}
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/gharial/{graph_name}/vertex/{handle}",
            params=params,
            headers=headers,
            write=vertex_collection_name,
        )

        def response_handler(response: Response) -> Union[bool, Json]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            if "old" in response.body:
                return response.body["old"]
            else:
                return bool(response.body["removed"])

        return await self.execute(request, response_handler)
