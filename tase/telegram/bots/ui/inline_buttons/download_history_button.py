from typing import Match, Optional

import pyrogram
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.db import graph_models
from tase.telegram.inline import CustomInlineQueryResult
from tase.utils import _trans, emoji
from .inline_button import InlineButton
from ..inline_items import AudioItem


class DownloadHistoryInlineButton(InlineButton):
    name = "download_history"

    s_my_downloads = _trans("My Downloads")
    text = f"{s_my_downloads} | {emoji._mobile_phone_with_arrow}"

    switch_inline_query_current_chat = f"#download_history"

    def on_inline_query(
        self,
        handler: "BaseHandler",
        result: CustomInlineQueryResult,
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        inline_query: "pyrogram.types.InlineQuery",
        query_date: int,
        reg: Optional[Match] = None,
    ):
        db_audios = handler.db.get_user_download_history(
            db_from_user,
            offset=result.from_,
        )

        results = []

        # todo: fix this
        chats_dict = handler.update_audio_cache(db_audios)

        for db_audio in db_audios:
            db_audio_file_cache = handler.db.get_audio_file_from_cache(
                db_audio,
                handler.telegram_client.telegram_id,
            )

            #  todo: Some audios have null titles, solution?
            if not db_audio_file_cache or not db_audio.title:
                continue

            results.append(
                AudioItem.get_item(
                    db_audio_file_cache,
                    db_from_user,
                    db_audio,
                    inline_query,
                    chats_dict,
                )
            )

        if len(results):
            result.results = results
        else:
            if result.from_ is None or result.from_ == 0:
                result.results = [
                    InlineQueryResultArticle(
                        title=_trans(
                            "No Results Were Found",
                            db_from_user.chosen_language_code,
                        ),
                        description=_trans(
                            "You haven't downloaded any audios yet",
                            db_from_user.chosen_language_code,
                        ),
                        input_message_content=InputTextMessageContent(
                            message_text=emoji.high_voltage,
                            parse_mode=ParseMode.HTML,
                        ),
                    )
                ]
