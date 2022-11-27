from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.models.index import BaseArangoIndex, InvertedIndex
from aioarango.typings import Result


class CreateInvertedIndex:
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_DUPLICATE_NAME,
        ErrorType.ARANGO_INDEX_CREATION_FAILED,  # todo: report this error to arangodb.com (happens when a request to create an existing index is executed)
    )
    status_codes = (
        200,
        # If the index already exists, then a HTTP 200 is returned.
        201,
        # If the index does not already exist and could be created, then a HTTP 201 is returned.
        400,  # 1235
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
        409,  # 1207
    )

    async def create_inverted_index(
        self: Endpoint,
        collection_name: str,
        index: InvertedIndex,
    ) -> Result[InvertedIndex]:
        """
        Create  an inverted index for the collection collection-name, if
        it does not already exist. The call expects an object containing the index
        details.


        Parameters
        ----------
        collection_name : str
            Name of the collection.
        index : InvertedIndex
            Index to create.

        Returns
        -------
        InvertedIndex
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
            endpoint=f"/_api/index#inverted",
            data=index.to_db(),
            params={
                "collection": collection_name,
            },
        )

        def response_handler(response: Response) -> InvertedIndex:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 201
            return BaseArangoIndex.from_db(response.body)

        return await self.execute(request, response_handler)
