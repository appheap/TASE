from typing import Optional

from .base_edge import BaseEdge
from ..vertices import User, Download


class Downloaded(BaseEdge):
    """
    Connection from `User` to `Download`
    """

    _collection_edge_name = "downloaded"

    _from_vertex_collections = [User]
    _to_vertex_collections = [Download]

    @staticmethod
    def parse_from_user_and_download(
        user: "User", download: "Download"
    ) -> Optional["Downloaded"]:
        if user is None or download is None:
            return None

        key = f"{user.key}@{download.key}"
        return Downloaded(
            key=key,
            from_node=user,
            to_node=download,
        )
