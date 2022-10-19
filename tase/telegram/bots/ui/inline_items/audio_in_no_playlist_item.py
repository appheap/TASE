from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from .base_inline_item import BaseInlineItem


class AudioInNoPlaylistItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        db_from_user: graph_models.vertices.User,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if db_from_user is None:
            return None

        return InlineQueryResultArticle(
            title=_trans("No Results Were Found", db_from_user.chosen_language_code),
            description=_trans(
                "You haven't added this audio to any playlist yet",
                db_from_user.chosen_language_code,
            ),
            input_message_content=InputTextMessageContent(
                message_text=emoji.high_voltage,
                parse_mode=ParseMode.HTML,
            ),
        )
