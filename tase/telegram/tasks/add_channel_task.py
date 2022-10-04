from kombu.mixins import ConsumerProducerMixin
from pydantic import Field
from pyrogram.enums import ChatType
from pyrogram.errors import UsernameNotOccupied

from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.channel_analyzer import ChannelAnalyzer
from tase.telegram.client import TelegramClient


class AddChannelTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.ADD_CHANNEL_TASK

    def run(
        self,
        consumer_producer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        try:
            tg_chat = telegram_client.get_chat(self.kwargs.get("channel_username"))

            # check if the chat is valid based on current policies of the bot
            if tg_chat.type == ChatType.CHANNEL:
                chat = db.graph.update_or_create_chat(tg_chat)
                if chat is not None:
                    score = ChannelAnalyzer.calculate_score(
                        telegram_client,
                        tg_chat,
                    )
                    logger.debug(f"Channel {chat.username} score: {score}")
                    updated = chat.update_audio_indexer_score(score)
                    logger.error(updated)
                else:
                    pass
            else:
                pass
        except UsernameNotOccupied:
            # The username is not occupied by anyone
            pass
        except ValueError as e:
            # In case the chat invite link points to a chat this telegram client hasn't joined yet.
            # todo: send an appropriate message to notify the user of this situation
            pass
        except KeyError as e:
            # the provided username is not valid
            # todo: send an appropriate message to notify the user of this situation
            pass
        except Exception as e:
            # this is an unexpected error
            logger.exception(e)
