from typing import Optional, List, Union

from aioarango.api_methods import CollectionsMethods, IndexesMethods
from aioarango.connection import Connection
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.executor import API_Executor
from aioarango.models import ArangoCollection, ComputedValue
from aioarango.models.index import (
    BaseArangoIndex,
)
from aioarango.typings import Result, Json, ArangoIndex


class BaseCollection:
    """
    Base class for collection API wrappers.
    """

    __slots__ = [
        "_connection",
        "_executor",
        "_collections_api",
        "_index_api",
        "_name",
        "_id_prefix",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
        name: str,
    ):
        if not name:
            raise ValueError(f"`name` has invalid value: `{name}`")

        self._connection = connection
        self._executor = executor
        self._name = name
        self._id_prefix = name + "/"

        self._collections_api = CollectionsMethods(connection, executor)
        self._index_api = IndexesMethods(connection, executor)

    @property
    def name(self) -> str:
        """
        Return the collection name.

        Returns
        -------
        str
            Collection name.

        """
        return self._name

    @property
    def id_prefix(self) -> str:
        """
        Return the collection ID prefix.

        Returns
        -------
        str
            Collection ID prefix.

        """
        return self._id_prefix

    async def revision(self) -> Result[str]:
        """
        Return collection revision.

        Returns
        -------
        str
            Collection revision.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._collections_api.get_collection_revision(name=self.name)

    async def checksum(
        self,
        with_revisions: Optional[bool] = False,
        with_data: Optional[bool] = False,
    ) -> Result[ArangoCollection]:
        """
        Return collection checksum.

        Parameters
        ----------
        with_revisions : bool, default : False
            Whether to include document revision ids in the checksum calculation or not.
        with_data : bool, default : False
            Whether to include document body data in the checksum calculation or not.

        Returns
        -------
        ArangoCollection
            An `ArangoCollection` object. (minimum version with `checksum` and `revision` attributes)

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._collections_api.get_collection_checksum(
            name=self.name,
            with_revisions=with_revisions,
            with_data=with_data,
        )

    async def properties(self) -> Result[ArangoCollection]:
        """
        Return collection properties.

        Returns
        -------
        ArangoCollection
            An `ArangoCollection` object is returned. (full version?)

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        return await self._collections_api.read_collection_properties(name=self.name)

    async def configure(
        self,
        wait_for_sync: Optional[bool] = None,
        enable_cache: Optional[bool] = None,
        schema: Optional[Json] = None,
        computed_values: Optional[List[ComputedValue]] = None,
        replication_factor: Optional[int] = None,
        write_concern: Optional[int] = None,
    ) -> Result[ArangoCollection]:
        """
        Configure collection properties.

        Parameters
        ----------
        wait_for_sync : bool, optional
            If `true` then the data is synchronized to disk before returning from a
            document create, update, replace or removal operation. (default: `false`)
        enable_cache : bool, optional
            Whether the in-memory hash cache for documents should be enabled for this
            collection (default: `false`). Can be controlled globally with the **--cache.size**
            startup option. The cache can speed up repeated reads of the same documents via
            their document keys. If the same documents are not fetched often or are
            modified frequently, then you may disable the cache to avoid the maintenance
            costs.
        schema : Json, optional
            Object that specifies the collection level schema for
            documents. The attribute keys `rule`, `level` and `message` must follow the
            rules documented in "Document Schema Validation".
        computed_values : list of ComputedValue, optional
            An optional list of objects, each representing a computed value.
        replication_factor : int, optional
            (The default is `1`): in a cluster, this attribute determines how many copies
            of each shard are kept on different DB-Servers. The value `1` means that only one
            copy (no synchronous replication) is kept. A value of k means that `k-1` replicas
            are kept. It can also be the string "satellite" for a SatelliteCollection,
            where the replication factor is matched to the number of DB-Servers
            (Enterprise Edition only).
            Any two copies reside on different DB-Servers. Replication between them is
            synchronous, that is, every write operation to the "leader" copy will be replicated
            to all "follower" replicas, before the write operation is reported successful.
            If a server fails, this is detected automatically and one of the servers holding
            copies take over, usually without an error being reported.
        write_concern : int, optional
            Write concern for this collection (default: `1`).
            It determines how many copies of each shard are required to be
            in sync on the different DB-Servers. If there are less then these many copies
            in the cluster a shard will refuse to write. Writes to shards with enough
            up-to-date copies will succeed at the same time however. The value of
            writeConcern can not be larger than replicationFactor. (cluster only)

        Returns
        -------
        ArangoCollection
            An `ArangoCollection` object. (full version)

        Raises
        ------
        ValueError
            If no parameter is set.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._collections_api.change_collection_properties(
            name=self.name,
            wait_for_sync=wait_for_sync,
            enable_cache=enable_cache,
            schema=schema,
            computed_values=computed_values,
            replication_factor=replication_factor,
            write_concern=write_concern,
        )

    async def statistics(
        self,
        show_details: Optional[bool] = False,
    ) -> Result[ArangoCollection]:
        """
        Return collection statistics.

        Parameters
        ----------
        show_details : bool, default : False
            Setting details to `true` will return extended storage engine-specific
            details to the figures. The details are intended for debugging ArangoDB itself
            and their format is subject to change. By default, details is set to `false`,
            so no details are returned and the behavior is identical to previous versions
            of ArangoDB.
            Please note that requesting details may cause additional load and thus have
            an impact on performance.

        Returns
        -------
        ArangoCollection
            An `ArangoCollection` object. (full version with `figures` attributes set)

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._collections_api.get_collection_statistics(
            name=self.name,
            show_details=show_details,
        )

    async def truncate(
        self,
        wait_for_sync: Optional[bool] = False,
        compact: Optional[bool] = True,
    ) -> Result[bool]:
        """
        Delete all documents in the collection.

        Parameters
        ----------
        wait_for_sync : bool, default : False
            If true then the data is synchronized to disk before returning from the truncate operation (default: false)
        compact : bool, default : True
            If `true` (default) then the storage engine is told to start a compaction
            in order to free up disk space. This can be resource intensive. If the only
            intention is to start over with an empty collection, specify `false`.

        Returns
        -------
        bool
            True if collection was truncated successfully.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return bool(
            await self._collections_api.truncate_collection(
                name=self.name,
                wait_for_sync=wait_for_sync,
                compact=compact,
            )
        )

    async def count(self) -> Result[int]:
        """
        Return the total document count.

        Returns
        -------
        int
            Total document count.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        response = await self._collections_api.get_collection_document_count(name=self.name)
        return response.count

    async def rename(
        self,
        new_name: str,
    ) -> Result[bool]:
        """
        Rename the collection.

        Parameters
        ----------
        new_name : str
            New name of the collection.

        Returns
        -------
        bool
            `True` if the collection was renamed successfully.

        Raises
        ------
        ValueError
            If new name of the collection is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        response = await self._collections_api.rename_collection(
            name=self.name,
            new_name=new_name,
        )

        self._name = response.name
        self._id_prefix = response.name + "/"
        return True

    async def recalculate_count(self) -> Result[bool]:
        """
        Recalculate the document count.

        Returns
        -------
        Result
            `True` if the recalculation was successful.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._collections_api.recalculate_collection_document_count(name=self.name)

    async def responsible_shard(
        self,
        document: Union[str, Json],
    ) -> Result[str]:
        """
        Return the ID of the shard responsible for given **document**.

        If the document does not exist, return the shard that would be
        responsible.

        Parameters
        ----------
        document : str or Json
            Document ID, key or body.

        Returns
        -------
        str
            Responsible Shard ID for the document.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._collections_api.get_document_responsible_shard(
            name=self.name,
            document=document,
            id_prefix=self.id_prefix,
        )

    ####################
    # Index Management #
    ####################

    async def indexes(
        self,
        with_stats: Optional[bool] = False,
        with_hidden: Optional[bool] = False,
    ) -> Result[List[BaseArangoIndex]]:
        """
        Return the collection indexes.

        Parameters
        ----------
        with_stats : bool, default : False
            Whether to include figures and estimates in the result or not.
        with_hidden : bool, default : False
            Whether to include hidden indexes in the result or not.

        Returns
        -------
        list
            List of all indexes of the collection.

        Raises
        ------
        ValueError
            If the `type` of an index in invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._index_api.read_all_collection_indexes(
            name=self.name,
            with_stats=with_stats,
            with_hidden=with_hidden,
        )

    async def add_index(
        self,
        index: ArangoIndex,
    ) -> Result[ArangoIndex]:
        """
        Create a new index.

        Parameters
        ----------
        index : ArangoIndex
            Index to create.

        Returns
        -------
        ArangoIndex
            Created Index will be returned.

        Raises
        ------
        ValueError
            If the `type` of index is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._index_api.create_index(
            collection_name=self.name,
            index=index,
        )

    async def delete_index(
        self,
        index_id: str,
        ignore_missing: Optional[bool] = False,
    ) -> Result[bool]:
        """
        Delete an index.

        Parameters
        ----------
        index_id : str
            ID of the index to delete.
        ignore_missing : bool, default : False
            Do not raise an exception on missing index.

        Returns
        -------
        Result
            `True` if index was deleted successfully, `False` if index was
            not found and **ignore_missing** was set to `True`.

        Raises
        ------
        ValueError
            If `index_id` is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        try:
            response = await self._index_api.delete_index(index_id=index_id)
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_INDEX_NOT_FOUND and ignore_missing:
                return False

            raise e
        else:
            return response

    async def load_indexes(self) -> Result[bool]:
        """
        Cache all indexes in the collection into memory.

        Returns
        -------
        bool
            `True` if index was loaded successfully.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._collections_api.load_indexes_into_memory(name=self.name)

    #################################
    # Document Management
    #################################
