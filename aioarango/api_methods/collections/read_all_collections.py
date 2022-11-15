from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.models import Request, Response


class ReadAllCollections:
    async def read_all_collections(self: Endpoint):
        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/collection",
        )

        def response_handler(response: Response):
            if response is None:
                raise Exception("Invalid response")

            return response.body

        return await self.execute(
            request,
            response_handler,
        )
