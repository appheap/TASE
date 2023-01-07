from __future__ import annotations

import asyncio
import collections
import uuid
from typing import Optional, TYPE_CHECKING, List, Tuple

from pydantic import Field

from aioarango.models import PersistentIndex
from tase.errors import (
    HitDoesNotExists,
    HitNoLinkedAudio,
    AudioNotInPlaylist,
    PlaylistNotFound,
    InvalidFromVertex,
    InvalidToVertex,
)
from tase.my_logger import logger
from .base_vertex import BaseVertex
from .user import User
from ...enums import ChatType, PlaylistInteractionType
from ...helpers import PlaylistInteractionCount

if TYPE_CHECKING:
    from .. import ArangoGraphMethods


class PlaylistInteraction(BaseVertex):
    __collection_name__ = "playlist_interactions"
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

    type: PlaylistInteractionType
    chat_type: ChatType

    is_active: bool = Field(default=True)

    @classmethod
    def parse(
        cls,
        key: str,
        type_: PlaylistInteractionType,
        chat_type: ChatType,
    ) -> Optional[PlaylistInteraction]:
        if not key or not type_ or not chat_type:
            return None

        return PlaylistInteraction(
            key=key,
            type=type_,
            chat_type=chat_type,
        )

    async def toggle(self) -> bool:
        self_copy: PlaylistInteraction = self.copy(deep=True)
        self_copy.is_active = not self.is_active
        return await self.update(self_copy, reserve_non_updatable_fields=False)


