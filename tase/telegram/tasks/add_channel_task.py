from pydantic import Field
from pyrogram.enums import ChatType

from .base_task import BaseTask
from ..channel_analyzer import ChannelAnalyzer
from ...my_logger import logger


class AddChannelTask(BaseTask):
    name = Field(default="add_channel_task")

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        try:
            chat = telegram_client.get_chat(self.kwargs.get("channel_username"))

            # check if the chat is valid based on current policies of the bot
            if chat.type == ChatType.CHANNEL:
                db_chat = db.update_or_create_chat(chat)
                if db_chat is not None:
                    score = ChannelAnalyzer.calculate_score(
                        telegram_client,
                        chat,
                    )
                    logger.debug(f"Channel {chat.username} score: {score}")
                    db.update_audio_indexer_score(chat=db_chat, score=score)
                else:
                    pass
            else:
                pass

        except ValueError as e:
            # In case the chat invite link points to a chat this telegram client hasn't joined yet.
            # todo: send an appropriate message to notify the user of this situation
            pass
        except Exception as e:
            # this is an unexpected error
            logger.exception(e)
