from __future__ import annotations

import collections
from typing import Optional, Union, List, Tuple, Generator, TYPE_CHECKING

import pyrogram

from tase.common.utils import get_now_timestamp, timing
from tase.db.helpers import SearchMetaData
from tase.errors import InvalidToVertex, InvalidFromVertex, EdgeCreationFailed
from tase.my_logger import logger
from . import Audio, Hit
from .base_vertex import BaseVertex
from .chat import ChatType
from .user import User

if TYPE_CHECKING:
    from .. import ArangoGraphMethods
from ...enums import InlineQueryType, HitType
from ...helpers import ElasticQueryMetadata, InlineQueryMetadata


class Query(BaseVertex):
    _collection_name = "queries"
    schema_version = 1

    query: str
    query_date: int

    inline_metadata: Optional[InlineQueryMetadata]
    elastic_metadata: Optional[ElasticQueryMetadata]

    @classmethod
    def parse_key(
        cls,
        bot_id: Union[int, str],
        user: User,
        query_date: int,
    ) -> Optional[str]:
        if bot_id is None or user is None or query_date is None:
            return None
        return f"{bot_id}:{user.key}:{query_date}"

    @classmethod
    def parse(
        cls,
        bot: User,
        user: User,
        query: str,
        query_date: int,
        query_metadata: Optional[ElasticQueryMetadata],
        # following parameters are intended to be used for `InlineQuery` rather than normal query.
        telegram_inline_query: Optional[pyrogram.types.InlineQuery],
        inline_query_type: Optional[InlineQueryType],
        next_offset: Optional[str],
    ) -> Optional[Query]:
        if bot is None or user is None:
            return None

        key = cls.parse_key(bot.key, user, query_date)
        if key is None:
            return None

        if telegram_inline_query is not None:
            inline_metadata = InlineQueryMetadata(
                query_id=telegram_inline_query.id,
                chat_type=ChatType.parse_from_pyrogram(telegram_inline_query.chat_type),
                offset=telegram_inline_query.offset,
                next_offset=next_offset,
                type=inline_query_type,
            )
        else:
            inline_metadata = None

        return Query(
            key=key,
            query=query,
            query_date=query_date,
            inline_metadata=inline_metadata,
            elastic_metadata=query_metadata,
        )


