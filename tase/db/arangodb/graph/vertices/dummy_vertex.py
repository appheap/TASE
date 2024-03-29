import random
from typing import Optional

from pydantic import BaseModel, Field

from tase.common.utils import get_now_timestamp
from .base_vertex import BaseVertex


class DummyObj(BaseModel):
    dummy_attr: int = Field(default=1)


class DummyVertex(BaseVertex):
    __collection_name__ = "dummy_vertices"

    dummy_int: int
    dummy_str: str

    dummy_obj: DummyObj = Field(default=DummyObj())

    async def update_dummy_str(self, new_dummy_str: str) -> bool:
        self_copy = self.copy(deep=True)
        self_copy.dummy_str = new_dummy_str
        return await self.update(self_copy)

    async def update_dummy_int(self, new_dummy_int: int) -> bool:
        self_copy = self.copy(deep=True)
        self_copy.dummy_int = new_dummy_int
        return await self.update(self_copy)


class DummyVertexMethods:
    async def create_a_dummy_vertex(
        self,
        dummy_int: int = random.randint(1, 100),
    ) -> Optional[DummyVertex]:
        v, success = await DummyVertex.insert(
            DummyVertex(
                key=str(get_now_timestamp()) + ":" + str(dummy_int).zfill(3),
                dummy_int=dummy_int,
                dummy_str="this is a dummy string",
            )
        )

        return v
