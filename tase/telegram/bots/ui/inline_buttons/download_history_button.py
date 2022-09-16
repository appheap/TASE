import collections
from typing import Match, Optional

import pyrogram
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans, emoji
from .base import InlineButton, InlineButtonType
from .common import populate_audio_items


class DownloadHistoryInlineButton(InlineButton):
    name = "download_history"
    type = InlineButtonType.DOWNLOAD_HISTORY

    s_my_downloads = _trans("My Downloads")
    text = f"{s_my_downloads} | {emoji._mobile_phone_with_arrow}"

    def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        audio_vertices = handler.db.graph.get_user_download_history(
            from_user,
            offset=result.from_,
        )

        audio_vertices = list(audio_vertices)

        results = collections.deque()

        populate_audio_items(
            results,
            audio_vertices,
            from_user,
            handler,
            query_date,
            result,
            telegram_inline_query,
        )

        if len(results):
            result.results = list(results)
        else:
            if result.from_ is None or result.from_ == 0:
                result.results = [
                    InlineQueryResultArticle(
                        title=_trans(
                            "No Results Were Found",
                            from_user.chosen_language_code,
                        ),
                        description=_trans(
                            "You haven't downloaded any audios yet",
                            from_user.chosen_language_code,
                        ),
                        input_message_content=InputTextMessageContent(
                            message_text=emoji.high_voltage,
                            parse_mode=ParseMode.HTML,
                        ),
                    )
                ]

    def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):

        result_id_list = telegram_chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        hit_download_url = result_id_list[1]

        # download_vertex = handler.db.graph.create_download(
        #     hit_download_url,
        #     from_user,
        #     handler.telegram_client.telegram_id,
        # )
        # if not download_vertex:
        #     # could not create the download
        #     logger.error("Could not create the `download` vertex:")
        #     logger.error(telegram_chosen_inline_result)
