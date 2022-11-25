from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class ReadCollectionProperties:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def read_collection_properties(
        self: Endpoint,
        name: str,
    ) -> Result[ArangoCollection]:
        """
        Read properties of a collection.

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

        Notes
        -----
        **Warnings**:
        Accessing collections by their numeric ID is deprecated from version 3.4.0 on.
        You should reference them via their names instead.

        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            An `ArangoCollection` object is returned.

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/collection/{name}/properties",
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
