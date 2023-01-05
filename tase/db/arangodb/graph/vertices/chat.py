from __future__ import annotations

import collections
from typing import Optional, List, Tuple, TYPE_CHECKING, Deque, Iterable, AsyncGenerator

import pyrogram

from aioarango.models import PersistentIndex
from tase.common.utils import prettify, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.db.helpers import ChatScores
from tase.errors import InvalidFromVertex, InvalidToVertex
from tase.my_logger import logger
from .base_vertex import BaseVertex

if TYPE_CHECKING:
    from .. import ArangoGraphMethods

from ...enums import ChatType
from ...helpers import (
    Restriction,
    AudioIndexerMetadata,
    AudioDocIndexerMetadata,
    UsernameExtractorMetadata,
)


class Chat(BaseVertex):
    __collection_name__ = "chats"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="chat_id",
            fields=[
                "chat_id",
            ],
            unique=True,
        ),
        PersistentIndex(
            custom_version=1,
            name="is_public",
            fields=[
                "is_public",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="chat_type",
            fields=[
                "chat_type",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_verified",
            fields=[
                "is_verified",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_restricted",
            fields=[
                "is_restricted",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_scam",
            fields=[
                "is_scam",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_fake",
            fields=[
                "is_fake",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_support",
            fields=[
                "is_support",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="username",
            fields=[
                "username",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="dc_id",
            fields=[
                "dc_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="has_protected_content",
            fields=[
                "has_protected_content",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="members_count",
            fields=[
                "members_count",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="audio_indexer_metadata_last_run_at",
            fields=[
                "audio_indexer_metadata.last_run_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="audio_doc_indexer_metadata_last_run_at",
            fields=[
                "audio_doc_indexer_metadata.last_run_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="username_extractor_metadata_last_run_at",
            fields=[
                "username_extractor_metadata.last_run_at",
            ],
        ),
    ]

    __non_updatable_fields__ = (
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

    is_valid: bool  # whether this chat is valid or not.

    audio_indexer_metadata: Optional[AudioIndexerMetadata]
    audio_doc_indexer_metadata: Optional[AudioDocIndexerMetadata]
    username_extractor_metadata: Optional[UsernameExtractorMetadata]

    @classmethod
    def parse_key(
        cls,
        telegram_chat: pyrogram.types.Chat,
    ) -> Optional[str]:
        if telegram_chat is None or telegram_chat.id is None:
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
            description=telegram_chat.description if telegram_chat.description else telegram_chat.bio,
            dc_id=telegram_chat.dc_id,
            has_protected_content=telegram_chat.has_protected_content,
            invite_link=telegram_chat.invite_link,
            restrictions=Restriction.parse_from_restrictions(telegram_chat.restrictions),
            distance=telegram_chat.distance,
            members_count=telegram_chat.members_count,
            is_valid=True,
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

    async def mark_as_invalid(self) -> bool:
        """
        Mark the `Chat` the as invalid. This happens when the chat is no longer valid or is deleted by Telegram.

        Returns
        -------
        bool
            Whether the operation was successful or not.

        """
        self_copy: Chat = self.copy(deep=True)
        self_copy.is_valid = False
        return await self.update(
            self_copy,
            reserve_non_updatable_fields=True,
            check_for_revisions_match=False,
        )

    async def update_username_extractor_metadata(
        self,
        metadata: UsernameExtractorMetadata,
    ) -> bool:
        """
        Update username extractor metadata of the chat after being indexed

        Parameters
        ----------
        metadata : UsernameExtractorMetadata
            Updated metadata

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if metadata is None:
            return False

        self_copy: Chat = self.copy(deep=True)
        if self_copy.username_extractor_metadata is None:
            self_copy.username_extractor_metadata = UsernameExtractorMetadata()
        updated_metadata = self_copy.username_extractor_metadata.update_metadata(metadata)
        updated_metadata.update_score()

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
        )

    async def update_audio_indexer_metadata(
        self,
        metadata: AudioIndexerMetadata,
    ) -> bool:
        """
        Update audio indexer metadata of the chat after being indexed

        Parameters
        ----------
        metadata : AudioIndexerMetadata
            Updated metadata

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if metadata is None:
            return False

        self_copy: Chat = self.copy(deep=True)
        if self_copy.audio_indexer_metadata is None:
            self_copy.audio_indexer_metadata = AudioIndexerMetadata()
        updated_metadata = self_copy.audio_indexer_metadata.update_metadata(metadata)
        updated_metadata.update_score()

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
        )

    async def update_audio_doc_indexer_metadata(
        self,
        metadata: AudioDocIndexerMetadata,
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
        if metadata is None:
            return False

        self_copy: Chat = self.copy(deep=True)
        if self_copy.audio_doc_indexer_metadata is None:
            self_copy.audio_doc_indexer_metadata = AudioDocIndexerMetadata()
        updated_metadata = self_copy.audio_doc_indexer_metadata.update_metadata(metadata)
        updated_metadata.update_score()

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
        )

    async def update_audio_indexer_score(
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

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
        )

    async def update_audio_doc_indexer_score(
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

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
        )

    async def update_username_extractor_score(
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

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
            retry_on_failure=True,
        )

    def get_chat_scores(self) -> ChatScores:
        """
        Return scores of this chat.

        Returns
        -------
        ChatScores
            A `ChatScores` object is returned.

        """
        return ChatScores(
            audio_indexer_score=self.audio_indexer_metadata.score if self.audio_indexer_metadata else 0.0,
            audio_doc_indexer_score=self.audio_doc_indexer_metadata.score if self.audio_doc_indexer_metadata else 0.0,
            username_extractor_score=self.username_extractor_metadata.score if self.username_extractor_metadata else 0.0,
        )


class ChatMethods:
    _get_chat_linked_chat_with_edge_query = (
        "for v,e in 1..1 outbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@linked_chat], vertexCollections:[@chat]}"
        "   return {linked_chat:v, edge:e}"
    )

    _get_chat_username_with_edge_query = (
        "for v,e in 1..1 outbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@has], vertexCollections:[@usernames]}"
        "   return {username:v, edge:e}"
    )

    _get_chats_sorted_by_username_extractor_score_query = (
        "for chat in @@chats"
        "   filter chat.is_valid == true and chat.chat_type == @chat_type and chat.is_public == true and chat.username_extractor_metadata != null"
        "   sort chat.username_extractor_metadata.score desc, chat.members_count desc"
        "   return chat"
    )

    _get_not_extracted_chats_sorted_by_members_count_query = (
        "for chat in @@chats"
        "   filter chat.is_valid == true and chat.chat_type == @chat_type and chat.is_public == true and chat.username_extractor_metadata == null"
        "   sort chat.members_count desc"
        "   return chat"
    )

    _get_chats_sorted_by_audio_indexer_score_query = (
        "for chat in @@chats"
        "   filter chat.is_valid == true and chat.chat_type == @chat_type and chat.is_public == true and chat.audio_indexer_metadata != null"
        "   sort chat.audio_indexer_metadata.score desc, chat.members_count desc"
        "   return chat"
    )

    _get_not_indexed_chats_sorted_by_members_count_query = (
        "for chat in @@chats"
        "   filter chat.is_valid == true and chat.chat_type == @chat_type and chat.is_public == true and chat.audio_indexer_metadata == null"
        "   sort chat.members_count desc"
        "   return chat"
    )

    _get_chats_sorted_by_audio_doc_indexer_score = (
        "for chat in @@chats"
        "   filter chat.is_valid == true and chat.chat_type == @chat_type and chat.audio_doc_indexer_metadata != null "
        "   sort chat.audio_doc_indexer_metadata.score desc, chat.members_count desc"
        "   return chat"
    )

    _get_chats_by_keys = "return document(@@chats, @chat_keys)"

    async def _create_chat(
        self: ArangoGraphMethods,
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

        chat, successful = await Chat.insert(Chat.parse(telegram_chat))
        if chat and successful:
            if telegram_chat.linked_chat:
                linked_chat = await self.get_or_create_chat(telegram_chat.linked_chat)
                if linked_chat:
                    try:
                        await LinkedChat.get_or_create_edge(chat, linked_chat)
                    except (InvalidFromVertex, InvalidToVertex):
                        pass
                else:
                    # todo: could not create linked_chat
                    logger.error(f"Could not create linked_chat: {prettify(telegram_chat.linked_chat)}")

            if chat.username:
                await self._create_chat_linked_username(chat)

            return chat

        return None

    async def get_or_create_chat(
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

        chat = await Chat.get(Chat.parse_key(telegram_chat))
        if chat is None:
            # chat does not exist in the database, create it
            chat = await self._create_chat(telegram_chat)

        return chat

    async def update_or_create_chat(
        self: ArangoGraphMethods,
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

        chat = await Chat.get(Chat.parse_key(telegram_chat))
        if chat is not None:
            successful = await chat.update(Chat.parse(telegram_chat))
            if successful:
                await self._update_linked_chat(chat, telegram_chat)
                await self._update_linked_username(chat, telegram_chat)

                if chat.chat_type == ChatType.CHANNEL and (not chat.username or not telegram_chat.username):
                    await chat.mark_as_invalid()
                    await self.mark_chat_audios_as_deleted(chat.chat_id)

        else:
            chat: Chat = await self._create_chat(telegram_chat)

        return chat

    async def _create_chat_linked_username(
        self: ArangoGraphMethods,
        chat: Chat,
    ) -> bool:
        usernames_vertex = await self.get_or_create_username(
            chat.username,
            create_mention_edge=False,
        )
        if usernames_vertex:
            if not usernames_vertex.is_checked:
                await usernames_vertex.check(True, get_now_timestamp(), True)

            from tase.db.arangodb.graph.edges import Has

            has_edge = await Has.get_or_create_edge(chat, usernames_vertex)
            if not has_edge:
                logger.error(f"could not create `has` edge from `chat` with key `{chat.key}` to `username` with key `{usernames_vertex.key}`")
                return False
        else:
            logger.error(f"could not create the username vertex for chat with key `{chat.key}`")
            return False

        return True

    async def _update_linked_username(
        self: ArangoGraphMethods,
        chat: Chat,
        telegram_chat: pyrogram.types.Chat,
    ):
        if chat is None or telegram_chat is None:
            return

        from tase.db.arangodb.graph.vertices import Username
        from tase.db.arangodb.graph.edges import Has

        async def remove_old_links(username_vertex_: Username, has_edge_: Has):
            deleted = await has_edge_.delete()
            if deleted:
                if not await username_vertex_.check(False, get_now_timestamp(), False):
                    logger.error(f"could not check username with key `{username_vertex_.key}`")
            else:
                logger.error(f"could not delete the `has` edge from chat with key `{chat.key}` to username with key `{username_vertex_.key}`")

        if telegram_chat.username:
            try:
                username_vertex, has_edge = await self.get_chat_username_with_edge(chat)
            except ValueError as e:
                # chat has more than one username linked with it
                logger.exception(e)
            else:
                if username_vertex and has_edge:
                    username_vertex: graph_models.vertices.Username = username_vertex
                    has_edge: graph_models.edges.Has = has_edge

                    if username_vertex.username != telegram_chat.username.lower():
                        # the username of the chat has changed since last time, remove the link between the
                        # chat and the old username and set the username's `is_checked` property as `False`
                        if await self._create_chat_linked_username(chat):
                            await remove_old_links(username_vertex, has_edge)
                    else:
                        # username has not changed since last, no need to update anything
                        pass

                else:
                    # the chat did not have any usernames before, create it now
                    await self._create_chat_linked_username(chat)
        else:
            # the chat doesn't have any linked username, check if it had any before and delete the link
            try:
                username_vertex, has_edge = await self.get_chat_username_with_edge(chat)
            except ValueError as e:
                # chat has more than one username linked with it
                logger.exception(e)
            else:
                if username_vertex and has_edge:
                    await remove_old_links(username_vertex, has_edge)

    async def _update_linked_chat(
        self,
        chat: Chat,
        telegram_chat: pyrogram.types.Chat,
    ):
        if chat is None or telegram_chat is None:
            return

        if telegram_chat.linked_chat:
            # check if an update of connected vertices is needed
            try:
                linked_chat, linked_chat_edge = await self.get_chat_linked_chat_with_edge(chat)
            except ValueError as e:
                logger.exception(e)
            else:
                from tase.db.arangodb.graph.edges import LinkedChat

                if linked_chat and linked_chat_edge:
                    # chat has linked chat already, check if it needs to create/update the existing one or delete the old one and add a new one.
                    if linked_chat.chat_id == telegram_chat.linked_chat.id:
                        # update the linked chat
                        updated = await linked_chat.update(Chat.parse(telegram_chat.linked_chat))
                    else:
                        # delete the old link
                        await linked_chat_edge.delete()

                        # create the new link and new chat
                        linked_chat = await self.update_or_create_chat(telegram_chat.linked_chat)
                        try:
                            await LinkedChat.get_or_create_edge(chat, linked_chat)
                        except (InvalidFromVertex, InvalidToVertex):
                            pass
                else:
                    # chat did not have any linked chat before, create it
                    linked_chat = await self.get_or_create_chat(telegram_chat.linked_chat)
                    try:
                        await LinkedChat.get_or_create_edge(chat, linked_chat)
                    except (InvalidFromVertex, InvalidToVertex):
                        pass

        else:
            # the chat doesn't have any linked chat, check if it had any before and delete the link
            try:
                linked_chat, linked_chat_edge = await self.get_chat_linked_chat_with_edge(chat)
            except ValueError as e:
                logger.exception(e)
            else:
                if linked_chat and linked_chat_edge:
                    # chat had linked chat before, remove the link
                    await linked_chat_edge.delete()

    async def get_chat_linked_chat_with_edge(
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

        results = collections.deque()

        async with await Chat.execute_query(
            self._get_chat_linked_chat_with_edge_query,
            bind_vars={
                "start_vertex": chat.id,
                "linked_chat": LinkedChat.__collection_name__,
                "chat": Chat.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                linked_chat: Chat = Chat.from_collection(doc["linked_chat"])
                edge: LinkedChat = LinkedChat.from_collection(doc["edge"])

                results.append((linked_chat, edge))

        if len(results) > 1:
            raise ValueError(f"Chat with id `{chat.id}` have more than one linked chats.")

        if results:
            return results[0]

        return None, None

    async def get_chat_username_with_edge(
        self,
        chat: Chat,
    ) -> Tuple[Optional[graph_models.vertices.Username], Optional[graph_models.edges.Has]]:
        """
        Get `Username` vertex with `has` edge for the given `Chat`.

        Parameters
        ----------
        chat : Chat
            Chat to get its linked chats

        Returns
        -------
        tuple
            Username and Has edge

        Raises
        ------
        ValueError
            If the given `Chat` has more than one username.

        """
        if chat is None or chat.id is None:
            return None, None

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Username

        results = collections.deque()

        async with await Chat.execute_query(
            self._get_chat_username_with_edge_query,
            bind_vars={
                "start_vertex": chat.id,
                "has": Has.__collection_name__,
                "usernames": Username.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                username: Username = Username.from_collection(doc["username"])
                edge: Has = Has.from_collection(doc["edge"])

                results.append((username, edge))

        if len(results) > 1:
            raise ValueError(f"Chat with id `{chat.id}` have more than one usernames.")

        if results:
            return results[0]

        return None, None

    async def get_chats_from_keys(
        self,
        keys: Iterable[str],
    ) -> Deque[Chat]:
        """
        Get a list of Chats from a list of keys.

        Parameters
        ----------
        keys : Iterable[str]
            List of keys to get the chats from.

        Returns
        -------
        Deque
            List of Chats if operation was successful, otherwise, return None

        """
        if not keys:
            return collections.deque()

        res = collections.deque()
        async with await Chat.execute_query(
            self._get_chats_by_keys,
            bind_vars={
                "@chats": Chat.__collection_name__,
                "chat_keys": list(keys),
            },
        ) as cursor:
            async for chats_lst in cursor:
                for doc in chats_lst:
                    res.append(Chat.from_collection(doc))

        return res

    async def get_chats_sorted_by_username_extractor_score(
        self,
        only_include_indexed_chats: bool = True,
    ) -> AsyncGenerator[Chat, None]:
        """
        Gets list of chats sorted by their username extractor importance score in a descending order.

        Parameters
        ----------
        only_include_indexed_chats : bool, default: True
            Whether to filter chats by whether they have been indexed before or not.

        Yields
        ------
        Chat
            List of Chat objects
        """
        # todo: only public channels can be indexed for now. add support for other types if necessary
        chat_type = ChatType.CHANNEL.value

        async with await Chat.execute_query(
            self._get_chats_sorted_by_username_extractor_score_query
            if only_include_indexed_chats
            else self._get_not_extracted_chats_sorted_by_members_count_query,
            stream=True,
            bind_vars={
                "@chats": Chat.__collection_name__,
                "chat_type": chat_type,
            },
        ) as cursor:
            async for doc in cursor:
                yield Chat.from_collection(doc)

    async def get_chats_sorted_by_audio_indexer_score(
        self,
        only_include_indexed_chats: bool = True,
    ) -> AsyncGenerator[Chat, None]:
        """
        Get list of chats sorted by their audio importance score in a descending order.

        Parameters
        ----------
        only_include_indexed_chats : bool, default: True
            Whether to filter chats by whether they have been indexed before or not.

        Yields
        ------
        Chat
            List of Chat objects
        """
        # todo: only public channels can be indexed for now. add support for other types if necessary
        chat_type = ChatType.CHANNEL.value

        async with await Chat.execute_query(
            self._get_chats_sorted_by_audio_indexer_score_query if only_include_indexed_chats else self._get_not_indexed_chats_sorted_by_members_count_query,
            stream=True,
            bind_vars={
                "@chats": Chat.__collection_name__,
                "chat_type": chat_type,
            },
        ) as cursor:
            async for doc in cursor:
                yield Chat.from_collection(doc)

    async def get_chats_sorted_by_audio_doc_indexer_score(self) -> AsyncGenerator[Chat, None]:
        """
        Gets list of chats sorted by their audio doc importance score in a descending order

        Yields
        ------
        Chat
            List of Chat objects
        """
        # todo: only public channels can be indexed for now. add support for other types if necessary
        chat_type = ChatType.CHANNEL.value

        async with await Chat.execute_query(
            self._get_chats_sorted_by_audio_doc_indexer_score,
            stream=True,
            bind_vars={
                "@chats": Chat.__collection_name__,
                "chat_type": chat_type,
            },
        ) as cursor:
            async for doc in cursor:
                yield Chat.from_collection(doc)

    async def get_chat_by_telegram_chat_id(
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

        return await Chat.get(str(chat_id))

    async def get_chat_by_username(
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

        return await Chat.find_one({"username": username.lower()})

    async def get_chat_by_key(
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

        return await Chat.get(key)
