from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, ArangoCollection
from aioarango.typings import Result


class GetCollectionChecksum:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def get_collection_checksum(
        self: Endpoint,
        name: str,
        with_revisions: Optional[bool] = False,
        with_data: Optional[bool] = False,
    ) -> Result[ArangoCollection]:
        """
        Calculate a checksum of the meta-data (keys and optionally revision ids) and optionally the document data in the collection.

        Notes
        -----
        - The checksum can be used to compare if two collections on different ArangoDB
          instances contain the same contents. The current revision of the collection is
          returned too so one can make sure the checksums are calculated for the same
          state of data.

        - By default, the checksum will only be calculated on the **_key** system attribute
          of the documents contained in the collection. For edge collections, the system
          attributes **_from** and **_to** will also be included in the calculation.

        - By setting the optional query parameter **withRevisions** to `true`, then revision
          ids (**_rev** system attributes) are included in the checksum.

        - By providing the optional query parameter **withData** with a value of `true`,
          the user-defined document attributes will be included in the calculation too.
          Note: Including user-defined attributes will make the checksum slower.



        - The response is a JSON object with the following attributes:

            - **checksum**: The calculated checksum as a number.
            - **revision**: The collection revision id as a string.

        **Warning**: Accessing collections by their numeric ID is deprecated from version 3.4.0 on.
        You should reference them via their names instead.



        Parameters
        ----------
        name : str
            Name of the collection.
        with_revisions : bool, default : False
            Whether to include document revision ids in the checksum calculation or not.
        with_data : bool, default : False
            Whether to include document body data in the checksum calculation or not.

        Returns
        -------
        Result
            An `ArangoCollection` object. (minimum version with `checksum` and `revision` attributes)

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
            endpoint=f"/_api/collection/{name}/checksum",
            params={
                "withRevisions": with_revisions,
                "withData": with_data,
            },
            read=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
