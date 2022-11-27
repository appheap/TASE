from typing import Optional, Sequence, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType, CollectionType, KeyOptionsType, ShardingStrategy
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Response, Request, ArangoCollection, ComputedValue
from aioarango.models.key_options_input import KeyOptionsInput
from aioarango.typings import Result, Json, Params


class CreateCollection:
    error_codes = (ErrorType.ARANGO_DUPLICATE_NAME,)
    status_codes = (
        200,
        409,  # 1207
    )

    async def create_collection(
        self: Endpoint,
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
    ) -> Result:
        """
        Create a new collection with the given name.

        A json document with these Properties is returned (status_code `200`):
            - **waitForSync**: If true then creating, changing or removing documents will wait until the data has been synchronized to disk.

            - **schema**: The collection level schema for documents.

            - **computedValues**: A list of objects, each representing a computed value.
                - **name**: The name of the target attribute.
                - **expression**: An AQL RETURN operation with an expression that computes the desired value.
                - **overwrite**: Whether the computed value takes precedence over a user-provided or existing attribute.
                - **computeOn** (string): An array of strings that defines on which write operations the value is computed. The possible values are "insert", "update", and "replace".
                - **keepNull**: Whether the target attribute is set if the expression evaluates to null.
                - **failOnWarning**: Whether the write operation fails if the expression produces a warning.

            - **keyOptions**:
                - **type**: specifies the type of the key generator. The currently available generators are `traditional`, `autoincrement`, `uuid` and `padded`.
                - **allowUserKeys**: if set to `true`, then it is allowed to supply own key values in the `_key` attribute of a document. If set to `false`, then the key generator is solely responsible for generating keys and supplying own key values in the _key attribute of documents is considered an error.
                - **lastValue**: # fixme

            - **cacheEnabled**: Whether the in-memory hash cache for documents is enabled for this collection.

            - **numberOfShards**: The number of shards of the collection. (cluster only)

            - **shardKeys** (string): contains the names of document attributes that are used to determine the target shard for documents. (cluster only)

            - **replicationFactor** : contains how many copies of each shard are kept on different DB-Servers. It is an integer number in the range of 1-10 or the string "satellite" for a SatelliteCollection (Enterprise Edition only). (cluster only)

            - **writeConcern**: determines how many copies of each shard are required to be
                            in sync on the different DB-Servers. If there are less then these many copies
                            in the cluster a shard will refuse to write. Writes to shards with enough
                            up-to-date copies will succeed at the same time however. The value of
                            writeConcern cannot be larger than replicationFactor. (cluster only)

            - **shardingStrategy**: the sharding strategy selected for the collection. One of 'hash' or 'enterprise-hash-smart-edge'. (cluster only)

            - **isSmart**: Whether the collection is used in a SmartGraph (Enterprise Edition only). (cluster only)

            - **smartGraphAttribute**: Attribute that is used in SmartGraphs (Enterprise Edition only). (cluster only)

            - **smartJoinAttribute**: Determines an attribute of the collection that must contain the shard key value of the referred-to SmartJoin collection (Enterprise Edition only). (cluster only)

            - **isSystem**: `true` if this is a system collection; usually name will start with an `underscore`.

            - **name**: literal name of this collection.

            - **id**: unique identifier of the collection; **deprecated**.

            - **type**: The type of the collection:
                - 0: "unknown"
                - 2: regular document collection
                - 3: edge collection

            - **globallyUniqueId**: Unique identifier of the collection.


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
        Result
            An `ArangoCollection` object.


        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            if create fails.


        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        data: Json = {
            "name": name,
            "waitForSync": wait_for_sync,
            "isSystem": is_system,
            "keyOptions": key_options.parse_for_arangodb(),
            "type": collection_type.value,
        }
        if shard_count is not None:
            data["numberOfShards"] = shard_count
        if shard_fields is not None:
            data["shardKeys"] = shard_fields
        if replication_factor is not None:
            data["replicationFactor"] = replication_factor
        if shard_like is not None:
            data["distributeShardsLike"] = shard_like
        if sharding_strategy is not None:
            data["shardingStrategy"] = sharding_strategy.value
        if smart_join_attribute is not None:
            data["smartJoinAttribute"] = smart_join_attribute
        if write_concern is not None:
            data["writeConcern"] = write_concern
        if schema is not None:
            data["schema"] = schema
        if computed_values is not None and len(computed_values):
            data["computedValues"] = [item.parse_for_arangodb() for item in computed_values]

        params: Params = {}
        if sync_replication is not None:
            params["waitForSyncReplication"] = sync_replication
        if enforce_replication_factor is not None:
            params["enforceReplicationFactor"] = enforce_replication_factor

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/collection",
            params=params,
            data=data,
            write=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
