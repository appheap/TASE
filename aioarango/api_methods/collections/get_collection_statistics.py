from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class GetCollectionStatistics:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        # Returns information about the collection:
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def get_collection_statistics(
        self: Endpoint,
        name: str,
        show_details: Optional[bool] = False,
    ) -> Result[ArangoCollection]:
        """
        Get statistics for a collection. In addition, the result also contains the number of documents
        and additional statistical information about the collection.

        Notes
        -----
        Returns information about the collection: (status_code 200)
            - **count**: The number of documents currently present in the collection.
            - **figures**:

                - **indexes**:

                    - **count**: The total number of indexes defined for the collection, including the pre-defined indexes (e.g. primary index).
                    - **size**: The total memory allocated for indexes in bytes.


        **Warning**: Accessing collections by their numeric ID is deprecated from version 3.4.0 on. You should reference them via their names instead.


        Parameters
        ----------
        name : str
            Name of the collection.
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
        Result
            An `ArangoCollection` object. (full version with `figures` attributes set)

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/collection/{name}/figures",
            params={
                "details": show_details,
            },
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
