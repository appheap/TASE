import random
import time

from kombu.mixins import ConsumerProducerMixin
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, FloodWait

from tase.common.utils import get_now_timestamp
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient


class CheckUsernameTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.CHECK_USERNAME_TASK

    def run(
        self,
        consumer_producer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        self.task_in_worker(db)

        username_key = self.kwargs.get("username_key", None)
        username_vertex: graph_models.vertices.Username = db.graph.get_username_by_key(
            username_key
        )
        if (
            username_vertex is None
            or username_vertex.username is None
            or username_vertex.is_checked
        ):
            self.task_failed(db)
            return

        logger.info(f"Checking: {username_vertex.username}")
        try:
            tg_mentioned_chat = telegram_client.get_chat(username_vertex.username)
        except (KeyError, ValueError, UsernameNotOccupied, UsernameInvalid) as e:
            # ValueError: In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # KeyError or UsernameNotOccupied: The username is not occupied by anyone, so update the username
            # UsernameInvalid: The username is invalid
            logger.info(f"Username `{username_vertex.username}` is invalid")

            if username_vertex.check(True, get_now_timestamp(), False):
                db.graph.update_mentions_edges_from_chat_to_username(username_vertex)
            else:
                # todo: update wasn't successful, what now?
                raise Exception("Unexpected error")

            self.task_done(db)

        except FloodWait as e:
            # fixme: find a solution for this
            self.task_failed(db)

            sleep_time = e.value + random.randint(1, 10)
            logger.info(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

        except Exception as e:
            logger.exception(e)
            self.task_failed(db)
        else:
            logger.info(f"Username `{username_vertex.username}` is valid")

            mentioned_chat = db.graph.update_or_create_chat(tg_mentioned_chat)

            if mentioned_chat:
                # the username is valid, update the username and create new edge from the original chat to the
                # mentioned chat
                if username_vertex.check(True, get_now_timestamp(), True):
                    # update `mentions` edges and `Username` vertices, Also, create new edges from `Username`
                    # vertices to `Chat` vertices and create edges from `Chat` to `Chat` vertices
                    db.graph.create_and_check_mentions_edges_after_username_check(
                        mentioned_chat,
                        username_vertex,
                    )

                    self.task_done(db)
                else:
                    # todo: update wasn't successful, what now?
                    self.task_failed(db)
                    raise Exception("Unexpected error")
            else:
                # fixme: this must not happen
                self.task_failed(db)
                raise Exception("Unexpected error")

        finally:
            # this is necessary to avoid flood errors
            # todo: is this one good enough?
            time.sleep(random.randint(10, 20))
