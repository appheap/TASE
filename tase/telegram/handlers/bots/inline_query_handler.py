from __future__ import annotations

from collections import defaultdict
from typing import List

import pyrogram
from pyrogram import handlers
from pyrogram.types import InlineQueryResultCachedAudio, InlineQueryResultArticle, InputTextMessageContent

from tase.db import elasticsearch_models
from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata
from tase.templates import AudioCaptionData
from tase.utils import get_timestamp


class InlineQueryHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.on_inline_query,
            )
        ]

    def on_inline_query(self, client: 'pyrogram.Client', inline_query: 'pyrogram.types.InlineQuery'):
        logger.debug(f"on_inline_query: {inline_query}")
        query_date = get_timestamp()

        found_any = True
        from_ = 0
        results = []
        next_offset = None

        if inline_query.query is None or not len(inline_query.query):
            # todo: query is empty
            found_any = False
        else:
            if inline_query.offset is not None and len(inline_query.offset):
                from_ = int(inline_query.offset)

            db_audio_docs, query_metadata = self.db.search_audio(inline_query.query, from_, size=15)

            if not db_audio_docs or not len(db_audio_docs) or not len(query_metadata):
                found_any = False

            db_audio_docs: List['elasticsearch_models.Audio'] = db_audio_docs

            chat_msg = defaultdict(list)
            chats_dict = {}

            for db_audio in db_audio_docs:
                if not self.db.get_audio_file_from_cache(db_audio, self.telegram_client.telegram_id):
                    chat_msg[db_audio.chat_id].append(db_audio.message_id)

                if not chats_dict.get(db_audio.chat_id, None):
                    db_chat = self.db.get_chat_by_chat_id(db_audio.chat_id)

                    chats_dict[db_chat.chat_id] = db_chat

            for chat_id, message_ids in chat_msg.items():
                db_chat = chats_dict[chat_id]

                # todo: this approach is only for public channels, what about private channels?
                messages = self.telegram_client.get_messages(chat_id=db_chat.username, message_ids=message_ids)

                for message in messages:
                    self.db.update_or_create_audio(
                        message,
                        self.telegram_client.telegram_id,
                    )

            db_user = self.db.get_user_by_user_id(inline_query.from_user.id)

            for db_audio in db_audio_docs:
                db_audio_file_cache = self.db.get_audio_file_from_cache(db_audio, self.telegram_client.telegram_id)

                #  todo: Some audios have null titles, solution?
                if not db_audio_file_cache or not db_audio.title:
                    continue

                text = self.audio_caption_template.render(
                    AudioCaptionData.parse_from_audio_doc(
                        db_audio,
                        db_user,
                        chats_dict[db_audio.chat_id],
                        bot_url='',
                        include_source=True,
                    )
                )

                results.append(
                    InlineQueryResultCachedAudio(
                        audio_file_id=db_audio_file_cache.file_id,
                        id=f'{inline_query.id}->{db_audio.id}',
                        caption=text,
                    )
                )

            # todo: `2` works, but why?
            plus = 2 if inline_query.offset is None or not len(inline_query.offset) else 0
            next_offset = str(from_ + len(results) + plus) if len(results) else None
            db_inline_query = self.db.get_or_create_inline_query(
                self.telegram_client.telegram_id,
                inline_query,
                query_date=query_date,
                query_metadata=query_metadata,
                audio_docs=db_audio_docs,
                next_offset=next_offset
            )

            # ids = [result.audio_file_id for result in results]
            logger.info(
                f"{inline_query.id} : {inline_query.query} ({len(results)}) => {inline_query.offset} : {next_offset}")
            # logger.info(ids)

        if found_any:
            try:
                inline_query.answer(results, cache_time=1, next_offset=next_offset)
            except Exception as e:
                logger.exception(e)
        else:
            # todo: No results matching the query found, what now?
            inline_query.answer(
                [
                    InlineQueryResultArticle(
                        title="No Results were found",
                        description="description",
                        input_message_content=InputTextMessageContent(
                            message_text="No Results were found",
                        )
                    )
                ]
            )
