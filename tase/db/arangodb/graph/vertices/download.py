import uuid
from typing import Optional, Generator

from tase.my_logger import logger
from . import User, Audio
from .base_vertex import BaseVertex
from .. import ArangoGraphMethods
from ..edges import Has, FromHit, Downloaded, FromBot


class Download(BaseVertex):
    _collection_name = "downloads"
    schema_version = 1

    @classmethod
    def parse(
        cls,
        key: str,
    ) -> Optional["Download"]:
        if key is None:
            return None

        return Download(key=key)


class DownloadMethods:
    _get_user_download_history_query = (
        "for dl_v,dl_e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@downloaded'], vertexCollections:['@downloads']}"
        "   sort dl_e.created_at DESC"
        "   limit @offset, @limit"
        "   for aud_v,has in 1..1 outbound dl_v graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "       collect audios = aud_v"
        "       for audio in audios"
        "           return audio"
    )

    def create_download(
        self: ArangoGraphMethods,
        hit_download_url: str,
        user: User,
        bot_id: int,
    ) -> Optional[Download]:
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

        Returns
        -------
        Download, optional
            Download vertex if the creation was successful, otherwise, return None

        """
        if hit_download_url is None or user is None or bot_id is None:
            return None

        bot = self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None

        hit = self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            return None

        try:
            audio = self.get_audio_from_hit(hit)
        except ValueError:
            # happens when the `Hit` has more than linked `Audio` vertices
            return None

        while True:
            key = str(uuid.uuid4())
            if Download.get(key) is None:
                break

        download = Download.parse(key)
        if download is None:
            return None

        try:
            has_edge = Has.get_or_create_edge(download, audio)
        except ValueError:
            logger.error("ValueError: Could not create `has` edge from `Download` vertex to `Audio` vertex")
            return None

        try:
            from_hit_edge = FromHit.get_or_create_edge(download, hit)
        except ValueError:
            logger.error("ValueError: Could not create `from_hit` edge from `Download` vertex to `Hit` vertex")
            return None

        try:
            downloaded_edge = Downloaded.get_or_create_edge(user, download)
        except ValueError:
            logger.error("ValueError: Could not create `downloaded` edge from `User` vertex to `Download` vertex")
            return None

        try:
            from_bot_edge = FromBot.get_or_create_edge(download, user)
        except ValueError:
            logger.error("ValueError: Could not create `from_bot` edge from `Download` vertex to `User` vertex")
            return None

        return download

    def get_user_download_history(
        self,
        user: User,
        offset: int = 0,
        limit: int = 10,
    ) -> Generator[Audio, None, None]:
        """
        Get `User` download history.

        Parameters
        ----------
        user : User
            User to get the download history
        offset : int, default : 0
            Offset to get the download history query after
        limit : int, default : 10
            Number of `Audio`s to query

        Returns
        -------
        Generator[Audio, None, None]
            Audios that the given user has downloaded

        """
        if user is None:
            return None

        cursor = Audio.execute_query(
            self._get_user_download_history_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has._collection_name,
                "audios": Audio._collection_name,
                "downloaded": Downloaded._collection_name,
                "downloads": Download._collection_name,
                "offset": offset,
                "limit": limit,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Audio.from_collection(doc)

        return None
