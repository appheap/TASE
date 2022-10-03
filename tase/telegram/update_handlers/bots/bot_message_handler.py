from typing import List

import pyrogram
from jinja2 import Template
from pyrogram import filters, handlers
from pyrogram.enums import ParseMode

from tase.common.utils import (
    datetime_to_timestamp,
    exception_handler,
    get_now_timestamp,
)
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.document import BotTask
from tase.db.arangodb.enums import (
    BotTaskType,
    BotTaskStatus,
)
from tase.errors import PlaylistDoesNotExists
from tase.my_logger import logger
from tase.telegram.bots.bot_commands import BaseCommand, BotCommandType
from tase.telegram.bots.ui.templates import (
    BaseTemplate,
    NoResultsWereFoundData,
    QueryResultsData,
)
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class BotMessageHandler(BaseHandler):
    results_template: Template = None
    no_results_were_found: Template = None

    def init_handlers(self) -> List[HandlerMetadata]:

        handlers_list = [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.commands_handler,
                filters=filters.command(BaseCommand.get_all_valid_commands()),
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
    def commands_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        logger.debug(f"commands_handler: {message.command}")

        BaseCommand.run_command(client, message, self)

    @exception_handler
    def downloads_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
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

        from_user = self.db.graph.get_interacted_user(message.from_user)
        self.download_audio(
            client,
            from_user,
            message.text,
            message,
        )

    @exception_handler
    def search_query_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        logger.info(f"search_query_handler: {message.text}")
        query = message.text

        from_user = self.db.graph.get_interacted_user(message.from_user)

        if from_user.chosen_language_code is None or not len(
            from_user.chosen_language_code
        ):
            BaseCommand.run_command(client, message, self, BotCommandType.LANGUAGE)
            return

        # check if this message is reply to any bot task
        bot_task = self.db.document.get_latest_bot_task(
            from_user.user_id,
            self.telegram_client.telegram_id,
        )
        if bot_task is not None:
            self.check_bot_tasks(
                bot_task,
                from_user,
                message,
            )
            return

        found_any = True
        if not query:
            found_any = False
        else:
            if len(query) <= 2:
                found_any = False
            else:
                es_audio_docs, query_metadata = self.db.index.search_audio(
                    query,
                    size=10,
                    filter_by_valid_for_inline_search=False,  # todo: is this a good idea?
                )
                if (
                    not es_audio_docs
                    or not len(es_audio_docs)
                    or query_metadata is None
                ):
                    found_any = False

                audio_vertices = list(
                    self.db.graph.get_audios_from_keys(
                        [doc.id for doc in es_audio_docs]
                    )
                )
                search_metadata_lst = [
                    es_audio_doc.search_metadata for es_audio_doc in es_audio_docs
                ]

                db_query, hits = self.db.graph.get_or_create_query(
                    self.telegram_client.telegram_id,
                    from_user,
                    query,
                    datetime_to_timestamp(message.date),
                    audio_vertices,
                    query_metadata,
                    search_metadata_lst,
                )
                if db_query and hits:
                    found_any = True
                else:
                    found_any = False

        if found_any:
            data = QueryResultsData.parse_from_query(
                query=query,
                lang_code=from_user.chosen_language_code,
                es_audio_docs=es_audio_docs,
                hits=hits,
            )

            text = BaseTemplate.registry.query_results_template.render(data)
        else:
            text = BaseTemplate.registry.no_results_were_found_template.render(
                NoResultsWereFoundData(
                    query=query,
                    lang_code=from_user.chosen_language_code,
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
        from_user: graph_models.vertices.User,
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
                db_playlist = self.db.graph.get_or_create_playlist(
                    from_user,
                    title,
                    description,
                )
                if db_playlist:
                    bot_task.update_status(BotTaskStatus.DONE)
                    message.reply_text("Successfully created the playlist.")

                    hit_download_url = bot_task.state_dict.get("hit_download_url", None)
                    if hit_download_url is not None:
                        created, successful = self.db.graph.add_audio_to_playlist(
                            from_user,
                            db_playlist.key,
                            hit_download_url,
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
                    playlist = self.db.graph.get_user_playlist_by_key(
                        from_user,
                        playlist_key,
                        filter_out_soft_deleted=True,
                    )
                    if playlist:
                        playlist.update_title(title)
                        bot_task.update_status(BotTaskStatus.DONE)
                        message.reply_text("Successfully updated the playlist.")
                    else:
                        bot_task.update_status(BotTaskStatus.FAILED)
                        message.reply_text("The target playlist does not exist!")
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
                    playlist = self.db.graph.get_user_playlist_by_key(
                        from_user,
                        playlist_key,
                        filter_out_soft_deleted=True,
                    )
                    if playlist:
                        playlist.update_description(description)
                        bot_task.update_status(BotTaskStatus.DONE)
                        message.reply_text("Successfully updated the playlist.")
                    else:
                        bot_task.update_status(BotTaskStatus.FAILED)
                        message.reply_text("The target playlist does not exist!")

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
                    deleted_at = get_now_timestamp()

                    try:
                        deleted = self.db.graph.remove_playlist(
                            from_user,
                            playlist_key,
                            deleted_at,
                        )
                    except PlaylistDoesNotExists:
                        bot_task.update_status(BotTaskStatus.FAILED)
                        message.reply_text("The target playlist does not exist!")
                    else:
                        if deleted:
                            bot_task.update_status(BotTaskStatus.DONE)
                            message.reply_text("Successfully Deleted The Playlist")
                        else:
                            message.reply_text("Could not delete the playlist")
                else:
                    # message sent does not equal to the result, send an error
                    message.reply_text("Confirmation code is wrong")
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
            elif title.lower() == "Favorite":
                error_message = "Title cannot be `Favorite`"
            elif title.lower() == "Favourite":
                error_message = "Title cannot be `Favourite`"
        else:
            error_message = "Title is incorrect, Please try again"
        return error_message