class PlaylistInteractionMethods:
    _get_playlist_audio_interaction_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type"
        "   for v_aud in 1..1 outbound v_int graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@audios]}"
        "       filter v_aud._key == @audio_key"
        "       return v_int"
    )

    # _get_playlist_audio_interaction_by_user_query = (
    #     "for audio in 1..1 outbound @playlist_id graph @graph_name options {order:'dfs', vertexCollections:[@audios], edgeCollections:[@has]}"
    #     "   filter audio._key == @audio_key"
    #     "   for int in 1..1 inbound audio graph @graph_name options {order:'dfs', vertexCollections:[@interactions], edgeCollections:[@has]}"
    #     "       filter int.type == @int_type"
    #     "       for user in 1..1 inbound int graph @graph_name options {order:'dfs', vertexCollections:[@users], edgeCollections:[@has]}"
    #     "           filter user.user_id == @user_id"
    #     "           return true"
    # )

    _get_playlist_interaction_by_user_query = (
        "for v_int in 1..1 outbound @user_id graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@interactions]}"
        "   filter v_int.type == @interaction_type"
        "   for v_playlist in 1..1 outbound v_int graph @graph_name options {order : 'dfs', edgeCollections : [@has], vertexCollections : [@playlists]}"
        "       filter v_playlist._key == @playlist_key"
        "       return v_int"
    )

    _count_playlist_interactions_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   filter (interaction.created_at > @last_run_at and interaction.is_active) or (@last_run_at == 0) or (@last_run_at > 0 and interaction.created_at < @last_run_at)"
        "   for v,e in 1..1 outbound interaction graph @graph_name options {order: 'dfs', edgeCollections:[@has], vertexCollections:[@vertices]}"
        "       filter v.is_public"
        "       collect playlist_key = v._key, interaction_type = interaction.type, is_active= interaction.is_active"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, interaction_type asc"
        "   return {playlist_key, interaction_type, count_, is_active}"
    )

    _remove_invalid_playlist_interactions_has_edges_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   filter interaction.created_at > @last_run_at and interaction.is_active == false"
        "   for v,e in 1..1 any interaction graph @graph_name options {order:'dfs', vertexCollections: [@playlists, @hits, @users, @audios], edgeCollections:[@has]}"
        "       remove e in @@has"
    )

    _remove_invalid_playlist_interactions_query = (
        "for interaction in @@interactions"
        "   filter interaction.modified_at >= @last_run_at and interaction.modified_at < @now"
        "   filter interaction.created_at > @last_run_at and interaction.is_active == false"
        "   remove interaction in @@interactions"
    )

    async def get_playlist_audio_interaction_by_user(
        self: ArangoGraphMethods,
        user: User,
        audio_hit_download_url: str,
        playlist_key: str,
        interaction_type: PlaylistInteractionType,
    ) -> Optional[PlaylistInteraction]:
        """
        Get `Interaction` vertex with an `Audio` in a playlist by a user.

        Parameters
        ----------
        user : User
            User to run the query on.
        audio_hit_download_url : str
            Hit `download_url` to get the audio from.
        playlist_key : str
            Key of the playlist this audio belongs to.
        interaction_type : PlaylistInteractionType
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
        PlaylistNotFound
            if not playlist exists with the given `playlist_key`.
        AudioNotInPlaylist
            If audio from the given `hit_download_url` is not in the given playlist.
        """
        if not user or not audio_hit_download_url or not playlist_key:
            return None

        hit = await self.find_hit_by_download_url(audio_hit_download_url)
        if not hit:
            raise HitDoesNotExists(audio_hit_download_url)

        audio = await self.get_audio_from_hit(hit)
        if not audio:
            raise HitNoLinkedAudio(audio_hit_download_url)

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Audio

        if not await self.is_audio_in_playlist(audio.key, playlist_key):
            raise AudioNotInPlaylist(audio.key, playlist_key)

        async with await PlaylistInteraction.execute_query(
            self._get_playlist_audio_interaction_by_user_query,
            bind_vars={
                "user_id": user.id,
                "interactions": PlaylistInteraction.__collection_name__,
                "has": Has.__collection_name__,
                "audios": Audio.__collection_name__,
                "audio_key": audio.key,
                "interaction_type": interaction_type.value,
            },
        ) as cursor:
            async for doc in cursor:
                return PlaylistInteraction.from_collection(doc)

        return None

    async def get_playlist_interaction_by_user(
        self: ArangoGraphMethods,
        user: User,
        interaction_type: PlaylistInteractionType,
        playlist_key: str,
    ) -> Optional[PlaylistInteraction]:
        """
        Get `Interaction` vertex with an `Playlist` by a user.

        Parameters
        ----------
        user : User
            User to run the query on.
        interaction_type : AudioInteractionType
            Type of the interaction to check.
        playlist_key : str
            Key of the playlist to check the interaction for.

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
            If the given `Hit` vertex has more than one linked `Playlist` vertices or both `hit_download_url` and `playlist_key` are **None** at the same
            time, or a `Playlist` with the given `playlist_key` does not exist.
        PlaylistNotFound
            If no playlist with given `playlist_key` exists.
        """
        if not user or not playlist_key:
            return None

        playlist = await self.get_playlist_by_key(playlist_key)
        if not playlist:
            PlaylistNotFound(playlist_key)

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Playlist

        async with await PlaylistInteraction.execute_query(
            self._get_playlist_interaction_by_user_query,
            bind_vars={
                "user_id": user.id,
                "interactions": PlaylistInteraction.__collection_name__,
                "has": Has.__collection_name__,
                "interaction_type": interaction_type.value,
                "playlists": Playlist.__collection_name__,
                "playlist_key": playlist_key,
            },
        ) as cursor:
            async for doc in cursor:
                return PlaylistInteraction.from_collection(doc)

        return None

    async def count_public_playlist_interactions(
        self,
        last_run_at: int,
        now: int,
    ) -> List[PlaylistInteractionCount]:
        """
        Count the interactions with playlist vertices that have been created in the ArangoDB between `now` and `last_run_at` parameters.

        Parameters
        ----------
        last_run_at : int
            Timestamp of last run.
        now : int
            Timestamp of now.

        Returns
        -------
        List
            List of InteractionCount objects.

        """
        if last_run_at is None:
            return []

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Playlist

        res = collections.deque()

        async with await PlaylistInteraction.execute_query(
            self._count_playlist_interactions_query,
            bind_vars={
                "@interactions": PlaylistInteraction.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
                "has": Has.__collection_name__,
                "vertices": Playlist.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                obj = PlaylistInteractionCount.parse(doc)
                if obj is not None:
                    res.append(obj)

        return list(res)

    async def remove_invalid_public_playlist_interactions(
        self,
        last_run_at: int,
        now: int,
    ) -> None:
        """
        Remove the invalid interactions with playlist vertices that have been created in the ArangoDB between `now` and `last_run_at` parameters.

        Parameters
        ----------
        last_run_at : int
            Timestamp of last run.
        now : int
            Timestamp of now.

        """
        if last_run_at is None:
            return

        from tase.db.arangodb.graph.vertices import Hit, Audio, Playlist

        from tase.db.arangodb.graph.edges import Has

        async with await PlaylistInteraction.execute_query(
            self._remove_invalid_playlist_interactions_has_edges_query,
            bind_vars={
                "@interactions": PlaylistInteraction.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
                "playlists": Playlist.__collection_name__,
                "hits": Hit.__collection_name__,
                "users": User.__collection_name__,
                "audios": Audio.__collection_name__,
                "has": Has.__collection_name__,
                "@has": Has.__collection_name__,
            },
        ) as c:
            pass

        async with await PlaylistInteraction.execute_query(
            self._remove_invalid_playlist_interactions_query,
            bind_vars={
                "@interactions": PlaylistInteraction.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
            },
        ) as c:
            pass

    async def create_playlist_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        type_: PlaylistInteractionType,
        chat_type: ChatType,
        playlist_key: str,
        *,
        is_active: Optional[bool] = None,
        audio_hit_download_url: Optional[str] = None,
    ) -> Optional[PlaylistInteraction]:
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
        playlist_key : str
            Key of the playlist to create the interaction for.
        is_active : bool, optional
            Whether this interaction should be set active or not.
        audio_hit_download_url : str, default : None
            Hit's `download_url` to create the `Interaction` vertex from.

        Returns
        -------
        Interaction, optional
            Interaction vertex if the creation was successful, otherwise, return None

        """
        if not user or bot_id is None or not chat_type or not type_:
            return None

        if not audio_hit_download_url and not playlist_key:
            return None

        audio = None
        hit = None

        if audio_hit_download_url:
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

        playlist = await self.get_playlist_by_key(playlist_key)
        if not playlist:
            return None

        bot = await self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None

        while True:
            key = str(uuid.uuid4())
            if await PlaylistInteraction.get(key) is None:
                break

        interaction = PlaylistInteraction.parse(
            key,
            type_,
            chat_type,
        )
        if interaction is None:
            logger.error(f"could not parse interaction : {key} : {type_} : {chat_type}")
            return None

        if is_active is not None:
            interaction.is_active = is_active

        interaction, created = await PlaylistInteraction.insert(interaction)
        if not interaction or not created:
            logger.error(f"could not create interaction : {key} : {type_} : {chat_type}")
            return None

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.edges import FromHit

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

        return interaction

    async def toggle_playlist_interaction(
        self: ArangoGraphMethods,
        user: User,
        bot_id: int,
        chat_type: ChatType,
        interaction_type: PlaylistInteractionType,
        playlist_key: str,
        *,
        is_active: Optional[bool] = None,
        audio_hit_download_url: Optional[str] = None,
        create_if_not_exists: Optional[bool] = True,
    ) -> Tuple[bool, bool]:
        """
        Toggle an interaction with an `Audio` by a user

        Parameters
        ----------
        user : User
            User to run the query on.
        bot_id : int
            ID of the BOT this query was ran on.
        chat_type : ChatType
            Type of the chat this interaction happened in.
        interaction_type : AudioInteractionType
            Type of the interaction to toggle.
        playlist_key : str
            Key of the playlist this interaction originated form.
        is_active : bool, optional
            Whether this interaction should be set active or not.
        audio_hit_download_url : str
            Hit download_url to get the audio from.
        create_if_not_exists : bool, default : True
            Create the interaction vertex if it does not exist.

        Returns
        -------
        tuple
            Whether the operation was successful and the user had interacted with the audio in the first place.

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
        if not audio_hit_download_url or not user or not playlist_key:
            return False, False

        hit = await self.find_hit_by_download_url(audio_hit_download_url)
        if hit is None:
            raise HitDoesNotExists(audio_hit_download_url)

        if audio_hit_download_url:
            audio = await self.get_audio_from_hit(hit)
            if not audio:
                raise HitNoLinkedAudio(audio_hit_download_url)

            interaction_vertex = await self.get_playlist_audio_interaction_by_user(
                user,
                audio_hit_download_url,
                playlist_key,
                interaction_type,
            )
        else:
            interaction_vertex = await self.get_playlist_interaction_by_user(
                user,
                interaction_type,
                playlist_key,
            )
        has_interacted = interaction_vertex is not None and interaction_vertex.is_active

        if interaction_vertex:
            # user has already interacted with the audio, remove the interaction
            from tase.db.arangodb.graph.edges import Has

            successful = await interaction_vertex.toggle()

            # only check for missing edge between interaction and playlist vertices if the interaction is `active`. By doing this, when counting interaction
            # with playlists, it is made sure that negative counts does not affect the playlist related attributes. The reason behind this is that if an
            # audio is downloaded from a playlist and the audio has already been `liked` or `disliked`, if the mentioned audio `like` or `dislike` is undone,
            # then it counts as a negative number which is not counted for that playlist before.
            return successful, has_interacted
        else:
            if not create_if_not_exists and not is_active:
                return False, False

            # user has not interacted with the audio or playlist, create the interaction
            interaction = await self.create_playlist_interaction(
                user,
                bot_id,
                interaction_type,
                chat_type,
                playlist_key,
                is_active=is_active,
                audio_hit_download_url=audio_hit_download_url,
            )
            if interaction is not None:
                return True, has_interacted
            else:
                return False, has_interacted
