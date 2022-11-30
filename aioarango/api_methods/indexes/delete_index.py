from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result


class DeleteIndex(Endpoint):
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_INDEX_NOT_FOUND,
    )
    status_codes = (
        200,
        # If the index could be deleted, then an HTTP 200 is returned.
        404,  # 1203, 1212
        # If the index does not exist, then a HTTP 404 is returned.
    )

    async def delete_index(
        self,
        index_id: str,
    ) -> Result[bool]:
        """
        Delete an index with **index_id**.

        Parameters
        ----------
        index_id : str
            ID of the index to delete.

        Returns
        -------
        Result
            `True` if the index was deleted successfully.

        Raises
        ------
        ValueError
            If `index_id` is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if index_id is None or not len(index_id):
            raise ValueError(f"`index_id` has invalid value: `{index_id}`")

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/index/{index_id}",
        )

        def response_handler(
            response: Response,
        ) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return True

        return await self.execute(request, response_handler)
