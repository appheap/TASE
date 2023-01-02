from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineItemType
from .base_inline_item import BaseInlineItem
from .item_info import CreateNewPublicPlaylistItemInfo


class CreateNewPublicPlaylistItem(BaseInlineItem):
    __type__ = InlineItemType.CREATE_NEW_PUBLIC_PLAYLIST

    @classmethod
    def get_item(
        cls,
        from_user: graph_models.vertices.User,
        telegram_inline_query: pyrogram.types.InlineQuery,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if from_user is None or telegram_inline_query is None:
            return None

        return InlineQueryResultArticle(
            id=CreateNewPublicPlaylistItemInfo.parse_id(telegram_inline_query),
            title=_trans("Create A New Public Playlist", from_user.chosen_language_code),
            description=_trans("Create a new public playlist", from_user.chosen_language_code),
            thumb_url="https://telegra.ph/file/f016463855dbaf876e8ba.png",
            input_message_content=InputTextMessageContent(
                message_text=emoji._clock_emoji,
                parse_mode=ParseMode.HTML,
            ),
        )
