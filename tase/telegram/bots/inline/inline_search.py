from re import Match
from typing import List, Optional

import pyrogram

from tase.db.arangodb.enums import InlineQueryType, InteractionType
from tase.db.arangodb.graph.vertices import User
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.ui.inline_items import AudioItem, NoResultItem
from tase.telegram.update_handlers.base import BaseHandler
from tase.telegram.update_interfaces import OnInlineQuery
from . import CustomInlineQueryResult

known_mime_types = (
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/mpeg3",
    "audio/flac",
    "audio/ogg",
    "audio/MP3",
    "audio/x-vorbis+ogg",
    "audio/x-opus+ogg",
)

forbidden_mime_types = (
    "audio/ogg",
    "audio/x-vorbis+ogg",
    "audio/x-opus+ogg",
)


class InlineSearch(OnInlineQuery):
    @classmethod
    def on_inline_query(
        cls,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        found_any = True
        results = []
        temp_res = []

        if telegram_inline_query.query is None or not len(telegram_inline_query.query):
            # todo: query is empty
            found_any = False
        else:

            if len(telegram_inline_query.query) <= 2:
                found_any = False
            else:
                es_audio_docs, query_metadata = handler.db.index.search_audio(
                    telegram_inline_query.query,
                    from_=result.from_,
                    size=15,  # todo: update?
                    valid_for_inline_search=True,
                )

                if not es_audio_docs or not len(es_audio_docs) or not query_metadata:
                    found_any = False

                es_audio_docs: List[elasticsearch_models.Audio] = es_audio_docs

                chats_dict = handler.update_audio_cache(es_audio_docs)

                search_metadata_lst = []
                audio_keys = []

                for es_audio_doc in es_audio_docs:
                    audio_doc = handler.db.document.get_audio_by_key(
                        handler.telegram_client.telegram_id,
                        es_audio_doc.id,
                    )

                    #  todo: Some audios have null titles, solution?
                    if not es_audio_doc.valid_for_inline_search:
                        continue

                    # todo: telegram cannot handle these mime types, any alternative?
                    if es_audio_doc.mime_type in forbidden_mime_types:
                        continue

                    search_metadata_lst.append(es_audio_doc.search_metadata)
                    audio_keys.append(es_audio_doc.id)

                    temp_res.append(
                        (
                            audio_doc,
                            es_audio_doc,
                        )
                    )

                audio_vertices = list(handler.db.graph.get_audios_from_keys(audio_keys))

                db_query, hits = handler.db.graph.get_or_create_query(
                    handler.telegram_client.telegram_id,
                    from_user,
                    telegram_inline_query.query,
                    query_date,
                    audio_vertices,
                    query_metadata,
                    search_metadata_lst,
                    telegram_inline_query,
                    InlineQueryType.SEARCH,
                    result.get_next_offset(),
                )

                if db_query and hits:
                    for (audio_doc, es_audio_doc), hit in zip(temp_res, hits):
                        results.append(
                            AudioItem.get_item(
                                handler.telegram_client.get_me().username,
                                audio_doc.file_id,
                                from_user,
                                es_audio_doc,
                                telegram_inline_query,
                                chats_dict,
                                hit,
                                handler.db.graph.audio_in_favorite_playlist(
                                    from_user,
                                    hit.download_url,
                                ),
                                handler.db.graph.audio_is_interacted_by_user(
                                    from_user,
                                    hit.download_url,
                                    InteractionType.LIKE,
                                ),
                                handler.db.graph.audio_is_interacted_by_user(
                                    from_user,
                                    hit.download_url,
                                    InteractionType.DISLIKE,
                                ),
                            )
                        )

        if found_any and len(results):
            result.results = results
        else:
            # todo: No results matching the query found, what now?
            if result.from_ is None or result.from_ == 0:
                result.results = [NoResultItem.get_item(from_user)]
