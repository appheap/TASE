from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class RenameCollection(Endpoint):
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_ILLEGAL_NAME,
    )
    status_codes = (
        200,
        400,  # 1208
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def rename_collection(
        self,
        name: str,
        new_name: str,
    ) -> Result[ArangoCollection]:
        """
        Rename a collection.

        Expects an object with the attribute:
            - `name`: The new name.

        It returns an object with the attributes:
            - `id`: The identifier of the collection.
            - `name`: The new name of the collection.
            - `status`: The status of the collection as number.
            - `type`: The collection type. Valid types are:
                - `2`: document collection
                - `3`: edges collection
            - `isSystem`: If true then the collection is a system collection.

        If renaming the collection succeeds, then the collection is also renamed in
        all graph definitions inside the `_graphs` collection in the current database.

        Notes
        -----
        - This method is not available in a cluster.
        - **Warning**: Accessing collections by their numeric ID is deprecated from version 3.4.0 on. You should reference them via their names instead.


        Parameters
        ----------
        name : str
            Name of the collection to rename.
        new_name : str
            New name of the collection.

        Returns
        -------
        Result
            An `ArangoCollection` object if the operation was successful.

        Raises
        ------
        ValueError
            If old or new name of the collection is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        if new_name is None or not len(name):
            raise ValueError(f"`new_name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/rename",
            data={
                "name": new_name,
            },
            write=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