class QueryMethods:
    _get_query_hits_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@hits']}"
        "   sort v.created_at asc"
        "   return v"
    )

    _get_total_queries_count = (
        "let non_inline_count = ("
        "   for query in @queries"
        "       filter query.inline_metadata == null"
        "       collect with count into count_"
        "       return count_"
        ")"
        ""
        "let inline_count = ("
        "   for query in @queries"
        "       filter query.inline_metadata != null and query.inline_metadata.type == 1 and query.inline_metadata.offset == ''"
        "       collect with count into count_"
        "       return count_"
        ")"
        ""
        "return non_inline_count + inline_count"
    )

    _get_new_queries_count = (
        "let non_inline_count = ("
        "   for query in @queries"
        "       filter query.inline_metadata == null and query.created_at >= @checkpoint"
        "       collect with count into count_"
        "       return count_"
        ")"
        ""
        "let inline_count = ("
        "   for query in @queries"
        "       filter query.inline_metadata != null and query.inline_metadata.type == 1 and query.inline_metadata.offset == '' and query.created_at >= @checkpoint"
        "       collect with count into count_"
        "       return count_"
        ")"
        ""
        "return non_inline_count + inline_count"
    )

    @timing
    def create_query(
        self: ArangoGraphMethods,
        bot_id: int,
        user: User,
        query: str,
        query_date: int,
        audio_vertices: List[Audio],
        query_metadata: Optional[ElasticQueryMetadata] = None,
        search_metadata_list: Optional[List[SearchMetaData]] = None,
        # following parameters are meant to be used with inline query
        telegram_inline_query: Optional[pyrogram.types.InlineQuery] = None,
        inline_query_type: Optional[InlineQueryType] = None,
        next_offset: Optional[str] = None,
        hit_download_urls: List[str] = None,
    ) -> Tuple[Optional[Query], Optional[List[Hit]]]:
        """
        Create a Query along with necessary vertices and edges.

        Parameters
        ----------
        bot_id : int
            ID of the bot that has been queried
        user : User
            User that has made this query
        query : str
            Query string
        query_date : int
            Timestamp of making the query
        audio_vertices : List[Audio]
            List of audios this query matches to
        query_metadata : ElasticQueryMetadata, default : None
            Metadata of this query that on ElasticSearch.
        search_metadata_list : List[SearchMetadata], default : None
            List of metadata for each of the audios this query matches to
        telegram_inline_query : pyrogram.types.InlineQuery, default : None
            Telegram InlineQuery object if the query is inline
        inline_query_type : InlineQueryType, default : None
            Type of the inline query if the query is inline
        next_offset : str, default : None
            Next offset of query if the query is inline and has more results that will be paginated
        hit_download_urls : list of str, default : None
            List of hit download URLs to initialize hits with

        Returns
        -------
        tuple of query and array of hits
            Query object and list of hits if the creation in the DB was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of any connected edges has not been successful.
        """
        if bot_id is None or user is None or query is None or query_date is None:
            return None, None

        bot = self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None, None

        db_query, successful = Query.insert(
            Query.parse(
                bot,
                user,
                query,
                query_date,
                query_metadata,
                telegram_inline_query,
                inline_query_type,
                next_offset,
            )
        )
        if db_query and successful:
            # todo: get/create a keyword vertex from this query and link them together
            from tase.db.arangodb.graph.edges import HasMade
            from tase.db.arangodb.graph.edges import ToBot
            from tase.db.arangodb.graph.edges import Has

            # link the user to this query
            try:
                has_made_edge = HasMade.get_or_create_edge(user, db_query)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error("ValueError: Could not create the `has_made` edge")
            else:
                if has_made_edge is None:
                    raise EdgeCreationFailed(HasMade.__class__.__name__)

            try:
                to_bot_edge = ToBot.get_or_create_edge(db_query, bot)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error("ValueError: Could not create the `to_bot` edge")
            else:
                if to_bot_edge is None:
                    raise EdgeCreationFailed(ToBot.__class__.__name__)

            hit_type = HitType.UNKNOWN
            if inline_query_type is not None and telegram_inline_query is not None:
                if inline_query_type == InlineQueryType.SEARCH:
                    hit_type = HitType.INLINE_SEARCH
                elif inline_query_type == InlineQueryType.COMMAND:
                    hit_type = HitType.INLINE_COMMAND
                else:
                    # unexpected hit_type
                    hit_type = HitType.UNKNOWN
            else:
                hit_type = HitType.SEARCH

            hits = collections.deque()

            if search_metadata_list is None or not len(search_metadata_list):
                search_metadata_list = (None for _ in range(len(audio_vertices)))

            if hit_download_urls is None or not len(hit_download_urls):
                hit_download_urls = (None for _ in range(len(audio_vertices)))

            for audio_vertex, search_metadata, hit_download_url in zip(audio_vertices, search_metadata_list, hit_download_urls):
                if audio_vertex is None:
                    # todo: what now?
                    continue

                hit = self.get_or_create_hit(
                    db_query,
                    audio_vertex,
                    hit_type,
                    hit_download_url,
                    search_metadata,
                )
                if hit is None:
                    raise Exception("Could not create `hit` vertex")

                hits.append(hit)

                try:
                    has_hit_edge = Has.get_or_create_edge(db_query, hit)
                except (InvalidFromVertex, InvalidToVertex):
                    pass
                else:
                    if has_hit_edge is None:
                        raise EdgeCreationFailed(Has.__class__.__name__)

            return db_query, list(hits)

        return None, None

    @timing
    def get_or_create_query(
        self,
        bot_id: int,
        user: User,
        query: str,
        query_date: int,
        audio_vertices: List[Audio],
        query_metadata: Optional[ElasticQueryMetadata] = None,
        search_metadata_list: Optional[List[SearchMetaData]] = None,
        # following parameters are meant to be used with inline query
        telegram_inline_query: Optional[pyrogram.types.InlineQuery] = None,
        inline_query_type: Optional[InlineQueryType] = None,
        next_offset: Optional[str] = None,
        hit_download_urls: List[str] = None,
    ) -> Tuple[Optional[Query], Optional[List[Hit]]]:
        """
        Get Query if it exists in the database, otherwise, create a Query along with necessary vertices and
        edges.

        Parameters
        ----------
        bot_id : int
            ID of the bot that has been queried
        user : User
            User that has made this query
        query : str
            Query string
        query_date : int
            Timestamp of making the query
        audio_vertices : List[Audio]
            List of audios this query matches to
        query_metadata : ElasticQueryMetadata, default : None
            Metadata of this query that on ElasticSearch.
        search_metadata_list : List[SearchMetadata], default : None
            List of metadata for each of the audios this query matches to
        telegram_inline_query : pyrogram.types.InlineQuery, default : None
            Telegram InlineQuery object if the query is inline
        inline_query_type : InlineQueryType, default : None
            Type of the inline query if the query is inline
        next_offset : str, default : None
            Next offset of query if the query is inline and has more results that will be paginated
        hit_download_urls : list of str, default : None
            List of hit download URLs to initialize hits with

        Returns
        -------
        tuple of query and list of hits
            Query object and list of hits if the operation in the DB was successful, otherwise, return None

        Raises
        ------
        Exception
            If creation of any connected edges and vertices has not been successful.
        """
        if bot_id is None or user is None or query is None or query_date is None:
            return None, None

        db_query = Query.get(Query.parse_key(bot_id, user, query_date))
        if db_query is None:
            db_query, hits = self.create_query(
                bot_id,
                user,
                query,
                query_date,
                audio_vertices,
                query_metadata,
                search_metadata_list,
                telegram_inline_query,
                inline_query_type,
                next_offset,
                hit_download_urls,
            )
            return db_query, hits
        else:
            return db_query, list(self.get_query_hits(db_query))

    def get_query_hits(
        self,
        query: Query,
    ) -> Generator[Hit, None, None]:
        """
        Get an `Audio` vertex from the given `Hit` vertex

        Parameters
        ----------
        query : Query
            Query to get the hits from.

        Yields
        ------
        Hit
            List of hits if operation was successful, otherwise, return None
        """
        if query is None:
            return

        from tase.db.arangodb.graph.edges import Has

        cursor = Hit.execute_query(
            self._get_query_hits_query,
            bind_vars={
                "start_vertex": query.id,
                "queries": Query._collection_name,
                "has": Has._collection_name,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Hit.from_collection(doc)

    def get_new_queries_count(self) -> int:
        """
        Get the total number of queries made in the last 24 hours

        Returns
        -------
        int
            Total number of queries made in the last 24 hours

        """
        checkpoint = get_now_timestamp() - 86400000

        cursor = Query.execute_query(
            self._get_new_queries_count,
            bind_vars={
                "queries": Query._collection_name,
                "checkpoint": checkpoint,
            },
        )

        if cursor is not None and len(cursor):
            return int(cursor.pop())

        return 0

    def get_total_queries_count(self) -> int:
        """
        Get the total number of queries made

        Returns
        -------
        int
            Total number of queries

        """
        cursor = Query.execute_query(
            self._get_total_queries_count,
            bind_vars={
                "queries": Query._collection_name,
            },
        )

        if cursor is not None and len(cursor):
            return int(cursor.pop())

        return 0
