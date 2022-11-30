from typing import Optional, Union

from .base_collection import BaseCollection
from ...api_methods import GraphMethods
from ...connection import Connection
from ...errors import ArangoServerError, ErrorType, DocumentRevisionMisMatchError, DocumentRevisionMatchError, CollectionUniqueConstraintViolated
from ...executor import API_Executor
from ...typings import Json, Result


class VertexCollection(BaseCollection):
    """
    Vertex collection API wrapper.
    """

    __slots__ = [
        "_connection",
        "_executor",
        "_collections_api",
        "_index_api",
        "_graph_name",
        "_graph_api",
        "_name",
        "_id_prefix",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
        name: str,
        graph_name: str,
    ):
        super(VertexCollection, self).__init__(
            connection=connection,
            executor=executor,
            name=name,
        )

        if not graph_name:
            raise ValueError(f"`graph_name` has invalid value: `{graph_name}`")

        self._graph_name = graph_name
        self._graph_api = GraphMethods(connection=connection, executor=executor)

    def __repr__(self) -> str:
        return f"<VertexCollection {self.name}>"

    @property
    def graph_name(self) -> str:
        """
        Return the graph name.

        Returns
        -------
        str
            Graph name.
        """
        return self._graph_name

    async def get(
        self,
        vertex: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        check_for_revisions_mismatch: Optional[bool] = None,
    ) -> Result[Optional[Json]]:
        """
        Return a vertex document.

        Parameters
        ----------
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
        Json, optional
            Vertex document or None if not found.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If collection name is invalid or the body is `None`.
        aioarango.errors.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.DocumentRevisionMatchError
            If revisions match.
        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        try:
            response = await self._graph_api.get_vertex(
                graph_name=self._graph_name,
                vertex_collection_name=self.name,
                id_prefix=self.id_prefix,
                vertex=vertex,
                revision=revision,
                check_for_revisions_match=check_for_revisions_match,
                check_for_revisions_mismatch=check_for_revisions_mismatch,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND:
                return None

            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.response.status_code == 304:
                raise DocumentRevisionMatchError(e.response, e.request)

            raise e
        else:
            return response

    async def insert(
        self,
        vertex: Json,
        return_new: Optional[bool] = False,
        wait_for_sync: Optional[bool] = None,
    ) -> Result[Json]:
        """
        Add a vertex to the given collection.

        Parameters
        ----------
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
        Json
            Document metadata (e.g. document key, revision).

        Raises
        ------
        aioarango.errors.DocumentParseError
            If the body is `None`.
        aioarango.errors.CollectionUniqueConstraintViolated
            If a unique constraint of the collection is violated.
        aioarango.errors.ArangoServerError
            If insert fails.
        """
        try:
            response = await self._graph_api.create_vertex(
                graph_name=self._graph_name,
                vertex_collection_name=self.name,
                id_prefix=self.id_prefix,
                vertex=vertex,
                return_new=return_new,
                wait_for_sync=wait_for_sync,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED:
                raise CollectionUniqueConstraintViolated(e.response, e.request)

            raise e
        else:
            return response

    async def update(
        self,
        vertex: Json,
        check_for_revisions_match: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
        keep_none: bool = True,
        return_old: bool = False,
        return_new: bool = False,
        ignore_missing: Optional[bool] = False,
    ) -> Result[Optional[Json]]:
        """
        Update a vertex document.


        Parameters
        ----------
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
        ignore_missing : bool, default : False
            Do not raise an exception on missing document.

        Returns
        -------
        Json, optional
            Document metadata (e.g. document key, revision), or None if document was not found and **ignore_missing** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If the body is `None`.
        aioarango.errors.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.ArangoServerError
            If update fails.
        """
        try:
            response = await self._graph_api.update_vertex(
                graph_name=self._graph_name,
                vertex_collection_name=self.name,
                id_prefix=self.id_prefix,
                vertex=vertex,
                check_for_revisions_match=check_for_revisions_match,
                wait_for_sync=wait_for_sync,
                keep_none=keep_none,
                return_old=return_old,
                return_new=return_new,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND and ignore_missing:
                return None

            raise e
        else:
            return response

    async def replace(
        self,
        vertex: Json,
        check_for_revisions_match: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
        keep_none: bool = True,
        return_old: bool = False,
        return_new: bool = False,
        ignore_missing: Optional[bool] = False,
    ) -> Result[Optional[Json]]:
        """
        Update a vertex document.


        Parameters
        ----------
        vertex : Json
            New vertex document to replace the old one with. It must contain the "_key" or "_id" field.
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
        ignore_missing : bool, default : False
            Do not raise an exception on missing document.

        Returns
        -------
        Json, optional
            Document metadata (e.g. document key, revision), or None if document was not found and **ignore_missing** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If the body is `None`.
        aioarango.errors.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.ArangoServerError
            If replace fails.
        """
        try:
            response = await self._graph_api.replace_vertex(
                graph_name=self._graph_name,
                vertex_collection_name=self.name,
                id_prefix=self.id_prefix,
                vertex=vertex,
                check_for_revisions_match=check_for_revisions_match,
                wait_for_sync=wait_for_sync,
                keep_none=keep_none,
                return_old=return_old,
                return_new=return_new,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND and ignore_missing:
                return None

            raise e
        else:
            return response

    async def delete(
        self,
        vertex: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        wait_for_sync: Optional[bool] = None,
        return_old: bool = False,
        ignore_missing: Optional[bool] = False,
    ) -> Result[Union[bool, Json]]:
        """
        Remove a vertex from the collection.

        Parameters
        ----------
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
        ignore_missing : bool, default : False
            Do not raise an exception on missing document.

        Returns
        -------
        bool | Json
            `True` if vertex was deleted successfully, `False` if vertex was
            not deleted. (does not apply in transactions).
            Old document is returned if **return_old** is set to
            True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or the vertex is `None`.
        aioarango.errors.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.ArangoServerError
            If delete fails.
        """
        try:
            response = await self._graph_api.remove_vertex(
                graph_name=self.graph_name,
                vertex_collection_name=self.name,
                id_prefix=self.id_prefix,
                vertex=vertex,
                revision=revision,
                check_for_revisions_match=check_for_revisions_match,
                wait_for_sync=wait_for_sync,
                return_old=return_old,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND and ignore_missing:
                return False

            raise e
        else:
            return response
