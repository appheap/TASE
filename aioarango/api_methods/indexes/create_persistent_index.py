from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.models.index import BaseArangoIndex, PersistentIndex
from aioarango.typings import Result


class CreatePersistentIndex(Endpoint):
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_DUPLICATE_NAME,
    )
    status_codes = (
        200,
        # If the index already exists, then a HTTP 200 is returned.
        201,
        # If the index does not already exist and could be created, then a HTTP 201 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
        409,  # 1207
    )

    async def create_persistent_index(
        self,
        collection_name: str,
        index: PersistentIndex,
    ) -> Result[PersistentIndex]:
        """
        Create a persistent index for the collection collection-name, if
        it does not already exist. The call expects an object containing the index
        details.

        Notes
        -----
        - In a sparse index all documents will be excluded from the index that do not
          contain at least one of the specified index attributes (i.e. `fields`) or that
          have a value of `null` in any of the specified index attributes. Such documents
          will not be indexed, and not be taken into account for uniqueness checks if
          the `unique` flag is set.
        - In a non-sparse index, these documents will be indexed (for non-present
          indexed attributes, a value of `null` will be used) and will be taken into
          account for uniqueness checks if the `unique` flag is set.
        - Unique indexes on non-shard keys are not supported in a cluster.

        Parameters
        ----------
        collection_name : str
            Name of the collection.
        index : PersistentIndex
            Index to create.

        Returns
        -------
        PersistentIndex
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
            endpoint=f"/_api/index#persistent",
            data=index.to_db(),
            params={
                "collection": collection_name,
            },
        )

        def response_handler(response: Response) -> PersistentIndex:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 201
            return BaseArangoIndex.from_db(response.body)

        return await self.execute(request, response_handler)
