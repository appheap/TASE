import collections
import math
import re
from typing import Iterable, Optional, Union

import pyrogram
from pydantic import Field

import tase.telegram
from .base_task import BaseTask
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import get_timestamp

username_pattern = re.compile(r"(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(?P<username>[a-zA-Z0-9_]{5,32})")


class ExtractChannelUserNamesTask(BaseTask):
    name: str = Field(default="extract_channel_usernames_task")

    chat_username: Optional[str]
    last_offset_id: Optional[int] = Field(default=1)
    last_offset_date: Optional[int] = Field(default=0)

    message_count: Optional[int] = Field(default=0)
    self_mention_count: Optional[int] = Field(default=0)
    mention_count: Optional[int] = Field(default=0)

    def find_usernames_in_text(
        self,
        db: "tase.db.DatabaseClient",
        text: Union[str, Iterable[Union[str, None]]],
    ) -> None:
        def find(text_: str):
            for username in username_pattern.findall(text_):
                self.add_username(db, username)

        if not isinstance(text, str) and isinstance(text, Iterable):
            for text__ in text:
                if text__ is not None:
                    find(text__)
        else:
            if text is not None:
                find(text)

    def add_username(
        self,
        db: "tase.db.DatabaseClient",
        username: str,
    ) -> None:
        if username is None or not len(username):
            return

        username = username.lower()
        db_username_buffer, created = db.get_or_create_chat_username_buffer(username)

        if self.chat_username:
            if username == self.chat_username:
                self.self_mention_count += 1
            else:
                self.mention_count += 1
        else:
            self.mention_count += 1

    def update_metadata(
        self,
        db: tase.db.DatabaseClient,
        db_chat: graph_models.vertices.Chat,
    ) -> None:
        mention_ratio = self.mention_count / (self.mention_count + self.self_mention_count)
        score = (math.log(self.mention_count, 1000_000_000_000) * 2 + mention_ratio) / 3

        # todo: find a better way for updating metadata attributes
        db.update_username_extractor_metadata(db_chat, self.last_offset_id, self.last_offset_date)
        db.update_username_extractor_score(db_chat, score)

        logger.info(f"Ratio: {mention_ratio} : {score}")
        logger.info(f"Count: {self.message_count} : {self.self_mention_count} : {self.mention_count}")

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        db_chat: graph_models.vertices.Chat = self.kwargs.get("db_chat")
        if db_chat is None:
            return

        self.chat_username = db_chat.username

        tg_user = None
        tg_chat = None

        chat_id = db_chat.username if db_chat.username else db_chat.invite_link
        title = db_chat.title

        try:
            tg_user = telegram_client.get_me()
            tg_chat = telegram_client.get_chat(chat_id)
        except ValueError as e:
            # In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # todo: fix this
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        else:
            creator = db.update_or_create_user(tg_user)
            db_chat = db.update_or_create_chat(tg_chat, creator)

            if creator and db_chat:
                self.last_offset_id = db_chat.username_extractor_metadata.last_message_offset_id
                self.last_offset_date = db_chat.username_extractor_metadata.last_message_offset_date

                lst = collections.deque()
                for message in telegram_client.iter_messages(
                    chat_id=chat_id,
                    offset_id=self.last_offset_id,
                    only_newer_messages=True,
                ):
                    message: pyrogram.types.Message = message

                    self.message_count += 1
                    # lst.append(message.id)

                    self.find_usernames_in_text(db, message.text if message.text else message.caption)

                    if message.forward_from_chat and message.forward_from_chat.username:
                        # fixme: it's a public channel or a public supergroup or a user or a bot
                        self.add_username(db, message.forward_from_chat.username)

                        # check the forwarded chat's description/bio for usernames
                        self.find_usernames_in_text(
                            db, [message.forward_from_chat.description, message.forward_from_chat.bio]
                        )

                    if message.audio:
                        self.find_usernames_in_text(
                            db, [message.audio.title, message.audio.performer, message.audio.file_name]
                        )

                    if message.id > self.last_offset_id:
                        self.last_offset_id = message.id
                        self.last_offset_date = get_timestamp(message.date)

                logger.debug(f"Finished extracting usernames from chat: {title}")
                # logger.info(lst)

                # check gathered usernames if they match the current policy of indexing and them to the Database
                self.update_metadata(db, db_chat)
            else:
                logger.debug(f"Error occurred: {title}")
