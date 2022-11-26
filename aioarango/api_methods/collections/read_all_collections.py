import collections
from typing import List, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, ArangoCollection
from aioarango.typings import Result


class ReadAllCollections:
    error_codes = ()
    status_codes = (200,)

    async def read_all_collections(
        self: Endpoint,
        exclude_system_collection: Optional[bool] = False,
    ) -> Result[List[ArangoCollection]]:
        """
        Return a list of **ArangoCollection** objects describing each collection's description.

        Notes
        -----
        By providing the optional query parameter **excludeSystem** with a value of
        `true`, all system collections will be excluded from the response.



        Parameters
        ----------
        exclude_system_collection : bool, default : False
            Whether system collections should be excluded from the result or not.


        Returns
        -------
        Result
            A list of `ArangoCollection` objects. (the minimum version)

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/collection",
            params={
                "excludeSystem": exclude_system_collection,
            },
        )

        def response_handler(response: Response) -> List[ArangoCollection]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            res = collections.deque()
            for col_obj in response.body["result"]:
                res.append(ArangoCollection.parse_from_dict(col_obj))

            return list(res)

        return await self.execute(
            request,
            response_handler,
        )
