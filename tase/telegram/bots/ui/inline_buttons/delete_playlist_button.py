from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class DeletePlaylistButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.DELETE_PLAYLIST

    playlist_key: str

    @classmethod
    def generate_data(cls, playlist_key: str) -> Optional[str]:
        return f"{cls.get_type_value()}|{playlist_key}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 2:
            return None

        return DeletePlaylistButtonData(playlist_key=data_split_lst[1])


class DeletePlaylistInlineButton(InlineButton):
    __type__ = InlineButtonType.DELETE_PLAYLIST
    action = ButtonActionType.CALLBACK

    s_delete = _trans("Delete Playlist")
    text = f"{s_delete} | {emoji._cross_mark}"

    @classmethod
    def get_keyboard(
        cls,
        playlist_key: str,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=DeletePlaylistButtonData.generate_data(playlist_key),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: DeletePlaylistButtonData,
    ):
        await telegram_callback_query.answer("")

        await handler.db.document.create_bot_task(
            from_user.user_id,
            handler.telegram_client.telegram_id,
            BotTaskType.DELETE_PLAYLIST,
            state_dict={
                "playlist_key": inline_button_data.playlist_key,
                "result": "1",
            },
        )

        # todo: make it translatable
        await client.send_message(
            from_user.user_id,
            "Please send 1 to confirm deleting the playlist:\nYou can cancel anytime by sending /cancel",
        )
