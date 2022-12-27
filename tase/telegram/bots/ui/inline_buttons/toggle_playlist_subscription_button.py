import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType
from tase.telegram.update_handlers.base import BaseHandler


class TogglePlaylistSubscriptionInlineButton(InlineButton):
    type = InlineButtonType.TOGGLE_PLAYLIST_SUBSCRIPTION
    action = ButtonActionType.CALLBACK

    s_subscribe = _trans("Subscribe")
    text = f"{s_subscribe} | {emoji._bell}"

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        result_id_list = telegram_callback_query.data.split("|")
        button_type_value = result_id_list[0]
        playlist_key = result_id_list[1]
        chat_type = ChatType(int(result_id_list[2]))

        playlist = await handler.db.graph.get_playlist_by_key(playlist_key)
        if not playlist:
            await telegram_callback_query.answer("Playlist is not valid anymore!")
            return

        if playlist.is_soft_deleted:
            await telegram_callback_query.answer("This playlist is deleted!")
            return

        # user who has created the playlist must not be allowed to subscribe/unsubscribe.
        if playlist.owner_user_id == playlist.owner_user_id:
            await telegram_callback_query.answer("Operation is not allowed!")
            return

        successful, subscribed = await handler.db.graph.toggle_playlist_subscription(from_user, playlist)
        if not successful:
            await telegram_callback_query.answer("Internal error occurred!")
            return

        await telegram_callback_query.answer(_trans("Subscribed!") if subscribed else _trans("Unsubscribed!"))
