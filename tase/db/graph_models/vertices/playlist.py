from typing import Optional

from .base_vertex import BaseVertex


class Playlist(BaseVertex):
    _vertex_name = "playlists"

    title: str
    description: Optional[str]

    def update_title(
        self,
        title: str,
    ):
        if title is None:
            return

        self._db.update(
            {
                "_key": self.key,
                "title": title,
            },
            silent=True,
        )

    def update_description(
        self,
        description: str,
    ):
        if description is None:
            return

        self._db.update(
            {
                "_key": self.key,
                "description": description,
            },
            silent=True,
        )
