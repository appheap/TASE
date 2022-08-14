import time

from pydantic import Field
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, FloodWait

from tase.db import DatabaseClient, graph_models
from tase.my_logger import logger
from tase.telegram.client import TelegramClient
from tase.utils import get_timestamp
from .base_task import BaseTask


class CheckUsernamesTask(BaseTask):
    name: str = Field(default="check_usernames_task")

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        db_username: graph_models.vertices.Username = self.kwargs.get("db_username")
        if db_username is None or db_username.username is None or db_username.is_checked:
            return

        if not db.get_username(db_username.username):
            return

        logger.info(f"Checking: {db_username.username}")
        chat_id = db_username.username

        try:
            tg_user = telegram_client.get_me()
            tg_mentioned_chat = telegram_client.get_chat(chat_id)

        except (KeyError, ValueError, UsernameNotOccupied, UsernameInvalid) as e:
            # ValueError: In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # KeyError or UsernameNotOccupied: The username is not occupied by anyone, so update the db_username
            # UsernameInvalid: The username is invalid

            if db_username.check(True, get_timestamp(), False):
                db_username = db.get_username(db_username.username)
                db.update_mentions_edges_from_chat_to_username(db_username)
            else:
                # todo: update wasn't successful, what now?
                raise Exception("Unexpected error")

        except FloodWait as e:
            # fixme: find a solution for this
            pass
        except Exception as e:
            logger.exception(e)
        else:
            creator = db.update_or_create_user(tg_user)
            db_mentioned_chat = db.update_or_create_chat(tg_mentioned_chat, creator)

            if creator and db_mentioned_chat:
                # the username is valid, update the db_username and create new edge from the original chat to the
                # mentioned chat
                if db_username.check(True, get_timestamp(), True):
                    # update `mentions` edges and `Username` vertices, Also, create new edges from `Username`
                    # vertices to `Chat` vertices and create edges from `Chat` to `Chat` vertices
                    db_username = db.get_username(db_username.username)
                    db.create_mentions_edges_after_username_check(db_mentioned_chat, db_username)
                else:
                    # todo: update wasn't successful, what now?
                    raise Exception("Unexpected error")
        finally:
            # this is necessary to avoid flood errors
            # todo: is this one good enough?
            time.sleep(20)
