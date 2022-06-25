from typing import Optional

from arango import DocumentUpdateError
from pydantic import Field

from tase.my_logger import logger
from .base_vertex import BaseVertex


class Playlist(BaseVertex):
    _vertex_name = "playlists"

    title: str
    description: Optional[str]

    deleted_at: Optional[int]
    is_deleted: bool = Field(default=False)

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

    def soft_delete(
        self,
        deleted_at: int,
    ):
        if deleted_at is None:
            return False

        try:

            self._db.update(
                {
                    "_key": self.key,
                    "is_deleted": True,
                    "deleted_at": deleted_at,
                },
                silent=True,
            )
            return True
        except DocumentUpdateError as e:
            logger.exception(e)
            return False
        except Exception as e:
            logger.exception(e)
            return False
