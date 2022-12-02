from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.models.index import BaseArangoIndex, GeoIndex
from aioarango.typings import Result


class CreateGeoIndex(Endpoint):
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

    async def create_geo_index(
        self,
        collection_name: str,
        index: GeoIndex,
    ) -> Result[GeoIndex]:
        """
        Create a geo-spatial index in the collection collection-name, if
        it does not already exist. Expects an object containing the index details.

        Notes
        -----
        Geo indexes are always sparse, meaning that documents that do not contain
        the index attributes or have non-numeric values in the index attributes
        will not be indexed.

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
            endpoint=f"/_api/index#geo",
            data=index.to_db(),
            params={
                "collection": collection_name,
            },
        )

        def response_handler(response: Response) -> GeoIndex:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 201
            return BaseArangoIndex.from_db(response.body)

        return await self.execute(request, response_handler)
