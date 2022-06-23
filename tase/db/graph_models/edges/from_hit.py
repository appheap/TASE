from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Download, Hit


class FromHit(BaseEdge):
    """
    Connection from `Download` to `Hit`
    """

    _collection_edge_name = "from_hit"

    _from_vertex_collections = [Download]
    _to_vertex_collections = [Hit]

    @staticmethod
    def parse_from_download_and_hit(
        download: "Download",
        hit: "Hit",
    ) -> Optional["FromHit"]:
        if download is None or hit is None:
            return None

        key = f"{download.key}:{hit.key}"
        return FromHit(
            key=key,
            from_node=download,
            to_node=hit,
        )
