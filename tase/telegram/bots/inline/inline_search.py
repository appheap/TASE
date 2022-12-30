from typing import Optional

import pyrogram

from tase.db.arangodb.enums import InlineQueryType
from tase.db.arangodb.graph.vertices import User
from tase.db.helpers import AudioAccessSourceType
from tase.telegram.bots.ui.base import InlineButtonData
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
        inline_button_data: Optional[InlineButtonData] = None,
    ):
        found_any = True
        query_metadata = None
        es_audio_docs = None
        hit_download_urls = None

        from tase.telegram.bots.ui.inline_items import AudioItem
        from tase.telegram.bots.ui.inline_items import NoResultItem

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
                    filter_by_valid_for_inline_search=False,
                )

                if not es_audio_docs or not len(es_audio_docs) or not query_metadata:
                    found_any = False

                if es_audio_docs:
                    chats_dict = {}
                    db_chats = await handler.db.graph.get_chats_from_keys((str(es_audio_doc.chat_id) for es_audio_doc in es_audio_docs))
                    for db_chat in db_chats:
                        if db_chat and db_chat.chat_id not in chats_dict:
                            chats_dict[db_chat.chat_id] = db_chat

                    hit_download_urls = await handler.db.graph.generate_hit_download_urls(size=size)

                    result.extend_results(
                        [
                            AudioItem.get_article_item(
                                (await handler.telegram_client.get_me()).username,
                                from_user,
                                es_audio_doc,
                                telegram_inline_query,
                                chats_dict,
                                hit_download_url,
                                AudioAccessSourceType.AUDIO_SEARCH,
                            )
                            for es_audio_doc, hit_download_url in zip(es_audio_docs, hit_download_urls)
                            if es_audio_doc
                        ]
                    )

                else:
                    found_any = False

        if not found_any and not len(result) and result.is_first_page():
            # todo: No results matching the query found, what now?
            result.set_results([NoResultItem.get_item(from_user)])

        await result.answer_query()

        if found_any and es_audio_docs:
            search_metadata_lst = [es_audio_doc.search_metadata for es_audio_doc in es_audio_docs]
            audio_vertices = await handler.db.graph.get_audios_from_keys([es_audio_doc.id for es_audio_doc in es_audio_docs])
        else:
            search_metadata_lst = None
            audio_vertices = None

        await handler.db.graph.get_or_create_query(
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
