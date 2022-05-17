from __future__ import annotations

import re
from typing import List

import pyrogram
from pyrogram import filters
from pyrogram import handlers

from tase.db import elasticsearch_models
from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler
from tase.telegram.inline_buton_globals import buttons
from tase.telegram.inline_items import NoResultItem, AudioItem
from tase.utils import get_timestamp, prettify

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
    "audio/x-opus+ogg"
)

forbidden_mime_types = (
    "audio/ogg",
    "audio/x-vorbis+ogg",
    "audio/x-opus+ogg"
)


class InlineQueryHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.custom_commands_handler,
                filters=filters.regex("^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.on_inline_query,
                group=0
            )
        ]

    @exception_handler
    def on_inline_query(self, client: 'pyrogram.Client', inline_query: 'pyrogram.types.InlineQuery'):
        logger.debug(f"on_inline_query: {inline_query}")
        query_date = get_timestamp()

        # todo: fix this
        db_from_user = self.db.get_user_by_user_id(inline_query.from_user.id)
        if not db_from_user:
            # update the user
            db_from_user = self.db.update_or_create_user(inline_query.from_user)

        found_any = True
        from_ = 0
        results = []
        temp_res = []
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

            chats_dict = self.update_audio_cache(db_audio_docs)

            for db_audio_doc in db_audio_docs:
                db_audio_file_cache = self.db.get_audio_file_from_cache(db_audio_doc, self.telegram_client.telegram_id)

                #  todo: Some audios have null titles, solution?
                if not db_audio_file_cache or not db_audio_doc.title:
                    continue

                # todo: telegram cannot handle these mime types, any alternative?
                if db_audio_doc.mime_type in forbidden_mime_types:
                    continue

                temp_res.append((db_audio_file_cache, db_audio_doc))

            next_offset = str(from_ + len(temp_res) + 1) if len(temp_res) else None
            db_inline_query, db_hits = self.db.get_or_create_inline_query(
                self.telegram_client.telegram_id,
                inline_query,
                query_date=query_date,
                query_metadata=query_metadata,
                audio_docs=db_audio_docs,
                next_offset=next_offset
            )

            if db_inline_query and db_hits:
                for (db_audio_file_cache, db_audio_doc), db_hit in zip(temp_res, db_hits):
                    results.append(
                        AudioItem.get_item(
                            db_audio_file_cache,
                            db_from_user,
                            db_audio_doc,
                            inline_query,
                            chats_dict,
                            db_hit,
                        )
                    )

            # logger.info(
            #     f"{inline_query.id} : {inline_query.query} ({len(results)}) => {inline_query.offset} : {next_offset}")

        if found_any and len(results):
            try:
                inline_query.answer(results, cache_time=1, next_offset=next_offset)
            except Exception as e:
                logger.exception(e)
        else:
            # todo: No results matching the query found, what now?
            if from_ is None or from_ == 0:
                inline_query.answer([NoResultItem.get_item(db_from_user)], cache_time=1)

    @exception_handler
    def custom_commands_handler(self, client: 'pyrogram.Client', inline_query: 'pyrogram.types.InlineQuery'):
        logger.debug(f"custom_commands_handler: {inline_query}")
        query_date = get_timestamp()

        # todo: fix this
        db_from_user = self.db.get_user_by_user_id(inline_query.from_user.id)
        if not db_from_user:
            # update the user
            db_from_user = self.db.update_or_create_user(inline_query.from_user)

        reg = re.search("^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?", inline_query.query)
        button = buttons.get(reg.group("command"), None)
        if button:
            button.on_inline_query(
                client,
                inline_query,
                self,
                self.db,
                self.telegram_client,
                db_from_user,
                reg,
            )
        else:
            pass
