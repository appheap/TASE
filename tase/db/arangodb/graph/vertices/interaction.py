from __future__ import annotations

import collections
import uuid
from typing import Optional, TYPE_CHECKING, Tuple, List

from pydantic import Field

from aioarango.models import PersistentIndex
from tase.errors import (
    InvalidFromVertex,
    InvalidToVertex,
    HitDoesNotExists,
    HitNoLinkedAudio,
    AudioVertexDoesNotExist,
)
from tase.my_logger import logger
from .base_vertex import BaseVertex
from .user import User
from ...enums import ChatType, InteractionType
from ...helpers import InteractionCount

if TYPE_CHECKING:
    from .. import ArangoGraphMethods


class Interaction(BaseVertex):
    __collection_name__ = "interactions"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="type",
            fields=[
                "type",
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
            name="is_active",
            fields=[
                "is_active",
            ],
        ),
    ]

    __non_updatable_fields__ = ("is_active",)

    type: InteractionType
    chat_type: ChatType

    is_active: bool = Field(default=True)

    @classmethod
    def parse(
        cls,
        key: str,
        type_: InteractionType,
        chat_type: ChatType,
    ) -> Optional[Interaction]:
        if key is None:
            return None

        return Interaction(
            key=key,
            type=type_,
            chat_type=chat_type,
        )

    async def toggle(self) -> bool:
        self_copy: Interaction = self.copy(deep=True)
        self_copy.is_active = not self.is_active
        return await self.update(self_copy, reserve_non_updatable_fields=False)


