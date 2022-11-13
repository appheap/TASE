from pydantic import BaseModel

from aioarango.methods import Methods


class ArangoClient(BaseModel):
    host: str
    methods: Methods = Methods()

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
