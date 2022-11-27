from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class CompactCollectionData:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        # Compaction started successfully
        401,
        # if the request was not authenticated as a user with sufficient rights
        404,  # 1203
    )

    async def compact_collection_data(
        self: Endpoint,
        name: str,
    ) -> Result[ArangoCollection]:
        """
        Compact the data of a collection in order to reclaim disk space.
        The operation will compact the document and index data by rewriting the
        underlying .sst files and only keeping the relevant entries.

        Notes
        -----
        Under normal circumstances, running a compact operation is not necessary, as
        the collection data will eventually get compacted anyway. However, in some
        situations, e.g. after running lots of update/replace or remove operations,
        the disk data for a collection may contain a lot of outdated data for which the
        space shall be reclaimed. In this case the compaction operation can be used.

        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            An `ArangoCollection` object. (minimum version)

        Raises
        ------
        ValueError
            If name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/compact",
            write=name,  # fixme: is this valid?
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
