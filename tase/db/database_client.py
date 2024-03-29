from typing import Optional

import pyrogram

from .arangodb import ArangoDB, graph as graph_models
from .arangodb.document import ArangoDocumentMethods
from .arangodb.enums import AudioType
from .arangodb.graph import ArangoGraphMethods
from .arangodb.graph.edges import SubscribeTo
from .arangodb.graph.vertices import ThumbnailFile
from .elasticsearchdb import ElasticsearchDatabase
from .elasticsearchdb.models import ElasticSearchMethods
from .helpers import ChatScores
from ..configs import ArangoDBConfig, ElasticConfig
from ..errors import UserDoesNotHasPlaylist, EdgeCreationFailed
from ..my_logger import logger


class DatabaseClient:
    es_db: ElasticsearchDatabase
    arangodb: ArangoDB

    index: ElasticSearchMethods = ElasticSearchMethods()
    graph: ArangoGraphMethods = ArangoGraphMethods()
    document: ArangoDocumentMethods = ArangoDocumentMethods()

    def __init__(
        self,
        elasticsearch_config: ElasticConfig,
        arangodb_config: ArangoDBConfig,
    ):
        self.es_db = ElasticsearchDatabase(elasticsearch_config=elasticsearch_config)
        self.arangodb = ArangoDB()

        self._arangodb_config = arangodb_config

    async def init_databases(
        self,
        update_arango_indexes: bool = False,
    ):
        await self.es_db.init_database()
        await self.arangodb.initialize(self._arangodb_config, update_arango_indexes)

    async def get_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> bool:
        """
        Create the audio vertex and document in the arangodb and audio document in the elasticsearch.
        These entities are created if they do not already exist in the database.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to use for creating the audio entities.
        telegram_client_id : int
            ID of the telegram client making this request.
        chat_id : int
            ID of the telegram chat this message belongs to.
        audio_type : AudioType
            Type of the audio to store in the databases.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        bool
            Whether the operation was successful or not.
        """
        if telegram_message is None or telegram_message.audio is None:
            return False

        try:
            audio_vertex = await self.graph.get_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
            audio_doc = await self.document.get_or_create_audio(telegram_message, telegram_client_id, chat_id)
            es_audio_doc = await self.index.get_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
        except Exception as e:
            logger.exception(e)
        else:
            if audio_vertex is not None and audio_doc is not None and es_audio_doc is not None:
                return True

        return False

    async def update_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> bool:
        """
        Create the audio vertex and document in the arangodb and audio document in the elasticsearch.
        These entities are created if they do not already exist in the database. Otherwise, they will get updated.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to use for creating the audio entities.
        telegram_client_id : int
            ID of the telegram client making this request.
        chat_id : int
            ID of the telegram chat this message belongs to.
        audio_type : AudioType
            Type of the audio to store in the databases.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        bool
            Whether the operation was successful or not.
        """
        if telegram_message is None or telegram_client_id is None:
            return False

        try:
            audio_vertex = await self.graph.update_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
            audio_doc = await self.document.update_or_create_audio(telegram_message, telegram_client_id, chat_id)
            es_audio_doc = await self.index.update_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
        except Exception as e:
            logger.exception(e)
        else:
            if audio_vertex is not None and audio_doc is not None and es_audio_doc is not None:
                return True

        return False

    async def invalidate_old_audios(
        self,
        chat_id: int,
        message_id: int,
        excluded_audio_vertex_key: Optional[str] = None,
    ) -> None:
        """
        Invalid old audios after a new audio has replaced an existent audio in the original chat.

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio belongs to.
        message_id : int
            ID of the telegram message that audio belongs to.
        excluded_audio_vertex_key : str, default : `None`
            Audio key to exclude from this update. All audio objects in the database with the given key/ID will not be affected.

        """
        if not chat_id or message_id is None:
            return

        await self.graph.mark_old_audio_vertices_as_deleted(
            chat_id=chat_id,
            message_id=message_id,
            excluded_key=excluded_audio_vertex_key,
        )

        await self.document.delete_old_audio_caches(
            chat_id=chat_id,
            message_id=message_id,
        )

        await self.index.mark_old_audios_as_deleted(
            chat_id=chat_id,
            message_id=message_id,
            excluded_id=excluded_audio_vertex_key,
        )

    async def mark_chat_as_invalid(self, chat: graph_models.vertices.Chat) -> None:
        """
        Mark a `Chat` vertex in the ArangoDB as invalid and invalidate its connected `Audio` vertices and documents as well.

        Parameters
        ----------
        chat : graph_models.vertices.Chat
            `Chat` vertex to mark as invalid.

        """
        if not chat:
            return

        if await chat.mark_as_invalid():
            await self.mark_chat_audios_as_deleted(chat.chat_id)
        else:
            logger.error(f"Error in marking the `Chat` with key `{chat.key}` as invalid.")

    async def mark_chat_audios_as_deleted(
        self,
        chat_id: int,
    ) -> None:
        """
        Mark `Audio` vertices in ArangoDB and documents in the Elasticsearch with the given `chat_id` as deleted.

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio documents belongs to.

        """
        if chat_id is None:
            return

        await self.graph.mark_chat_audios_as_deleted(chat_id=chat_id)
        await self.index.mark_chat_audios_as_deleted(chat_id=chat_id)

    async def update_audio_thumbnails(
        self,
        telegram_client_id: int,
        thumbnail_file_unique_id: str,
        telegram_uploaded_photo_message: pyrogram.types.Message,
        file_hash: str,
    ) -> None:
        """
        Update the related vertices and documents after a thumbnail file is uploaded.

        Parameters
        ----------
        telegram_client_id : int
            ID of the telegram client that uploaded the thumbnail file.
        thumbnail_file_unique_id : str
            File unique ID of the thumbnail file that was uploaded.
        telegram_uploaded_photo_message : pyrogram.types.Message
            Telegram message containing the uploaded thumbnail file.
        file_hash : str
            Hash of the uploaded thumbnail file.

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was failed.
        """
        uploaded_thumbnail_file_document = await self.document.get_or_create_uploaded_thumbnail_file(
            telegram_client_id=telegram_client_id,
            thumbnail_file_unique_id=thumbnail_file_unique_id,
            telegram_uploaded_photo_message=telegram_uploaded_photo_message,
        )

        thumbnail_file_vertex = await self.graph.get_or_create_thumbnail_file(
            telegram_uploaded_photo_message=telegram_uploaded_photo_message,
            file_hash=file_hash,
        )

        # Connect all thumbnail vertices with the given `file_unique_id` to the new thumbnail file vertex.
        await self.update_connected_thumbnail_files(thumbnail_file_unique_id, thumbnail_file_vertex)

    async def update_connected_thumbnail_files(
        self,
        thumbnail_file_unique_id: str,
        thumbnail_file_vertex: ThumbnailFile,
    ):
        """
        Connect all thumbnail files with the same file unique ID to the given `ThumbnailFile` vertex. Also, all `Audio` vertices in the ArangoDb and `Audio`
        documents in the ElasticSearch that are connected to the updated `Thumbnail` vertices will also be updated.

        Parameters
        ----------
        thumbnail_file_unique_id : str
            File unique ID of the `Thumbnail` vertices to connect to the given `ThumbnailFile` vertex.
        thumbnail_file_vertex : ThumbnailFile
            `ThumbnailFile` vertex to connect the `Thumbnail` vertices to.

        """
        if not thumbnail_file_vertex or not thumbnail_file_unique_id:
            return

        thumbnail_vertices = await self.graph.get_thumbnails_by_file_unique_id(file_unique_id=thumbnail_file_unique_id)
        if not thumbnail_vertices:
            return

        for thumbnail_vertex in thumbnail_vertices:
            from tase.db.arangodb.graph.edges import Has

            if not await Has.get_or_create_edge(thumbnail_vertex, thumbnail_file_vertex):
                raise EdgeCreationFailed(Has.__class__.__name__)

            if thumbnail_vertex.index != 0:
                # Update all audio vertices in the ArangoDB and all audio documents in the ElasticSearch to use the uploaded thumbnail photos.
                continue

            audio_vertices = await self.graph.get_audio_files_by_thumbnail_file_unique_id(file_unique_id=thumbnail_vertex.file_unique_id)
            if not audio_vertices:
                continue

            for audio_vertex in audio_vertices:
                if not await audio_vertex.update_thumbnails(thumbnail_file_vertex):
                    logger.error(f"Could not update audio vertex with key: `{audio_vertex.key}`")

                es_audio_doc = await self.index.get_audio_by_id(audio_vertex.key)
                if not es_audio_doc:
                    continue

                if not await es_audio_doc.update_thumbnails(thumbnail_file_vertex):
                    logger.error(f"Could not update es audio document with ID: `{es_audio_doc.id}`")

    async def remove_playlist(
        self,
        user: graph_models.vertices.User,
        playlist_key: str,
        deleted_at: int,
    ) -> bool:
        """
        Remove the `Playlist` with the given `playlist_key` and return whether the deletion was successful or not.

        This method deletes the playlist from both `ArangoDB` and `ElasticSearch`.

        Parameters
        ----------
        user : graph_models.vertices.User
            User that playlist belongs to
        playlist_key : str
            Key of the playlist to delete
        deleted_at : int
            Timestamp of the deletion

        Raises
        ------
        PlaylistDoesNotExists
            If the user does not have a playlist with the given `playlist_key` parameter.

        Returns
        -------
        bool
            Whether the deletion operation was successful or not.
        """
        if not user or not playlist_key or deleted_at is None:
            return False

        graph_updated = await self.graph.remove_playlist(user, playlist_key, deleted_at)

        try:
            es_updated = await self.index.remove_playlist(user, playlist_key, deleted_at)
        except UserDoesNotHasPlaylist:
            es_updated = True

        return graph_updated & es_updated

    async def update_playlist_title(
        self,
        user: graph_models.vertices.User,
        playlist_key: str,
        title: str,
    ) -> bool:
        """
        Update playlist's title.

        Parameters
        ----------
        user : graph_models.vertices.User
            User requesting this update.
        playlist_key : str
            Key of the playlist to update its title.
        title : str
            New title for the playlist.

        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        if not playlist_key or not title:
            return False

        playlist_vertex = await self.graph.get_user_playlist_by_key(
            user,
            playlist_key,
            filter_out_soft_deleted=True,
        )
        if not playlist_vertex:
            return False

        graph_successful = await playlist_vertex.update_title(title)
        if not graph_successful:
            return False

        await self.graph.update_connected_hashtags(playlist_vertex, playlist_vertex.find_hashtags())

        if playlist_vertex.is_public:
            es_playlist_doc = await self.index.get_playlist_by_id(playlist_key)
            if not es_playlist_doc:
                return False

            es_successful = await es_playlist_doc.update_title(title)
            if not es_successful:
                return False

            return graph_successful & es_successful

        return graph_successful

    async def update_playlist_description(
        self,
        user: graph_models.vertices.User,
        playlist_key: str,
        description: str,
    ) -> bool:
        """
        Update playlist's description.

        Parameters
        ----------
        user : graph_models.vertices.User
            User requesting this update.
        playlist_key : str
            Key of the playlist to update its description.
        description : str
            New description for the playlist.

        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        if not playlist_key or not description:
            return False

        playlist_vertex = await self.graph.get_user_playlist_by_key(
            user,
            playlist_key,
            filter_out_soft_deleted=True,
        )
        if not playlist_vertex:
            return False

        graph_successful = await playlist_vertex.update_description(description)
        if not graph_successful:
            return False

        await self.graph.update_connected_hashtags(playlist_vertex, playlist_vertex.find_hashtags())

        if playlist_vertex.is_public:
            es_playlist_doc = await self.index.get_playlist_by_id(playlist_key)
            if not es_playlist_doc:
                return False

            es_successful = await es_playlist_doc.update_description(description)
            if not es_successful:
                return False

            return graph_successful & es_successful

        return graph_successful

    async def get_or_create_playlist(
        self,
        user: graph_models.vertices.User,
        title: str,
        description: str,
        is_favorite: bool,
        is_public: bool,
    ) -> Optional[graph_models.vertices.Playlist]:
        """
        Get a `Playlist` with the given `title` if it exists, otherwise, create it and return it.

        Parameters
        ----------
        user : User
            User to get/create this playlist.
        title : str
            Title of the Playlist
        description : str, default : None
            Description of the playlist
        is_favorite : bool
            Whether this playlist is favorite or not.
        is_public : bool, default : False
            Whether the created playlist is public or not.

        Returns
        -------
        Playlist, optional
            Created/Retrieved `Playlist` if the operation successful, return `None` otherwise.

        Raises
        ------
        ValueError
            If `is_public` and `is_favorite` are **True** at the same time.
        """
        if not user or not title:
            return None

        if is_favorite and is_public:
            raise ValueError(f"Playlist cannot be favorite and public at the same time.")

        db_playlist = await self.graph.get_or_create_playlist(
            user,
            title,
            description,
            is_favorite=False,
            is_public=is_public,
        )
        if not db_playlist:
            return None

        if db_playlist.is_public:
            if not await self.index.get_or_create_playlist(
                user,
                db_playlist.key,
                db_playlist.title,
                db_playlist.description,
            ):
                logger.error(f"Error in creating `Playlist` document in the ElasticSearch : `{db_playlist.key}`")

            successful, subscribed = await self.graph.toggle_playlist_subscription(user, db_playlist)
            if not successful or not subscribed:
                logger.error(f"Error in creating `{SubscribeTo.__class__.__name__}` edge from `{user.key}` to `{db_playlist.key}`")

        return db_playlist
