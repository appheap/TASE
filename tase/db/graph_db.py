import uuid
from string import Template
from typing import List, Optional, Tuple, Union

import pyrogram
from arango import ArangoClient, AQLQueryExecuteError
from arango.database import StandardDatabase
from arango.graph import Graph

from . import elasticsearch_db
from .enums import MentionSource
from .graph_models.edges import (
    Downloaded,
    FileRef,
    FromBot,
    FromHit,
    Had,
    Has,
    HasMade,
    IsCreatorOf,
    IsMemberOf,
    LinkedChat,
    Mentions,
    SentBy,
    ToBot,
    edges,
)
from .graph_models.helper_models import UsernameExtractorMetadata, AudioIndexerMetadata
from .graph_models.vertices import (
    Audio,
    Chat,
    ChatType,
    Download,
    File,
    Hit,
    InlineQuery,
    InlineQueryType,
    Playlist,
    Query,
    QueryKeyword,
    User,
    Username,
    vertices,
)
from ..configs import ArangoDBConfig
from ..my_logger import logger
from ..utils import get_timestamp


class GraphDatabase:
    arango_client: "ArangoClient"
    db: "StandardDatabase"
    graph: "Graph"

    def __init__(
        self,
        arangodb_config: ArangoDBConfig,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=arangodb_config.db_host_url)
        sys_db = self.arango_client.db(
            "_system",
            username=arangodb_config.db_username,
            password=arangodb_config.db_password,
        )

        if not sys_db.has_database(arangodb_config.db_name):
            sys_db.create_database(
                arangodb_config.db_name,
            )

        self.db = self.arango_client.db(
            arangodb_config.db_name,
            username=arangodb_config.db_username,
            password=arangodb_config.db_password,
        )

        self.aql = self.db.aql

        if not self.db.has_graph(arangodb_config.graph_name):
            self.graph = self.db.create_graph(arangodb_config.graph_name)
        else:
            self.graph = self.db.graph(arangodb_config.graph_name)

        for v_class in vertices:
            if not self.graph.has_vertex_collection(v_class._vertex_name):
                _db = self.graph.create_vertex_collection(v_class._vertex_name)
            else:
                _db = self.graph.vertex_collection(v_class._vertex_name)
            v_class._db = _db

        for e_class in edges:
            if not self.graph.has_edge_definition(e_class._collection_edge_name):
                _db = self.graph.create_edge_definition(
                    edge_collection=e_class._collection_edge_name,
                    from_vertex_collections=e_class.from_vertex_collections(),
                    to_vertex_collections=e_class.to_vertex_collections(),
                )
            else:
                _db = self.graph.vertex_collection(e_class._collection_edge_name)
            e_class._db = _db

    def create_user(
        self,
        telegram_user: "pyrogram.types.User",
    ) -> Optional[Tuple["User", bool]]:
        if telegram_user is None:
            return None

        user, successful = User.create(User.parse_from_user(telegram_user))
        return user, successful

    def get_or_create_user(
        self,
        telegram_user: "pyrogram.types.User",
    ) -> Optional["User"]:
        if telegram_user is None:
            return None

        user = User.find_by_key(User.get_key(telegram_user))
        if not user:
            # user does not exist in the database, create it
            user, successful = self.create_user(telegram_user)

        return user

    def update_or_create_user(
        self,
        telegram_user: "pyrogram.types.User",
    ) -> Optional["User"]:
        if telegram_user is None:
            return None

        user = User.find_by_key(User.get_key(telegram_user))
        if user:
            # user exists in the database, update it
            user, successful = User.update(user, User.parse_from_user(telegram_user))
        else:
            # user does not exist in the database, create it
            user, successful = self.create_user(telegram_user)

        if not user.is_bot:
            self.get_or_create_user_favorite_playlist(user)

        return user

    def get_or_create_chat(
        self,
        telegram_chat: "pyrogram.types.Chat",
        creator: "User" = None,
        member: "User" = None,
    ) -> Optional["Chat"]:
        if telegram_chat is None:
            return None

        chat = Chat.find_by_key(Chat.get_key(telegram_chat))
        if not chat:
            # audio does not exist, create it
            chat = self.create_chat(telegram_chat, creator, member)
        return chat

    def update_or_create_chat(
        self,
        telegram_chat: "pyrogram.types.Chat",
        creator: "User" = None,
        member: "User" = None,
    ) -> Optional["Chat"]:
        if telegram_chat is None:
            return None

        chat = Chat.find_by_key(Chat.get_key(telegram_chat))
        if chat:
            # audio exists in the database, update the audio
            chat, successful = Chat.update(chat, Chat.parse_from_chat(telegram_chat))
        else:
            # audio does not exist, create it
            chat = self.create_chat(telegram_chat, creator, member)

        return chat

    def create_chat(
        self,
        telegram_chat: "pyrogram.types.Chat",
        creator: "User" = None,
        member: "User" = None,
    ) -> Optional["Chat"]:
        if telegram_chat is None:
            return None

        chat, successful = Chat.create(Chat.parse_from_chat(telegram_chat))
        if chat and successful:
            if telegram_chat.linked_chat:
                # todo: fix this
                linked_chat = self.get_or_create_chat(telegram_chat.linked_chat, creator, member)
                if linked_chat:
                    db_linked_chat_edge, successful = self.get_or_create_linked_chat_edge(chat, linked_chat)
                else:
                    pass
        else:
            pass

        self.get_or_create_is_creator_of_edge(chat, creator, telegram_chat)
        self.get_or_create_is_member_of_edge(chat, member)

        return chat

    def get_or_create_is_member_of_edge(
        self,
        chat: Chat,
        member: User,
    ) -> Tuple[Optional[IsMemberOf], bool]:
        is_member_of_edge = None
        successful = False

        if chat and member:
            is_member_of_edge = IsMemberOf.find_by_key(IsMemberOf.get_key(member, chat))
            successful = True

            if not is_member_of_edge:
                is_member_of_edge, successful = IsMemberOf.create(
                    IsMemberOf.parse_from_user_and_chat(
                        user=member,
                        chat=chat,
                    )
                )

        return is_member_of_edge, successful

    def get_or_create_is_creator_of_edge(
        self,
        chat: Chat,
        creator: User,
        telegram_chat: pyrogram.types.Chat,
    ) -> Tuple[Optional[IsCreatorOf], bool]:
        is_creator_of_edge = None
        successful = False

        if chat and telegram_chat.is_creator and creator:
            is_creator_of_edge = IsCreatorOf.find_by_key(IsCreatorOf.get_key(chat, creator))
            successful = True

            if not is_creator_of_edge:
                is_creator_of_edge, successful = IsCreatorOf.create(
                    IsCreatorOf.parse_from_chat_and_user(
                        chat,
                        creator,
                    )
                )

        return is_creator_of_edge, successful

    def get_or_create_linked_chat_edge(
        self,
        chat: Chat,
        linked_chat: Chat,
    ) -> Tuple[Optional[LinkedChat], bool]:
        if chat is None or linked_chat is None:
            return None, False

        db_linked_chat_edge = LinkedChat.find_by_key(LinkedChat.get_key(chat, linked_chat))
        successful = False

        if not db_linked_chat_edge:
            db_linked_chat_edge, successful = LinkedChat.create(LinkedChat.parse_from_chat_and_chat(chat, linked_chat))

        return db_linked_chat_edge, successful

    def update_or_create_audio(
        self,
        message: "pyrogram.types.Message",
    ) -> Optional["Audio"]:
        if message is None or (message.audio is None and message.document is None):
            return None

        audio = Audio.find_by_key(Audio.get_key(message))
        if audio:
            # audio exists in the database, update the audio
            audio, successful = Audio.update(audio, Audio.parse_from_message(message, audio.download_url))
        else:
            # audio does not exist in the database, create it
            audio = self.create_audio(message)

        return audio

    def get_or_create_audio(
        self,
        message: "pyrogram.types.Message",
    ) -> Optional["Audio"]:
        if message is None or (message.audio is None and message.document is None):
            return None

        audio = Audio.find_by_key(Audio.get_key(message))
        if not audio:
            # audio does not exist in the database, create it
            audio = self.create_audio(message)

        return audio

    def create_audio(
        self,
        message: "pyrogram.types.Message",
    ) -> Optional["Audio"]:
        if message is None or (message.audio is None and message.document is None):
            return None

        audio, successful = Audio.create(Audio.parse_from_message(message))
        if audio and successful:
            chat = self.get_or_create_chat(message.chat)

            sent_by, successful = SentBy.create(SentBy.parse_from_audio_and_chat(audio, chat))

            db_file = File.find_by_key(audio.file_unique_id)
            if db_file:
                file_ref, successful = FileRef.create(FileRef.parse_from_audio_and_file(audio, db_file))
            else:
                file, successful = File.create(File.parse_from_audio(message.audio))
                if file and successful:
                    if not FileRef._db.find({"_from": audio.id, "_to": file.id}):  # todo: fix me
                        file_ref, successful = FileRef.create(FileRef.parse_from_audio_and_file(audio, file))
                    else:
                        pass
                else:
                    pass

        return audio

    def get_user_by_user_id(
        self,
        user_id,
    ) -> Optional["User"]:
        if user_id is None:
            return None
        return User.find_by_key(str(user_id))

    def get_or_create_query_keyword(
        self,
        query: str,
    ) -> Optional[QueryKeyword]:
        if query is None:
            return None

        query_keyword = QueryKeyword.find_by_key(QueryKeyword.get_key(query))
        if not query_keyword:
            query_keyword, successful = QueryKeyword.create(QueryKeyword.parse_from_query(query))

        return query_keyword

    def get_or_create_inline_query(
        self,
        bot_id: int,
        inline_query: "pyrogram.types.InlineQuery",
        inline_query_type: InlineQueryType,
        query_date: int,
        query_metadata: dict,
        audio_docs: List["elasticsearch_db.Audio"],
        db_audios: List["Audio"],
        next_offset: Optional[str],
    ) -> Tuple[Optional[InlineQuery], Optional[List[Hit]]]:
        if (
            bot_id is None
            or inline_query is None
            or query_date is None
            or query_metadata is None
            or audio_docs is None
            or db_audios is None
        ):
            return None, None
        db_bot = self.get_user_by_user_id(bot_id)
        db_from_user = self.get_user_by_user_id(inline_query.from_user.id)
        db_inline_query = None

        # todo: this is a temporary solution
        hits = []

        if db_bot and db_from_user:
            db_inline_query = InlineQuery.find_by_key(
                InlineQuery.get_key(
                    db_bot,
                    inline_query,
                )
            )
            if not db_inline_query:
                db_inline_query, successful = InlineQuery.create(
                    InlineQuery.parse_from_inline_query(
                        db_bot,
                        inline_query,
                        inline_query_type,
                        query_date,
                        query_metadata,
                        next_offset,
                    )
                )

            if db_inline_query:
                db_query_keyword = self.get_or_create_query_keyword(inline_query.query)
                db_has_query_keyword, successful = Has.create(
                    Has.parse_from_inline_query_and_query_keyword(
                        db_inline_query,
                        db_query_keyword,
                    )
                )

                db_has_made, successful = HasMade.create(
                    HasMade.parse_from_user_and_inline_query(
                        db_from_user,
                        db_inline_query,
                    )
                )
                db_to_bot_edge, successful = ToBot.create(
                    ToBot.parse_from_inline_query_and_user(
                        db_inline_query,
                        db_bot,
                    )
                )

                for audio_doc, db_audio in zip(audio_docs, db_audios):
                    db_hit, successful = self.get_or_create_hit(audio_doc, db_audio, db_inline_query)

                    if db_hit and successful:
                        hits.append(db_hit)

                        db_has_hit, successful = Has.create(
                            Has.parse_from_inline_query_and_hit(
                                db_inline_query,
                                db_hit,
                            )
                        )
                        db_has_audio, successful = Has.create(
                            Has.parse_from_hit_and_audio(
                                db_hit,
                                db_audio,
                            )
                        )
        return db_inline_query, hits

    def get_or_create_hit(
        self,
        audio_doc: elasticsearch_db.Audio,
        db_audio: Audio,
        db_inline_query: InlineQuery,
    ) -> Tuple[Optional[Hit], bool]:
        successful = False

        db_hit = Hit.find_by_key(
            Hit.get_key(
                db_inline_query,
                db_audio,
            )
        )
        if not db_hit:
            db_hit, successful = Hit.create(
                Hit.parse_from_inline_query_and_audio(
                    db_inline_query,
                    db_audio,
                    audio_doc.search_metadata,
                )
            )
        return db_hit, successful

    def get_or_create_query(
        self,
        bot_id: int,
        from_user: "pyrogram.types.User",
        query: "str",
        query_date: int,
        query_metadata: dict,
        audio_docs: List["elasticsearch_db.Audio"],
        db_audios: List["Audio"],
    ) -> Optional[Tuple[Query, List[Hit]]]:
        if (
            bot_id is None
            or from_user is None
            or query is None
            or query_date is None
            or query_metadata is None
            or audio_docs is None
            or db_audios is None
        ):
            return None

        # todo: this is a temporary solution
        hits = []

        db_bot = self.get_user_by_user_id(bot_id)
        db_from_user = self.get_user_by_user_id(from_user.id)
        db_query = None

        if db_bot and db_from_user:
            db_query = Query.find_by_key(
                Query.get_key(
                    db_bot,
                    db_from_user,
                    query_date,
                )
            )
            if not db_query:
                db_query, successful = Query.create(
                    Query.parse_from_query(
                        db_bot,
                        db_from_user,
                        query,
                        query_date,
                        query_metadata,
                    )
                )

            if db_query:
                db_query_keyword = self.get_or_create_query_keyword(query)
                db_has_query_keyword, successful = Has.create(
                    Has.parse_from_query_and_query_keyword(
                        db_query,
                        db_query_keyword,
                    )
                )

                db_has_made, successful = HasMade.create(
                    HasMade.parse_from_user_and_query(
                        db_from_user,
                        db_query,
                    )
                )
                db_to_bot_edge, successful = ToBot.create(
                    ToBot.parse_from_query_and_user(
                        db_query,
                        db_bot,
                    )
                )

                for audio_doc, db_audio in zip(audio_docs, db_audios):
                    db_hit, successful = Hit.create(
                        Hit.parse_from_query_and_audio(
                            db_query,
                            db_audio,
                            audio_doc.search_metadata,
                        )
                    )
                    if db_hit and successful:
                        hits.append(db_hit)

                        db_has_hit, successful = Has.create(
                            Has.parse_from_query_and_hit(
                                db_query,
                                db_hit,
                            )
                        )
                        db_has_audio, successful = Has.create(
                            Has.parse_from_hit_and_audio(
                                db_hit,
                                db_audio,
                            )
                        )
        return db_query, hits

    def get_chat_by_chat_id(
        self,
        chat_id,
    ) -> Optional[Chat]:
        if chat_id is None:
            return None

        return Chat.find_by_key(str(chat_id))

    def get_chat_by_username(
        self,
        username,
    ) -> Optional[Chat]:
        if username is None:
            return None

        # todo: fix this
        cursor = Chat._db.find({"username": username.lower()})
        if cursor and len(cursor):
            return Chat.parse_from_graph(cursor.pop())
        else:
            return None

    def get_audio_by_key(
        self,
        id: str,
    ) -> Optional[Audio]:
        if id is None:
            return None

        return Audio.find_by_key(id)

    def get_playlist_by_key(
        self,
        key: str,
    ) -> Optional[Playlist]:
        if key is None:
            return None

        return Playlist.find_by_key(key)

    def get_user_playlist_by_title(
        self,
        db_user: "User",
        title: str,
    ) -> Optional[Playlist]:
        if db_user is None or title is None:
            return None

        query_template = Template(
            'for v_pl in 1..1 outbound "$user_id" graph "tase" options {order:"dfs", edgeCollections:['
            '"$has_edge_name"], '
            'vertexCollections:["playlists"]}'
            '  filter v_pl.title == "$title"'
            "  return v_pl",
        )
        query = query_template.substitute(
            {
                "user_id": db_user.id,
                "title": title,
                "has_edge_name": Has._collection_edge_name,
            }
        )

        cursor = self.db.aql.execute(
            query,
            count=True,
        )
        if cursor and len(cursor):
            return Playlist.parse_from_graph(vertex=cursor.pop())
        else:
            return None

    def get_user_favorite_playlist(
        self,
        db_user: "User",
    ) -> Optional[Playlist]:
        if db_user is None:
            return None

        return self.get_user_playlist_by_title(
            db_user,
            "Favorite",
        )

    def get_or_create_user_favorite_playlist(
        self,
        db_user: "User",
    ) -> Optional[Playlist]:
        if db_user is None:
            return None

        db_playlist = self.get_user_playlist_by_title(
            db_user,
            "Favorite",
        )
        if db_playlist is None:
            db_playlist, _ = self.create_user_favorite_playlist(db_user)

        return db_playlist

    def create_user_favorite_playlist(
        self,
        db_user: "User",
    ) -> Optional[Tuple["User", bool]]:
        if db_user is None:
            return None

        return self.create_playlist(
            db_user,
            title="Favorite",
            description="Favorite Playlist",
            is_favorite=True,
        )

    def create_playlist(
        self,
        db_user: "User",
        title: str,
        description: str = None,
        is_favorite: bool = False,
    ) -> Optional[Tuple["Playlist", bool]]:
        if db_user is None or title is None:
            return None

        v = Playlist(
            key=Playlist.generate_token_urlsafe(10),
            title=title,
            is_favorite=is_favorite,
            rank=1 if is_favorite else 2,
        )
        if description is not None:
            v.description = description

        playlist, successful = Playlist.create(v)

        if playlist and successful:
            db_has = Has.parse_from_user_and_playlist(
                db_user,
                playlist,
            )
            if db_has is not None and not Has.find_by_key(db_has.key):
                has_edge, _ = Has.create(db_has)
                created = True
                successful = True
            else:
                created = False
                successful = True

        return playlist, successful

    def get_or_create_playlist(
        self,
        db_user: "User",
        title: str,
        description: str = None,
        is_favorite: bool = False,
    ) -> Optional["Playlist"]:
        if db_user is None or title is None:
            return None

        db_playlist = self.get_user_playlist_by_title(
            db_user,
            title,
        )
        if db_playlist is None:
            db_playlist, _ = self.create_playlist(
                db_user,
                title,
                description,
                is_favorite,
            )

        return db_playlist

    def get_or_create_download_from_chosen_inline_query(
        self,
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
        bot_id: int,
    ) -> Optional["Download"]:
        if chosen_inline_result is None or bot_id is None:
            return None

        inline_query_id, audio_key = chosen_inline_result.result_id.split("->")
        cursor = InlineQuery._db.find(  # todo: fix me
            {
                "query_id": inline_query_id,
                "query": chosen_inline_result.query,
            }
        )
        if cursor and len(cursor):
            db_inline_query = InlineQuery.parse_from_graph(cursor.pop())
        else:
            db_inline_query = None

        if db_inline_query:
            db_audio = self.get_audio_by_key(audio_key)
            db_bot = self.get_user_by_user_id(bot_id)
            db_user = self.get_user_by_user_id(chosen_inline_result.from_user.id)
            if db_bot and db_audio and db_user:
                # todo: fix this
                d = Download()
                d.key = str(uuid.uuid4())
                db_download, successful = Download.create(d)
                if db_download:
                    db_downloaded_edge, successful = Downloaded.create(
                        Downloaded.parse_from_user_and_download(
                            db_user,
                            db_download,
                        )
                    )
                    db_from_bot = FromBot.create(
                        FromBot.parse_from_download_and_user(
                            db_download,
                            db_bot,
                        )
                    )
                    db_downloaded_audio = Has.create(
                        Has.parse_from_download_and_audio(
                            db_download,
                            db_audio,
                        )
                    )
                    db_hit = Hit.find_by_key(
                        Hit.get_key(
                            db_inline_query,
                            db_audio,
                        )
                    )
                    if db_hit:
                        db_from_hit_edge, successful = FromHit.create(
                            FromHit.parse_from_download_and_hit(
                                db_download,
                                db_hit,
                            )
                        )
                    else:
                        # todo: what then?
                        pass

                    return db_download
                else:
                    return None
            else:
                return None
        else:
            return None

    def get_or_create_download_from_hit_download_url(
        self,
        download_url: "str",
        from_user: "User",
        bot_id: int,
    ) -> Optional["Download"]:
        if download_url is None or bot_id is None or from_user is None:
            return None

        db_hit = self.get_hit_by_download_url(download_url)
        db_audio = self.get_audio_from_hit(db_hit)
        db_bot = self.get_user_by_user_id(bot_id)
        db_user = from_user
        if db_hit and db_bot and db_audio and db_user:
            # todo: fix this
            d = Download()
            d.key = str(uuid.uuid4())
            db_download, successful = Download.create(d)
            if db_download:
                db_downloaded_edge, successful = Downloaded.create(
                    Downloaded.parse_from_user_and_download(
                        db_user,
                        db_download,
                    )
                )
                db_from_bot = FromBot.create(
                    FromBot.parse_from_download_and_user(
                        db_download,
                        db_bot,
                    )
                )
                db_downloaded_audio = Has.create(
                    Has.parse_from_download_and_audio(
                        db_download,
                        db_audio,
                    )
                )
                db_from_hit_edge, successful = FromHit.create(
                    FromHit.parse_from_download_and_hit(
                        db_download,
                        db_hit,
                    )
                )
                return db_download
            else:
                return None
        else:
            return None

    def get_hit_by_download_url(
        self,
        download_url: str,
    ) -> Optional[Hit]:
        if download_url is None:
            return None

        return Hit.find_by_download_url(download_url)

    def get_audio_by_download_url(
        self,
        download_url: str,
    ) -> Optional[Audio]:
        if download_url is None:
            return None

        return Audio.find_by_download_url(download_url)

    def get_audio_from_hit(
        self,
        hit: Hit,
    ) -> Optional[Audio]:
        if hit is None:
            return None

        query_template = Template(
            'for v_audio in 1..1 outbound "$hit_id" graph "tase" options {order:"dfs",edgeCollections:['
            '"$has_edge_name"], vertexCollections:["audios"]}'
            "  return v_audio",
        )
        query = query_template.substitute(
            {
                "hit_id": hit.id,
                "has_edge_name": Has._collection_edge_name,
            }
        )

        cursor = self.db.aql.execute(
            query,
            count=True,
        )
        if cursor and len(cursor):
            return Audio.parse_from_graph(vertex=cursor.pop())
        else:
            return None

    def update_user_chosen_language(
        self,
        user: User,
        lang_code: str,
    ):
        if user is None or lang_code is None:
            return

        user.update_chosen_language(lang_code)

    def get_user_download_user_history(
        self,
        db_from_user: User,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[Audio]]:
        if db_from_user is None:
            return None

        # todo: fix this
        query_template = Template(
            'for v in 1..1 any "$user_id" graph "tase" options {order : "dfs", edgeCollections : ["downloaded"], vertexCollections : ["downloads"]}'
            "   sort v.created_at DESC"
            '   for v_aud in 1..1 any v graph "tase" options {order : "dfs", edgeCollections : ["has"], vertexCollections : ["audios"]}'
            "       collect aggregate audios = unique(v_aud)"
            "       for aud in audios"
            "           limit $offset, $limit"
            "           return aud"
        )
        query = query_template.substitute(
            {
                "offset": offset,
                "limit": limit,
                "user_id": db_from_user.id,
            }
        )
        results = []
        for aud in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Audio.parse_from_graph(aud))

        return results

    def get_user_playlists(
        self,
        db_from_user: User,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[Playlist]]:
        if db_from_user is None:
            return None

        # todo: fix this
        query_template = Template(
            'for v in 1..1 any "$user_id" graph "tase" options {order : "dfs", edgeCollections : ["has"], vertexCollections : ["playlists"]}'
            "   sort v.rank , v.modified DESC"
            "   limit $offset, $limit"
            "   return v"
        )
        query = query_template.substitute(
            {
                "offset": offset,
                "limit": limit,
                "user_id": db_from_user.id,
            }
        )
        results = []
        for pl in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Playlist.parse_from_graph(pl))

        # todo: remove None objects from the result (it's present when there are warnings)
        # results = [res for res in results if res]

        return results

    def remove_audio_from_playlist(
        self,
        playlist_key: str,
        audio_download_url: str,
        deleted_at: int,
    ) -> bool:
        if playlist_key is None or audio_download_url is None or deleted_at is None:
            return False

        db_audio = self.get_audio_by_download_url(audio_download_url)
        db_playlist = self.get_playlist_by_key(playlist_key)
        if db_audio is None or db_playlist is None:
            return False

        has_edge = Has.find_by_key(
            Has.parse_from_playlist_and_audio(
                db_playlist,
                db_audio,
            ).key
        )
        if has_edge is None:
            return False

        deleted = Has.delete_edge(has_edge)
        if not deleted:
            return False
        else:
            had_edge = Had.parse_from_playlist_and_audio(
                db_playlist,
                db_audio,
                deleted_at,
                has_edge,
            )
            if had_edge:
                had_edge, successful = Had.create(had_edge)
                if had_edge and successful:
                    return True
                else:
                    return False

        return False

    def add_audio_to_playlist(
        self,
        playlist_key: str,
        audio_download_url: str,
    ) -> Tuple[bool, bool]:
        if playlist_key is None or audio_download_url is None:
            return False, False

        created = False
        successful = False

        db_audio = self.get_audio_by_download_url(audio_download_url)
        db_playlist = self.get_playlist_by_key(playlist_key)

        if db_audio and db_playlist:
            if db_audio.title is not None:
                # todo: fix me
                # if title is empty, audio cannot be used in inline mode

                edge = Has.parse_from_playlist_and_audio(
                    db_playlist,
                    db_audio,
                )
                if edge is not None and not Has.find_by_key(edge.key):
                    has_edge, _ = Has.create(edge)
                    created = True
                    successful = True
                else:
                    created = False
                    successful = True

        return created, successful

    def get_playlist_audios(
        self,
        db_from_user: User,
        playlist_key: str,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[Audio]]:
        if db_from_user is None or playlist_key is None or offset is None or limit is None:
            return None

        db_playlist = Playlist.find_by_key(playlist_key)

        if db_playlist is None:
            return None

        # todo: fix this
        query_template = Template(
            'for v,e in 1..1 outbound "$playlist_id" graph "tase" options {order : "dfs", edgeCollections : ["$has"], '
            'vertexCollections : ["$audios"]}'
            "   sort e.created_at DESC"
            "   limit $offset, $limit"
            "   return v"
        )
        query = query_template.substitute(
            {
                "playlist_id": db_playlist.id,
                "offset": offset,
                "limit": limit,
                "audios": Audio._vertex_name,
                "has": Has._collection_edge_name,
            }
        )

        results = []
        for aud in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Audio.parse_from_graph(aud))
        return results

    def get_audio_playlists(
        self,
        db_from_user: User,
        audio_download_url: str,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[Playlist]]:
        if db_from_user is None or audio_download_url is None or offset is None or limit is None:
            return None

        db_audio = self.get_audio_by_download_url(audio_download_url)

        if db_audio is None:
            return None

        # todo: fix this
        query_template = Template(
            'for v,e in 1..1 inbound "$audio_id" graph "tase" options {order : "dfs", edgeCollections : ["$has"], '
            'vertexCollections : ["$playlists"]}'
            "   sort v.rank ASC, e.created_at DESC"
            "   limit $offset, $limit"
            "   return v"
        )
        query = query_template.substitute(
            {
                "audio_id": db_audio.id,
                "offset": offset,
                "limit": limit,
                "playlists": Playlist._vertex_name,
                "has": Has._collection_edge_name,
            }
        )

        results = []
        for aud in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Playlist.parse_from_graph(aud))
        return results

    def get_audios_from_keys(
        self,
        audio_keys: List[str],
    ) -> Optional[List["Audio"]]:
        if audio_keys is None or not len(audio_keys):
            return None

        query_template = Template('return document("$audios",$audio_keys)')
        query = query_template.substitute(
            {
                "audios": Audio._vertex_name,
                "audio_keys": audio_keys,
            }
        )

        results = []
        try:

            cursor = self.aql.execute(
                query,
                count=True,
            )
            if cursor and len(cursor):
                audios_raw = cursor.pop()
                for audio_raw in audios_raw:
                    results.append(Audio.parse_from_graph(audio_raw))
        except Exception as e:
            pass

        return results

    def update_playlist_title(
        self,
        playlist_key: str,
        title: str,
    ):
        if playlist_key is None or title is None:
            return

        db_playlist = Playlist.find_by_key(playlist_key)
        if db_playlist is None:
            return
        else:
            db_playlist.update_title(title)

    def update_playlist_description(
        self,
        playlist_key: str,
        description: str,
    ):
        if playlist_key is None or description is None:
            return

        db_playlist = Playlist.find_by_key(playlist_key)
        if db_playlist is None:
            return
        else:
            db_playlist.update_description(description)

    def delete_playlist(
        self,
        db_from_user: User,
        playlist_key: str,
        deleted_at: int,
    ):
        if db_from_user is None and playlist_key is None or deleted_at is None:
            return False

        db_playlist = Playlist.find_by_key(playlist_key)
        if db_playlist is None:
            return False
        else:
            has_edge = Has.find_by_key(
                Has.parse_from_user_and_playlist(
                    db_from_user,
                    db_playlist,
                ).key
            )

            if has_edge is None:
                return False

            deleted = Has.delete_edge(has_edge)
            if not deleted:
                return False
            else:
                had_edge = Had.parse_from_user_and_playlist(
                    db_from_user,
                    db_playlist,
                    deleted_at,
                    has_edge,
                )
                if had_edge:
                    had_edge, successful = Had.create(had_edge)
                    if had_edge and successful:
                        return True
                    else:
                        return False
            return False

    def get_chats_sorted_by_audio_indexer_score(self) -> List[Chat]:
        """
        Gets the list of chats sorted by their audio importance score in a descending order

        Returns
        -------
        A list of Chat objects
        """
        query_template = Template(
            "for chat in chats"
            "   filter chat.chat_type==$chat_type"
            "   sort chat.audio_indexer_metadata.score desc, chat.member_count desc"
            "   return chat"
        )
        # todo: only public channels can be indexed for now. add support supergroups
        query = query_template.substitute({"chat_type": ChatType.CHANNEL.value})

        # fixme: use a generator instead of returning all results
        results = []
        for aud in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Chat.parse_from_graph(aud))
        return results

    def get_chats_sorted_by_username_extractor_score(self) -> List[Chat]:
        """
        Gets the list of chats sorted by their username extractor importance score in a descending order

        Returns
        -------
        A list of Chat objects
        """
        query_template = Template(
            "for chat in chats"
            "   filter chat.chat_type==$chat_type"
            "   sort chat.username_extractor_metadata.score desc, chat.member_count desc"
            "   return chat"
        )

        # todo: only public channels can be indexed for now. add support for other types if necessary
        query = query_template.substitute({"chat_type": ChatType.CHANNEL.value})

        # fixme: use a generator instead of returning all results
        results = []
        for aud in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Chat.parse_from_graph(aud))
        return results

    def get_unchecked_usernames(self) -> List[Username]:
        """
        Gets the list of usernames sorted by their creation date in a ascending order

        Returns
        -------
        A list of Username objects
        """
        now = get_timestamp() - 60
        query_template = Template(
            "for username in usernames"
            "   filter username.is_checked == false and username.created_at < $now"
            "   sort username.created_at desc"
            "   return username"
        )

        query = query_template.substitute(
            {
                "now": now,
            }
        )

        # fixme: use a generator instead of returning all results
        results = []
        for username in self.aql.execute(
            query,
            count=True,
        ):
            results.append(Username.parse_from_graph(username))
        return results

    def update_audio_indexer_metadata(
        self,
        chat: Chat,
        metadata: AudioIndexerMetadata,
    ) -> bool:
        """
        Updates audio indexer offset attributes of the chat after being indexed

        Parameters
        ----------
        chat : Chat
            Chat to update its metadata
        metadata : AudioIndexerMetadata
            New offset id

        Returns
        -------
        Whether the update was successful or not
        """
        if not all((chat, metadata)):
            return False

        query_template = Template(
            "for chat in chats"
            "   filter chat._key=='$key'"
            "   update chat with {"
            "       audio_indexer_metadata: $metadata"
            "   } in chats options {mergeObjects: true}"
            "   return chat"
        )
        query = query_template.substitute(
            {
                "key": chat.key,
                "metadata": metadata.dict(),
            }
        )

        cursor = self.aql.execute(
            query,
            count=True,
        )

        return True if len(cursor) else False

    def update_username_extractor_metadata(
        self,
        chat: Chat,
        metadata: UsernameExtractorMetadata,
        run_depth: int = 1,
    ) -> bool:
        """
        Updates username extractor metadata of the chat after being indexed

        Parameters
        ----------
        chat : Chat
            Chat to update its metadata
        metadata : UsernameExtractorMetadata
            Updated metadata
        run_depth : int
            Depth of running the function. stop and return False after 10 runs.

        Returns
        -------
        Whether the update was successful or not
        """
        if not all((chat, metadata)):
            return False

        updated_metadata = chat.username_extractor_metadata.update_metadata(metadata)
        updated_metadata.update_score()

        query_template = Template(
            "update {_key:'$key', _rev:'$rev'}"
            "   with {"
            "       username_extractor_metadata: $metadata"
            "   } in chats options {mergeObjects: true, ignoreRevs:false}"
            "return NEW"
        )
        query = query_template.substitute(
            {
                "key": chat.key,
                "rev": chat.rev,
                "metadata": updated_metadata.dict(),
            }
        )

        try:
            cursor = self.aql.execute(
                query,
                count=True,
            )
            return True if len(cursor) else False
        except AQLQueryExecuteError as e:
            # 'AQL: conflict, _rev values do not match (while executing)'

            if e.error_code == 1200:
                if run_depth > 20:
                    return False

                db_chat = self.get_chat_by_chat_id(chat.chat_id)
                if db_chat:
                    return self.update_username_extractor_metadata(
                        db_chat,
                        metadata,
                        run_depth + 1,
                    )
                else:
                    return False
        except Exception as e:
            logger.exception(e)

        return False

    def update_audio_indexer_score(
        self,
        chat: Chat,
        score: float,
    ) -> bool:
        """
        Updates audio indexer score of a chat

        Parameters
        ----------
        chat : Chat
            Chat to update its score
        score : float
            New score

        Returns
        -------
        Whether the update was successful or not
        """
        if chat is None or score is None:
            return False

        query_template = Template(
            "for chat in chats"
            "   filter chat._key=='$key'"
            "   update chat with {"
            "       audio_indexer_metadata: {score: $score }"
            "   } in chats options {mergeObjects: true}"
            "   return chat"
        )
        query = query_template.substitute(
            {
                "key": chat.key,
                "score": score,
            }
        )

        cursor = self.aql.execute(
            query,
            count=True,
        )

        return True if len(cursor) else False

    def update_username_extractor_score(
        self,
        chat: Chat,
        score: float,
    ) -> bool:
        """
        Updates username extractor score of a chat

        Parameters
        ----------
        chat : Chat
            Chat to update its score
        score : float
            New score

        Returns
        -------
        Whether the update was successful or not
        """
        if chat is None or score is None:
            return False

        query_template = Template(
            "for chat in chats"
            "   filter chat._key=='$key'"
            "   update chat with {"
            "       username_extractor_metadata: {score: $score }"
            "   } in chats options {mergeObjects: true}"
            "   return chat"
        )
        query = query_template.substitute(
            {
                "key": chat.key,
                "score": score,
            }
        )

        cursor = self.aql.execute(
            query,
            count=True,
        )

        return True if len(cursor) else False

    def create_username(
        self,
        chat: Chat,
        username: str,
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Tuple[Optional[Username], bool]:
        if (
            chat is None
            or username is None
            or is_direct_mention is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None, False

        db_username, successful = Username.create(Username.parse_from_username(username))

        if not successful:  # todo: is it necessary?
            raise Exception(f"Could not create vertex {Username.__class__.__name__}")

        return db_username, successful

    def get_or_create_username(
        self,
        chat: Chat,
        username: str,
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Tuple[Optional[Username], bool]:
        if (
            chat is None
            or username is None
            or is_direct_mention is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None, False

        db_username = Username.find_by_key(Username.get_key(username))
        created = False

        if not db_username:
            # username does not exist in the database, create it
            db_username, successful = self.create_username(
                chat,
                username,
                is_direct_mention,
                mentioned_at,
                mention_source,
                mention_start_index,
                from_message_id,
            )
            created = True

        if chat.username is not None:
            if chat.username.lower() != username.lower():
                # this is not a self-mention edge, so it should be created
                create_mention_edge = True
            else:
                # don't create self-mention edges
                create_mention_edge = False
        else:
            # the username is mentioned from a chat that doesn't have a username itself
            create_mention_edge = True

        if create_mention_edge:
            self.get_or_create_mentions_edge(
                chat,
                db_username,
                from_message_id,
                is_direct_mention,
                mention_source,
                mention_start_index,
                mentioned_at,
            )

        return db_username, created

    def get_or_create_mentions_edge(
        self,
        from_: Union[Chat, Username],
        to_: Union[Chat, Username],
        from_message_id: int,
        is_direct_mention: bool,
        mention_source: MentionSource,
        mention_start_index: int,
        mentioned_at: int,
    ) -> Tuple[Mentions, bool]:
        created = False
        # successful = False

        db_mentions = Mentions.find_by_key(
            Mentions.get_key(
                from_,
                to_,
                mentioned_at,
                mention_source,
                mention_start_index,
                from_message_id,
            )
        )
        if db_mentions is None:
            db_mentions, successful = Mentions.create(
                Mentions.parse(
                    from_,
                    to_,
                    is_direct_mention,
                    mentioned_at,
                    mention_source,
                    mention_start_index,
                    from_message_id,
                )
            )
            created = successful

        return db_mentions, created

    def get_username(
        self,
        username: str,
    ) -> Optional[Username]:
        """
        Get a Username by the key from the provided username

        Parameters
        ----------
        username : str
            username to get the key from

        Returns
        -------
        A Username if it exists otherwise returns None
        """
        if username is None:
            return None

        return Username.find_by_key(Username.get_key(username))

    def update_mentions_edges_from_chat_to_username(
        self,
        db_username: Username,
    ) -> bool:
        """
        Update mentions edges based on the data provided from `db_username` parameter

        Parameters
        ----------
        db_username : Username
            Username object to get data from for this update
        Returns
        -------
        bool
            Whether this update was successful or not

        """
        if db_username is None or not isinstance(db_username, Username):
            return False

        query_template = Template(
            "for v,e in 1..1 inbound '$to' graph 'tase' options {order:'dfs', edgeCollections:['mentions'], vertexCollections:['chats']}"
            "   filter e.is_checked != $is_checked"
            "   sort e.created_at ASC"
            "   update e with {"
            "       is_checked:$is_checked, checked_at:$checked_at"
            "   } in mentions options {mergeObjects: true}"
            "   return NEW"
        )
        query = query_template.substitute(
            {
                "to": db_username.id,
                "is_checked": db_username.is_checked,
                "checked_at": db_username.checked_at,
            }
        )

        try:
            cursor = self.aql.execute(
                query,
                count=True,
            )
            return True if len(cursor) else False
        except Exception as e:
            logger.exception(e)
            return False

    def create_mentions_edges_after_username_check(
        self,
        db_mentioned_chat: Chat,
        db_username: Username,
    ) -> None:
        """
        Update mentions edges based on the data provided from `db_username` parameter and create new edges from
        `db_username` to `db_chat` and from `db_chat` to `db_mentioned_chat`.

        Parameters
        ----------
        db_mentioned_chat: Chat
            Mentioned chat
        db_username : Username
            Username object to get data from for this update
        Returns
        -------
        None
            This method does not return anything

        """
        if db_mentioned_chat is None or db_username is None or db_username.checked_at is None:
            return

        query_template = Template(
            "for v,e in 1..1 inbound '$to' graph 'tase' options {order:'dfs', edgeCollections:['mentions'], vertexCollections:['chats']}"
            "   filter e.is_checked == false"
            "   sort e.created_at ASC"
            "   update e with {"
            "       is_checked:true, checked_at:$checked_at"
            "   } in mentions options {mergeObjects: true}"
            "   return {chat:v, mention_:NEW}"
        )
        query = query_template.substitute(
            {
                "to": db_username.id,
                "checked_at": db_username.checked_at,
            }
        )
        for obj_dict in self.aql.execute(
            query,
            count=True,
        ):
            db_mentions_edge = Mentions.parse_from_graph(obj_dict["mention_"])
            db_source_chat = Chat.parse_from_graph(obj_dict["chat"])

            if db_mentions_edge and db_source_chat:
                if (
                    not db_source_chat.username
                    or not db_mentioned_chat.username
                    or db_source_chat.username != db_mentioned_chat.username
                ):
                    self.get_or_create_mentions_edge(
                        db_username,
                        db_mentioned_chat,
                        db_mentions_edge.from_message_id,
                        db_mentions_edge.is_direct_mention,
                        db_mentions_edge.mention_source,
                        db_mentions_edge.mention_start_index,
                        db_mentions_edge.mentioned_at,
                    )
                    self.get_or_create_mentions_edge(
                        db_source_chat,
                        db_mentioned_chat,
                        db_mentions_edge.from_message_id,
                        db_mentions_edge.is_direct_mention,
                        db_mentions_edge.mention_source,
                        db_mentions_edge.mention_start_index,
                        db_mentions_edge.mentioned_at,
                    )

                    metadata = db_source_chat.username_extractor_metadata.copy()
                    metadata.reset_counters()

                    if db_mentions_edge.is_direct_mention:
                        metadata.direct_valid_mention_count += 1

                        if db_mentioned_chat.chat_type == ChatType.BOT:
                            metadata.direct_valid_bot_mention_count += 1
                        elif db_mentioned_chat.chat_type == ChatType.PRIVATE:
                            metadata.direct_valid_user_mention_count += 1
                        elif db_mentioned_chat.chat_type == ChatType.SUPERGROUP:
                            metadata.direct_valid_supergroup_mention_count += 1
                        elif db_mentioned_chat.chat_type == ChatType.CHANNEL:
                            metadata.direct_valid_channel_mention_count += 1

                    else:
                        metadata.indirect_valid_mention_count += 1

                        if db_mentioned_chat.chat_type == ChatType.BOT:
                            metadata.indirect_valid_bot_mention_count += 1
                        elif db_mentioned_chat.chat_type == ChatType.PRIVATE:
                            metadata.indirect_valid_user_mention_count += 1
                        elif db_mentioned_chat.chat_type == ChatType.SUPERGROUP:
                            metadata.indirect_valid_supergroup_mention_count += 1
                        elif db_mentioned_chat.chat_type == ChatType.CHANNEL:
                            metadata.indirect_valid_channel_mention_count += 1

                    successful = self.update_username_extractor_metadata(db_source_chat, metadata)
                    if not successful:
                        # todo: the update wasn't successful, uncheck the edge so it could be updated later
                        db_mentions_edge.check(False, None)
                        pass

                else:
                    # do not create self-loop mentions for chats
                    pass
            else:
                pass
