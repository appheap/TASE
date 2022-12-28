from __future__ import annotations

import pyrogram
from pydantic import BaseModel

from tase.common.utils import get_now_timestamp
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.document import BotTask
from tase.db.arangodb.enums import BotTaskType, BotTaskStatus
from tase.db.arangodb.graph.edges import SubscribeTo
from tase.errors import PlaylistDoesNotExists
from tase.my_logger import logger


class BotTaskChecker(BaseModel):
    @classmethod
    async def check(
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

        if bot_task.type in (BotTaskType.CREATE_NEW_PRIVATE_PLAYLIST, BotTaskType.CREATE_NEW_PUBLIC_PLAYLIST):
            await cls.create_new_playlist(bot_task, db, from_user, message)

        elif bot_task.type == BotTaskType.EDIT_PLAYLIST_TITLE:
            await cls.edit_playlist_title(bot_task, db, from_user, message)

        elif bot_task.type == BotTaskType.EDIT_PLAYLIST_DESCRIPTION:
            await cls.edit_playlist_description(bot_task, db, from_user, message)

        elif bot_task.type == BotTaskType.DELETE_PLAYLIST:
            await cls.delete_playlist(bot_task, db, from_user, message)

        else:
            # check for other types of bot tasks
            pass

        return True

    @classmethod
    async def delete_playlist(
        cls,
        bot_task: BotTask,
        db: DatabaseClient,
        from_user: graph_models.vertices.User,
        message: pyrogram.types.Message,
    ) -> None:
        playlist_key = bot_task.state_dict.get("playlist_key", None)
        result = bot_task.state_dict.get("result", None)
        if playlist_key is None or result is None:
            # todo: An error has occurred, notify user
            pass
        else:
            if message.text == result:
                deleted_at = get_now_timestamp()

                try:
                    deleted = db.remove_playlist(
                        from_user,
                        playlist_key,
                        deleted_at,
                    )
                except PlaylistDoesNotExists:
                    await bot_task.update_status(BotTaskStatus.FAILED)
                    await message.reply_text("The target playlist does not exist!")
                else:
                    if deleted:
                        await bot_task.update_status(BotTaskStatus.DONE)
                        await message.reply_text("Successfully Deleted The Playlist")
                    else:
                        await message.reply_text("Could not delete the playlist")
            else:
                # message sent does not equal to the result, send an error
                await message.reply_text("Confirmation code is wrong")
                await bot_task.update_retry_count()

    @classmethod
    async def edit_playlist_description(
        cls,
        bot_task: BotTask,
        db: DatabaseClient,
        from_user: graph_models.vertices.User,
        message: pyrogram.types.Message,
    ) -> None:
        description = message.text
        error_message = cls.validate_playlist_description(description)
        playlist_key = bot_task.state_dict["playlist_key"]
        if playlist_key is None:
            # todo: An error has occurred, notify user
            pass
        else:
            if error_message is None:
                # update playlist description
                playlist = await db.graph.get_user_playlist_by_key(
                    from_user,
                    playlist_key,
                    filter_out_soft_deleted=True,
                )
                if playlist:
                    await playlist.update_description(description)
                    await bot_task.update_status(BotTaskStatus.DONE)
                    await message.reply_text("Successfully updated the playlist.")
                else:
                    await bot_task.update_status(BotTaskStatus.FAILED)
                    await message.reply_text("The target playlist does not exist!")

            else:
                await message.reply_text(error_message)
                await bot_task.update_retry_count()

    @classmethod
    async def edit_playlist_title(
        cls,
        bot_task: BotTask,
        db: DatabaseClient,
        from_user: graph_models.vertices.User,
        message: pyrogram.types.Message,
    ) -> None:
        title = message.text
        error_message = cls.validate_playlist_title(title)
        playlist_key = bot_task.state_dict["playlist_key"]
        if playlist_key is None:
            # todo: An error has occurred, notify user
            pass
        else:
            if error_message is None:
                # update playlist title
                playlist = await db.graph.get_user_playlist_by_key(
                    from_user,
                    playlist_key,
                    filter_out_soft_deleted=True,
                )
                if playlist:
                    await playlist.update_title(title)
                    await bot_task.update_status(BotTaskStatus.DONE)
                    await message.reply_text("Successfully updated the playlist.")
                else:
                    await bot_task.update_status(BotTaskStatus.FAILED)
                    await message.reply_text("The target playlist does not exist!")
            else:
                await message.reply_text(error_message)
                await bot_task.update_retry_count()

    @classmethod
    async def create_new_playlist(
        cls,
        bot_task: BotTask,
        db: DatabaseClient,
        from_user: graph_models.vertices.User,
        message: pyrogram.types.Message,
    ) -> None:
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
            db_playlist = await db.graph.get_or_create_playlist(
                from_user,
                title,
                description,
                is_favorite=False,
                is_public=True if bot_task.type == BotTaskType.CREATE_NEW_PUBLIC_PLAYLIST else False,
            )
            if db_playlist:
                await bot_task.update_status(BotTaskStatus.DONE)
                await message.reply_text("Successfully created the playlist.")

                hit_download_url = bot_task.state_dict.get("hit_download_url", None)
                if hit_download_url is not None:
                    created, successful = await db.graph.add_audio_to_playlist(
                        from_user,
                        db_playlist.key,
                        hit_download_url,
                    )

                    # todo: update these messages
                    if successful:
                        if created:
                            await message.reply_text(
                                "Added to the playlist",
                            )
                        else:
                            await message.reply_text(
                                "It's already on the playlist",
                            )
                    else:
                        await message.reply_text(
                            "Did not add to the playlist",
                        )

                if db_playlist.is_public:
                    if not await db.index.get_or_create_playlist(
                        from_user,
                        db_playlist.key,
                        db_playlist.title,
                        db_playlist.description,
                    ):
                        logger.error(f"Error in creating `Playlist` document in the ElasticSearch : `{db_playlist.key}`")

                    successful, subscribed = await db.graph.toggle_playlist_subscription(from_user, db_playlist)
                    # subscribe_to_edge = SubscribeTo.get_or_create_edge(from_user, db_playlist)
                    if not successful or not subscribed:
                        logger.error(f"Error in creating `{SubscribeTo.__class__.__name__}` edge from `{from_user.key}` to `{db_playlist.key}`")

            else:
                # todo: make this translatable
                await bot_task.update_status(BotTaskStatus.FAILED)
                await message.reply_text("An error has occurred")

        else:
            await message.reply_text(error_message)

            if bot_task.retry_count + 1 >= bot_task.max_retry_count:
                await message.reply_text("Failed to create the Playlist")

            await bot_task.update_retry_count()

    @classmethod
    def validate_playlist_description(
        cls,
        description,
    ):
        error_message = None
        if description is not None:
            if len(description) > 200:
                error_message = "Description length is more than 200, Please try again"
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
            elif len(title) > 40:
                error_message = "Title length is more than 40, Please try again"
            elif title.lower() == "Favorite":
                error_message = "Title cannot be `Favorite`"
            elif title.lower() == "Favourite":
                error_message = "Title cannot be `Favourite`"
        else:
            error_message = "Title is incorrect, Please try again"
        return error_message
