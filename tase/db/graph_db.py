from typing import Optional

import pyrogram
from arango import ArangoClient
from arango.database import StandardDatabase
from arango.graph import Graph

from .graph_models.edges import FileRef, ArchivedAudio, SenderChat, LinkedChat, ContactOf, Creator, Downloaded, \
    DownloadedAudio, DownloadedFromBot, MemberOf, HasAudio, HasPlaylist
from .graph_models.vertices import Audio, Chat, File, User, Download, Playlist
from ..my_logger import logger


class GraphDatabase:
    arango_client: 'ArangoClient'
    db: 'StandardDatabase'
    graph: 'Graph'

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

            self.audios = self.graph.create_vertex_collection(Audio._vertex_name)
            self.chats = self.graph.create_vertex_collection(Chat._vertex_name)
            self.downloads = self.graph.create_vertex_collection(Download._vertex_name)
            self.files = self.graph.create_vertex_collection(File._vertex_name)
            self.playlists = self.graph.create_vertex_collection(Playlist._vertex_name)
            self.users = self.graph.create_vertex_collection(User._vertex_name)

            self.archived_audio = self.graph.create_edge_definition(
                edge_collection=ArchivedAudio._collection_edge_name,
                from_vertex_collections=[Audio._vertex_name],
                to_vertex_collections=[Audio._vertex_name],
            )
            self.contact_of = self.graph.create_edge_definition(
                edge_collection=ContactOf._collection_edge_name,
                from_vertex_collections=[User._vertex_name],
                to_vertex_collections=[User._vertex_name],
            )
            self.creator = self.graph.create_edge_definition(
                edge_collection=Creator._collection_edge_name,
                from_vertex_collections=[Chat._vertex_name],
                to_vertex_collections=[User._vertex_name],
            )
            self.downloaded = self.graph.create_edge_definition(
                edge_collection=Downloaded._collection_edge_name,
                from_vertex_collections=[User._vertex_name],
                to_vertex_collections=[Download._vertex_name],
            )
            self.downloaded_audio = self.graph.create_edge_definition(
                edge_collection=DownloadedAudio._collection_edge_name,
                from_vertex_collections=[Download._vertex_name],
                to_vertex_collections=[Audio._vertex_name],
            )
            self.downloaded_from_bot = self.graph.create_edge_definition(
                edge_collection=DownloadedFromBot._collection_edge_name,
                from_vertex_collections=[Download._vertex_name],
                to_vertex_collections=[User._vertex_name],
            )
            self.file_ref = self.graph.create_edge_definition(
                edge_collection=FileRef._collection_edge_name,
                from_vertex_collections=[Audio._vertex_name],
                to_vertex_collections=[File._vertex_name],
            )
            self.has_audio = self.graph.create_edge_definition(
                edge_collection=HasAudio._collection_edge_name,
                from_vertex_collections=[Playlist._vertex_name],
                to_vertex_collections=[Audio._vertex_name],
            )
            self.has_playlist = self.graph.create_edge_definition(
                edge_collection=HasPlaylist._collection_edge_name,
                from_vertex_collections=[User._vertex_name],
                to_vertex_collections=[Playlist._vertex_name],
            )
            self.linked_chat = self.graph.create_edge_definition(
                edge_collection=LinkedChat._collection_edge_name,
                from_vertex_collections=[Chat._vertex_name],
                to_vertex_collections=[Chat._vertex_name],
            )
            self.member_of = self.graph.create_edge_definition(
                edge_collection=MemberOf._collection_edge_name,
                from_vertex_collections=[User._vertex_name],
                to_vertex_collections=[Chat._vertex_name],
            )
            self.sender_chat = self.graph.create_edge_definition(
                edge_collection=SenderChat._collection_edge_name,
                from_vertex_collections=[Audio._vertex_name],
                to_vertex_collections=[Chat._vertex_name],
            )

        else:
            self.graph = self.db.graph(graph_db_config.get('graph_name'))

            self.files = self.graph.vertex_collection(File._vertex_name)
            self.audios = self.graph.vertex_collection(Audio._vertex_name)
            self.chats = self.graph.vertex_collection(Chat._vertex_name)
            self.users = self.graph.vertex_collection(User._vertex_name)
            self.downloads = self.graph.vertex_collection(Download._vertex_name)

            self.archived_audio = self.graph.edge_collection(ArchivedAudio._collection_edge_name)
            self.contact_of = self.graph.edge_collection(ContactOf._collection_edge_name)
            self.creator = self.graph.edge_collection(Creator._collection_edge_name)
            self.downloaded = self.graph.edge_collection(Downloaded._collection_edge_name)
            self.downloaded_audio = self.graph.edge_collection(DownloadedAudio._collection_edge_name)
            self.downloaded_from_bot = self.graph.edge_collection(DownloadedFromBot._collection_edge_name)
            self.file_ref = self.graph.edge_collection(FileRef._collection_edge_name)
            self.linked_chat = self.graph.edge_collection(LinkedChat._collection_edge_name)
            self.member_of = self.graph.edge_collection(MemberOf._collection_edge_name)
            self.sender_chat = self.graph.edge_collection(SenderChat._collection_edge_name)

    def create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None

        user = None
        if not User.find_by_key(self.users, User.get_key(telegram_user)):
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