class InteractionMethods:
    _is_audio_interacted_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type and v_int.is_active == true"
        "   for v_aud in 1..1 outbound v_int._id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@audios]}"
        "       filter v_aud._key == @audio_key"
        "       return true"
    )

    _interaction_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type"
        "   for v_aud in 1..1 outbound v_int._id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@audios]}"
        "       filter v_aud._key == @audio_key"
        "       return v_int"
    )

    _count_interactions_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   for v,e in 1..1 outbound interaction graph @graph_name options {order: 'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "       collect audio_key = v._key, interaction_type = interaction.type, is_active= interaction.is_active"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, interaction_type asc"
        "   return {audio_key, interaction_type, count_, is_active}"
    )

    async def create_interaction(
        self: ArangoGraphMethods,
        hit_download_url: str,
        user: User,
        bot_id: int,
        type_: InteractionType,
        chat_type: ChatType,
    ) -> Optional[Interaction]:
        """
        Create `Download` vertex from the given `hit_download_url` parameter.

        Parameters
        ----------
        hit_download_url : str
            Hit's `download_url` to create the `Download` vertex
        user : User
            User to create the `Download` vertex for
        bot_id : int
            Telegram ID of the Bot which the query has been made to
        type_ : InteractionType
            Type of interaction to create
        chat_type : ChatType
            Type of the chat this interaction happened in

        Returns
        -------
        Interaction, optional
            Interaction vertex if the creation was successful, otherwise, return None

        """
        if not hit_download_url or not user or bot_id is None or not chat_type or not type_:
            return None

        bot = await self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None

        hit = await self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            return None

        try:
            audio = await self.get_audio_from_hit(hit)
        except ValueError:
            # happens when the `Hit` has more than linked `Audio` vertices
            return None

        while True:
            key = str(uuid.uuid4())
            if await Interaction.get(key) is None:
                break

        interaction = Interaction.parse(
            key,
            type_,
            chat_type,
        )
        if interaction is None:
            logger.error(f"could not parse interaction : {key} : {type_} : {chat_type}")
            return None

        interaction, created = await Interaction.insert(interaction)
        if not interaction or not created:
            logger.error(f"could not create interaction : {key} : {type_} : {chat_type}")
            return None

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.edges import FromHit

        # from tase.db.arangodb.graph.edges import FromBot

        try:
            await Has.get_or_create_edge(interaction, audio)
        except (InvalidFromVertex, InvalidToVertex):
            logger.error("ValueError: Could not create `has` edge from `Interaction` vertex to `Audio` vertex")
            return None

        try:
            await FromHit.get_or_create_edge(interaction, hit)
        except (InvalidFromVertex, InvalidToVertex):
            logger.error("ValueError: Could not create `from_hit` edge from `Interaction` vertex to `Hit` vertex")
            return None

        try:
            await Has.get_or_create_edge(user, interaction)
        except (InvalidFromVertex, InvalidToVertex):
            logger.error("ValueError: Could not create `has` edge from `User` vertex to `Interaction` vertex")
            return None

        # try:
        #     FromBot.get_or_create_edge(download, bot)
        # except (InvalidFromVertex, InvalidToVertex):
        #     logger.error(
        #         "ValueError: Could not create `from_bot` edge from `Interaction` vertex to `User` vertex"
        #     )
        #     return None

        return interaction

    async def get_audio_interaction_by_user(
        self: ArangoGraphMethods,
        user: User,
        hit_download_url: str,
        interaction_type: InteractionType,
    ) -> Optional[Interaction]:
        """
        Get `Interaction` vertex with an `Audio` by a user.

        Parameters
        ----------
        user : User
            User to run the query on
        hit_download_url : str
            Hit download_url to get the audio from
        interaction_type : InteractionType
            Type of the interaction to check

        Returns
        -------
        Interaction, optional
            Whether the audio is liked by a user or not.

        Raises
        ------
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter
        HitNoLinkedAudio
            If `Hit` vertex does not have any linked `Audio` vertex with it
        ValueError
            If the given `Hit` vertex has more than one linked `Audio` vertices.
        """
        if user is None or hit_download_url is None:
            return None

        hit = await self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            raise HitDoesNotExists(hit_download_url)

        audio = await self.get_audio_from_hit(hit)
        if audio is None:
            raise HitNoLinkedAudio(hit_download_url)

        from tase.db.arangodb.graph.edges import Has

        from tase.db.arangodb.graph.vertices import Audio

        async with await Interaction.execute_query(
            self._interaction_by_user_query,
            bind_vars={
                "user_id": user.id,
                "audio_key": audio.key,
                "interaction_type": interaction_type.value,
                "has": Has.__collection_name__,
                "interactions": Interaction.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                return Interaction.from_collection(doc)

        return None

    async def audio_is_interacted_by_user(
        self: ArangoGraphMethods,
        user: User,
        interaction_type: InteractionType,
        *,
        hit_download_url: str = None,
        audio_vertex_key: str = None,
    ) -> Optional[bool]:
        """
        Check whether an `Audio` is interacted by a user or not.

        Parameters
        ----------
        user : User
            User to run the query on
        interaction_type : InteractionType
            Type of the interaction to check
        hit_download_url : str, default : None
            Hit download_url to get the audio from
        audio_vertex_key : str, default : None
            Key of the audio vertex in the ArangoDB

        Returns
        -------
        bool, optional
            Whether the audio is liked by a user or not.

        Raises
        ------
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter
        HitNoLinkedAudio
            If `Hit` vertex does not have any linked `Audio` vertex with it
        AudioVertexDoesNotExist
            If `Audio` vertex does not exist with the given `key`
        ValueError
            If the given `Hit` vertex has more than one linked `Audio` vertices.
        """
        if user is None or (hit_download_url is None and audio_vertex_key is None):
            return None

        if hit_download_url is not None:
            hit = await self.find_hit_by_download_url(hit_download_url)
            if hit is None:
                raise HitDoesNotExists(hit_download_url)

            audio = await self.get_audio_from_hit(hit)
            if audio is None:
                raise HitNoLinkedAudio(hit_download_url)
        else:
            audio = await self.get_audio_by_key(audio_vertex_key)
            if audio is None:
                raise AudioVertexDoesNotExist(audio_vertex_key)

        from tase.db.arangodb.graph.edges import Has

        from tase.db.arangodb.graph.vertices import Audio

        cursor = await Interaction.execute_query(
            self._is_audio_interacted_by_user_query,
            bind_vars={
                "user_id": user.id,
                "audio_key": audio.key,
                "interaction_type": interaction_type.value,
                "has": Has.__collection_name__,
                "interactions": Interaction.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        )

        return True if cursor is not None and len(cursor) else False

    async def toggle_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        hit_download_url: str,
        chat_type: ChatType,
        interaction_type: InteractionType,
    ) -> Tuple[bool, bool]:
        """
        Toggle an interaction with an `Audio` by a user

        Parameters
        ----------
        user : User
            User to run the query on
        bot_id : int
            ID of the BOT this query was ran on
        hit_download_url : str
            Hit download_url to get the audio from
        chat_type : ChatType
            Type of the chat this interaction happened in
        interaction_type : InteractionType
            Type of the interaction to toggle

        Returns
        -------
        tuple
            Whether the operation was successful and the user had interacted with the audio in the first place

        Raises
        ------
        PlaylistDoesNotExists
            If `Playlist` vertex does not exist with the `playlist_key` parameter
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter
        HitNoLinkedAudio
            If `Hit` vertex does not have any linked `Audio` vertex with it
        EdgeDeletionFailed
            If deletion of an edge fails
        """
        if user is None or hit_download_url is None:
            return False, False

        hit = await self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            raise HitDoesNotExists(hit_download_url)

        audio = await self.get_audio_from_hit(hit)
        if audio is None:
            raise HitNoLinkedAudio(hit_download_url)

        interaction_vertex = await self.get_audio_interaction_by_user(
            user,
            hit_download_url,
            interaction_type,
        )
        has_interacted = interaction_vertex is not None and interaction_vertex.is_active

        if interaction_vertex:
            # user has already interacted with the audio, remove the interaction
            from tase.db.arangodb.graph.edges import Has

            successful = await interaction_vertex.toggle()

            return successful, has_interacted
        else:
            # user has not interacted with the audio, create the interaction
            interaction = await self.create_interaction(
                hit_download_url,
                user,
                bot_id,
                interaction_type,
                chat_type,
            )
            if interaction is not None:
                return True, has_interacted
            else:
                return False, has_interacted

    async def count_interactions(
        self,
        last_run_at: int,
        now: int,
    ) -> List[InteractionCount]:
        """
        Count the interactions that have been created in the ArangoDB between `now` and `last_run_at` parameters.

        Parameters
        ----------
        last_run_at : int
            Timestamp of last run
        now : int
            Timestamp of now

        Returns
        -------
        list of InteractionCount
            List of InteractionCount objects

        """
        if last_run_at is None:
            return []

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Audio

        res = collections.deque()

        async with await Interaction.execute_query(
            self._count_interactions_query,
            bind_vars={
                "@interactions": Interaction.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
                "has": Has.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                obj = InteractionCount.parse(doc)
                if obj is not None:
                    res.append(obj)

        return list(res)
