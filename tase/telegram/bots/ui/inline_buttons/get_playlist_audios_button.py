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

    def on_inline_query(
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

        if result.is_first_page():
            playlist = handler.db.graph.get_user_playlist_by_key(
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
                    ),
                    count=False,
                )
            else:
                playlist_is_valid = False
        else:
            playlist_is_valid = True

        if playlist_is_valid:
            try:
                audio_vertices = handler.db.graph.get_playlist_audios(
                    from_user,
                    playlist_key,
                    offset=result.from_,
                )
            except PlaylistDoesNotExists:
                # since it is already been checked that the playlist belongs to the user, this exception will not occur
                pass
            else:
                audio_vertices = list(audio_vertices)

                hit_download_urls = populate_audio_items(
                    audio_vertices,
                    from_user,
                    handler,
                    result,
                    telegram_inline_query,
                )

        if not len(result) and not playlist_is_valid and result.is_first_page():
            result.set_results([NoDownloadItem.get_item(from_user)])

        result.answer_query()

        if playlist_is_valid:
            handler.db.graph.get_or_create_query(
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

    def on_chosen_inline_query(
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

        if chat_type == ChatType.BOT:
            # fixme: only store audio inline messages for inline queries in the bot chat
            updated = handler.db.document.set_audio_inline_message_id(
                handler.telegram_client.telegram_id,
                from_user.user_id,
                inline_query_id,
                hit_download_url,
                telegram_chosen_inline_result.inline_message_id,
            )
            if not updated:
                # could not update the audio inline message, what now?
                pass

        interaction_vertex = handler.db.graph.create_interaction(
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
