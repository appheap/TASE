from __future__ import annotations

from hashlib import sha1
from typing import Optional

from .base_vertex import BaseVertex
from ...base.index import PersistentIndex


class Keyword(BaseVertex):
    _collection_name = "keywords"
    schema_version = 1
    _extra_indexes = [
        PersistentIndex(
            version=1,
            name="keyword",
            fields=[
                "keyword",
            ],
        ),
    ]

    keyword: str

    @classmethod
    def parse_key(
        cls,
        keyword: str,
    ) -> Optional[str]:
        if keyword is None:
            return None

        return f"{sha1(keyword.encode('utf-8')).hexdigest()}"

    @classmethod
    def parse(
        cls,
        keyword: str,
    ) -> Optional[Keyword]:
        if keyword is None:
            return None

        key = Keyword.parse_key(keyword)
        if not key:
            return None

        return Keyword(
            key=key,
            keyword=keyword,
        )


class KeywordMethods:
    pass
