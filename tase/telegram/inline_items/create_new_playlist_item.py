from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from .base_inline_item import BaseInlineItem
from ...db import graph_models
from ...utils import _trans, emoji


class CreateNewPlaylistItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        db_from_user: graph_models.vertices.User,
        inline_query: pyrogram.types.InlineQuery,
    ) -> Optional["pyrogram.types.InlineQueryResult"]:
        if db_from_user is None or inline_query is None:
            return None

        return InlineQueryResultArticle(
            title=_trans("Create A New Playlist", db_from_user.chosen_language_code),
            description=_trans("Create a new playlist", db_from_user.chosen_language_code),
            id=f"{inline_query.id}->add_a_new_playlist",
            thumb_url="https://telegra.ph/file/aaafdf705c6745e1a32ee.png",
            input_message_content=InputTextMessageContent(
                message_text=emoji._clock_emoji,
                parse_mode=ParseMode.HTML,
            ),
        )
