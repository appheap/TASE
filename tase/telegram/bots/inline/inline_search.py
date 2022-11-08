from re import Match
from typing import List, Optional

import pyrogram

from tase.db.arangodb.enums import InlineQueryType
from tase.db.arangodb.graph.vertices import User
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.my_logger import logger
from tase.telegram.bots.ui.inline_items import AudioItem, NoResultItem
from tase.telegram.update_handlers.base import BaseHandler
from tase.telegram.update_interfaces import OnInlineQuery
from . import CustomInlineQueryResult


class InlineSearch(OnInlineQuery):
    @classmethod
    async def on_inline_query(
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
        temp_res = []

        if telegram_inline_query.query is None or not len(telegram_inline_query.query):
            # todo: query is empty
            found_any = False
        else:

            if len(telegram_inline_query.query) <= 2:
                found_any = False
            else:
                size = 15

                es_audio_docs, query_metadata = await handler.db.index.search_audio(
                    telegram_inline_query.query,
                    from_=result.from_,
                    size=size,  # todo: update?
                    filter_by_valid_for_inline_search=True,
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

                    search_metadata_lst.append(es_audio_doc.search_metadata)
                    audio_keys.append(es_audio_doc.id)

                    temp_res.append(
                        (
                            audio_doc,
                            es_audio_doc,
                        )
                    )
                if len(temp_res):
                    hit_download_urls = handler.db.graph.generate_hit_download_urls(size=size)

                    for (audio_doc, es_audio_doc), hit_download_url in zip(temp_res, hit_download_urls):
                        status = AudioKeyboardStatus.get_status(
                            handler.db,
                            from_user,
                            audio_vertex_key=es_audio_doc.id,
                        )
                        if status is None:
                            logger.error(f"Unexpected error: `status` is None")
                            continue

                        result.add_item(
                            AudioItem.get_item(
                                (await handler.telegram_client.get_me()).username,
                                audio_doc.file_id,
                                from_user,
                                es_audio_doc,
                                telegram_inline_query,
                                chats_dict,
                                hit_download_url,
                                status,
                            )
                        )
                else:
                    found_any = False

        if not found_any and not len(result) and result.is_first_page():
            # todo: No results matching the query found, what now?
            result.set_results([NoResultItem.get_item(from_user)])

        await result.answer_query()

        if found_any:
            # fixme
            audio_vertices = list(handler.db.graph.get_audios_from_keys(audio_keys))
            handler.db.graph.get_or_create_query(
                handler.telegram_client.telegram_id,
                from_user,
                telegram_inline_query.query,
                query_date,
                audio_vertices,
                query_metadata,
                search_metadata_lst,
                telegram_inline_query,
                InlineQueryType.SEARCH,
                result.get_next_offset(only_countable=True),
                hit_download_urls=hit_download_urls,
            )
