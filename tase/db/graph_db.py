import uuid
from string import Template
from typing import Optional, List, Tuple

import pyrogram
from arango import ArangoClient
from arango.collection import VertexCollection, EdgeCollection
from arango.database import StandardDatabase
from arango.graph import Graph

from . import elasticsearch_db
from .graph_models.edges import FileRef, SentBy, LinkedChat, IsCreatorOf, IsMemberOf, edges, HasMade, ToBot, Has, \
    Downloaded, FromBot, FromHit
from .graph_models.vertices import Audio, Chat, File, User, InlineQuery, vertices, Query, QueryKeyword, Hit, Download, \
    Playlist
from ..configs import ArangoDBConfig


class GraphDatabase:
    arango_client: 'ArangoClient'
    db: 'StandardDatabase'
    graph: 'Graph'

    audios: 'VertexCollection'
    chats: 'VertexCollection'
    downloads: 'VertexCollection'
    files: 'VertexCollection'
    hits: 'VertexCollection'
    inline_queries: 'VertexCollection'
    playlists: 'VertexCollection'
    queries: 'VertexCollection'
    query_keywords: 'VertexCollection'
    users: 'VertexCollection'

    archived_audio: 'EdgeCollection'
    downloaded: 'EdgeCollection'
    file_ref: 'EdgeCollection'
    from_bot: 'EdgeCollection'
    from_hit: 'EdgeCollection'
    has: 'EdgeCollection'
    has_made: 'EdgeCollection'
    is_contact_of: 'EdgeCollection'
    is_creator_of: 'EdgeCollection'
    is_member_of: 'EdgeCollection'
    linked_chat: 'EdgeCollection'
    sent_by: 'EdgeCollection'
    to_bot: 'EdgeCollection'

    def __init__(
            self,
            arangodb_config: ArangoDBConfig,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=arangodb_config.db_host_url)
        sys_db = self.arango_client.db(
            '_system',
            username=arangodb_config.db_username,
            password=arangodb_config.db_password
        )

        if not sys_db.has_database(arangodb_config.db_name):
            sys_db.create_database(
                arangodb_config.db_name,
            )

        self.db = self.arango_client.db(
            arangodb_config.db_name,
            username=arangodb_config.db_username,
            password=arangodb_config.db_password
        )

        self.aql = self.db.aql

        if not self.db.has_graph(arangodb_config.graph_name):
            self.graph = self.db.create_graph(arangodb_config.graph_name)
        else:
            self.graph = self.db.graph(arangodb_config.graph_name)

        for v_class in vertices:
            if not self.graph.has_vertex_collection(v_class._vertex_name):
                setattr(self, v_class._vertex_name, self.graph.create_vertex_collection(v_class._vertex_name))
            else:
                setattr(self, v_class._vertex_name, self.graph.vertex_collection(v_class._vertex_name))

        for e_class in edges:
            if not self.graph.has_edge_definition(e_class._collection_edge_name):
                setattr(
                    self,
                    e_class._collection_edge_name,
                    self.graph.create_edge_definition(
                        edge_collection=e_class._collection_edge_name,
                        from_vertex_collections=e_class.from_vertex_collections(),
                        to_vertex_collections=e_class.to_vertex_collections(),
                    )
                )
            else:
                setattr(
                    self,
                    e_class._collection_edge_name,
                    self.graph.vertex_collection(e_class._collection_edge_name)
                )

    def create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None

        user = None
        if not User.find_by_key(self.users, User.get_key(telegram_user)):
            user, successful = User.create(self.users, User.parse_from_user(telegram_user))
        return user

    def get_or_create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None

        user = User.find_by_key(self.users, User.get_key(telegram_user))
        if not user:
            # user does not exist in the database, create it
            user, successful = User.create(self.users, User.parse_from_user(telegram_user))

        return user

    def update_or_create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None

        user = User.find_by_key(self.users, User.get_key(telegram_user))
        if user:
            # user exists in the database, update it
            user, successful = User.update(self.users, user, User.parse_from_user(telegram_user))
        else:
            # user does not exist in the database, create it
            user, successful = User.create(self.users, User.parse_from_user(telegram_user))

        return user

    def get_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None

        chat = Chat.find_by_key(self.chats, Chat.get_key(telegram_chat))
        if not chat:
            # audio does not exist, create it
            chat = self.create_chat(telegram_chat, creator, member)
        return chat

    def update_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None

        chat = Chat.find_by_key(self.chats, Chat.get_key(telegram_chat))
        if chat:
            # audio exists in the database, update the audio
            chat, successful = Chat.update(self.chats, chat, Chat.parse_from_chat(telegram_chat))
        else:
            # audio does not exist, create it
            chat = self.create_chat(telegram_chat, creator, member)

        return chat

    def create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None

        chat, successful = Chat.create(self.chats, Chat.parse_from_chat(telegram_chat))
        if chat and successful:
            if telegram_chat.linked_chat:
                # todo: fix this
                linked_chat = self.get_or_create_chat(telegram_chat.linked_chat, creator, member)
                if linked_chat:
                    linked_chat_edge, successful = LinkedChat.create(
                        self.linked_chat,
                        LinkedChat.parse_from_chat_and_chat(chat, linked_chat),
                    )
                else:
                    pass
        else:
            pass

        if chat and telegram_chat.is_creator and creator:
            is_creator_of, successful = IsCreatorOf.create(self.is_creator_of,
                                                           IsCreatorOf.parse_from_chat_and_user(chat, creator))

        if chat and member:
            is_member_of, successful = IsMemberOf.create(
                self.is_creator_of,
                IsMemberOf.parse_from_user_and_chat(user=member, chat=chat)
            )

        return chat

    def update_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return None

        audio = Audio.find_by_key(self.audios, Audio.get_key(message))
        if audio:
            # audio exists in the database, update the audio
            audio, successful = Audio.update(self.audios, audio, Audio.parse_from_message(message))
        else:
            # audio does not exist in the database, create it
            audio = self.create_audio(message)

        return audio

    def get_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return None

        audio = Audio.find_by_key(self.audios, Audio.get_key(message))
        if not audio:
            # audio does not exist in the database, create it
            audio = self.create_audio(message)

        return audio

    def create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return None

        audio, successful = Audio.create(self.audios, Audio.parse_from_message(message))
        if audio and successful:
            chat = self.get_or_create_chat(message.chat)

            sent_by, successful = SentBy.create(
                self.sent_by,
                SentBy.parse_from_audio_and_chat(audio, chat)
            )

            if self.files.has(audio.file_unique_id):
                file = File.parse_from_graph(self.files.get(audio.file_unique_id))
                if file:
                    file_ref, successful = FileRef.create(
                        self.file_ref,
                        FileRef.parse_from_audio_and_file(audio, file)
                    )
            else:
                file, successful = File.create(self.files, File.parse_from_audio(message.audio))
                if file and successful:
                    if not self.file_ref.find({'_from': audio.id, '_to': file.id}):
                        file_ref, successful = FileRef.create(
                            self.file_ref,
                            FileRef.parse_from_audio_and_file(audio, file)
                        )
                    else:
                        pass
                else:
                    pass

        return audio

    def get_user_by_user_id(self, user_id) -> Optional['User']:
        if user_id is None:
            return None
        return User.find_by_key(self.users, str(user_id))

    def get_or_create_query_keyword(self, query: str) -> Optional[QueryKeyword]:
        if query is None:
            return None

        query_keyword = QueryKeyword.find_by_key(self.query_keywords, QueryKeyword.get_key(query))
        if not query_keyword:
            query_keyword, successful = QueryKeyword.create(self.query_keywords, QueryKeyword.parse_from_query(query))

        return query_keyword

    def get_or_create_inline_query(
            self,
            bot_id: int,
            inline_query: 'pyrogram.types.InlineQuery',
            query_date: int,
            query_metadata: dict,
            audio_docs: List['elasticsearch_db.Audio'],
            next_offset: Optional[str],
    ) -> Optional[Tuple[InlineQuery, List[Hit]]]:
        if bot_id is None or inline_query is None or query_date is None or query_metadata is None or audio_docs is None:
            return None
        db_bot = self.get_user_by_user_id(bot_id)
        db_from_user = self.get_user_by_user_id(inline_query.from_user.id)
        db_inline_query = None

        # todo: this is a temporary solution
        hits = []

        if db_bot and db_from_user:
            db_inline_query = InlineQuery.find_by_key(self.inline_queries, InlineQuery.get_key(db_bot, inline_query))
            if not db_inline_query:
                db_inline_query, successful = InlineQuery.create(
                    self.inline_queries,
                    InlineQuery.parse_from_inline_query(db_bot, inline_query, query_date, query_metadata, next_offset)
                )

            if db_inline_query:
                db_query_keyword = self.get_or_create_query_keyword(inline_query.query)
                db_has_query_keyword, successful = Has.create(
                    self.has,
                    Has.parse_from_inline_query_and_query_keyword(
                        db_inline_query,
                        db_query_keyword,
                    )
                )

                db_has_made, successful = HasMade.create(
                    self.has_made,
                    HasMade.parse_from_user_and_inline_query(db_from_user, db_inline_query)
                )
                db_to_bot_edge, successful = ToBot.create(
                    self.to_bot,
                    ToBot.parse_from_inline_query_and_user(db_inline_query, db_bot)
                )

                for audio_doc in audio_docs:
                    db_audio = self.get_audio_by_key(audio_doc.id)
                    if db_audio:
                        db_hit, successful = Hit.create(
                            self.hits,
                            Hit.parse_from_inline_query_and_audio(
                                db_inline_query,
                                db_audio,
                                audio_doc.search_metadata,
                            )
                        )

                        if db_hit and successful:
                            hits.append(db_hit)

                        db_has_hit, successful = Has.create(
                            self.has,
                            Has.parse_from_inline_query_and_hit(db_inline_query, db_hit)
                        )
                        db_has_audio, successful = Has.create(
                            self.has,
                            Has.parse_from_hit_and_audio(db_hit, db_audio),
                        )
        return db_inline_query, hits

    def get_or_create_query(
            self,
            bot_id: int,
            from_user: 'pyrogram.types.User',
            query: 'str',
            query_date: int,
            query_metadata: dict,
            audio_docs: List['elasticsearch_db.Audio']
    ) -> Optional[Tuple[Query, List[Hit]]]:
        if bot_id is None or from_user is None or query is None or query_date is None or query_metadata is None or audio_docs is None:
            return None

        # todo: this is a temporary solution
        hits = []

        db_bot = self.get_user_by_user_id(bot_id)
        db_from_user = self.get_user_by_user_id(from_user.id)
        db_query = None

        if db_bot and db_from_user:
            db_query = Query.find_by_key(self.queries, Query.get_key(db_bot, db_from_user, query_date))
            if not db_query:
                db_query, successful = Query.create(
                    self.queries,
                    Query.parse_from_query(db_bot, db_from_user, query, query_date, query_metadata)
                )

            if db_query:
                db_query_keyword = self.get_or_create_query_keyword(query)
                db_has_query_keyword, successful = Has.create(
                    self.has,
                    Has.parse_from_query_and_query_keyword(
                        db_query,
                        db_query_keyword,
                    )
                )

                db_has_made, successful = HasMade.create(
                    self.has_made,
                    HasMade.parse_from_user_and_query(db_from_user, db_query)
                )
                db_to_bot_edge, successful = ToBot.create(
                    self.to_bot,
                    ToBot.parse_from_query_and_user(db_query, db_bot)
                )

                for audio_doc in audio_docs:
                    db_audio = self.get_audio_by_key(audio_doc.id)
                    if db_audio:
                        db_hit, successful = Hit.create(
                            self.hits,
                            Hit.parse_from_query_and_audio(
                                db_query,
                                db_audio,
                                audio_doc.search_metadata,
                            )
                        )
                        if db_hit and successful:
                            hits.append(db_hit)

                        db_has_hit, successful = Has.create(
                            self.has,
                            Has.parse_from_query_and_hit(db_query, db_hit)
                        )
                        db_has_audio, successful = Has.create(
                            self.has,
                            Has.parse_from_hit_and_audio(db_hit, db_audio),
                        )
        return db_query, hits

    def get_chat_by_chat_id(self, chat_id) -> Optional[Chat]:
        if chat_id is None:
            return None

        return Chat.find_by_key(self.chats, str(chat_id))

    def get_audio_by_key(self, id: str) -> Optional[Audio]:
        if id is None:
            return None

        return Audio.find_by_key(self.audios, id)

    def get_playlist_by_key(self, key: str) -> Optional[Playlist]:
        if key is None:
            return None

        return Playlist.find_by_key(self.playlists, key)

    def get_or_create_download_from_chosen_inline_query(
            self,
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult',
            bot_id: int,
    ) -> Optional['Download']:
        if chosen_inline_result is None or bot_id is None:
            return None

        inline_query_id, audio_key = chosen_inline_result.result_id.split("->")
        cursor = self.inline_queries.find(
            {
                'query_id': inline_query_id,
                'query': chosen_inline_result.query,
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
                db_download, successful = Download.create(
                    self.downloads,
                    d,
                )
                if db_download:
                    db_downloaded_edge, successful = Downloaded.create(
                        self.downloaded,
                        Downloaded.parse_from_user_and_download(db_user, db_download),
                    )
                    db_from_bot = FromBot.create(
                        self.from_bot,
                        FromBot.parse_from_download_and_user(db_download, db_bot),
                    )
                    db_downloaded_audio = Has.create(
                        self.has,
                        Has.parse_from_download_and_audio(db_download, db_audio),
                    )
                    db_hit = Hit.find_by_key(self.hits, Hit.get_key(db_inline_query, db_audio))
                    if db_hit:
                        db_from_hit_edge, successful = FromHit.create(
                            self.from_hit,
                            FromHit.parse_from_download_and_hit(db_download, db_hit)
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

    def get_or_create_download_from_download_link(
            self,
            download_url: 'str',
            from_user: 'User',
            bot_id: int,
    ) -> Optional['Download']:
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
            db_download, successful = Download.create(
                self.downloads,
                d,
            )
            if db_download:
                db_downloaded_edge, successful = Downloaded.create(
                    self.downloaded,
                    Downloaded.parse_from_user_and_download(db_user, db_download),
                )
                db_from_bot = FromBot.create(
                    self.from_bot,
                    FromBot.parse_from_download_and_user(db_download, db_bot),
                )
                db_downloaded_audio = Has.create(
                    self.has,
                    Has.parse_from_download_and_audio(db_download, db_audio),
                )
                db_from_hit_edge, successful = FromHit.create(
                    self.from_hit,
                    FromHit.parse_from_download_and_hit(db_download, db_hit)
                )
                return db_download
            else:
                return None
        else:
            return None

    def get_hit_by_download_url(self, download_url: str) -> Optional[Hit]:
        if download_url is None:
            return None

        return Hit.find_by_download_url(self.hits, download_url)

    def get_audio_from_hit(self, hit: Hit) -> Optional[Audio]:
        if hit is None:
            return None

        cursor = self.db.aql.execute(
            f"for v_audio in 1..1 outbound '{hit.id}' {Has._collection_edge_name}"
            f"  return v_audio",
            count=True,
        )
        if cursor and len(cursor):
            return Audio.parse_from_graph(vertex=cursor.pop())
        else:
            return None

    def update_user_chosen_language(self, user: User, lang_code: str):
        if user is None or lang_code is None:
            return

        user.update_chosen_language(self.users, lang_code)

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
            '   sort v.created_at DESC'
            '   for v_aud in 1..1 any v graph "tase" options {order : "dfs", edgeCollections : ["has"], vertexCollections : ["audios"]}'
            '       collect aggregate audios = unique(v_aud)'
            '       for aud in audios'
            '           limit $offset, $limit'
            '           return aud'
        )
        query = query_template.substitute(
            {
                'offset': offset,
                'limit': limit,
                'user_id': db_from_user.id,
            }
        )
        res = self.aql.execute(
            query,
            count=True,
        )
        results = []
        try:
            while True:
                results.append(Audio.parse_from_graph(res.pop()))
        except Exception as e:
            pass
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
            '   sort v.created_at DESC'
            '   limit $offset, $limit'
            '   return v'
        )
        query = query_template.substitute(
            {
                'offset': offset,
                'limit': limit,
                'user_id': db_from_user.id,
            }
        )
        res = self.aql.execute(
            query,
            count=True,
        )
        results = []
        try:
            while True:
                results.append(Playlist.parse_from_graph(res.pop()))
        except Exception as e:
            pass
        return results

    def add_audio_to_playlist(self, playlist_key: str, hit_download_url: str) -> Tuple[bool, bool]:
        if playlist_key is None or hit_download_url is None:
            return False, False

        created = False
        successful = False

        db_hit = self.get_hit_by_download_url(hit_download_url)
        db_audio = self.get_audio_from_hit(db_hit)
        db_playlist = self.get_playlist_by_key(playlist_key)

        if db_hit and db_audio and db_playlist:
            if db_audio.title is not None:
                # todo: fix me
                # if title is empty, audio cannot be used in inline mode

                edge = Has.parse_from_playlist_and_audio(db_playlist, db_audio)
                if edge is not None and not Has.find_by_key(self.has, edge.key):
                    has_edge = Has.create(self.has, edge)
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

        db_playlist = Playlist.find_by_key(self.playlists, playlist_key)

        # todo: fix this
        query_template = Template(
            'for v,e in 1..1 outbound "$playlist_id" graph "tase" options {order : "dfs", edgeCollections : ["has"], vertexCollections : ["audios"]}'
            '   sort e.created_at DESC'
            '   limit $offset, $limit'
            '   return v'
        )
        query = query_template.substitute(
            {
                'playlist_id': db_playlist.id,
                'offset': offset,
                'limit': limit,
            }
        )
        res = self.aql.execute(
            query,
            count=True,
        )
        results = []
        try:
            while True:
                results.append(Audio.parse_from_graph(res.pop()))
        except Exception as e:
            pass
        return results
