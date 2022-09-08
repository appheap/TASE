from typing import Optional, Union, List

import pyrogram

from tase.db.helpers import SearchMetaData
from . import Audio
from .base_vertex import BaseVertex
from .chat import ChatType
from .user import User
from .. import ArangoGraphMethods
from ..edges import HasMade, Has, ToBot
from ...enums import InlineQueryType
from ...helpers import ElasticQueryMetadata, InlineQueryMetadata


class Query(BaseVertex):
    _collection_name = "queries"
    schema_version = 1

    query: str
    query_date: int

    inline_metadata: Optional[InlineQueryMetadata]
    elastic_metadata: ElasticQueryMetadata

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
        query_metadata: dict,
        # following parameters are intended to be used for `InlineQuery` rather than normal query.
        telegram_inline_query: pyrogram.types.InlineQuery,
        inline_query_type: InlineQueryType,
        next_offset: Optional[str],
    ) -> Optional["Query"]:
        if bot is None or user is None:
            return None

        key = cls.parse_key(bot.key, user, query_date)
        if key is None:
            return None

        metadata = ElasticQueryMetadata.parse(query_metadata)
        if metadata is None:
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
            elastic_metadata=metadata,
        )


class QueryMethods:
    def create_query(
        self: ArangoGraphMethods,
        bot_id: int,
        user: User,
        query: str,
        query_date: int,
        query_metadata: dict,
        audios: List[Audio],
        search_metadata_list: List[SearchMetaData],
        # following parameters are meant to be used with inline query
        telegram_inline_query: Optional[pyrogram.types.InlineQuery],
        inline_query_type: Optional[InlineQueryType],
        next_offset: Optional[str],
    ) -> Optional[Query]:
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
        query_metadata : dict
            Metadata of this query that on ElasticSearch. It must have `duration`, `max_score`, `total_hits`,
            and `total_rel` attributes
        audios : List[Audio]
            List of audios this query matches to
        search_metadata_list : List[SearchMetadata]
            List of metadata for each of the audios this query matches to
        telegram_inline_query : pyrogram.types.InlineQuery, optional
            Telegram InlineQuery object if the query is inline
        inline_query_type : InlineQueryType, optional
            Type of the inline query if the query is inline
        next_offset : str, optional
            Next offset of query if the query is inline and has more results that will be paginated

        Returns
        -------
        Query, optional
            Query object if the creation in the DB was successful, otherwise, return None

        Raises
        ------
        Exception
            If creation of any connected edges and vertices has not been successful.
        ValueError
            When the start or the end vertex provided to the function does not match the edge definition in the
            database.
        """
        if bot_id is None or user is None or query is None or query_date is None:
            return None

        bot = self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None

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

            # link the user to this query
            has_made_edge = HasMade.get_or_create_edge(user, db_query)
            if has_made_edge is None:
                raise Exception("Could not create the `has_made` edge")

            to_bot_edge = ToBot.get_or_create_edge(db_query, bot)
            if to_bot_edge is None:
                raise Exception("Could not create the `to_bot` edge")

            for audio, search_metadata in zip(audios, search_metadata_list):
                if audio is None or search_metadata is None:
                    # todo: what now?
                    continue

                hit = self.get_or_create_hit(db_query, audio, search_metadata)
                if hit is None:
                    raise Exception("Could not create `hit` vertex")

                has_hit_edge = Has.get_or_create_edge(db_query, hit)
                if has_hit_edge is None:
                    raise Exception("Could not create `has` edge from `query` vertex to `hit` vertex")

            return db_query

        return None

    def get_or_create_query(
        self,
        bot_id: int,
        user: User,
        query: str,
        query_date: int,
        query_metadata: dict,
        audios: List[Audio],
        search_metadata_list: List[SearchMetaData],
        # following parameters are meant to be used with inline query
        telegram_inline_query: Optional[pyrogram.types.InlineQuery],
        inline_query_type: Optional[InlineQueryType],
        next_offset: Optional[str],
    ) -> Optional[Query]:
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
        query_metadata : dict
            Metadata of this query that on ElasticSearch. It must have `duration`, `max_score`, `total_hits`,
            and `total_rel` attributes
        audios : List[Audio]
            List of audios this query matches to
        search_metadata_list : List[SearchMetadata]
            List of metadata for each of the audios this query matches to
        telegram_inline_query : pyrogram.types.InlineQuery, optional
            Telegram InlineQuery object if the query is inline
        inline_query_type : InlineQueryType, optional
            Type of the inline query if the query is inline
        next_offset : str, optional
            Next offset of query if the query is inline and has more results that will be paginated

        Returns
        -------
        Query, optional
            Query object if the operation in the DB was successful, otherwise, return None

        Raises
        ------
        Exception
            If creation of any connected edges and vertices has not been successful.
        ValueError
            When the start or the end vertex provided to the function does not match the edge definition in the
            database.
        """
        if bot_id is None or user is None or query is None or query_date is None:
            return None

        db_query = Query.get(Query.parse_key(bot_id, user, query_date))
        if db_query is None:
            db_query = self.create_query(
                bot_id,
                user,
                query,
                query_date,
                query_metadata,
                audios,
                search_metadata_list,
                telegram_inline_query,
                inline_query_type,
                next_offset,
            )

        return db_query
