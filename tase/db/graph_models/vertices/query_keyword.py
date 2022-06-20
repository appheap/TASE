from hashlib import sha1
from typing import Optional

from .base_vertex import BaseVertex


class QueryKeyword(BaseVertex):
    _vertex_name = "query_keywords"

    query: str

    @staticmethod
    def get_key(
        query: "str",
    ) -> Optional["str"]:
        if query is None:
            return None

        return f"{sha1(query.encode('utf-8')).hexdigest()}"

    @staticmethod
    def parse_from_query(
        query: "str",
    ) -> Optional["QueryKeyword"]:
        if query is None:
            return None

        key = QueryKeyword.get_key(query)
        if not key:
            return None

        return QueryKeyword(
            key=key,
            query=query,
        )
