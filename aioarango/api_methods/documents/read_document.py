from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.models import Request, Response


class ReadDocument:
    async def read_document(
        self: Endpoint,
        collection_name: str,
        document_key: str,
    ):
        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/document/{collection_name}/{document_key}",
        )

        def response_handler(response: Response):
            if response is None:
                raise Exception("Invalid response")

            return response.body

        return await self.execute(
            request,
            response_handler,
        )
