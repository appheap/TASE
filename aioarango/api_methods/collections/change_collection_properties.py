from typing import Optional, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response, ComputedValue
from aioarango.typings import Result, Json


class ChangeCollectionProperties(Endpoint):
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def change_collection_properties(
        self,
        name: str,
        wait_for_sync: Optional[bool] = None,
        enable_cache: Optional[bool] = None,
        schema: Optional[Json] = None,
        computed_values: Optional[List[ComputedValue]] = None,
        replication_factor: Optional[int] = None,
        write_concern: Optional[int] = None,
    ) -> Result[ArangoCollection]:
        """
        Change the properties of a collection. Only the provided attributes are
        updated. Collection properties cannot be changed once a collection is
        created except for the listed properties, as well as the collection name via
        the rename endpoint (but not in clusters).

        Parameters
        ----------
        name : str
            Name of the collection.
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
        Result
            An `ArangoCollection` object. (full version)

        Raises
        ------
        ValueError
            If collection name is invalid or no parameter is set.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        data = {}
        if wait_for_sync is not None:
            data["waitForSync"] = wait_for_sync
        if enable_cache is not None:
            data["cacheEnabled"] = enable_cache
        if schema is not None:
            data["schema"] = schema
        if computed_values is not None and len(computed_values):
            data["computedValues"] = [item.parse_for_arangodb() for item in computed_values]
        if replication_factor is not None:
            data["replicationFactor"] = replication_factor
        if write_concern is not None:
            data["writeConcern"] = write_concern

        if not len(data):
            raise ValueError(f"`data` dictionary must have at least one entry: `{data}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/properties",
            data=data,
            write=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
