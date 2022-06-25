import pyrogram

from .inline_button import InlineButton
from ..telegram_client import TelegramClient

# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...db.document_models import BotTaskType
from ...utils import _trans, emoji


class EditPlaylistDescriptionInlineButton(InlineButton):
    name = "edit_playlist_description"

    s_edit = _trans("Edit Description")
    text = f"{s_edit} | {emoji._gear}"
    callback_data = "edit_playlist_description->edit_playlist_description"

    def on_callback_query(
        self,
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
        handler: "BaseHandler",
        db: "DatabaseClient",
        telegram_client: "TelegramClient",
        db_from_user: graph_models.vertices.User,
    ):
        callback_query.answer("")

        db.create_bot_task(
            db_from_user.user_id,
            telegram_client.telegram_id,
            BotTaskType.EDIT_PLAYLIST_DESCRIPTION,
            state_dict={
                "playlist_key": callback_query.data.split("->")[1],
            },
        )

        # todo: make it translatable
        client.send_message(
            db_from_user.user_id,
            "Enter the new Description:",
        )
