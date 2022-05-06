import secrets
from typing import Optional

import pyrogram
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch

from .base_document import BaseDocument
from ...my_logger import logger
from ...utils import get_timestamp


class Audio(BaseDocument):
    _index_name = 'audios_index'
    _mappings = {
        "properties": {
            "created_at": {
                "type": "long"
            },
            "modified_at": {
                "type": "long"
            },
            "chat_id": {
                "type": "long"
            },
            "message_id": {
                "type": "long"
            },
            "message_caption": {
                "type": "text"
            },
            "message_date": {
                "type": "date"
            },
            "file_unique_id": {
                "type": "keyword"
            },
            "duration": {
                "type": "integer"
            },
            "performer": {
                "type": "text"
            },
            "title": {
                "type": "text"
            },
            "file_name": {
                "type": "text"
            },
            "mime_type": {
                "type": "keyword"
            },
            "file_size": {
                "type": "integer"
            },
            "date": {
                "type": "date"
            },
            "download_count": {
                "type": "long"
            },
        }
    }

    _do_not_update = ['created_at', 'download_count', ]
    _search_fields = ['performer', 'file_name', 'message_caption', 'title']

    chat_id: int
    message_id: int
    message_caption: Optional[str]
    message_date: int

    file_unique_id: str
    duration: int
    performer: Optional[str]
    title: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: int
    date: int

    download_count: int

    @staticmethod
    def get_id(message: 'pyrogram.types.Message'):
        return f'{message.audio.file_unique_id}:{message.chat.id}:{message.id}'

    @classmethod
    def parse_from_message(cls, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None:
            return None

        while True:
            download_url = secrets.token_urlsafe(6)
            if download_url.find('-') == -1:
                break

        return Audio(
            id=cls.get_id(message),
            chat_id=message.chat.id,
            message_id=message.id,
            message_caption=message.caption,
            message_date=get_timestamp(message.date),
            file_unique_id=message.audio.file_unique_id,
            duration=message.audio.duration,
            performer=message.audio.performer,
            title=message.audio.title,
            file_name=message.audio.file_name,
            mime_type=message.audio.mime_type,
            file_size=message.audio.file_size,
            date=get_timestamp(message.audio.date),
            download_count=0,
        )

    @classmethod
    def search_by_download_url(cls, es: 'Elasticsearch', download_url: str) -> Optional['Audio']:
        if es is None or download_url is None:
            return None
        db_docs = []

        try:
            res: 'ObjectApiResponse' = es.search(
                index=cls._index_name,
                query={
                    "match": {
                        "download_url": download_url,
                    },
                }
            )

            hits = res.body['hits']['hits']

            for index, hit in enumerate(hits, start=1):
                db_doc = cls.parse_from_db_hit(hit, len(hits) - index + 1)
                db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        return db_docs[0] if len(db_docs) else None

    @classmethod
    def search_by_id(cls, es: 'Elasticsearch', key: str) -> Optional['Audio']:
        if es is None or key is None:
            return None
        db_docs = []

        try:
            res: 'ObjectApiResponse' = es.search(
                index=cls._index_name,
                query={
                    "match": {
                        "_id": key,
                    },
                }
            )

            hits = res.body['hits']['hits']

            for index, hit in enumerate(hits, start=1):
                db_doc = cls.parse_from_db_hit(hit, len(hits) - index + 1)
                db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        return db_docs[0] if len(db_docs) else None
