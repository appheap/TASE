from typing import Optional, List, Sequence, Union

from .aql import AQL
from .collection import StandardCollection
from ..api_methods import APIMethods
from ..connection import Connection
from ..enums import ShardingMethod, CollectionType, KeyOptionsType, ShardingStrategy
from ..errors import ArangoServerError, ErrorType
from ..executor import API_Executor
from ..models import ArangoCollection, User, ComputedValue
from ..models.key_options_input import KeyOptionsInput
from ..typings import Result, Json


class Database:
    """Base class for Database API wrappers."""

    __slots__ = [
        "_connection",
        "_executor",
        "_api",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
    ):
        self._connection = connection
        self._executor = executor

        self._api = APIMethods(connection, executor)

    @property
    def aql(self) -> AQL:
        return AQL(self._connection, self._executor)

    #######################
    # Database Management #
    #######################
    async def databases(self) -> Result[List[str]]:
        """
        Return the names of all databases.

        Notes
        -----
        - retrieving the list of databases is only possible from within the **_system** database.

        Returns
        -------
        list
            Database names.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        return await self._api.list_of_databases()

    async def has_database(
        self,
        name: str,
    ) -> Result[bool]:
        """
        Return the names of all databases.

        Notes
        -----
        - retrieving the list of databases is only possible from within the **_system** database.


        Parameters
        ----------
        name : str
            Name of the database to check.

        Returns
        -------
        bool
            `True` if the database exists, `False` otherwise.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        return name in await self._api.list_of_databases()

    async def create_database(
        self,
        name: str,
        users: Optional[Sequence[User]] = None,
        replication_factor: Union[int, str, None] = None,
        write_concern: Optional[int] = None,
        sharding: Optional[ShardingMethod] = None,
    ) -> Result[bool]:
        """
        Create a new database.

        Notes
        -----
        -  creating a new database is only possible from within the **_system** database.


        Parameters
        ----------
        name : str
            Database name.

        users : list of User
            List of users with access to the new database, where each
            user is a dictionary with fields "username", "password", "active"
            and "extra" (see below for example). If not set, only the admin and
            current user are granted access.

        replication_factor : int or str, optional
            Default replication factor for collections
            created in this database. Special values include "satellite" which
            replicates the collection to every DBServer, and 1 which disables
            replication. Used for clusters only.

        write_concern : int, optional
            Default write concern for collections created in
            this database. Determines how many copies of each shard are
            required to be in sync on different DBServers. If there are less
            than these many copies in the cluster a shard will refuse to write.
            Writes to shards with enough up-to-date copies will succeed at the
            same time, however. Value of this parameter can not be larger than
            the value of **replication_factor**. Used for clusters only.

        sharding : ShardingMethod, optional
            Sharding method used for new collections in this
            database. Allowed values are: "", "flexible" and "single". The
            first two are equivalent. Used for clusters only.

        Returns
        -------
        Result
            True if database was created successfully.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If insert fails.

        """
        return await self._api.create_database(
            name=name,
            users=users,
            replication_factor=replication_factor,
            write_concern=write_concern,
            sharding=sharding,
        )

    async def delete_database(
        self,
        name: str,
        ignore_missing: Optional[bool] = False,
    ) -> Result[bool]:
        """
        Delete a database along with all data stored in it.

        Notes
        -----
        dropping a database is only possible from within the **_system** database.
        The **_system** database itself cannot be dropped.


        Parameters
        ----------
        name : str
            Database name.
        ignore_missing : bool, default : False
            Do not raise an exception on missing database.

        Returns
        -------
        bool
            `True` if database was deleted successfully, `False` if database
            was not found and **ignore_missing** was set to `True`.

        Raises
        ------
        aioarango.server.ArangoServerError
            If delete fails.
        """
        try:
            response = await self._api.drop_database(name=name)
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_DATABASE_NOT_FOUND and ignore_missing:
                return False

            raise e

        else:
            return response

    #########################
    # Collection Management #
    #########################

    def collection(
        self,
        name: str,
    ) -> StandardCollection:
        """
        Return the standard collection API wrapper.

        Parameters
        ----------
        name : str
            Collection name.

        Returns
        -------
        StandardCollection
            Standard collection API wrapper.

        Raises
        ------
        ValueError
            If `name` has invalid value.

        """
        if not name:
            raise ValueError(f"`name` has invalid value: `{name}`")

        return StandardCollection(
            connection=self._connection,
            executor=self._executor,
            name=name,
        )

    async def has_collection(
        self,
        name: str,
        exclude_system_collection: Optional[bool] = False,
    ) -> Result[bool]:
        """
        Check if a collection exists in the database.

        Parameters
        ----------
        name : str
            Name of the collection to check.
        exclude_system_collection : bool, default : False
            Whether system collections should be excluded from the result or not.


        Returns
        -------
        bool
            `True` if the collection exists, `False` otherwise.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        return any(
            col.name == name
            for col in await self._api.read_all_collections(
                exclude_system_collection=exclude_system_collection,
            )
        )

    async def collections(
        self,
        exclude_system_collection: Optional[bool] = False,
    ) -> Result[List[ArangoCollection]]:
        """
        Return the collections in the database.

        Parameters
        ----------
        exclude_system_collection : bool, default : False
            Whether system collections should be excluded from the result or not.


        Returns
        -------
        list
            A list of `ArangoCollection` objects. (the minimum version)

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        return await self._api.read_all_collections(
            exclude_system_collection=exclude_system_collection,
        )

    async def create_collection(
        self,
        name: str,
        wait_for_sync: bool = False,
        is_system: bool = False,
        collection_type: CollectionType = CollectionType.DOCUMENT,
        key_options: Optional[KeyOptionsInput] = KeyOptionsInput(type=KeyOptionsType.TRADITIONAL, allow_user_keys=True),
        shard_fields: Optional[Sequence[str]] = None,
        shard_count: Optional[int] = None,
        replication_factor: Optional[int] = None,
        shard_like: Optional[str] = None,
        sync_replication: Optional[bool] = None,
        enforce_replication_factor: Optional[bool] = None,
        sharding_strategy: Optional[ShardingStrategy] = None,
        smart_join_attribute: Optional[str] = None,
        write_concern: Optional[int] = None,
        schema: Optional[Json] = None,
        computed_values: Optional[List[ComputedValue]] = None,
    ) -> Result[StandardCollection]:
        """
        Create a new collection.

        Parameters
        ----------
        name : str
            Collection name.
        wait_for_sync : bool, default : False
            If set to `True`, document operations via the collection will block until synchronized to disk by default.
        is_system : bool, default : False
            If set to `True`, a system collection is created. The collection name must have leading underscore "_" character.
        collection_type : CollectionType, default : CollectionType.DOCUMENT
            Type of the collection, it can be `EDGE` or `DOCUMENT`.
        key_options : KeyOptionsInput, optional
            Key Options object.
        shard_fields : list of str, optional
            Field(s) used to determine the target shard.
        shard_count : int, optional
            Number of shards to create.
        replication_factor : int, optional
            Number of copies of each shard on different
            servers in a cluster. Allowed values are `1` (only one copy is kept
            and no synchronous replication), and `n` (n-1 replicas are kept and
            any two copies are replicated across servers synchronously, meaning
            every write to the master is copied to all slaves before operation
            is reported successful).
        shard_like : str, optional
            Name of prototype collection whose sharding
            specifics are imitated. Prototype collections cannot be dropped
            before imitating collections. Applies to enterprise version of ArangoDB only.
        sync_replication : bool, optional
            If set to `True`, server reports success only
            when collection is created in all replicas. You can set this to
            `False` for faster server response, and if full replication is not a
            concern.
        enforce_replication_factor : bool, optional
            Check if there are enough replicas available at creation time, or halt the operation.
        sharding_strategy : ShardingStrategy, optional
            Sharding strategy. Available for ArangoDB
            version  and up only. Possible values are "community-compat",
            "enterprise-compat", "enterprise-smart-edge-compat", "hash" and
            "enterprise-hash-smart-edge". Refer to ArangoDB documentation for more details on each value.
        smart_join_attribute : str, optional
            Attribute of the collection which must
            contain the shard key value of the smart join collection. The shard
            key for the documents must contain the value of this attribute,
            followed by a colon ":" and the primary key of the document.
            Requires parameter **shard_like** to be set to the name of another
            collection, and parameter **shard_fields** to be set to a single
            shard key attribute, with another colon ":" at the end. Available
            only for enterprise version of ArangoDB.
        write_concern : int, optional
            Write concern for the collection. Determines how
            many copies of each shard are required to be in sync on different
            DBServers. If there are less than these many copies in the cluster
            a shard will refuse to write. Writes to shards with enough
            up-to-date copies will succeed at the same time. The value of this
            parameter cannot be larger than that of **replication_factor**.
            Default value is 1. Used for clusters only.
        schema : dict, optional
            Dictionary specifying the collection level schema
            for documents. See ArangoDB documentation for more information on
            document schema validation.
        computed_values : list of ComputedValue
            Array of computed values for the new collection
            enabling default values to new documents or the maintenance of
            auxiliary attributes for search queries. Available in ArangoDB
            version 3.10 or greater. See ArangoDB documentation for more information on computed values.

        Returns
        -------
        StandardCollection
            Standard collection API wrapper.

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            if create fails.
        """
        response = await self._api.create_collection(
            name=name,
            wait_for_sync=wait_for_sync,
            is_system=is_system,
            collection_type=collection_type,
            key_options=key_options,
            shard_fields=shard_fields,
            shard_count=shard_count,
            replication_factor=replication_factor,
            shard_like=shard_like,
            sync_replication=sync_replication,
            enforce_replication_factor=enforce_replication_factor,
            sharding_strategy=sharding_strategy,
            smart_join_attribute=smart_join_attribute,
            write_concern=write_concern,
            schema=schema,
            computed_values=computed_values,
        )

        return StandardCollection(
            connection=self._connection,
            executor=self._executor,
            name=response.name,
        )

    async def delete_collection(
        self,
        name: str,
        is_system_collection: Optional[bool] = None,
        ignore_missing: Optional[bool] = False,
    ) -> Result[bool]:
        """
        Delete a collection.

        Parameters
        ----------
        name :
        is_system_collection : bool, optional
            Whether the collection is a system collection or not.
        ignore_missing : bool, default : False
            Do not raise an exception on missing collection.

        Returns
        -------
        bool
            `True` if collection was deleted successfully, `False` if
            collection was not found and **ignore_missing** was set to `True`.

        Raises
        ------
        aioarango.errors.ArangoServerError
            if delete fails.
        """
        try:
            response = await self._api.drop_collection(name=name, is_system_collection=is_system_collection)
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND and ignore_missing:
                return False

            raise e
        else:
            return response

    ####################
    # Graph Management #
    ####################
