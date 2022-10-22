from typing import Optional

from tase.db.arangodb.base import BaseCollectionAttributes


class ElasticQueryMetadata(BaseCollectionAttributes):
    duration: float
    max_score: Optional[float]
    total_hits: int
    total_rel: str

    @classmethod
    def parse(cls, query_metadata: dict):
        if query_metadata is None:
            return None

        return ElasticQueryMetadata(
            duration=query_metadata.get("duration"),
            max_score=query_metadata.get("max_score", None),
            total_hits=query_metadata.get("total_hits"),
            total_rel=query_metadata.get("total_rel"),
        )
