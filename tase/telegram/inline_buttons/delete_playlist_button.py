import pyrogram

from .inline_button import InlineButton
from ...db import graph_models
from ...db.document_models import BotTaskType
from ...utils import _trans, emoji


class DeletePlaylistInlineButton(InlineButton):
    name = "delete_playlist"

    s_delete = _trans("Delete Playlist")
    text = f"{s_delete} | {emoji._cross_mark}"
    callback_data = "delete_playlist->delete_playlist"

    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        callback_query.answer("")

        handler.db.create_bot_task(
            db_from_user.user_id,
            handler.telegram_client.telegram_id,
            BotTaskType.DELETE_PLAYLIST,
            state_dict={
                "playlist_key": callback_query.data.split("->")[1],
                "result": "1",
            },
        )

        # todo: make it translatable
        client.send_message(
            db_from_user.user_id,
            "Please send 1 to confirm deleting the playlist:",
        )
