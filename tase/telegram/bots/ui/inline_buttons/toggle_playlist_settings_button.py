import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType
from .common import get_playlist_markup_keyboard


class TogglePlaylistSettingsInlineButton(InlineButton):
    name = "toggle_playlist_settings_inline_button"
    type = InlineButtonType.TOGGLE_PLAYLIST_SETTINGS

    s_settings = _trans("Settings")
    text = f"{s_settings} | {emoji._gear}"
    is_inline = False

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        result_id_list = telegram_callback_query.data.split("->")
        button_type_value = result_id_list[0]
        playlist_key, is_settings_visible = result_id_list[1].split("#")
        chat_type = ChatType(int(result_id_list[2]))

        is_settings_visible = bool(int(is_settings_visible))

        playlist = await handler.db.graph.get_user_playlist_by_key(
            from_user,
            playlist_key,
        )
        if not playlist:
            await telegram_callback_query.answer("Playlist is not valid!")
            return

        if playlist.is_soft_deleted:
            await telegram_callback_query.answer("This playlist is deleted!")
            return

        reply_markup = get_playlist_markup_keyboard(
            playlist,
            from_user.chosen_language_code,
            is_settings_visible=not is_settings_visible,
        )

        if reply_markup:
            await client.edit_inline_reply_markup(telegram_callback_query.inline_message_id, reply_markup)

        await telegram_callback_query.answer("")
