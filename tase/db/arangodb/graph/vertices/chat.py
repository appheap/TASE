from typing import Optional, List, Tuple

import pyrogram
from arango import CursorEmptyError
from pydantic import Field

from tase.my_logger import logger
from tase.utils import prettify
from .base_vertex import BaseVertex
from ..edges import LinkedChat
from ...enums import ChatType
from ...helpers import Restriction, AudioIndexerMetadata, AudioDocIndexerMetadata, UsernameExtractorMetadata


class Chat(BaseVertex):
    _collection_name = "chats"
    schema_version = 1

    _extra_do_not_update_fields = (
        "audio_indexer_metadata",
        "audio_doc_indexer_metadata",
        "username_extractor_metadata",
    )

    chat_id: int
    is_public: bool
    chat_type: ChatType
    is_verified: Optional[bool]
    is_restricted: Optional[bool]
    # is_creator: creator => User
    is_scam: Optional[bool]
    is_fake: Optional[bool]
    is_support: Optional[bool]
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    description: Optional[str]
    dc_id: Optional[int]
    has_protected_content: Optional[bool]
    invite_link: Optional[str]
    restrictions: Optional[List[Restriction]]
    # linked_chat: linked_chat => Chat
    available_reactions: Optional[List[str]]
    distance: Optional[int]
    members_count: Optional[int]

    audio_indexer_metadata: Optional[AudioIndexerMetadata] = Field(default=None)
    audio_doc_indexer_metadata: Optional[AudioDocIndexerMetadata] = Field(default=None)
    username_extractor_metadata: Optional[UsernameExtractorMetadata] = Field(default=None)

    @classmethod
    def parse_key(
        cls,
        telegram_chat: pyrogram.types.Chat,
    ) -> Optional[str]:
        if telegram_chat is None:
            return None
        return f"{telegram_chat.id}"

    @classmethod
    def parse(
        cls,
        telegram_chat: pyrogram.types.Chat,
    ) -> Optional["Chat"]:
        key = Chat.parse_key(telegram_chat)
        if key is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_chat.type)

        description = telegram_chat.description if telegram_chat.description else telegram_chat.bio

        return Chat(
            key=key,
            chat_id=telegram_chat.id,
            is_public=Chat.get_is_public(telegram_chat, chat_type),
            chat_type=chat_type,
            is_verified=telegram_chat.is_verified,
            is_restricted=telegram_chat.is_restricted,
            is_scam=telegram_chat.is_scam,
            is_fake=telegram_chat.is_fake,
            is_support=telegram_chat.is_support,
            title=telegram_chat.title,
            username=telegram_chat.username.lower() if telegram_chat.username else None,
            # it's useful for searching by username
            first_name=telegram_chat.first_name,
            last_name=telegram_chat.last_name,
            description=description,
            dc_id=telegram_chat.dc_id,
            has_protected_content=telegram_chat.has_protected_content,
            invite_link=telegram_chat.invite_link,
            restrictions=Restriction.parse_from_restrictions(telegram_chat.restrictions),
            available_reactions=telegram_chat.available_reactions,
            distance=telegram_chat.distance,
            members_count=telegram_chat.members_count,
        )

    @staticmethod
    def get_is_public(
        telegram_chat: pyrogram.types.Chat,
        chat_type: ChatType,
    ) -> bool:
        """
        Check whether a chat is public or not

        Parameters
        ----------
        telegram_chat : pyrogram.types.Chat
            Chat object from pyrogram
        chat_type : ChatType
            Type of the chat

        Returns
        -------
        bool
            Whether the chat is public or not
        """
        is_public = False
        if chat_type in (ChatType.PRIVATE, ChatType.BOT):
            is_public = True
        elif chat_type == ChatType.GROUP:
            is_public = False
        elif chat_type in (ChatType.CHANNEL, ChatType.SUPERGROUP):
            if telegram_chat.username:
                is_public = True
            else:
                is_public = False

        return is_public

    def update_username_extractor_metadata(
        self,
        metadata: UsernameExtractorMetadata,
        run_depth: int = 1,
    ) -> bool:
        """
        Update username extractor metadata of the chat after being indexed

        Parameters
        ----------
        metadata : UsernameExtractorMetadata
            Updated metadata
        run_depth : int
            Depth of running the function. stop and return False after 10 runs.

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if metadata is None or run_depth > 10:
            return False

        self_copy = self.copy(deep=True)
        updated_metadata = self_copy.username_extractor_metadata.update_metadata(metadata)
        updated_metadata.update_score()

        updated = self.update(self_copy, reserve_non_updatable_fields=True)

        if not updated:
            chat = Chat.get(self.key)
            return chat.update_username_extractor_metadata(metadata, run_depth + 1)

        return True

    def update_audio_indexer_score(
        self,
        score: float,
    ) -> bool:
        """
        Updates audio indexer score of the chat

        Parameters
        ----------
        score : float
            New score

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if score is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.audio_indexer_metadata.score = score

        return self.update(self_copy, reserve_non_updatable_fields=True)

    def update_audio_doc_indexer_score(
        self,
        score: float,
    ) -> bool:
        """
        Updates audio doc indexer score of the chat

        Parameters
        ----------
        score : float
            New score

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if score is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.audio_doc_indexer_metadata.score = score

        return self.update(self_copy, reserve_non_updatable_fields=True)

    def update_username_extractor_score(
        self,
        score: float,
    ) -> bool:
        """
        Updates username extractor score of the chat

        Parameters
        ----------
        score : float
            New score

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if score is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.username_extractor_metadata.score = score

        return self.update(self_copy, reserve_non_updatable_fields=True)

