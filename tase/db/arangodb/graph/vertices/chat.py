from __future__ import annotations

from typing import Optional, List, Tuple, Generator

import pyrogram
from arango import CursorEmptyError

from tase.common.utils import prettify
from tase.db.arangodb import graph as graph_models
from tase.errors import InvalidFromVertex, InvalidToVertex
from tase.my_logger import logger
from .base_vertex import BaseVertex
from ...enums import ChatType
from ...helpers import (
    Restriction,
    AudioIndexerMetadata,
    AudioDocIndexerMetadata,
    UsernameExtractorMetadata,
)


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
    distance: Optional[int]
    members_count: Optional[int]

    audio_indexer_metadata: Optional[AudioIndexerMetadata]
    audio_doc_indexer_metadata: Optional[AudioDocIndexerMetadata]
    username_extractor_metadata: Optional[UsernameExtractorMetadata]

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
    ) -> Optional[Chat]:
        """
        Parse the `Chat` vertex from the given `telegram_chat` parameter

        Parameters
        ----------
        telegram_chat : pyrogram.types.Chat
            Telegram Chat object

        Returns
        -------
        Chat, optional
            Parsed chat if successful, otherwise, return None
        """
        key = Chat.parse_key(telegram_chat)
        if key is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_chat.type)

        return Chat(
            key=key,
            chat_id=telegram_chat.id,
            is_public=Chat.get_is_public(telegram_chat.username, chat_type),
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
            description=telegram_chat.description
            if telegram_chat.description
            else telegram_chat.bio,
            dc_id=telegram_chat.dc_id,
            has_protected_content=telegram_chat.has_protected_content,
            invite_link=telegram_chat.invite_link,
            restrictions=Restriction.parse_from_restrictions(
                telegram_chat.restrictions
            ),
            distance=telegram_chat.distance,
            members_count=telegram_chat.members_count,
        )

    @staticmethod
    def get_is_public(
        username: Optional[str],
        chat_type: ChatType,
    ) -> bool:
        """
        Check whether a chat is public or not

        Parameters
        ----------
        username : str, optional
            Chat username
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
            if username is not None and len(username):
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

        self_copy: Chat = self.copy(deep=True)
        if self_copy.username_extractor_metadata is None:
            self_copy.username_extractor_metadata = UsernameExtractorMetadata()
        updated_metadata = self_copy.username_extractor_metadata.update_metadata(
            metadata
        )
        updated_metadata.update_score()

        updated = self.update(self_copy, reserve_non_updatable_fields=False)

        if not updated:
            chat = Chat.get(self.key)
            updated = chat.update_username_extractor_metadata(metadata, run_depth + 1)

        return updated

    def update_audio_indexer_metadata(
        self,
        metadata: AudioIndexerMetadata,
        run_depth: int = 1,
    ) -> bool:
        """
        Update audio indexer metadata of the chat after being indexed

        Parameters
        ----------
        metadata : AudioIndexerMetadata
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

        self_copy: Chat = self.copy(deep=True)
        if self_copy.audio_indexer_metadata is None:
            self_copy.audio_indexer_metadata = AudioIndexerMetadata()
        updated_metadata = self_copy.audio_indexer_metadata.update_metadata(metadata)
        updated_metadata.update_score()

        updated = self.update(self_copy, reserve_non_updatable_fields=False)

        if not updated:
            chat = Chat.get(self.key)
            updated = chat.update_audio_indexer_metadata(metadata, run_depth + 1)

        return updated

    def update_audio_doc_indexer_metadata(
        self,
        metadata: AudioDocIndexerMetadata,
        run_depth: int = 1,
    ) -> bool:
        """
        Update audio doc indexer metadata of the chat after being indexed

        Parameters
        ----------
        metadata : AudioDocIndexerMetadata
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

        self_copy: Chat = self.copy(deep=True)
        if self_copy.audio_doc_indexer_metadata is None:
            self_copy.audio_doc_indexer_metadata = AudioDocIndexerMetadata()
        updated_metadata = self_copy.audio_doc_indexer_metadata.update_metadata(
            metadata
        )
        updated_metadata.update_score()

        updated = self.update(self_copy, reserve_non_updatable_fields=False)

        if not updated:
            chat = Chat.get(self.key)
            updated = chat.update_audio_doc_indexer_metadata(metadata, run_depth + 1)

        return updated

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

        self_copy: Chat = self.copy(deep=True)
        if self_copy.audio_indexer_metadata is None:
            self_copy.audio_indexer_metadata = AudioIndexerMetadata()
        self_copy.audio_indexer_metadata.score = score

        return self.update(self_copy, reserve_non_updatable_fields=False)

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

        self_copy: Chat = self.copy(deep=True)
        if self_copy.audio_doc_indexer_metadata is None:
            self_copy.audio_doc_indexer_metadata = AudioDocIndexerMetadata()
        self_copy.audio_doc_indexer_metadata.score = score

        return self.update(self_copy, reserve_non_updatable_fields=False)

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

        self_copy: Chat = self.copy(deep=True)
        if self_copy.username_extractor_metadata is None:
            self_copy.username_extractor_metadata = UsernameExtractorMetadata()
        self_copy.username_extractor_metadata.score = score

        return self.update(self_copy, reserve_non_updatable_fields=False)


class ChatMethods:
    _get_chat_linked_chat_with_edge_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@linked_chat'],vertexCollections:['@chat']}"
        "   return {linked_chat:v, edge:e}"
    )

    _get_chats_sorted_by_username_extractor_score_query = (
        "for chat in @chats"
        "   filter chat.chat_type == @chat_type and chat.is_public == true and chat.username_extractor_metadata != null"
        "   sort chat.username_extractor_metadata.score desc, chat.members_count desc"
        "   return chat"
    )

    _get_not_extracted_chats_sorted_by_members_count_query = (
        "for chat in @chats"
        "   filter chat.chat_type == @chat_type and chat.is_public == true and chat.username_extractor_metadata == null"
        "   sort chat.members_count desc"
        "   return chat"
    )

    _get_chats_sorted_by_audio_indexer_score_query = (
        "for chat in @chats"
        "   filter chat.chat_type == @chat_type and chat.is_public == true and chat.audio_indexer_metadata != null"
        "   sort chat.audio_indexer_metadata.score desc, chat.members_count desc"
        "   return chat"
    )

    _get_not_indexed_chats_sorted_by_members_count_query = (
        "for chat in @chats"
        "   filter chat.chat_type == @chat_type and chat.is_public == true and chat.audio_indexer_metadata == null"
        "   sort chat.members_count desc"
        "   return chat"
    )

    _get_chats_sorted_by_audio_doc_indexer_score = (
        "for chat in @chats"
        "   filter chat.chat_type == @chat_type and chat.audio_doc_indexer_metadata != null "
        "   sort chat.audio_doc_indexer_metadata.score desc, chat.members_count desc"
        "   return chat"
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

        from tase.db.arangodb.graph.edges import LinkedChat

        chat, successful = Chat.insert(Chat.parse(telegram_chat))
        if chat and successful:
            if telegram_chat.linked_chat:
                linked_chat = self.get_or_create_chat(telegram_chat.linked_chat)
                if linked_chat:
                    try:
                        LinkedChat.get_or_create_edge(chat, linked_chat)
                    except (InvalidFromVertex, InvalidToVertex):
                        pass
                else:
                    # todo: could not create linked_chat
                    logger.error(
                        f"Could not create linked_chat: {prettify(telegram_chat.linked_chat)}"
                    )

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

        from tase.db.arangodb.graph.edges import LinkedChat

        chat = Chat.get(Chat.parse_key(telegram_chat))
        if chat is not None:
            successful = chat.update(Chat.parse(telegram_chat))
            if successful:
                if telegram_chat.linked_chat:
                    # check if an update of connected vertices is needed
                    try:
                        (
                            linked_chat,
                            linked_chat_edge,
                        ) = self.get_chat_linked_chat_with_edge(chat)
                    except ValueError as e:
                        logger.exception(e)
                    else:
                        if linked_chat and linked_chat_edge:
                            # chat has linked chat already, check if it needs to create/update the existing one or delete
                            # the old one and add a new one.
                            if linked_chat.chat_id == telegram_chat.linked_chat.id:
                                # update the linked chat
                                updated = linked_chat.update(
                                    Chat.parse(telegram_chat.linked_chat)
                                )
                            else:
                                # delete the old link
                                linked_chat_edge.delete()

                                # create the new link and new chat
                                linked_chat = self.update_or_create_chat(
                                    telegram_chat.linked_chat
                                )
                                try:
                                    LinkedChat.get_or_create_edge(chat, linked_chat)
                                except (InvalidFromVertex, InvalidToVertex):
                                    pass
                        else:
                            # chat did not have any linked chat before, create it
                            linked_chat = self.get_or_create_chat(
                                telegram_chat.linked_chat
                            )
                            try:
                                LinkedChat.get_or_create_edge(chat, linked_chat)
                            except (InvalidFromVertex, InvalidToVertex):
                                pass

                else:
                    # the chat doesn't have any linked chat, check if it had any before and delete the link
                    try:
                        (
                            linked_chat,
                            linked_chat_edge,
                        ) = self.get_chat_linked_chat_with_edge(chat)
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
    ) -> Tuple[Optional[Chat], Optional[graph_models.edges.LinkedChat]]:
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

        from tase.db.arangodb.graph.edges import LinkedChat

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
                raise ValueError(
                    f"Chat with id `{chat.id}` have more than one linked chats."
                )
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

    def get_chats_sorted_by_username_extractor_score(
        self,
        filter_by_indexed_chats: bool = True,
    ) -> Generator[Chat, None, None]:
        """
        Gets list of chats sorted by their username extractor importance score in a descending order

        Parameters
        ----------
        filter_by_indexed_chats : bool, default: True
            Whether to filter chats by whether they have been indexed before or not

        Yields
        ------
        Chat
            List of Chat objects
        """
        # todo: only public channels can be indexed for now. add support for other types if necessary
        chat_type = ChatType.CHANNEL.value

        cursor = Chat.execute_query(
            self._get_chats_sorted_by_username_extractor_score_query
            if filter_by_indexed_chats
            else self._get_not_extracted_chats_sorted_by_members_count_query,
            bind_vars={
                "chats": Chat._collection_name,
                "chat_type": chat_type,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Chat.from_collection(doc)

    def get_chats_sorted_by_audio_indexer_score(
        self,
        filter_by_indexed_chats: bool = True,
    ) -> Generator[Chat, None, None]:
        """
        Get list of chats sorted by their audio importance score in a descending order

        Parameters
        ----------
        filter_by_indexed_chats : bool, default: True
            Whether to filter chats by whether they have been indexed before or not

        Yields
        ------
        Chat
            List of Chat objects
        """
        # todo: only public channels can be indexed for now. add support for other types if necessary
        chat_type = ChatType.CHANNEL.value

        cursor = Chat.execute_query(
            self._get_chats_sorted_by_audio_indexer_score_query
            if filter_by_indexed_chats
            else self._get_not_indexed_chats_sorted_by_members_count_query,
            bind_vars={
                "chats": Chat._collection_name,
                "chat_type": chat_type,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Chat.from_collection(doc)

    def get_chats_sorted_by_audio_doc_indexer_score(
        self,
    ) -> Generator[Chat, None, None]:
        """
        Gets list of chats sorted by their audio doc importance score in a descending order

        Yields
        ------
        Chat
            List of Chat objects
        """
        # todo: only public channels can be indexed for now. add support for other types if necessary
        chat_type = ChatType.CHANNEL.value

        cursor = Chat.execute_query(
            self._get_chats_sorted_by_audio_doc_indexer_score,
            bind_vars={
                "chats": Chat._collection_name,
                "chat_type": chat_type,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Chat.from_collection(doc)

    def get_chat_by_telegram_chat_id(
        self,
        chat_id: int,
    ) -> Optional[Chat]:
        """
        Get `Chat` vertex by its `key` (`chat_id`)

        Parameters
        ----------
        chat_id : int
            ID of telegram chat

        Returns
        -------
        Chat, optional
            Chat vertex if it exists in the ArangoDB, otherwise, return None

        """
        if chat_id is None:
            return None

        return Chat.get(str(chat_id))

    def get_chat_by_username(
        self,
        username: str,
    ) -> Optional[Chat]:
        """
        Get `Chat` vertex by its `username`

        Parameters
        ----------
        username : str
            Username to find the chat by

        Returns
        -------
        Chat, optional
            Chat if it exists by the given username, otherwise, return None

        """
        if username is None:
            return None

        return Chat.find_one({"username": username.lower()})

    def get_chat_by_key(
        self,
        key: str,
    ) -> Optional[Chat]:
        """
        Get `Chat` vertex by its `key`

        Parameters
        ----------
        key : str
            Key to find the chat by

        Returns
        -------
        Chat, optional
            Chat if it exists by the given key, otherwise, return None

        """
        if key is None:
            return None

        return Chat.get(key)
