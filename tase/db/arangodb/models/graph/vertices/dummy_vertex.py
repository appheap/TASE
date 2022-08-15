from .base_vertex import BaseVertex


class DummyVertex(BaseVertex):
    _collection_name = "dummy_vertices"

    dummy_int:int
    dummy_str:str
