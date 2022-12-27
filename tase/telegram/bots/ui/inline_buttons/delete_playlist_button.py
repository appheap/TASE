import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType, ButtonActionType


class DeletePlaylistInlineButton(InlineButton):
    type = InlineButtonType.DELETE_PLAYLIST
    action = ButtonActionType.CALLBACK

    s_delete = _trans("Delete Playlist")
    text = f"{s_delete} | {emoji._cross_mark}"

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        await telegram_callback_query.answer("")

        await handler.db.document.create_bot_task(
            from_user.user_id,
            handler.telegram_client.telegram_id,
            BotTaskType.DELETE_PLAYLIST,
            state_dict={
                "playlist_key": telegram_callback_query.data.split("->")[1],
                "result": "1",
            },
        )

        # todo: make it translatable
        await client.send_message(
            from_user.user_id,
            "Please send 1 to confirm deleting the playlist:\nYou can cancel anytime by sending /cancel",
        )
