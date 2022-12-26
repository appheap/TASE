import asyncio
from typing import Match, Optional

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InteractionType, ChatType, InlineQueryType
from tase.errors import PlaylistDoesNotExists
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType
from .common import populate_audio_items
from ..inline_items import PlaylistItem, NoDownloadItem


class GetPlaylistAudioInlineButton(InlineButton):
    name = "get_playlist_audios"
    type = InlineButtonType.GET_PLAYLIST_AUDIOS

    s_audios = _trans("Audio Files")
    text = f"{s_audios} | {emoji._headphone}"
    is_inline = True

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        playlist_key = reg.group("arg1")

        playlist_is_valid = False  # whether the requested playlist belongs to the user or not
        audio_vertices = None
        hit_download_urls = None

        if result.is_first_page():
            playlist = await handler.db.graph.get_user_playlist_by_key(
                from_user,
                playlist_key,
                filter_out_soft_deleted=True,
            )
            if playlist:
                playlist_is_valid = True
                result.add_item(
                    PlaylistItem.get_item(
                        playlist,
                        from_user,
                        telegram_inline_query,
                        view_playlist=True,
                    ),
                    count=False,
                )
            else:
                playlist_is_valid = False
        else:
            playlist_is_valid = True

        if playlist_is_valid:
            try:
                audio_vertices = await handler.db.graph.get_playlist_audios(
                    from_user,
                    playlist_key,
                    offset=result.from_,
                )
            except PlaylistDoesNotExists:
                # since it is already been checked that the playlist belongs to the user, this exception will not occur
                pass
            else:
                hit_download_urls = await populate_audio_items(
                    audio_vertices,
                    from_user,
                    handler,
                    result,
                    telegram_inline_query,
                )

        if not len(result) and not playlist_is_valid and result.is_first_page():
            result.set_results([NoDownloadItem.get_item(from_user)])

        await result.answer_query()

        if playlist_is_valid and audio_vertices and hit_download_urls:
            await handler.db.graph.get_or_create_query(
                handler.telegram_client.telegram_id,
                from_user,
                telegram_inline_query.query,
                query_date,
                audio_vertices,
                telegram_inline_query=telegram_inline_query,
                inline_query_type=InlineQueryType.COMMAND,
                next_offset=result.get_next_offset(only_countable=True),
                hit_download_urls=hit_download_urls,
            )

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):

        result_id_list = telegram_chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        hit_download_url = result_id_list[1]
        chat_type = ChatType(int(result_id_list[2]))

        # update the keyboard markup of the downloaded audio
        update_keyboard_task = asyncio.create_task(
            handler.update_audio_keyboard_markup(
                client,
                from_user,
                telegram_chosen_inline_result,
                hit_download_url,
                chat_type,
            )
        )

        interaction_vertex = await handler.db.graph.create_interaction(
            hit_download_url,
            from_user,
            handler.telegram_client.telegram_id,
            InteractionType.SHARE,
            chat_type,
        )
        if not interaction_vertex:
            # could not create the interaction_vertex
            logger.error("Could not create the `interaction_vertex` vertex:")
            logger.error(telegram_chosen_inline_result)

        await update_keyboard_task
