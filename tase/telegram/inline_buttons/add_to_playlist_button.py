from typing import Match

import pyrogram
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from .button import InlineButton
# from ..handlers import BaseHandler
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import emoji, _trans


class AddToPlaylistInlineButton(InlineButton):
    name = "add_to_playlist"

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{s_add_to_playlist} | {emoji._plus}"

    switch_inline_query_current_chat = f"#add_to_playlist"

    def on_inline_query(
            self,
            client: 'pyrogram.Client',
            inline_query: 'pyrogram.types.InlineQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
            reg: Match,
    ):
        from_ = 0
        if inline_query.offset is not None and len(inline_query.offset):
            from_ = int(inline_query.offset)

        db_playlists = db.get_user_playlists(db_from_user, offset=from_)

        results = []

        if from_ == 0:
            results.append(
                InlineQueryResultArticle(
                    title=_trans("Create A New Playlist", db_from_user.chosen_language_code),
                    description=_trans("Create a new playlist", db_from_user.chosen_language_code),
                    id=f'{inline_query.id}->add_a_new_playlist',
                    thumb_url="https://telegra.ph/file/aaafdf705c6745e1a32ee.png",
                    input_message_content=InputTextMessageContent(message_text=emoji._clock_emoji),
                )
            )

        for db_playlist in db_playlists:
            results.append(
                InlineQueryResultArticle(
                    title=db_playlist.title,
                    description=f"{db_playlist.description}",
                    id=f'{inline_query.id}->{db_playlist.key}',
                    thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                    input_message_content=InputTextMessageContent(message_text=emoji._clock_emoji),
                )
            )

        if len(results):
            try:
                if len(results) > 1:
                    next_offset = str(from_ + len(results) + 1) if len(results) else None
                else:
                    next_offset = None

                inline_query.answer(results, cache_time=1, next_offset=next_offset)
            except Exception as e:
                logger.exception(e)

    def on_chosen_inline_query(
            self,
            client: 'pyrogram.Client',
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
            reg: Match,
    ):
        hit_download_url = reg.group("arg1")

        result_id_list = chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]

        # db_hit = db.get_hit_by_download_url(hit_download_url)
        # db_audio = db.get_audio_from_hit(db_hit)

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            pass
        else:
            # add the audio to the playlist
            created, successful = db.add_audio_to_playlist(playlist_key, hit_download_url)

            # todo: update these messages
            if successful:
                if created:
                    client.send_message(
                        db_from_user.user_id,
                        "Added to the playlist"
                    )
                else:
                    client.send_message(
                        db_from_user.user_id,
                        "It's already on the playlist"
                    )
            else:
                client.send_message(
                    db_from_user.user_id,
                    "Did not add to the playlist"
                )
