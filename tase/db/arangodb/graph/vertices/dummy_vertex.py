from pydantic.typing import Optional

from tase.utils import get_timestamp
from .base_vertex import BaseVertex


class DummyVertex(BaseVertex):
    _collection_name = "dummy_vertices"

    dummy_int: int
    dummy_str: str


class DummyVertexMethods:
    def create_a_dummy_vertex(self) -> Optional[DummyVertex]:
        v, success = DummyVertex.insert(
            DummyVertex(
                key=str(get_timestamp()),
                dummy_int=12,
                dummy_str="this is a dummy string",
            )
        )

        return v
