import textwrap
from datetime import datetime, timedelta
from typing import List

import pyrogram
from jinja2 import Template
from pyrogram import filters, handlers
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup

from tase.db import elasticsearch_models, graph_models
from tase.db.document_models import BotTask, BotTaskStatus, BotTaskType
from tase.db.graph_models.vertices import UserRole
from tase.my_logger import logger
from tase.telegram.globals import add_job, tase_telegram_queue
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler
from tase.telegram.inline_buttons import InlineButton
from tase.telegram.tasks import AddChannelTask
from tase.telegram.templates import (
    AudioCaptionData,
    BaseTemplate,
    NoResultsWereFoundData,
    QueryResultsData,
)
from tase.utils import _trans, get_timestamp


class BotMessageHandler(BaseHandler):
    results_template: Template = None
    no_results_were_found: Template = None

    def init_handlers(self) -> List[HandlerMetadata]:

        handlers_list = [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.start_bot_handler,
                filters=filters.command(["start"]),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.base_commands_handler,
                filters=filters.command(
                    [
                        "lang",
                        "help",
                        "home",
                    ]
                ),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.admin_commands_handler,
                filters=filters.command(
                    [
                        "add",  # is used to add a new channel to the DB to be indexed later
                    ]
                ),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.downloads_handler,
                filters=filters.private & filters.regex("^/dl_[a-zA-Z0-9_]+$"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.search_query_handler,
                filters=filters.private
                & filters.text
                & ~filters.bot
                & ~filters.via_bot
                & ~filters.media
                & ~filters.regex("^(.*/+.*)+$"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.bot_message_handler,
                group=0,
            ),
        ]
        return handlers_list

    @exception_handler
    def start_bot_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        logger.debug(f"start_bot_handler: {message.command}")

        db_from_user = self.db.get_or_create_user(message.from_user)

        self.say_welcome(client, db_from_user, message)

        if db_from_user.chosen_language_code is None:
            self.choose_language(client, db_from_user)

    @exception_handler
    def base_commands_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        logger.debug(f"base_commands_handler: {message.command}")

        db_from_user = self.db.get_or_create_user(message.from_user)

        command = message.command[0]
        if not command or command is None:
            return

        if command == "lang":
            self.choose_language(client, db_from_user)
        elif command == "help":
            self.show_help(client, db_from_user, message)
        elif command == "home":
            self.show_home(client, db_from_user, message)
        else:
            pass

    @exception_handler
    def admin_commands_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        logger.debug(f"admin_commands_handler: {message.command}")

        db_from_user = self.db.get_or_create_user(message.from_user)

        command = message.command[0]
        if not command or command is None:
            return

        # check if the user has permission to execute admin/owner commands
        if db_from_user.role not in (UserRole.ADMIN, UserRole.OWNER):
            # todo: log users who query these commands without having permission
            return

        if command == "add":
            if len(message.command) == 2:
                channel_username = message.command[1]
                add_job(
                    AddChannelTask(kwargs={"channel_username": channel_username}),
                    tase_telegram_queue,
                    None,
                    self.telegram_client,
                )
            else:
                # `index` command haven't been provided with `channel_username` argument
                pass
        else:
            pass

    @exception_handler
    def downloads_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        """
        Check if the message is coming from a Telegram client and contains "dl_" regex, and then submit
        a thread to retrieve the searched audio file

        Parameters
        ----------
        client : pyrogram.Client
            Client receiving this update
        message : pyrogram.types.Message
            Message associated with update
        """
        logger.debug(f"base_downloads_handler: {message.text}")

        # todo: find a better way to update user when it's necessary
        db_user = self.db.get_user_by_user_id(message.from_user.id)
        if not db_user:
            db_user = self.db.update_or_create_user(message.from_user)

        # todo: handle errors for invalid messages
        download_url = message.text.split("/dl_")[1]
        db_hit = self.db.get_hit_by_download_url(download_url)
        db_audio = self.db.get_audio_from_hit(db_hit)
        db_audio_doc = self.db.get_audio_doc_by_key(db_audio.key)
        if db_audio_doc:
            audio_file_cache = self.db.get_audio_file_from_cache(
                db_audio_doc, self.telegram_client.telegram_id
            )
            db_chat = self.db.get_chat_by_chat_id(db_audio_doc.chat_id)
            if not audio_file_cache:
                messages = client.get_messages(
                    db_chat.username, [db_audio_doc.message_id]
                )
                if not messages or not len(messages):
                    # todo: could not get the audio from telegram servers, what to do now?
                    logger.error(
                        "could not get the audio from telegram servers, what to do now?"
                    )
                    return
                file_id = messages[0].audio.file_id
            else:
                file_id = audio_file_cache.file_id

            text = BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_audio_doc(
                    db_audio_doc,
                    db_user,
                    db_chat,
                    bot_url="https://t.me/bot?start",
                    include_source=True,
                )
            )

            markup = [
                [
                    InlineButton.get_button(
                        "add_to_playlist"
                    ).get_inline_keyboard_button(
                        db_user.chosen_language_code,
                        db_audio.download_url,
                    ),
                ],
                [
                    InlineButton.get_button(
                        "remove_from_playlist"
                    ).get_inline_keyboard_button(
                        db_user.chosen_language_code,
                        db_audio.download_url,
                    ),
                ],
                [
                    InlineButton.get_button("home").get_inline_keyboard_button(
                        db_user.chosen_language_code,
                    ),
                ],
            ]
            markup = InlineKeyboardMarkup(markup)

            message.reply_audio(
                audio=file_id,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )

            db_download = self.db.get_or_create_download_from_hit_download_url(
                download_url,
                db_user,
                self.telegram_client.telegram_id,
            )
        else:
            # todo: An Error occurred while processing this audio download url, why?
            logger.error(
                f"An error occurred while processing the download URL for this audio: {download_url}"
            )
            message.reply_text(
                _trans(
                    "An error occurred while processing the download URL for this audio",
                    db_user.chosen_language_code,
                )
            )

    @exception_handler
    def search_query_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        logger.info(f"search_query_handler: {message.text}")
        # todo: fix this
        lang_code = message.from_user.language_code

        from_user = message.from_user
        chat = message.chat
        message_date = message.date
        query = message.text

        # update the user
        db_from_user = self.db.update_or_create_user(
            message.from_user,
        )

        if db_from_user.chosen_language_code is None or not len(
            db_from_user.chosen_language_code,
        ):
            self.choose_language(
                client,
                db_from_user,
            )
            return

        # check if this message is reply to any bot task
        bot_task = self.db.get_latest_bot_task(
            db_from_user.user_id,
            self.telegram_client.telegram_id,
        )
        if bot_task is not None:
            self.check_bot_tasks(
                bot_task,
                db_from_user,
                message,
            )
            return

        found_any = True
        db_audio_docs = []

        if not query:
            found_any = False
        else:
            if len(query) <= 2:
                found_any = False
            else:
                db_audio_docs, query_metadata = self.db.search_audio(
                    query,
                    size=10,
                )
                if (
                    not db_audio_docs
                    or not len(db_audio_docs)
                    or not len(query_metadata)
                ):
                    found_any = False

                db_audios = self.db.get_audios_from_keys(
                    [doc.id for doc in db_audio_docs]
                )

                res = self.db.get_or_create_query(
                    self.telegram_client.telegram_id,
                    from_user,
                    query,
                    query_date=get_timestamp(message.date),
                    query_metadata=query_metadata,
                    audio_docs=db_audio_docs,
                    db_audios=db_audios,
                )
                if res is not None:
                    db_query, db_hits = res
                else:
                    found_any = False

        if found_any:

            def process_item(index, db_audio_doc: "elasticsearch_models.Audio", db_hit):
                duration = timedelta(seconds=db_audio_doc.duration)
                d = datetime(1, 1, 1) + duration
                _performer = db_audio_doc.performer or ""
                _title = db_audio_doc.title or ""
                _file_name = db_audio_doc.file_name or ""
                if not (len(_title) < 2 or len(_performer) < 2):
                    name = f"{_performer} - {_title}"
                elif not len(_performer) < 2:
                    name = f"{_performer} - {_file_name}"
                else:
                    name = _file_name

                return {
                    "index": f"{index + 1:02}",
                    "name": textwrap.shorten(name, width=35, placeholder="..."),
                    "file_size": round(db_audio_doc.file_size / 1000_000, 1),
                    "time": f"{str(d.hour) + ':' if d.hour > 0 else ''}{d.minute:02}:{d.second:02}",
                    "url": db_hit.download_url,
                    "sep": f"{40 * '-' if index != 0 else ''}",
                }

            items = [
                process_item(index, db_audio, db_hit)
                for index, (db_audio, db_hit) in reversed(
                    list(
                        enumerate(
                            filter(
                                lambda args: args[0].title is not None,
                                zip(db_audio_docs, db_hits),
                            )
                        )
                    )
                )
            ]

            data = QueryResultsData(
                query=query,
                items=items,
                lang_code=db_from_user.chosen_language_code,
            )

            text = BaseTemplate.registry.query_results_template.render(data)
        else:
            text = BaseTemplate.registry.no_results_were_found_template.render(
                NoResultsWereFoundData(
                    query=query,
                    lang_code=db_from_user.chosen_language_code,
                )
            )

        message.reply_text(
            text=text,
            quote=True,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    @exception_handler
    def bot_message_handler(
        self,
        client: "pyrogram.Client",
        message: "pyrogram.types.Message",
    ):
        logger.info(f"bot_message_handler: {message}")

    #######################################################################################################

    def check_bot_tasks(
        self,
        bot_task: BotTask,
        db_from_user: graph_models.vertices.User,
        message: pyrogram.types.Message,
    ) -> None:
        if bot_task.type == BotTaskType.CREATE_NEW_PLAYLIST:
            error_message = None

            items = message.text.split("\n")
            if len(items) > 1:
                title, description = items
                if isinstance(description, list):
                    temp_desc = []
                    for item in description:
                        if item is not None and len(item):
                            temp_desc.append(item)

                    description = "\n".join(temp_desc)
                else:
                    pass
            else:
                title = items[0]
                description = None

            error_message = self.validate_title(title)

            if error_message is not None:
                error_message = self.validate_description(description)

            # if the inputs are valid, change the status of the task to `done`
            if error_message is None:
                db_playlist, successful = self.db.create_playlist(
                    db_from_user,
                    title,
                    description,
                )
                if db_playlist and successful:
                    db_playlist: graph_models.vertices.Playlist = db_playlist

                    bot_task.update_status(BotTaskStatus.DONE)
                    message.reply_text("Successfully created the playlist.")

                    audio_download_url = bot_task.state_dict.get(
                        "audio_download_url", None
                    )
                    if audio_download_url is not None:
                        created, successful = self.db.add_audio_to_playlist(
                            db_playlist.key,
                            audio_download_url,
                        )

                        # todo: update these messages
                        if successful:
                            if created:
                                message.reply_text(
                                    "Added to the playlist",
                                )
                            else:
                                message.reply_text(
                                    "It's already on the playlist",
                                )
                        else:
                            message.reply_text(
                                "Did not add to the playlist",
                            )

                else:
                    # todo: make this translatable
                    bot_task.update_status(BotTaskStatus.FAILED)
                    message.reply_text("An error has occurred")

            else:
                message.reply_text(error_message)

                if bot_task.retry_count + 1 >= bot_task.max_retry_count:
                    message.reply_text("Failed to create the Playlist")

                bot_task.update_retry_count()

        elif bot_task.type == BotTaskType.EDIT_PLAYLIST_TITLE:
            title = message.text
            error_message = self.validate_title(title)

            playlist_key = bot_task.state_dict["playlist_key"]
            if playlist_key is None:
                # todo: An error has occurred, notify user
                pass
            else:
                if error_message is None:
                    # update playlist title
                    self.db.update_playlist_title(
                        playlist_key,
                        title,
                    )
                    bot_task.update_status(BotTaskStatus.DONE)
                    message.reply_text("Successfully updated the playlist.")
                else:
                    message.reply_text(error_message)
                    bot_task.update_retry_count()

        elif bot_task.type == BotTaskType.EDIT_PLAYLIST_DESCRIPTION:
            description = message.text
            error_message = self.validate_description(description)

            playlist_key = bot_task.state_dict["playlist_key"]
            if playlist_key is None:
                # todo: An error has occurred, notify user
                pass
            else:
                if error_message is None:
                    # update playlist description
                    self.db.update_playlist_description(
                        playlist_key,
                        description,
                    )
                    bot_task.update_status(BotTaskStatus.DONE)
                    message.reply_text("Successfully updated the playlist.")
                else:
                    message.reply_text(error_message)
                    bot_task.update_retry_count()

        elif bot_task.type == BotTaskType.DELETE_PLAYLIST:
            playlist_key = bot_task.state_dict.get("playlist_key", None)
            result = bot_task.state_dict.get("result", None)
            if playlist_key is None or result is None:
                # todo: An error has occurred, notify user
                pass
            else:
                if message.text == result:
                    # delete the playlist
                    deleted_at = get_timestamp()
                    self.db.delete_playlist(
                        db_from_user,
                        playlist_key,
                        deleted_at,
                    )
                    bot_task.update_status(BotTaskStatus.DONE)
                    message.reply_text("Successfully Deleted The Playlist")
                else:
                    # message sent does not equal to the result, send an error
                    message.reply_text("Confirm code is wrong")
                    bot_task.update_retry_count()

        else:
            # check for other types of bot tasks
            pass

    def validate_description(
        self,
        description,
    ):
        error_message = None
        if description is not None:
            if len(description) > 100:
                error_message = "Description length is more than 100, Please try again"
            elif len(description) < 3:
                error_message = "Description length is less than 3, Please try again"
        return error_message

    def validate_title(
        self,
        title: str,
    ):
        error_message = None
        if title is not None:
            if len(title) < 3:
                error_message = "Title length is less than 3, Please try again"
            elif len(title) > 20:
                error_message = "Title length is more than 20, Please try again"
        else:
            error_message = "Title is incorrect, Please try again"
        return error_message
