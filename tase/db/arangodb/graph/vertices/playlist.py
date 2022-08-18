from pydantic import Field
from pydantic.typing import Optional, Tuple

from tase.my_logger import logger
from tase.utils import generate_token_urlsafe, prettify
from .base_vertex import BaseVertex
from .user import User
from ..edges import Has


class Playlist(BaseVertex):
    _collection_name = "playlists"
    _extra_do_not_update_fields = [
        "is_favorite",
    ]

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
    def get_user_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        if user is None:
            return None

        playlists = Playlist.find(
            filters={
                "_from": user.id,
                "is_favorite": True,
            },
            limit=1,
        )
        if playlists is None:
            return None
        else:
            playlists = list(playlists)
            if not len(playlists):
                return None
            else:
                return playlists[0]

    def create_playlist(
        self,
        user: User,
        title: str,
        description: str = None,
        is_favorite: bool = False,
    ) -> Tuple[Optional[Playlist], bool]:
        if user is None or title is None:
            return None, False

        key = None
        # making sure the `key` is unique
        while True:
            key = generate_token_urlsafe(10)
            key_exists = Playlist.has(key)
            if key_exists is not None and not key_exists:
                break

        if key is None:
            return None, False

        if is_favorite:
            # check if there is a favorite playlist already, one favorite playlist is allowed per user
            user_fav_playlist = self.get_user_favorite_playlist(user)
            if user_fav_playlist:
                # the user has a favorite playlist already
                return None, False

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
                has_edge = None
                has_edge = Has.get_or_create_edge(user, playlist)
            except ValueError:
                # todo: could not create the has_edge, abort the transaction
                deleted = playlist.delete()
                if not deleted:
                    # todo: could not delete the playlist, what now?
                    logger.error(f"Could not delete playlist: {prettify(playlist)}")
            else:
                return playlist, successful if has_edge else False

        return playlist, successful

    def create_favorite_playlist(
        self,
        user: User,
    ) -> Tuple[Optional[Playlist], bool]:
        return self.create_playlist(
            user,
            title="Favorite",
            description="Favorite Playlist",
            is_favorite=True,
        )

    def get_or_create_favorite_playlist(
        self,
        user: User,
    ) -> Tuple[Optional[Playlist], bool]:
        playlist = self.get_user_favorite_playlist(user)
        successful = False
        if playlist is None:
            playlist, successful = self.create_favorite_playlist(user)

        return playlist, successful
