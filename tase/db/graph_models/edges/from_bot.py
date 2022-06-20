from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Download, User


class FromBot(BaseEdge):
    """
    Connection from `Download` to `User`
    """

    _collection_edge_name = "from_bot"

    _from_vertex_collections = [Download]
    _to_vertex_collections = [User]

    @staticmethod
    def parse_from_download_and_user(
        download: "Download", user: "User"
    ) -> Optional["FromBot"]:
        if download is None or user is None:
            return None

        key = f"{download.key}@{user.key}"
        return FromBot(
            key=key,
            from_node=download,
            to_node=user,
        )
