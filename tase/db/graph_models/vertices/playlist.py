from typing import Optional

from .base_vertex import BaseVertex


class Playlist(BaseVertex):
    _vertex_name = "playlists"

    title: str
    description: Optional[str]
