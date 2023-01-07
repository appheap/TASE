from __future__ import annotations

import asyncio
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
from ...enums import ChatType, AudioInteractionType
from ...helpers import AudioInteractionCount

if TYPE_CHECKING:
    from .. import ArangoGraphMethods


class AudioInteraction(BaseVertex):
    __collection_name__ = "audio_interactions"
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

    type: AudioInteractionType
    chat_type: ChatType

    is_active: bool = Field(default=True)

    @classmethod
    def parse(
        cls,
        key: str,
        type_: AudioInteractionType,
        chat_type: ChatType,
    ) -> Optional[AudioInteraction]:
        if not key or not type_ or not chat_type:
            return None

        return AudioInteraction(
            key=key,
            type=type_,
            chat_type=chat_type,
        )

    async def toggle(self) -> bool:
        self_copy: AudioInteraction = self.copy(deep=True)
        self_copy.is_active = not self.is_active
        return await self.update(self_copy, reserve_non_updatable_fields=False)


class AudioInteractionMethods:
    _is_audio_interacted_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type and v_int.is_active == true"
        "   for v_aud in 1..1 outbound v_int._id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@audios]}"
        "       filter v_aud._key == @audio_key"
        "       return true"
    )

    _get_audio_interaction_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type"
        "   for v_aud in 1..1 outbound v_int._id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@audios]}"
        "       filter v_aud._key == @audio_key"
        "       return v_int"
    )

    _count_audio_interactions_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   for v,e in 1..1 outbound interaction graph @graph_name options {order: 'dfs', edgeCollections:[@has], vertexCollections:[@vertices]}"
        "       collect audio_key = v._key, interaction_type = interaction.type, is_active= interaction.is_active"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, interaction_type asc"
        "   return {audio_key, interaction_type, count_, is_active}"
    )

    async def create_audio_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        type_: AudioInteractionType,
        chat_type: ChatType,
        audio_hit_download_url: str,
    ) -> Optional[AudioInteraction]:
        """
        Create an interaction vertex for and audio vertex from the given `hit_download_url` parameter.

        Parameters
        ----------
        user : User
            User to create the `Download` vertex for.
        bot_id : int
            Telegram ID of the Bot which the query has been made to.
        type_ : AudioInteractionType
            Type of interaction to create.
        chat_type : ChatType
            Type of the chat this interaction happened in.
        audio_hit_download_url : str
            Hit's `download_url` to create the `Interaction` vertex from.

        Returns
        -------
        Interaction, optional
            Interaction vertex if the creation was successful, otherwise, return None

        """
        if not user or bot_id is None or not chat_type or not type_ or not audio_hit_download_url:
            return None

        retry_left = 5
        hit = None
        while retry_left:
            hit = await self.find_hit_by_download_url(audio_hit_download_url)
            if not hit:
                retry_left -= 1
                await asyncio.sleep(2)
                continue

            break

        if not hit:
            return None

        try:
            audio = await self.get_audio_from_hit(hit)
        except ValueError:
            # happens when the `Hit` has more than linked `Audio` vertices
            return None
        else:
            if not audio:
                return None

        bot = await self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None

        while True:
            key = str(uuid.uuid4())
            if await AudioInteraction.get(key) is None:
                break

        interaction = AudioInteraction.parse(
            key,
            type_,
            chat_type,
        )
        if interaction is None:
            logger.error(f"could not parse interaction : {key} : {type_} : {chat_type}")
            return None

        interaction, created = await AudioInteraction.insert(interaction)
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
        interaction_type: AudioInteractionType,
    ) -> Optional[AudioInteraction]:
        """
        Get `Interaction` vertex with an `Audio` by a user.

        Parameters
        ----------
        user : User
            User to run the query on.
        hit_download_url : str
            Hit download_url to get the audio from.
        interaction_type : AudioInteractionType
            Type of the interaction to check.

        Returns
        -------
        Interaction, optional
            Whether the audio is liked by a user or not.

        Raises
        ------
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter.
        HitNoLinkedAudio
            If `Hit` vertex does not have any linked `Audio` vertex with it.
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

        async with await AudioInteraction.execute_query(
            self._get_audio_interaction_by_user_query,
            bind_vars={
                "user_id": user.id,
                "audio_key": audio.key,
                "interaction_type": interaction_type.value,
                "has": Has.__collection_name__,
                "interactions": AudioInteraction.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                return AudioInteraction.from_collection(doc)

        return None

    async def toggle_audio_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        audio_hit_download_url: str,
        chat_type: ChatType,
        interaction_type: AudioInteractionType,
    ) -> Tuple[bool, bool]:
        """
        Toggle an interaction with an `Audio` by a user.

        Parameters
        ----------
        user : User
            User to run the query on.
        bot_id : int
            ID of the BOT this query was ran on.
        audio_hit_download_url : str
            Hit download_url to get the audio from.
        chat_type : ChatType
            Type of the chat this interaction happened in.
        interaction_type : AudioInteractionType
            Type of the interaction to toggle.

        Returns
        -------
        tuple
            Whether the operation was successful and the user had interacted with the audio in the first place.

        Raises
        ------
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter.
        HitNoLinkedAudio
            If `Hit` vertex does not have any linked `Audio` vertex with it.
        EdgeDeletionFailed
            If deletion of an edge fails.
        ValueError
            If the given `Hit` vertex has more than one linked `Audio` vertices.
        """
        if not audio_hit_download_url or not user:
            return False, False

        hit = await self.find_hit_by_download_url(audio_hit_download_url)
        if hit is None:
            raise HitDoesNotExists(audio_hit_download_url)

        audio = await self.get_audio_from_hit(hit)
        if audio is None:
            raise HitNoLinkedAudio(audio_hit_download_url)

        interaction_vertex = await self.get_audio_interaction_by_user(
            user,
            audio_hit_download_url,
            interaction_type,
        )
        has_interacted = interaction_vertex is not None and interaction_vertex.is_active

        if interaction_vertex:
            # user has already interacted with the audio, remove the interaction
            from tase.db.arangodb.graph.edges import Has

            successful = await interaction_vertex.toggle()
            return successful, has_interacted
        else:
            # user has not interacted with the audio or playlist, create the interaction
            interaction = await self.create_audio_interaction(
                user,
                bot_id,
                interaction_type,
                chat_type,
                audio_hit_download_url,
            )
            if interaction is not None:
                return True, has_interacted
            else:
                return False, has_interacted

    async def audio_is_interacted_by_user(
        self: ArangoGraphMethods,
        user: User,
        interaction_type: AudioInteractionType,
        *,
        hit_download_url: str = None,
        audio_vertex_key: str = None,
    ) -> Optional[bool]:
        """
        Check whether an `Audio` is interacted by a user or not.

        Parameters
        ----------
        user : User
            User to run the query on.
        interaction_type : AudioInteractionType
            Type of the interaction to check.
        hit_download_url : str, default : None
            Hit download_url to get the audio from.
        audio_vertex_key : str, default : None
            Key of the audio vertex in the ArangoDB.

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
        if user is None or (not hit_download_url and not audio_vertex_key):
            return None

        if hit_download_url:
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

        async with await AudioInteraction.execute_query(
            self._is_audio_interacted_by_user_query,
            bind_vars={
                "user_id": user.id,
                "audio_key": audio.key,
                "interaction_type": interaction_type.value,
                "has": Has.__collection_name__,
                "interactions": AudioInteraction.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        ) as cursor:
            return not cursor.empty()

    async def count_audio_interactions(
        self,
        last_run_at: int,
        now: int,
    ) -> List[AudioInteractionCount]:
        """
        Count the interactions with audio files that have been created in the ArangoDB between `now` and `last_run_at` parameters.

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

        async with await AudioInteraction.execute_query(
            self._count_audio_interactions_query,
            bind_vars={
                "@interactions": AudioInteraction.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
                "has": Has.__collection_name__,
                "vertices": Audio.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                obj = AudioInteractionCount.parse(doc)
                if obj is not None:
                    res.append(obj)

        return list(res)
