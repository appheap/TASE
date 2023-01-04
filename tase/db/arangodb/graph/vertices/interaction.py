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
    HitNoLinkedPlaylist,
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
        if not key or not type_ or not chat_type:
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

    _get_audio_interaction_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type"
        "   for v_aud in 1..1 outbound v_int._id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@audios]}"
        "       filter v_aud._key == @audio_key"
        "       return v_int"
    )

    _get_playlist_interaction_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type"
        "   for v_playlist in 1..1 outbound v_int._id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@playlists]}"
        "       filter v_playlist._key == @playlist_key"
        "       return v_int"
    )

    _count_audio_interactions_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   for v,e in 1..1 outbound interaction graph @graph_name options {order: 'dfs', edgeCollections:[@has], vertexCollections:[@vertices]}"
        "       collect vertex_key = v._key, interaction_type = interaction.type, is_active= interaction.is_active"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, interaction_type asc"
        "   return {vertex_key, interaction_type, count_, is_active}"
    )

    _count_playlist_interactions_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   for v,e in 1..1 outbound interaction graph @graph_name options {order: 'dfs', edgeCollections:[@has], vertexCollections:[@vertices]}"
        "       filter v.is_public"
        "       collect vertex_key = v._key, interaction_type = interaction.type, is_active= interaction.is_active"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, interaction_type asc"
        "   return {vertex_key, interaction_type, count_, is_active}"
    )

    async def create_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        type_: InteractionType,
        chat_type: ChatType,
        audio_hit_download_url: Optional[str] = None,
        playlist_hit_download_url: Optional[str] = None,
        playlist_key: Optional[str] = None,
    ) -> Optional[Interaction]:
        """
        Create an interaction vertex for and audio vertex from the given `hit_download_url` parameter.

        Parameters
        ----------
        user : User
            User to create the `Download` vertex for
        bot_id : int
            Telegram ID of the Bot which the query has been made to
        type_ : InteractionType
            Type of interaction to create
        chat_type : ChatType
            Type of the chat this interaction happened in
        audio_hit_download_url : str, default : None
            Hit's `download_url` to create the `Interaction` vertex from.
        playlist_hit_download_url : str, default : None
            Hit's `download_url` to create the `Interaction` vertex from.
        playlist_key : str, default : None
            Key of the playlist to create the interaction for.

        Returns
        -------
        Interaction, optional
            Interaction vertex if the creation was successful, otherwise, return None

        """
        if not user or bot_id is None or not chat_type or not type_:
            return None

        if not audio_hit_download_url and not playlist_hit_download_url and not playlist_key:
            return None

        audio = None
        playlist = None
        hit = None

        if audio_hit_download_url or playlist_hit_download_url:
            retry_left = 5
            hit = None
            while retry_left:
                hit = await self.find_hit_by_download_url(audio_hit_download_url or playlist_hit_download_url)
                if not hit:
                    retry_left -= 1
                    await asyncio.sleep(2)
                    continue

                break

            if not hit:
                return None

        if playlist_key:
            playlist = await self.get_playlist_by_key(playlist_key)
            if not playlist:
                return None

        if audio_hit_download_url:
            try:
                audio = await self.get_audio_from_hit(hit)
            except ValueError:
                # happens when the `Hit` has more than linked `Audio` vertices
                return None

        if audio_hit_download_url and not audio:
            return None

        if playlist_key and not playlist:
            return None

        if (audio_hit_download_url or playlist_hit_download_url) and not hit:
            return None

        bot = await self.get_user_by_telegram_id(bot_id)
        if bot is None:
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

        if playlist:
            try:
                await Has.get_or_create_edge(interaction, playlist)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error("ValueError: Could not create `has` edge from `Interaction` vertex to `Playlist` vertex")
                return None

        if audio:
            try:
                await Has.get_or_create_edge(interaction, audio)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error("ValueError: Could not create `has` edge from `Interaction` vertex to `Audio` vertex")
                return None

        if hit:
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
            User to run the query on.
        hit_download_url : str
            Hit download_url to get the audio from.
        interaction_type : InteractionType
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

        async with await Interaction.execute_query(
            self._get_audio_interaction_by_user_query,
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

    async def get_playlist_interaction_by_user(
        self: ArangoGraphMethods,
        user: User,
        hit_download_url: str,
        interaction_type: InteractionType,
    ) -> Optional[Interaction]:
        """
        Get `Interaction` vertex with an `Playlist` by a user.

        Parameters
        ----------
        user : User
            User to run the query on
        hit_download_url : str
            Hit download_url to get the playlist from
        interaction_type : InteractionType
            Type of the interaction to check

        Returns
        -------
        Interaction, optional
            Whether the playlist is liked by a user or not.

        Raises
        ------
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter.
        HitNoLinkedPlaylist
            If `Hit` vertex does not have any linked `Playlist` vertex with it.
        ValueError
            If the given `Hit` vertex has more than one linked `Playlist` vertices.
        """
        if user is None or hit_download_url is None:
            return None

        hit = await self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            raise HitDoesNotExists(hit_download_url)

        playlist = await self.get_playlist_from_hit(hit)
        if playlist is None:
            raise HitNoLinkedPlaylist(hit_download_url)

        from tase.db.arangodb.graph.edges import Has

        from tase.db.arangodb.graph.vertices import Playlist

        async with await Interaction.execute_query(
            self._get_playlist_interaction_by_user_query,
            bind_vars={
                "user_id": user.id,
                "playlist_key": playlist.key,
                "interaction_type": interaction_type.value,
                "has": Has.__collection_name__,
                "interactions": Interaction.__collection_name__,
                "playlists": Playlist.__collection_name__,
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

        async with await Interaction.execute_query(
            self._is_audio_interacted_by_user_query,
            bind_vars={
                "user_id": user.id,
                "audio_key": audio.key,
                "interaction_type": interaction_type.value,
                "has": Has.__collection_name__,
                "interactions": Interaction.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        ) as cursor:
            return not cursor.empty()

    async def toggle_audio_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        hit_download_url: str,
        chat_type: ChatType,
        interaction_type: InteractionType,
        playlist_key: Optional[str] = None,
    ) -> Tuple[bool, bool]:
        """
        Toggle an interaction with an `Audio` by a user

        Parameters
        ----------
        user : User
            User to run the query on.
        bot_id : int
            ID of the BOT this query was ran on.
        hit_download_url : str
            Hit download_url to get the audio from.
        chat_type : ChatType
            Type of the chat this interaction happened in.
        interaction_type : InteractionType
            Type of the interaction to toggle.
        playlist_key : str, optional
            Key of the playlist this interaction originated form.

        Returns
        -------
        tuple
            Whether the operation was successful and the user had interacted with the audio in the first place

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
        return await self._toggle_interaction(
            user=user,
            bot_id=bot_id,
            chat_type=chat_type,
            interaction_type=interaction_type,
            audio_hit_download_url=hit_download_url,
            playlist_key=playlist_key,
        )

    async def toggle_playlist_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        hit_download_url: str,
        chat_type: ChatType,
        interaction_type: InteractionType,
    ) -> Tuple[bool, bool]:
        """
        Toggle an interaction with an `Playlist` by a user

        Parameters
        ----------
        user : User
            User to run the query on
        bot_id : int
            ID of the BOT this query was ran on
        hit_download_url : str
            Hit download_url to get the audio from.
        chat_type : ChatType
            Type of the chat this interaction happened in
        interaction_type : InteractionType
            Type of the interaction to toggle

        Returns
        -------
        tuple
            Whether the operation was successful and the user had interacted with the playlist in the first place

        Raises
        ------
        PlaylistDoesNotExists
            If `Playlist` vertex does not exist with the `playlist_key` parameter.
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter.
        HitNoLinkedPlaylist
            If `Hit` vertex does not have any linked `Playlist` vertex with it.
        EdgeDeletionFailed
            If deletion of an edge fails.
        ValueError
            If the given `Hit` vertex has more than one linked `Playlist` vertices.
        """
        return await self._toggle_interaction(
            user=user,
            bot_id=bot_id,
            chat_type=chat_type,
            interaction_type=interaction_type,
            playlist_hit_download_url=hit_download_url,
        )

    async def _toggle_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        chat_type: ChatType,
        interaction_type: InteractionType,
        audio_hit_download_url: Optional[str] = None,
        playlist_hit_download_url: Optional[str] = None,
        playlist_key: Optional[str] = None,
    ) -> Tuple[bool, bool]:
        """
        Toggle an interaction with an `Audio` by a user

        Parameters
        ----------
        user : User
            User to run the query on
        bot_id : int
            ID of the BOT this query was ran on
        audio_hit_download_url : str
            Hit download_url to get the audio from.
        playlist_hit_download_url : str
            Hit download_url to get the playlist from.
        chat_type : ChatType
            Type of the chat this interaction happened in
        interaction_type : InteractionType
            Type of the interaction to toggle.
        playlist_key : str, optional
            Key of the playlist this interaction originated form.


        Returns
        -------
        tuple
            Whether the operation was successful and the user had interacted with the audio in the first place

        Raises
        ------
        PlaylistDoesNotExists
            If `Playlist` vertex does not exist with the `playlist_key` parameter.
        HitDoesNotExists
            If `Hit` vertex does not exist with the `hit_download_url` parameter.
        HitNoLinkedAudio
            If `Hit` vertex does not have any linked `Audio` vertex with it.
        HitNoLinkedPlaylist
            If `Hit` vertex does not have any linked `Playlist` vertex with it.
        EdgeDeletionFailed
            If deletion of an edge fails.
        ValueError
            If the given `Hit` vertex has more than one linked `Audio` or `Playlist` vertices.
        """
        if (not audio_hit_download_url and not playlist_hit_download_url) or not user:
            return False, False

        hit = await self.find_hit_by_download_url(audio_hit_download_url or playlist_hit_download_url)
        if hit is None:
            raise HitDoesNotExists(audio_hit_download_url or playlist_hit_download_url)

        if audio_hit_download_url:
            audio = await self.get_audio_from_hit(hit)
            if audio is None:
                raise HitNoLinkedAudio(audio_hit_download_url)

            interaction_vertex = await self.get_audio_interaction_by_user(
                user,
                audio_hit_download_url,
                interaction_type,
            )
        else:
            playlist = await self.get_playlist_from_hit(hit)
            if playlist is None:
                raise HitNoLinkedPlaylist(playlist_hit_download_url)

            interaction_vertex = await self.get_playlist_interaction_by_user(
                user,
                playlist_hit_download_url,
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
            interaction = await self.create_interaction(
                user,
                bot_id,
                interaction_type,
                chat_type,
                audio_hit_download_url=audio_hit_download_url,
                playlist_hit_download_url=playlist_hit_download_url,
                playlist_key=playlist_key,
            )
            if interaction is not None:
                return True, has_interacted
            else:
                return False, has_interacted

    async def count_public_playlist_interactions(
        self,
        last_run_at: int,
        now: int,
    ) -> List[InteractionCount]:
        """
        Count the interactions with playlist vertices that have been created in the ArangoDB between `now` and `last_run_at` parameters.

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
        return await self._count_interactions(
            count_audio_interactions=False,
            count_playlist_interactions=True,
            last_run_at=last_run_at,
            now=now,
        )

    async def count_audio_interactions(
        self,
        last_run_at: int,
        now: int,
    ) -> List[InteractionCount]:
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
        return await self._count_interactions(
            count_audio_interactions=True,
            count_playlist_interactions=False,
            last_run_at=last_run_at,
            now=now,
        )

    async def _count_interactions(
        self,
        count_audio_interactions: bool,
        count_playlist_interactions: bool,
        last_run_at: int,
        now: int,
    ) -> List[InteractionCount]:
        """
        Count the interactions with audio or playlist vertices that have been created in the ArangoDB between `now` and `last_run_at` parameters.

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
        if last_run_at is None or (count_audio_interactions and count_playlist_interactions):
            return []

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Audio, Playlist

        res = collections.deque()

        async with await Interaction.execute_query(
            self._count_audio_interactions_query if count_audio_interactions else self._count_playlist_interactions_query,
            bind_vars={
                "@interactions": Interaction.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
                "has": Has.__collection_name__,
                "vertices": Audio.__collection_name__ if count_audio_interactions else Playlist.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                obj = InteractionCount.parse(doc)
                if obj is not None:
                    res.append(obj)

        return list(res)
