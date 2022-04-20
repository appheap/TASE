from typing import Tuple

import pyrogram.types
from elasticsearch import Elasticsearch
import datetime

from arango import ArangoClient

from tase.my_logger import logger


class DatabaseClient:
    _es_client: 'Elasticsearch'
    arango_client: 'ArangoClient'

    def __init__(
            self,
            elasticsearch_config: dict,
            graph_db_config: dict,
    ):

        self._es_client = Elasticsearch(
            elasticsearch_config.get('cluster_url'),
            ca_certs=elasticsearch_config.get('https_certs_url'),
            basic_auth=(
                elasticsearch_config.get('basic_auth_username'),
                elasticsearch_config.get('basic_auth_password'))
        )

        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=graph_db_config.get('db_host_url'))

        # Connect to "test" database as root user.
        db = self.arango_client.db(
            graph_db_config.get('db_name'),
            username=graph_db_config.get('db_username'),
            password=graph_db_config.get('db_password')
        )

        self.db = db

        if not db.has_graph(graph_db_config.get('graph_name')):
            self.graph = db.create_graph(graph_db_config.get('graph_name'))

            self.audios = self.graph.create_vertex_collection('audios')
            self.chats = self.graph.create_vertex_collection('chats')

            self.sent_message = self.graph.create_edge_definition(
                edge_collection='sent_message',
                from_vertex_collections=['chats'],
                to_vertex_collections=['audios'],
            )
            self.edges = self.graph.create_edge_definition(
                edge_collection='is',
                from_vertex_collections=['audios'],
                to_vertex_collections=['audios'],
            )
        else:
            self.graph = db.graph('tase_songs')
            self.audios = self.graph.vertex_collection('audios')
            self.chats = self.graph.vertex_collection('chats')
            self.sent_message = self.graph.edge_collection('sent_message')
            self.edges = self.graph.edge_collection('is')

    def create_audio(self, message: 'pyrogram.types.Message'):
        if message is None or message.audio is None:
            return

        try:
            audio: 'pyrogram.types.Audio' = message.audio
            # self._es_client.create(
            #     index='tase-test-index',
            #     id=audio.file_unique_id,
            #     document={
            #         'chat_id': message.chat.id,
            #         'chat_title': message.chat.title,
            #         'message_id': message.message_id,
            #         'caption': message.caption,
            #         'file_id': audio.file_id,
            #         'file_unique_id': audio.file_unique_id,
            #         'duration': audio.duration,
            #         'performer': audio.performer,
            #         'title': audio.title,
            #         'file_name': audio.file_name,
            #         'mime_type': audio.mime_type,
            #         'file_size': audio.file_size,
            #         'date': audio.date,
            #     }
            # )

            self.process_audio_message(audio, message)
        except Exception as e:
            logger.exception(e)

    def process_audio_message(self, audio: 'pyrogram.types.Audio', message: 'pyrogram.types.Message'):
        key = f'{audio.file_unique_id}{message.chat.id}{message.message_id}'
        if self.audios.find({'_key': key}):
            pass
        else:
            self.insert_audio_arangodb(audio, key, message)
            result = self.audios.find({"file_unique_id": audio.file_unique_id})
            if result and len(result) > 1:
                message_date = datetime.datetime.now().replace(year=2100).timestamp()
                target_audio = None

                audio_nodes = []
                for audio_node in result:
                    audio_nodes.append(audio_node)
                    if audio_node['message_date'] < message_date:
                        message_date = audio_node['message_date']
                        target_audio = audio_node
                for audio_node in audio_nodes:
                    if audio_node['_key'] != target_audio['_key']:
                        self.edges.insert(
                            {
                                '_from': audio_node['_id'],
                                '_to': target_audio['_id']
                            }
                        )
            else:
                self.insert_audio_arangodb(audio, key, message)

    def insert_audio_arangodb(self, audio: 'pyrogram.types.Audio', key, message: 'pyrogram.types.Message'):
        if not self.chats.find({"_key": str(message.chat.id)}):
            self.chats.insert(
                {
                    '_key': str(message.chat.id),
                    'title': message.chat.title,
                    'type': message.chat.type,
                    'is_verified': message.chat.is_verified,
                    'is_restricted': message.chat.is_restricted,
                    'is_scam': message.chat.is_scam,
                    'is_fake': message.chat.is_fake,
                    'is_support': message.chat.is_support,
                    'username': message.chat.username,
                    'first_name': message.chat.first_name,
                    'last_name': message.chat.last_name,
                    'bio': message.chat.bio,
                    'description': message.chat.description,
                    'has_protected_account': message.chat.has_protected_content,
                    'invite_link': message.chat.invite_link,
                    'members_count': message.chat.members_count,
                }
            )

        if not self.audios.has(key):
            self.audios.insert(
                vertex={
                    '_key': key,
                    'message_date': message.date,
                    'chat_id': message.chat.id,
                    'chat_title': message.chat.title,
                    'message_id': message.message_id,
                    'caption': message.caption,
                    'file_id': audio.file_id,
                    'file_unique_id': audio.file_unique_id,
                    'duration': audio.duration,
                    'performer': audio.performer,
                    'title': audio.title,
                    'file_name': audio.file_name,
                    'mime_type': audio.mime_type,
                    'file_size': audio.file_size,
                    'date': audio.date,
                }
            )
            self.sent_message.insert({"_from": f"chats/{message.chat.id}", "_to": f"audios/{key}"})


def extract_audio(obj_dict):
    audio_dict = obj_dict['_source']
    chat_id_str = str(audio_dict['chat_id'])
    if not es.chats.has(str(audio_dict['chat_id'])):
        es.chats.insert(
            {
                '_key': chat_id_str,
                'chat_id': chat_id_str,
                'title': audio_dict['chat_title']
            }
        )
    key = f"{audio_dict['file_unique_id']}{chat_id_str}{str(audio_dict['message_id'])}"
    if not es.audios.has(key):
        es.audios.insert(
            vertex={
                '_key': key,
                'message_date': audio_dict.get('date', None),
                'chat_id': audio_dict.get('chat_id', None),
                'chat_title': audio_dict.get('chat_title', None),
                'message_id': audio_dict.get('message_id', None),
                'caption': audio_dict.get('caption', None),
                'file_id': audio_dict.get('file_id', None),
                'file_unique_id': audio_dict.get('file_unique_id', None),
                'duration': audio_dict.get('duration', None),
                'performer': audio_dict.get('performer', None),
                'title': audio_dict.get('title', None),
                'file_name': audio_dict.get('file_name', None),
                'mime_type': audio_dict.get('mime_type', None),
                'file_size': audio_dict.get('file_size', None),
                'date': audio_dict.get('date', None),
            }
        )

        es.sent_message.insert({'_from': f'chats/{chat_id_str}', '_to': f'audios/{key}'})


if __name__ == '__main__':
    es = DatabaseClient(
        'https://localhost:9200',
        elastic_http_certs='../../ca.crt',
        elastic_basic_auth=('elastic', 'abcdef')
    )

    offset = 0
    counter = 0
    while True:
        result = es._es_client.search(index='tase-test-index', size=1000, from_=offset)
        if len(result.body['hits']['hits']):
            offset += len(result.body['hits']['hits'])
            for obj_dict in result.body['hits']['hits']:
                extract_audio(obj_dict)
                counter += 1
                if counter % 100 == 0:
                    logger.info(f'extracted {counter} audios')
                pass

        else:
            break
    print(result)
