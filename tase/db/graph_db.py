from typing import Optional

import pyrogram
from arango import ArangoClient
from arango.database import StandardDatabase
from arango.graph import Graph

from .graph_models.edges import FileRef, ArchivedAudio, SenderChat, LinkedChat, ContactOf, Creator, Downloaded, \
    DownloadedAudio, DownloadedFromBot, MemberOf
from .graph_models.vertices import Audio, Chat, File, User, Download
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

            self.files = self.graph.create_vertex_collection(File._vertex_name)
            self.audios = self.graph.create_vertex_collection(Audio._vertex_name)
            self.chats = self.graph.create_vertex_collection(Chat._vertex_name)
            self.users = self.graph.create_vertex_collection(User._vertex_name)
            self.downloads = self.graph.create_vertex_collection(Download._vertex_name)

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
        if not self.users.find({'_key': str(telegram_user.id)}):
            user = User.parse_from_user(telegram_user)
            if user:
                user.create(self.users)
            else:
                user = None

        return user

    def update_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None

        cursor = self.chats.find({'_key': Chat.get_key(telegram_chat)})
        if cursor and len(cursor):
            # update the audio
            chat = Chat.parse_from_graph(cursor.pop())
            if chat:
                chat.update(self.chats, Chat.parse_from_chat(telegram_chat))
            else:
                chat = None
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

        if not self.chats.find({'_key': Chat.get_key(telegram_chat)}):
            chat = Chat.parse_from_chat(chat=telegram_chat)
            if chat:
                chat.create(self.chats)

                if telegram_chat.linked_chat:
                    # todo: fix this
                    linked_chat = self.update_or_create_chat(telegram_chat.linked_chat, creator, member)
                    if linked_chat:
                        linked_chat_edge = LinkedChat.parse_from_chat_and_chat(chat, linked_chat)
                        if linked_chat_edge:
                            metadata = self.linked_chat.insert(linked_chat_edge.parse_for_graph())
                            linked_chat_edge.update_from_metadata(metadata)
                        else:
                            pass
                    else:
                        pass
            else:
                pass
        else:
            chat = None

        if chat and telegram_chat.is_creator and creator:
            creator_of = Creator.parse_from_chat_and_user(chat, creator)
            metadata = self.creator.insert(creator_of.parse_for_graph())
            creator_of.update_from_metadata(metadata)

        if chat and member:
            member_of = MemberOf.parse_from_user_and_chat(user=member, chat=chat)
            if member_of:
                metadata = self.member_of.insert(member_of.parse_for_graph())
                member_of.update_from_metadata(metadata)
            else:
                pass

        return chat

    def update_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return None

        cursor = self.audios.find({'_key': Audio.get_key(message)})
        if cursor and len(cursor):
            # update the audio
            audio = Audio.parse_from_graph(cursor.pop())
            if audio:
                audio.update(self.audios, Audio.parse_from_message(message))
            else:
                audio = None
        else:
            # audio does not exist, create it
            audio = self.create_audio(message)

        return audio

    def create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return None

        if not self.audios.has(Audio.get_key(message)):
            audio = Audio.parse_from_message(message)
            if audio:
                audio.create(self.audios)

                chat = self.update_or_create_chat(message.chat)

                sender_chat = SenderChat.parse_from_audio_and_chat(audio, chat)
                if sender_chat:
                    metadata = self.sender_chat.insert(sender_chat.parse_for_graph())
                    sender_chat.update_from_metadata(metadata)
                else:
                    pass

                if self.files.has(audio.file_unique_id):
                    file = File.parse_from_graph(self.files.get(audio.file_unique_id))
                    if file:
                        file_ref = FileRef.parse_from_audio_and_file(audio, file)
                        if file_ref:
                            file_ref_metadata = self.file_ref.insert(file_ref.parse_for_graph())
                            file_ref.update_from_metadata(file_ref_metadata)
                        else:
                            pass
                else:
                    file = File.parse_from_audio(message.audio)
                    if file:
                        file.create(self.files)

                        if not self.file_ref.find({'_from': audio.id, '_to': file.id}):
                            file_ref = FileRef.parse_from_audio_and_file(audio, file)
                            if file_ref:
                                file_ref_metadata = self.file_ref.insert(file_ref.parse_for_graph())
                                file_ref.update_from_metadata(file_ref_metadata)
                        else:
                            pass
                    else:
                        pass

        return None
