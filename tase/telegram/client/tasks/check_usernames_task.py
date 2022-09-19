import time

from pydantic import Field
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, FloodWait

from tase.common.utils import get_now_timestamp
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.my_logger import logger
from tase.telegram.client import TelegramClient
from .base_task import BaseTask


class CheckUsernamesTask(BaseTask):
    name: str = Field(default="check_usernames_task")

    def run_task(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
    ):
        username_vertex: graph_models.vertices.Username = self.kwargs.get("username")
        if (
            username_vertex is None
            or username_vertex.username is None
            or username_vertex.is_checked
        ):
            return

        if not db.graph.get_username(username_vertex.username):
            return

        logger.info(f"Checking: {username_vertex.username}")
        chat_id = username_vertex.username

        try:
            tg_mentioned_chat = telegram_client.get_chat(chat_id)
        except (KeyError, ValueError, UsernameNotOccupied, UsernameInvalid) as e:
            # ValueError: In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # KeyError or UsernameNotOccupied: The username is not occupied by anyone, so update the username
            # UsernameInvalid: The username is invalid

            if username_vertex.check(True, get_now_timestamp(), False):
                username_vertex = db.graph.get_username(username_vertex.username)
                db.graph.update_mentions_edges_from_chat_to_username(username_vertex)
            else:
                # todo: update wasn't successful, what now?
                raise Exception("Unexpected error")

        except FloodWait as e:
            # fixme: find a solution for this
            pass
        except Exception as e:
            logger.exception(e)
        else:
            mentioned_chat = db.graph.update_or_create_chat(tg_mentioned_chat)

            if mentioned_chat:
                # the username is valid, update the username and create new edge from the original chat to the
                # mentioned chat
                if username_vertex.check(True, get_now_timestamp(), True):
                    # update `mentions` edges and `Username` vertices, Also, create new edges from `Username`
                    # vertices to `Chat` vertices and create edges from `Chat` to `Chat` vertices
                    username_vertex = db.graph.get_username(username_vertex.username)
                    db.graph.create_and_check_mentions_edges_after_username_check(
                        mentioned_chat, username_vertex
                    )
                else:
                    # todo: update wasn't successful, what now?
                    raise Exception("Unexpected error")
        finally:
            # this is necessary to avoid flood errors
            # todo: is this one good enough?
            time.sleep(20)
