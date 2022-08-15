from pydantic.typing import Optional

from tase.db.arangodb.models.graph.vertices import DummyVertex
from tase.utils import get_timestamp


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
