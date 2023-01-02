from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineItemType
from .base_inline_item import BaseInlineItem


class NoPlaylistItem(BaseInlineItem):
    __type__ = InlineItemType.NO_PLAYLIST

    @classmethod
    def get_item(
        cls,
        db_from_user: graph_models.vertices.User,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if db_from_user is None:
            return None

        return InlineQueryResultArticle(
            id=f"{cls.get_type_value()}|",
            title=_trans("No Results Were Found", db_from_user.chosen_language_code),
            description=_trans(
                "You haven't created any playlist yet",
                db_from_user.chosen_language_code,
            ),
            input_message_content=InputTextMessageContent(
                message_text=emoji.high_voltage,
                parse_mode=ParseMode.HTML,
            ),
        )
