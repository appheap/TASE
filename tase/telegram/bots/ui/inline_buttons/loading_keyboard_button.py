import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButtonType, InlineButton


class LoadingKeyboardInlineButton(InlineButton):
    name = "loading_keyboard"
    type = InlineButtonType.LOADING_KEYBOARD

    s_loading = _trans("Loading...")
    text = f"{s_loading}"
    is_inline = False
    is_url = False

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        await telegram_callback_query.answer("")
