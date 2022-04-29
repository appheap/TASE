from typing import Optional, List

import pyrogram
from arango import ArangoClient
from arango.collection import VertexCollection, EdgeCollection
from arango.database import StandardDatabase
from arango.graph import Graph

from . import elasticsearch_db
from .graph_models.edges import FileRef, SenderChat, LinkedChat, Creator, MemberOf, edges, FromUser, ToBot, Hit
from .graph_models.vertices import Audio, Chat, File, User, InlineQuery, vertices, Query


class GraphDatabase:
    arango_client: 'ArangoClient'
    db: 'StandardDatabase'
    graph: 'Graph'

    audios: 'VertexCollection'
    chats: 'VertexCollection'
    downloads: 'VertexCollection'
    files: 'VertexCollection'
    inline_queries: 'VertexCollection'
    playlists: 'VertexCollection'
    queries: 'VertexCollection'
    users: 'VertexCollection'

    archived_audio: 'EdgeCollection'
    contact_of: 'EdgeCollection'
    creator: 'EdgeCollection'
    downloaded: 'EdgeCollection'
    downloaded_audio: 'EdgeCollection'
    downloaded_from_bot: 'EdgeCollection'
    file_ref: 'EdgeCollection'
    from_user: 'EdgeCollection'
    has_audio: 'EdgeCollection'
    has_playlist: 'EdgeCollection'
    hit: 'EdgeCollection'
    linked_chat: 'EdgeCollection'
    member_of: 'EdgeCollection'
    sender_chat: 'EdgeCollection'
    to_bot: 'EdgeCollection'

    def __init__(
            self,
            graph_db_config: dict,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=graph_db_config.get('db_host_url'))
        sys_db = self.arango_client.db(
            '_system',
            username=graph_db_config.get('db_username'),
            password=graph_db_config.get('db_password')
        )

        if not sys_db.has_database(graph_db_config.get('db_name')):
            sys_db.create_database(
                graph_db_config.get('db_name'),
            )

        self.db = self.arango_client.db(
            graph_db_config.get('db_name'),
            username=graph_db_config.get('db_username'),
            password=graph_db_config.get('db_password')
        )

        if not self.db.has_graph(graph_db_config.get('graph_name')):
            self.graph = self.db.create_graph(graph_db_config.get('graph_name'))
        else:
            self.graph = self.db.graph(graph_db_config.get('graph_name'))

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
                        from_vertex_collections=e_class._from_vertex_collections,
                        to_vertex_collections=e_class._to_vertex_collections,
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
            creator_of, successful = Creator.create(self.creator, Creator.parse_from_chat_and_user(chat, creator))

        if chat and member:
            member_of, successful = MemberOf.create(
                self.member_of,
                MemberOf.parse_from_user_and_chat(user=member, chat=chat)
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

            sender_chat, successful = SenderChat.create(
                self.sender_chat,
                SenderChat.parse_from_audio_and_chat(audio, chat)
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

    def get_or_create_inline_query(
            self,
            bot_id: int,
            inline_query: 'pyrogram.types.InlineQuery'
    ) -> Optional['InlineQuery']:
        if bot_id is None or inline_query is None:
            return None
        db_bot = self.get_user_by_user_id(bot_id)
        db_from_user = self.update_or_create_user(inline_query.from_user)
        db_inline_query = None

        if db_bot and db_from_user:
            db_inline_query = InlineQuery.find_by_key(self.inline_queries, InlineQuery.get_key(db_bot, inline_query))
            if not db_inline_query:
                db_inline_query, successful = InlineQuery.create(
                    self.inline_queries,
                    InlineQuery.parse_from_inline_query(db_bot, inline_query)
                )

            if db_inline_query:
                db_from_user_edge = FromUser.create(
                    self.from_user,
                    FromUser.parse_from_inline_query_and_user(db_inline_query, db_from_user)
                )
                db_to_bot_edge = ToBot.create(
                    self.to_bot,
                    ToBot.parse_from_inline_query_and_user(db_inline_query, db_bot)
                )
        return db_inline_query

    def get_or_create_query(
            self,
            bot_id: int,
            from_user: 'pyrogram.types.User',
            query: 'str',
            query_date: int,
            query_metadata: dict,
            audio_docs: List['elasticsearch_db.Audio']
    ) -> Optional['Query']:
        if bot_id is None or from_user is None or query is None or query_date is None or query_metadata is None or audio_docs is None:
            return None

        db_bot = self.get_user_by_user_id(bot_id)
        db_from_user = self.update_or_create_user(from_user)
        db_query = None

        if db_bot and db_from_user:
            db_query = Query.find_by_key(self.queries, Query.get_key(db_bot, db_from_user, query_date))
            if not db_query:
                db_query, successful = Query.create(
                    self.queries,
                    Query.parse_from_query(db_bot, db_from_user, query, query_date, query_metadata)
                )

            if db_query:
                db_from_user_edge = FromUser.create(
                    self.from_user,
                    FromUser.parse_from_query_and_user(db_query, db_from_user)
                )
                db_to_bot_edge = ToBot.create(
                    self.to_bot,
                    ToBot.parse_from_query_and_user(db_query, db_bot)
                )

                for audio_doc in audio_docs:
                    db_audio = self.get_audio_by_key(audio_doc.id)
                    if db_audio:
                        db_hit = Hit.create(
                            self.hit,
                            Hit.parse_from_query_and_audio(db_query, db_audio, audio_doc.search_metadata)
                        )
        return db_query

    def get_chat_by_chat_id(self, chat_id) -> Optional[Chat]:
        if chat_id is None:
            return None

        return Chat.find_by_key(self.chats, str(chat_id))

    def get_audio_by_key(self, id: str) -> Optional[Audio]:
        if id is None:
            return None

        return Audio.find_by_key(self.audios, id)
