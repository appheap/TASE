from typing import Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.models.index import (
    BaseArangoIndex,
    EdgeIndex,
    FullTextIndex,
    GeoIndex,
    HashIndex,
    InvertedIndex,
    PersistentIndex,
    PrimaryIndex,
    SkipListIndex,
    TTLIndex,
    MultiDimensionalIndex,
)
from aioarango.typings import Result


class CreateIndex:
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_DUPLICATE_NAME,
    )
    status_codes = (
        200,
        # If the index already exists, then a HTTP 200 is returned.
        201,
        # If the index does not already exist and could be created, then a HTTP 201 is returned.
        400,
        # If an invalid index description is posted or attributes are used that the
        # target index will not support, then an HTTP 400 is returned
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
        409,  # 1207
    )

    async def create_index(
        self: Endpoint,
        collection_name: str,
        index: Union[
            EdgeIndex, FullTextIndex, GeoIndex, HashIndex, InvertedIndex, PersistentIndex, PrimaryIndex, SkipListIndex, TTLIndex, MultiDimensionalIndex
        ],
    ) -> Result[
        Union[EdgeIndex, FullTextIndex, GeoIndex, HashIndex, InvertedIndex, PersistentIndex, PrimaryIndex, SkipListIndex, TTLIndex, MultiDimensionalIndex]
    ]:
        """
        Create a new index in the collection. Expects an object containing the index details.

        Notes
        -----
        - The type of the index to be created must be specified in the type
          attribute of the index details. Depending on the index type, additional
          other attributes may need to specified in the request in order to create
          the index.

        - Indexes require the to be indexed attribute(s) in the fields attribute
          of the index details. Depending on the index type, a single attribute or
          multiple attributes can be indexed. In the latter case, an array of
          strings is expected.

        - Indexing the system attribute **_id** is not supported for user-defined indexes.
          Manually creating an index using **_id** as an index attribute will fail with
          an error.

        - Optionally, an index name may be specified as a string in the **name** attribute.
          Index names have the same restrictions as collection names. If no value is
          specified, one will be auto-generated.

        - Some indexes can be created as unique or non-unique variants. Uniqueness
          can be controlled for most indexes by specifying the unique flag in the
          index details. Setting it to true will create a unique index.
          Setting it to false or omitting the unique attribute will
          create a non-unique index.

        - The following index types do not support uniqueness, and using
          the **unique** attribute with these types may lead to an error:

          - **geo** indexes
          - **fulltext** indexes (deprecated from ArangoDB 3.10 onwards)

        - Unique indexes on non-shard keys are not supported in a cluster.

        - Persistent indexes can optionally be created in a `sparse`
          variant. A `sparse` index will be created if the **sparse** attribute in
          the index details is set to `true`. Sparse indexes do not index documents
          for which any of the index attributes is either not set or is `null`.

        - The optional **deduplicate** attribute is supported by array indexes of type
          `persistent`. It controls whether inserting duplicate index values
          from the same document into a unique array index will lead to a unique constraint
          error or not. The default value is `true`, so only a single instance of each
          non-unique index value will be inserted into the index per document. Trying to
          insert a value into the index that already exists in the index will always fail,
          regardless of the value of this attribute.

        - The optional attribute **estimates** is supported by indexes of type
          `persistent`. This attribute controls whether index selectivity estimates are
          maintained for the index. Not maintaining index selectivity estimates can have
          a slightly positive impact on write performance.
          The downside of turning off index selectivity estimates will be that
          the query optimizer will not be able to determine the usefulness of different
          competing indexes in AQL queries when there are multiple candidate indexes to
          choose from.
          The estimates attribute is optional and defaults to `true` if not set. It will
          have no effect on indexes other than persistent.

        - The optional attribute **cacheEnabled** is supported by indexes of type
          `persistent`. This attribute controls whether an extra in-memory hash cache is
          created for the index. The hash cache can be used to speed up index lookups.
          The cache can only be used for queries that look up all index attributes via
          an equality lookup (==). The hash cache cannot be used for range scans,
          partial lookups or sorting.

          The cache will be populated lazily upon reading data from the index. Writing data
          into the collection or updating existing data will invalidate entries in the
          cache. The cache may have a negative effect on performance in case index values
          are updated more often than they are read.

          The maximum size of cache entries that can be stored is currently `4` MB, i.e.
          the cumulated size of all index entries for any index lookup value must be
          less than `4` MB. This limitation is there to avoid storing the index entries
          of "super nodes" in the cache.

          **cacheEnabled** defaults to `false` and should only be used for indexes that
          are known to benefit from an extra layer of caching.

        - The optional attribute **inBackground** can be set to `true` to create the index
          in the background, which will not write-lock the underlying collection for
          as long as if the index is built in the foreground.



        Parameters
        ----------
        collection_name : str
            Name of the collection.
        index : GeoIndex
            Index to create.

        Returns
        -------
        GeoIndex
            Created Index will be returned.

        Raises
        ------
        ValueError
            If collection name or the type of index is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if collection_name is None or not len(collection_name):
            raise ValueError(f"`collection_name` has invalid value: `{collection_name}`")

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/index",
            data=index.to_db(),
            params={
                "collection": collection_name,
            },
        )

        def response_handler(
            response: Response,
        ) -> Union[EdgeIndex, FullTextIndex, GeoIndex, HashIndex, InvertedIndex, PersistentIndex, PrimaryIndex, SkipListIndex, TTLIndex, MultiDimensionalIndex]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 201
            return BaseArangoIndex.from_db(response.body)

        return await self.execute(request, response_handler)
