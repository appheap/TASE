from __future__ import annotations

import pyrogram
from pydantic import BaseModel

from tase.common.utils import get_now_timestamp
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.document import BotTask
from tase.db.arangodb.enums import BotTaskType, BotTaskStatus
from tase.errors import PlaylistDoesNotExists


class BotTaskChecker(BaseModel):
    @classmethod
    def check(
        cls,
        db: DatabaseClient,
        bot_task: BotTask,
        from_user: graph_models.vertices.User,
        message: pyrogram.types.Message,
    ) -> bool:
        """
        Check the given bot task and run necessary operations.

        Parameters
        ----------
        db : DatabaseClient
            Database Client
        bot_task : BotTask
            Bot task to check
        from_user : graph_modesl.vertices.User
            User to check this bot task belongs to
        message : pyrogram.types.Message
            Telegram Message which contains the initiated this check

        Returns
        -------
        bool
            Whether there the given bot task was a valid object or not (returns True if the `bot_task` parameter is
            not None)

        """
        if bot_task is None:
            return False

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

            error_message = cls.validate_playlist_title(title)

            if error_message is None:
                error_message = cls.validate_playlist_description(description)

            # if the inputs are valid, change the status of the task to `done`
            if error_message is None:
                db_playlist = db.graph.get_or_create_playlist(
                    from_user,
                    title,
                    description,
                )
                if db_playlist:
                    bot_task.update_status(BotTaskStatus.DONE)
                    message.reply_text("Successfully created the playlist.")

                    hit_download_url = bot_task.state_dict.get("hit_download_url", None)
                    if hit_download_url is not None:
                        created, successful = db.graph.add_audio_to_playlist(
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
            error_message = cls.validate_playlist_title(title)

            playlist_key = bot_task.state_dict["playlist_key"]
            if playlist_key is None:
                # todo: An error has occurred, notify user
                pass
            else:
                if error_message is None:
                    # update playlist title
                    playlist = db.graph.get_user_playlist_by_key(
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
            error_message = cls.validate_playlist_description(description)

            playlist_key = bot_task.state_dict["playlist_key"]
            if playlist_key is None:
                # todo: An error has occurred, notify user
                pass
            else:
                if error_message is None:
                    # update playlist description
                    playlist = db.graph.get_user_playlist_by_key(
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
                        deleted = db.graph.remove_playlist(
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

        return True

    @classmethod
    def validate_playlist_description(
        cls,
        description,
    ):
        error_message = None
        if description is not None:
            if len(description) > 100:
                error_message = "Description length is more than 100, Please try again"
            elif len(description) < 3:
                error_message = "Description length is less than 3, Please try again"
        return error_message

    @classmethod
    def validate_playlist_title(
        cls,
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
