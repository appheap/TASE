from re import Match
from typing import List, Optional

import pyrogram

from . import CustomInlineQueryResult
from ..inline_items import AudioItem, NoResultItem
from ..interfaces import OnInlineQuery
from ...db import elasticsearch_models, graph_models
from ...db.graph_models.vertices import InlineQueryType

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
        handler: "BaseHandler",
        result: CustomInlineQueryResult,
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        inline_query: "pyrogram.types.InlineQuery",
        query_date: int,
        reg: Optional[Match] = None,
    ):
        found_any = True
        results = []
        temp_res = []

        if inline_query.query is None or not len(inline_query.query):
            # todo: query is empty
            found_any = False
        else:

            if len(inline_query.query) <= 2:
                found_any = False
            else:
                db_audio_docs, query_metadata = handler.db.search_audio(
                    inline_query.query,
                    from_=result.from_,
                    size=15,  # todo: update?
                )

                if not db_audio_docs or not len(db_audio_docs) or not len(query_metadata):
                    found_any = False

                db_audio_docs: List["elasticsearch_models.Audio"] = db_audio_docs

                chats_dict = handler.update_audio_cache(db_audio_docs)

                for db_audio_doc in db_audio_docs:
                    db_audio_file_cache = handler.db.get_audio_file_from_cache(
                        db_audio_doc,
                        handler.telegram_client.telegram_id,
                    )

                    #  todo: Some audios have null titles, solution?
                    if not db_audio_file_cache or not db_audio_doc.title:
                        continue

                    # todo: telegram cannot handle these mime types, any alternative?
                    if db_audio_doc.mime_type in forbidden_mime_types:
                        continue

                    temp_res.append(
                        (
                            db_audio_file_cache,
                            db_audio_doc,
                        )
                    )

                db_audios = handler.db.get_audios_from_keys([tup[1].id for tup in temp_res])

                db_inline_query, db_hits = handler.db.get_or_create_inline_query(
                    handler.telegram_client.telegram_id,
                    inline_query,
                    InlineQueryType.SEARCH,
                    query_date=query_date,
                    query_metadata=query_metadata,
                    audio_docs=db_audio_docs,
                    db_audios=db_audios,
                    next_offset=result.get_next_offset(),
                )
                if db_inline_query and db_hits:
                    for (db_audio_file_cache, db_audio_doc), db_audio, db_hit in zip(
                        temp_res,
                        db_audios,
                        db_hits,
                    ):
                        results.append(
                            AudioItem.get_item(
                                db_audio_file_cache,
                                db_from_user,
                                db_audio,
                                inline_query,
                                chats_dict,
                                db_hit,
                            )
                        )

        if found_any and len(results):
            result.results = results
        else:
            # todo: No results matching the query found, what now?
            if result.from_ is None or result.from_ == 0:
                result.results = [NoResultItem.get_item(db_from_user)]
