import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType
from tase.telegram.update_handlers.base import BaseHandler


class LoadingKeyboardInlineButton(InlineButton):
    type = InlineButtonType.LOADING_KEYBOARD
    action = ButtonActionType.CALLBACK

    s_loading = _trans("Loading...")
    text = f"{s_loading}"

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        await telegram_callback_query.answer("")
