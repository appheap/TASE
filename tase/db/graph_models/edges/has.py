from typing import Optional

from .base_edge import BaseEdge
from ..vertices import (Audio, Download, Hit, InlineQuery, Playlist, Query, QueryKeyword, User)


class Has(BaseEdge):
    """ """

    _collection_edge_name = "has"

    _from_vertex_collections = [
        User,
        Playlist,
        Query,
        InlineQuery,
        Hit,
        Download,
    ]
    _to_vertex_collections = [Playlist, Audio, Hit, QueryKeyword]

    @staticmethod
    def parse_from_user_and_playlist(
        user: "User", playlist: "Playlist"
    ) -> Optional["Has"]:
        if user is None or playlist is None:
            return None

        key = f"{user.key}@{playlist.key}"
        return Has(
            key=key,
            from_node=user,
            to_node=playlist,
        )

    @staticmethod
    def parse_from_playlist_and_audio(
        playlist: "Playlist", audio: "Audio"
    ) -> Optional["Has"]:
        if playlist is None or audio is None:
            return None

        key = f"{playlist.key}@{audio.key}"
        return Has(
            key=key,
            from_node=playlist,
            to_node=audio,
        )

    @staticmethod
    def parse_from_hit_and_audio(hit: "Hit", audio: "Audio") -> Optional["Has"]:
        if hit is None or audio is None:
            return None

        key = f"{hit.key}@{audio.key}"
        return Has(
            key=key,
            from_node=hit,
            to_node=audio,
        )

    ########################################################################################

    @staticmethod
    def parse_from_query_and_hit(
        query: "Query",
        hit: "Hit",
    ) -> Optional["Has"]:
        if query is None or hit is None:
            return None

        key = f"{query.key}:{hit.key}"
        return Has(
            key=key,
            from_node=query,
            to_node=hit,
        )

    @staticmethod
    def parse_from_inline_query_and_hit(
        inline_query: "InlineQuery",
        hit: "Hit",
    ) -> Optional["Has"]:
        if inline_query is None or hit is None:
            return None

        key = f"{inline_query.key}@{hit.key}"
        return Has(
            key=key,
            from_node=inline_query,
            to_node=hit,
        )

    ########################################################################################

    @staticmethod
    def parse_from_user_and_playlist(
        user: "User", playlist: "Playlist"
    ) -> Optional["Has"]:
        if user is None or playlist is None:
            return None

        key = f"{user.key}@{playlist.key}"
        return Has(
            key=key,
            from_node=user,
            to_node=playlist,
        )

    ########################################################################################

    @staticmethod
    def parse_from_download_and_audio(
        download: "Download", audio: "Audio"
    ) -> Optional["Has"]:
        if download is None or audio is None:
            return None

        key = f"{download.key}@{audio.key}"
        return Has(
            key=key,
            from_node=download,
            to_node=audio,
        )

    ########################################################################################

    @staticmethod
    def parse_from_query_and_query_keyword(
        query: "Query",
        query_keyword: "QueryKeyword",
    ) -> Optional["Has"]:
        if query is None or query_keyword is None:
            return None

        key = f"{query.key}@{query_keyword.key}"
        return Has(key=key, from_node=query, to_node=query_keyword)

    @staticmethod
    def parse_from_inline_query_and_query_keyword(
        inline_query: "InlineQuery", query_keyword: "QueryKeyword"
    ) -> Optional["Has"]:
        if inline_query is None or query_keyword is None:
            return None

        key = f"{inline_query.key}@{query_keyword.key}"
        return Has(
            key=key,
            from_node=inline_query,
            to_node=query_keyword,
        )

    ########################################################################################
