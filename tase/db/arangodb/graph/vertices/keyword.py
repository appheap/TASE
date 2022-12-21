from __future__ import annotations

from hashlib import sha1
from typing import Optional

from aioarango.models import PersistentIndex
from .base_vertex import BaseVertex


class Keyword(BaseVertex):
    __collection_name__ = "keywords"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
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