class ChatMethods:
    _get_chat_linked_chat_with_edge_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@linked_chat'],vertexCollections:['@chat']}"
        "   return {linked_chat:v, edge:e}"
    )

    def _create_chat(
        self,
        telegram_chat: pyrogram.types.Chat,
    ) -> Optional[Chat]:
        """
        Create a `Chat` from `telegram_chat` argument.

        Parameters
        ----------
        telegram_chat : pyrogram.types.Chat
            Telegram Chat to create `Chat` document from.

        Returns
        -------
        Chat, optional
            Chat if the operation was successful, otherwise, return `None`.

        Notes
        -----
        This method is not meant to be accessed directly, it is only to be used inside other methods.
        """
        if telegram_chat is None:
            return None

        chat, successful = Chat.insert(Chat.parse(telegram_chat))
        if chat and successful:
            if telegram_chat.linked_chat:
                linked_chat = self.get_or_create_chat(telegram_chat.linked_chat)
                if linked_chat:
                    try:
                        LinkedChat.get_or_create_edge(chat, linked_chat)
                    except ValueError as e:
                        pass
                else:
                    # todo: could not create linked_chat
                    logger.error(f"Could not create linked_chat: {prettify(telegram_chat.linked_chat)}")

            return chat

        return None

    def get_or_create_chat(
        self,
        telegram_chat: pyrogram.types.Chat,
    ) -> Optional[Chat]:
        """
        Get a `Chat` document if it exists, otherwise create it.

        Parameters
        ----------
        telegram_chat : pyrogram.types.Chat
            Telegram chat to create the `Chat` document from.

        Returns
        -------
        Chat, optional
            `Chat` document if it was successful, otherwise, return `None`.

        """
        if telegram_chat is None:
            return None

        chat = Chat.get(Chat.parse_key(telegram_chat))
        if chat is None:
            # chat does not exist in the database, create it
            chat = self._create_chat(telegram_chat)

        return chat

    def update_or_create_chat(
        self,
        telegram_chat: pyrogram.types.Chat,
    ) -> Optional[Chat]:
        """
        Update or create a `Chat` and return it if the operation was successful, otherwise, return `None`.

        Parameters
        ----------
        telegram_chat : pyrogram.types.Chat
            Telegram chat object to create the `Chat` document from

        Returns
        -------
        Chat, optional
            Updated/Created `Chat` if successful, otherwise return `None`.

        """
        if telegram_chat is None:
            return None

        chat = Chat.get(Chat.parse_key(telegram_chat))
        if chat is not None:
            successful = chat.update(Chat.parse(telegram_chat))
            if successful:
                if telegram_chat.linked_chat:
                    # check if an update of connected vertices is needed
                    try:
                        linked_chat, linked_chat_edge = self.get_chat_linked_chat_with_edge(chat)
                    except ValueError as e:
                        logger.exception(e)
                    else:
                        if linked_chat and linked_chat_edge:
                            # chat has linked chat already, check if it needs to create/update the existing one or delete
                            # the old one and add a new one.
                            if linked_chat.chat_id == telegram_chat.linked_chat.id:
                                # update the linked chat
                                linked_chat.update(Chat.parse(telegram_chat.linked_chat))
                            else:
                                # delete the old link
                                linked_chat_edge.delete()

                                # create the new link and new chat
                                linked_chat = self.update_or_create_chat(telegram_chat.linked_chat)
                                try:
                                    LinkedChat.get_or_create_edge(chat, linked_chat)
                                except ValueError:
                                    logger.error(
                                        f"Could not create `linked_chat` edge: {prettify(telegram_chat.linked_chat)}"
                                    )
                        else:
                            # chat did not have any linked chat before, create it
                            linked_chat = self.get_or_create_chat(telegram_chat.linked_chat)
                            try:
                                LinkedChat.get_or_create_edge(chat, linked_chat)
                            except ValueError:
                                logger.error(
                                    f"Could not create `linked_chat` edge:" f" {prettify(telegram_chat.linked_chat)}"
                                )

                else:
                    # the chat doesn't have any linked chat, check if it had any before and delete the link
                    try:
                        linked_chat, linked_chat_edge = self.get_chat_linked_chat_with_edge(chat)
                    except ValueError as e:
                        logger.exception(e)
                    else:
                        if linked_chat and linked_chat_edge:
                            # chat had linked chat before, remove the link
                            linked_chat_edge.delete()
        else:
            chat: Chat = self._create_chat(telegram_chat)

        return chat

    def get_chat_linked_chat_with_edge(
        self,
        chat: Chat,
    ) -> Tuple[Optional[Chat], Optional[LinkedChat]]:
        """
        Get linked `Chat` with `LinkedChat` edge for the given `Chat`.

        Parameters
        ----------
        chat : Chat
            Chat to get its linked chats

        Returns
        -------
        tuple
            Chat and Linked Chat edge

        Raises
        ------
        ValueError
            If the given `Chat` has more than one linked chats.

        """
        if chat is None or chat.id is None:
            return None, None

        cursor = Chat.execute_query(
            self._get_chat_linked_chat_with_edge_query,
            bind_vars={
                "start_vertex": chat.id,
                "linked_chat": LinkedChat._collection_name,
                "chat": Chat._collection_name,
            },
        )
        if cursor is not None and len(cursor):
            if len(cursor) > 1:
                raise ValueError(f"Chat with id `{chat.id}` have more than one linked chats.")
            else:
                try:
                    doc = cursor.pop()
                except CursorEmptyError:
                    pass
                except Exception as e:
                    logger.exception(e)
                else:
                    linked_chat: Chat = Chat.from_collection(doc["linked_chat"])
                    edge: LinkedChat = LinkedChat.from_collection(doc["edge"])
                    return linked_chat, edge

        return None, None
