import math
import re
from typing import List, Optional, Union

import pyrogram
from pydantic import Field

import tase.telegram
from tase.telegram.client import TelegramClient
from .base_task import BaseTask
from ...db import DatabaseClient, graph_models
from ...db.enums import MentionSource
from ...my_logger import logger
from ...utils import get_timestamp

username_pattern = re.compile(r"(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(?P<username>[a-zA-Z0-9_]{5,32})")


class ExtractUsernamesTask(BaseTask):
    name: str = Field(default="extract_usernames_task")

    db: Optional[tase.db.DatabaseClient] = Field(default=None)
    chat: Optional[tase.db.graph_models.vertices.Chat] = Field(default=None)

    chat_username: Optional[str]
    last_offset_id: Optional[int] = Field(default=1)
    last_offset_date: Optional[int] = Field(default=0)

    message_count: Optional[int] = Field(default=0)
    self_mention_count: Optional[int] = Field(default=0)
    mention_count: Optional[int] = Field(default=0)

    def find_usernames_in_text(
        self,
        text: Union[str, List[Union[str, None]]],
        is_direct_mention: bool,
        message: pyrogram.types.Message,
        mention_source: Union[MentionSource, List[MentionSource]],
    ) -> None:
        if message is None or mention_source is None:
            return None

        def find(text_: str, mention_source_: MentionSource):
            for match in username_pattern.finditer(text_):
                self.add_username(
                    match.group("username"),
                    is_direct_mention,
                    message,
                    mention_source_,
                    match.start(),
                )

        if not isinstance(text, str) and isinstance(text, List):
            if isinstance(mention_source, List):
                if len(mention_source) != len(text):
                    raise Exception(
                        f"mention_source and text must of the the same size: {len(mention_source)} != " f"{len(text)}"
                    )
                for text__, mention_source_ in zip(text, mention_source):
                    if text__ is not None and mention_source_ is not None:
                        find(text__, mention_source_)
            else:
                for text__ in text:
                    if text__ is not None:
                        find(text__, mention_source)

        else:
            if text is not None:
                find(text, mention_source)

    def add_username(
        self,
        username: str,
        is_direct_mention: bool,
        message: pyrogram.types.Message,
        mention_source: MentionSource,
        mention_start_index: int,
    ) -> None:
        if (
            username is None
            or not len(username)
            or is_direct_mention is None
            or message is None
            or mention_source is None
            or mention_start_index is None
        ):
            return

        username = username.lower()

        # todo: this is not a valid username, it's an invite link for a private supergroup / channel.
        if username in ("joinchat",):
            return

        mentioned_at = get_timestamp(message.date)
        db_username_buffer, created = self.db.get_or_create_username(
            self.chat,
            username,
            is_direct_mention,
            mentioned_at,
            mention_source,
            mention_start_index,
            message.id,
        )

        if self.chat_username:
            if username == self.chat_username:
                self.self_mention_count += 1
            else:
                self.mention_count += 1
        else:
            self.mention_count += 1

    def update_metadata(
        self,
    ) -> None:
        mention_ratio = self.mention_count / (self.mention_count + self.self_mention_count)
        score = (math.log(self.mention_count, 1000_000_000_000) * 2 + mention_ratio) / 3

        # todo: find a better way for updating metadata attributes
        self.db.update_username_extractor_metadata(self.chat, self.last_offset_id, self.last_offset_date)
        self.db.update_username_extractor_score(self.chat, score)

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

            self.chat = db_chat
            self.db = db

            if creator and db_chat:
                self.last_offset_id = db_chat.username_extractor_metadata.last_message_offset_id
                self.last_offset_date = db_chat.username_extractor_metadata.last_message_offset_date

                for message in telegram_client.iter_messages(
                    chat_id=chat_id,
                    offset_id=self.last_offset_id,
                    only_newer_messages=True,
                ):
                    message: pyrogram.types.Message = message

                    self.message_count += 1
                    # lst.append(message.id)

                    self.find_usernames_in_text(
                        message.text if message.text else message.caption,
                        True,
                        message,
                        MentionSource.MESSAGE_TEXT,
                    )

                    if message.forward_from_chat and message.forward_from_chat.username:
                        # fixme: it's a public channel or a public supergroup or a user or a bot
                        self.find_usernames_in_text(
                            message.forward_from_chat.username,
                            True,
                            message,
                            MentionSource.FORWARDED_CHAT_USERNAME,
                        )

                        # check the forwarded chat's description/bio for usernames
                        self.find_usernames_in_text(
                            [message.forward_from_chat.description, message.forward_from_chat.bio],
                            True,
                            message,
                            MentionSource.FORWARDED_CHAT_DESCRIPTION,
                        )

                    if message.audio:
                        self.find_usernames_in_text(
                            [message.audio.title, message.audio.performer, message.audio.file_name],
                            False,
                            message,
                            [MentionSource.AUDIO_TITLE, MentionSource.AUDIO_PERFORMER, MentionSource.AUDIO_FILE_NAME],
                        )

                    if message.id > self.last_offset_id:
                        self.last_offset_id = message.id
                        self.last_offset_date = get_timestamp(message.date)

                logger.info(f"Finished extracting usernames from chat: {title}")

                # check gathered usernames if they match the current policy of indexing and them to the Database
                self.update_metadata()
            else:
                logger.error(f"Error occurred: {title}")

    class Config:
        arbitrary_types_allowed = True
