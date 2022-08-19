from pydantic import Field
from pydantic.typing import Optional

from tase.my_logger import logger
from tase.utils import generate_token_urlsafe, prettify
from .base_vertex import BaseVertex
from .user import User
from ..edges import Has
from ...base import BaseSoftDeletableDocument


class Playlist(BaseVertex, BaseSoftDeletableDocument):
    _collection_name = "playlists"
    schema_version = 1
    _extra_do_not_update_fields = ("is_favorite",)

    title: str
    description: Optional[str]

    rank: int
    is_favorite: bool = Field(default=False)

    def update_title(
        self,
        title: str,
    ) -> bool:
        if title is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.title = title
        return self.update(self_copy, reserve_non_updatable_fields=False)

    def update_description(
        self,
        description: str,
    ) -> bool:
        if description is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.description = description
        return self.update(self_copy, reserve_non_updatable_fields=False)


class PlaylistMethods:
    def get_user_playlist_by_title(
        self,
        user: User,
        title: str,
        filter_out_soft_deleted: Optional[bool] = None,
    ) -> Optional[Playlist]:
        if user is None or title is None:
            return None

        return Playlist.find_one(
            filters={
                "_from": user.id,
                "title": title,
            },
            filter_out_soft_deleted=filter_out_soft_deleted,
        )

    def get_user_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        if user is None:
            return None

        playlist: Playlist = Playlist.find_one(
            filters={
                "_from": user.id,
                "is_favorite": True,
            },
        )
        return playlist

    def create_playlist(
        self,
        user: User,
        title: str,
        description: str,
        is_favorite: bool,
    ) -> Optional[Playlist]:
        # making sure of the `key` uniqueness
        while True:
            key = generate_token_urlsafe(10)
            key_exists = Playlist.has(key)
            if key_exists is not None and not key_exists:
                break

        if key is None:
            return None

        v = Playlist(
            key=key,
            title=title,
            description=description,
            is_favorite=is_favorite,
            rank=1 if is_favorite else 2,
        )

        playlist, successful = Playlist.insert(v)
        playlist: Playlist = playlist  # todo: what's the fix?

        if playlist and successful:
            try:
                has_edge = Has.get_or_create_edge(user, playlist)
            except ValueError:
                # todo: could not create the has_edge, abort the transaction
                deleted = playlist.delete()
                if not deleted:
                    # todo: could not delete the playlist, what now?
                    logger.error(f"Could not delete playlist: {prettify(playlist)}")
            else:
                return playlist if has_edge else None

        return playlist

    def get_or_create_playlist(
        self,
        user: User,
        title: str,
        description: str = None,
        is_favorite: bool = False,
    ) -> Optional[Playlist]:
        if user is None or title is None:
            return None

        if is_favorite:
            # check if there is a favorite playlist already, one favorite playlist is allowed per user
            user_fav_playlist = self.get_user_favorite_playlist(user)
            if user_fav_playlist:
                # the user has a favorite playlist already
                return user_fav_playlist
        else:
            # non-favorite playlists with reserved names aren't allowed
            if title == "Favorite":
                return None

        # only check the playlists that haven't been soft-deleted.
        playlist = self.get_user_playlist_by_title(user, title, filter_out_soft_deleted=True)
        if playlist:
            return playlist

        return self.create_playlist(user, title, description, is_favorite)

    def create_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        return self.get_or_create_playlist(
            user,
            title="Favorite",
            description="Favorite Playlist",
            is_favorite=True,
        )

    def get_or_create_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        playlist = self.get_user_favorite_playlist(user)
        if playlist is None:
            playlist = self.create_favorite_playlist(user)

        return playlist
