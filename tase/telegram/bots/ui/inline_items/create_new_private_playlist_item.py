from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from .base_inline_item import BaseInlineItem


class CreateNewPrivatePlaylistItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        from_user: graph_models.vertices.User,
        telegram_inline_query: pyrogram.types.InlineQuery,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if from_user is None or telegram_inline_query is None:
            return None

        return InlineQueryResultArticle(
            title=_trans("Create A New Private Playlist", from_user.chosen_language_code),
            description=_trans("Create a new private playlist", from_user.chosen_language_code),
            id=f"{telegram_inline_query.id}->add_a_new_private_playlist",
            thumb_url="https://telegra.ph/file/aaafdf705c6745e1a32ee.png",
            input_message_content=InputTextMessageContent(
                message_text=emoji._clock_emoji,
                parse_mode=ParseMode.HTML,
            ),
        )
