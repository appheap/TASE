from __future__ import annotations

from typing import Optional, Union

from aioarango.models import PersistentIndex
from tase.errors import InvalidFromVertex, InvalidToVertex
from tase.my_logger import logger
from . import Has
from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Chat, Username
from ...enums import MentionSource, ChatType


class Mentions(BaseEdge):
    """
    Connection from `Chat` to [`Chat`,`Username`]
    """

    __collection_name__ = "mentions"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="is_direct_mention",
            fields=[
                "is_direct_mention",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="mentioned_at",
            fields=[
                "mentioned_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="mention_source",
            fields=[
                "mention_source",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="checked_at",
            fields=[
                "checked_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="is_checked",
            fields=[
                "is_checked",
            ],
        ),
    ]

    __from_vertex_collections__ = (Chat,)
    __to_vertex_collections__ = (
        Chat,
        Username,
    )

    is_direct_mention: bool
    mentioned_at: int
    mention_source: MentionSource
    mention_start_index: int
    from_message_id: int

    # this two attributes are only ment for connections from a `chat` to a `username`.
    checked_at: Optional[int]
    is_checked: Optional[bool]
    """
    whether this mention has been checked and, its effect has been calculated on the chat username extractor metadata
    """

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[Chat, Username],
        to_vertex: Union[Chat, Username],
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None or mentioned_at is None or mention_source is None or mention_start_index is None or from_message_id is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}:{mentioned_at}:{from_message_id}:{mention_source.value}:{mention_start_index}"

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Union[Chat, Username],
        to_vertex: Union[Chat, Username],
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional[Mentions]:
        key = Mentions.parse_key(
            from_vertex,
            to_vertex,
            is_direct_mention,
            mentioned_at,
            mention_source,
            mention_start_index,
            from_message_id,
        )
        if key is None:
            return None

        return Mentions(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
            is_direct_mention=is_direct_mention,
            mentioned_at=mentioned_at,
            mention_source=mention_source,
            mention_start_index=mention_start_index,
            from_message_id=from_message_id,
            is_checked=False if isinstance(to_vertex, Username) else None,
        )

    async def check(
        self,
        is_checked: bool,
        checked_at: Optional[int],
    ) -> bool:
        self_copy = self.copy(deep=True)
        self_copy.is_checked = is_checked
        self_copy.checked_at = checked_at

        return await self.update(self_copy, reserve_non_updatable_fields=False)


class MentionsMethods:
    _create_and_check_mentions_edges_query = (
        "for v,e in 1..1 inbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@mentions], vertexCollections:[@chats]}"
        "   filter e.is_checked == false"
        "   sort e.created_at ASC"
        "   update e with {"
        "       is_checked:true, checked_at:@checked_at"
        "   } in @@mentions options {mergeObjects: true}"
        "   return {chat:v, mention_:NEW}"
    )

    _update_mentions_edges_from_chat_to_username_query = (
        "for v,e in 1..1 inbound @start_vertex graph @graph_name options {order:'dfs', edgeCollections:[@mentions], vertexCollections:[@chats]}"
        "   filter e.is_checked != @is_checked"
        "   sort e.created_at ASC"
        "   update e with {"
        "       is_checked:@is_checked, checked_at:@checked_at"
        "   } in @@mentions options {mergeObjects: true}"
        "   return NEW"
    )

    async def create_and_check_mentions_edges_after_username_check(
        self,
        mentioned_chat: Chat,
        username: Username,
    ) -> None:
        """
        Update mentions edges based on the data provided from `username` parameter and create new edges from
        `Username` to `Chat` and from `Chat` to mentioned `Chat`.

        Parameters
        ----------
        mentioned_chat: Chat
            Mentioned chat
        username : Username
            Username object to get data from for this update

        """
        if mentioned_chat is None or username is None:
            return None

        async with await Mentions.execute_query(
            self._create_and_check_mentions_edges_query,
            bind_vars={
                "start_vertex": username.id,
                "chats": Chat.__collection_name__,
                "mentions": Mentions.__collection_name__,
                "@mentions": Mentions.__collection_name__,
                "checked_at": username.checked_at,
            },
        ) as cursor:
            async for doc_dict in cursor:
                mentions_edge: Mentions = Mentions.from_collection(doc_dict["mention_"])
                source_chat: Chat = Chat.from_collection(doc_dict["chat"])

                if mentions_edge and source_chat:
                    if source_chat.username is not None and mentioned_chat.username is not None and mentioned_chat.username != source_chat.username:
                        # self-mentions and private chats are excluded

                        try:
                            # create the edge from `Username` vertex to mentioned `Chat` vertex
                            has_edge = await Has.get_or_create_edge(
                                mentioned_chat,
                                username,
                            )
                            if not has_edge:
                                logger.error(f"could not create `has` edge from `username` to `chat` vertex. [username:`{username.username}`]")

                            # create the edge from `Chat` vertex to mentioned `Chat` vertex
                            await Mentions.get_or_create_edge(
                                source_chat,
                                mentioned_chat,
                                mentions_edge.is_direct_mention,
                                mentions_edge.mentioned_at,
                                mentions_edge.mention_source,
                                mentions_edge.mention_start_index,
                                mentions_edge.from_message_id,
                            )
                        except (InvalidFromVertex, InvalidToVertex) as e:
                            # fixme
                            logger.info("invalid start or end vertex")

                        metadata = source_chat.username_extractor_metadata.copy()
                        metadata.reset_counters()

                        if mentions_edge.is_direct_mention:
                            metadata.direct_valid_mention_count += 1

                            if mentioned_chat.chat_type == ChatType.BOT:
                                metadata.direct_valid_bot_mention_count += 1
                            elif mentioned_chat.chat_type == ChatType.PRIVATE:
                                metadata.direct_valid_user_mention_count += 1
                            elif mentioned_chat.chat_type == ChatType.SUPERGROUP:
                                metadata.direct_valid_supergroup_mention_count += 1
                            elif mentioned_chat.chat_type == ChatType.CHANNEL:
                                metadata.direct_valid_channel_mention_count += 1

                        else:
                            metadata.indirect_valid_mention_count += 1

                            if mentioned_chat.chat_type == ChatType.BOT:
                                metadata.indirect_valid_bot_mention_count += 1
                            elif mentioned_chat.chat_type == ChatType.PRIVATE:
                                metadata.indirect_valid_user_mention_count += 1
                            elif mentioned_chat.chat_type == ChatType.SUPERGROUP:
                                metadata.indirect_valid_supergroup_mention_count += 1
                            elif mentioned_chat.chat_type == ChatType.CHANNEL:
                                metadata.indirect_valid_channel_mention_count += 1

                        successful = await source_chat.update_username_extractor_metadata(metadata)
                        if not successful:
                            # todo: the update wasn't successful, uncheck the edge so it could be updated later
                            await mentions_edge.check(False, None)

    async def update_mentions_edges_from_chat_to_username(
        self,
        username: Username,
    ) -> bool:
        """
        Update mentions edges based on the data provided from `username` parameter

        Parameters
        ----------
        username : Username
            Username object to get data from for this update
        Returns
        -------
        bool
            Whether the update was successful or not

        """
        if username is None or not isinstance(username, Username):
            return False

        async with await Mentions.execute_query(
            self._update_mentions_edges_from_chat_to_username_query,
            bind_vars={
                "start_vertex": username.id,
                "chats": Chat.__collection_name__,
                "@mentions": Mentions.__collection_name__,
                "mentions": Mentions.__collection_name__,
                "is_checked": username.is_checked,
                "checked_at": username.checked_at,
            },
        ) as cursor:
            return not cursor.empty()
