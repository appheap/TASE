from __future__ import annotations

import uuid
from typing import Optional, TYPE_CHECKING

from tase.my_logger import logger
from .base_vertex import BaseVertex
from .user import User

if TYPE_CHECKING:
    from .. import ArangoGraphMethods


class Download(BaseVertex):
    _collection_name = "downloads"
    schema_version = 1

    @classmethod
    def parse(
        cls,
        key: str,
    ) -> Optional[Download]:
        if key is None:
            return None

        return Download(key=key)


class DownloadMethods:
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

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.edges import FromHit
        from tase.db.arangodb.graph.edges import Downloaded
        from tase.db.arangodb.graph.edges import FromBot

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
