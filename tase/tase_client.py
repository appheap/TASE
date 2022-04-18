import multiprocessing as mp
from typing import List

import pyrogram

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import TelegramClient, ClientTypes, UserClientRoles
from tase.telegram.client_manager import ClientManager
from tase.utils import _get_config_from_file


class TASE():
    clients: List['TelegramClient']

    def __init__(
            self,
            tase_config_path: str = './tase.toml',
    ):
        self.clients = []
        self.client_managers = []
        self.tase_config_path = tase_config_path
        self.tase_config = None

    def init_telegram_clients(self):
        mgr = mp.Manager()
        shared_ns = mgr.Namespace()
        task_queues = mgr.dict()

        if self.tase_config_path is not None:
            tase_config = _get_config_from_file(self.tase_config_path)
            self.tase_config = tase_config
            if tase_config is not None:
                pyrogram_config = tase_config.get('pyrogram', None)
                # todo: what if it's None?

                pyrogram_workdir = None
                if pyrogram_config:
                    pyrogram_workdir = pyrogram_config.get('workdir', None)
                    print(pyrogram_workdir)

                for user_dict in tase_config.get('users', None).values():
                    pass
                    tg_client = TelegramClient._parse(ClientTypes.USER, user_dict, pyrogram_workdir)
                    client_manager = ClientManager(name=tg_client.name, )
                    client_manager.telegram_client = tg_client
                    client_manager.task_queues = task_queues
                    client_manager.start()
                    self.clients.append(tg_client)
                    self.client_managers.append(client_manager)

                for user_dict in tase_config.get('bots', None).values():
                    tg_client = TelegramClient._parse(ClientTypes.BOT, user_dict, pyrogram_workdir)
                    client_manager = ClientManager(name=tg_client.name, )
                    client_manager.telegram_client = tg_client
                    client_manager.task_queues = task_queues
                    client_manager.start()
                    self.clients.append(tg_client)
                    self.client_managers.append(client_manager)
            else:
                # todo: raise error (config file is invalid)
                pass

        else:
            # todo: raise error (empty config file path)
            pass

        for client_mgr in self.client_managers:
            client_mgr.join()

    def connect_clients(self):
        for client in self.clients:
            client.start()

    def index_audios(self):
        es = DatabaseClient(
            'https://localhost:9200',
            elastic_http_certs='../ca.crt',
            elastic_basic_auth=('elastic', 'abcdef')
        )
        for client in self.clients:
            if client.client_type == ClientTypes.USER and client.role == UserClientRoles.INDEXER:
                # chat_id = -1001020660397
                chat_id = 'kurdinus'
                chat_id = 'Radio_Hawre'
                # for dialog in client._client.iter_dialogs():
                #     if dialog.chat and dialog.chat.title and 'Spotdlrobot' in dialog.chat.title:
                #         chat_id = dialog.chat.id
                #         break

                target_channel: 'pyrogram.types.Chat' = client._client.get_chat(chat_id)
                logger.info(target_channel)
                counter = 0
                # for audio_message in client._client.search_messages(chat_id, filter='audio', offset_id=11720, limit=100):
                # for audio_message in client._client.search_messages(chat_id, filter='audio', max_date=datetime.now().replace(year=2015,month=12,day=28).timestamp(), limit=100):
                # for audio_message in client._client.search_messages(chat_id, filter='audio', min_date=1448836708, limit=100):
                for audio_message in client._client.search_messages(
                        chat_id,
                        filter='audio',
                        # offset_id=11751,
                        # offset_id=5225,
                        # offset_id=4281,
                        # offset_id=3126,
                        offset_id=1,
                        # only_newer_messages=False
                ):
                    counter += 1
                    es.create_audio(
                        audio_message
                    )
                    if counter % 100 == 0:
                        logger.info(f'Added {counter} audios')
                        logger.info(audio_message.message_id)

                logger.info(f"indexed audios: {counter}")


if __name__ == '__main__':
    # toml_dict = get_toml_from_file('./tast.toml')
    tase = TASE('../tase.toml')
    # tase.connect_clients()
    # time.sleep(3)
    tase.init_telegram_clients()
    pass
