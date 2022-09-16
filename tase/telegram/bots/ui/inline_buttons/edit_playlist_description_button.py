import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans, emoji
from .inline_button import InlineButton


class EditPlaylistDescriptionInlineButton(InlineButton):
    name = "edit_playlist_description"

    s_edit = _trans("Edit Description")
    text = f"{s_edit} | {emoji._gear}"
    callback_data = "edit_playlist_description->edit_playlist_description"

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        telegram_callback_query.answer("")

        handler.db.document.create_bot_task(
            from_user.user_id,
            handler.telegram_client.telegram_id,
            BotTaskType.EDIT_PLAYLIST_DESCRIPTION,
            state_dict={
                "playlist_key": telegram_callback_query.data.split("->")[1],
            },
        )

        # todo: make it translatable
        client.send_message(
            from_user.user_id,
            "Enter the new Description:",
        )
