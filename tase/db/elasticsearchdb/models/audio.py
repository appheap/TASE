import secrets
from typing import Optional

import pyrogram
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch

from .base_document import BaseDocument
from tase.my_logger import logger
from tase.utils import datetime_to_timestamp


class Audio(BaseDocument):
    _index_name = "audios_index"
    _mappings = {
        "properties": {
            "created_at": {"type": "long"},
            "modified_at": {"type": "long"},
            "chat_id": {"type": "long"},
            "message_id": {"type": "long"},
            "message_caption": {"type": "text"},
            "message_date": {"type": "date"},
            "file_unique_id": {"type": "keyword"},
            "duration": {"type": "integer"},
            "performer": {"type": "text"},
            "title": {"type": "text"},
            "file_name": {"type": "text"},
            "mime_type": {"type": "keyword"},
            "file_size": {"type": "integer"},
            "date": {"type": "date"},
            "download_count": {"type": "long"},
            "is_audio_file": {"type": "boolean"},
            "valid_for_inline_search": {"type": "bool"},
        }
    }

    _do_not_update = [
        "created_at",
        "download_count",
    ]
    _search_fields = [
        "performer",
        "title",
        "file_name",
        "message_caption",
    ]

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    message_date: int

    file_unique_id: str
    duration: Optional[int]
    performer: Optional[str]
    title: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: int
    date: int

    download_count: int
    is_audio_file: bool  # whether the audio file is shown in the `audios` or `files/documents` section of telegram app
    valid_for_inline_search: bool
    """
     when an audio's title is None or the audio is shown in document section of
     telegram, then that audio could not be shown in telegram inline mode. Moreover, it should not have keyboard
     markups like `add_to_playlist`, etc... . On top of that, if any audio of this kind gets downloaded through
     query search, then, it cannot be shown in `download_history` section or any other sections that work in inline
     mode.
    """

    @staticmethod
    def get_id(
        message: "pyrogram.types.Message",
    ):
        if message.audio:
            _audio = message.audio
        elif message.document:
            _audio = message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")
        return f"{_audio.file_unique_id}:{message.chat.id}:{message.id}"

    @classmethod
    def parse_from_message(
        cls,
        message: "pyrogram.types.Message",
    ) -> Optional["Audio"]:
        if message is None:
            return None

        if message.audio:
            _audio = message.audio
            is_audio_file = True
        elif message.document:
            _audio = message.document
            is_audio_file = False
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

        while True:
            download_url = secrets.token_urlsafe(6)
            if download_url.find("-") == -1:
                break

        title = getattr(_audio, "title", None)

        # todo: check if the following statement is actually true
        valid_for_inline = True if title is not None and is_audio_file is not None else False

        return Audio(
            id=cls.get_id(message),
            chat_id=message.chat.id,
            message_id=message.id,
            message_caption=message.caption,
            message_date=datetime_to_timestamp(message.date),
            file_unique_id=_audio.file_unique_id,
            duration=getattr(_audio, "duration", None),
            performer=getattr(_audio, "performer", None),
            title=title,
            file_name=_audio.file_name,
            mime_type=_audio.mime_type,
            file_size=_audio.file_size,
            date=datetime_to_timestamp(_audio.date),
            download_count=0,
            valid_for_inline_search=valid_for_inline,
            is_audio_file=is_audio_file,
        )

    @classmethod
    def search_by_download_url(
        cls,
        es: "Elasticsearch",
        download_url: str,
    ) -> Optional["Audio"]:
        if es is None or download_url is None:
            return None
        db_docs = []

        try:
            res: "ObjectApiResponse" = es.search(
                index=cls._index_name,
                query={
                    "match": {
                        "download_url": download_url,
                    },
                },
            )

            hits = res.body["hits"]["hits"]

            for index, hit in enumerate(hits, start=1):
                db_doc = cls.parse_from_db_hit(hit, len(hits) - index + 1)
                db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        return db_docs[0] if len(db_docs) else None

    @classmethod
    def search_by_id(
        cls,
        es: "Elasticsearch",
        key: str,
    ) -> Optional["Audio"]:
        if es is None or key is None:
            return None
        db_docs = []

        try:
            res: "ObjectApiResponse" = es.search(
                index=cls._index_name,
                query={
                    "match": {
                        "_id": key,
                    },
                },
            )

            hits = res.body["hits"]["hits"]

            for index, hit in enumerate(hits, start=1):
                db_doc = cls.parse_from_db_hit(hit, len(hits) - index + 1)
                db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        return db_docs[0] if len(db_docs) else None

    @classmethod
    def get_query(
        cls,
        query: Optional[str],
        valid_for_inline_search: Optional[bool] = True,
    ):
        if valid_for_inline_search:
            return {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fuzziness": "AUTO",
                            "type": "best_fields",
                            "minimum_should_match": "65%",
                            "fields": cls._search_fields,
                        }
                    },
                    "filter": {"exists": {"field": "title"}},
                }
            }
        else:
            return {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fuzziness": "AUTO",
                            "type": "best_fields",
                            "minimum_should_match": "65%",
                            "fields": cls._search_fields,
                        }
                    },
                    "filter": {"exists": {"field": "title"}},
                }
            }

    @classmethod
    def get_sort(
        cls,
    ):
        return {
            "_score": {"order": "desc"},
            "download_count": {"order": "desc"},
            "date": {"order": "desc"},
        }
