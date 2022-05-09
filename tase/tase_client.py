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
        self.database_client = None

    def init_telegram_clients(self):
        mgr = mp.Manager()
        shared_ns = mgr.Namespace()
        task_queues = mgr.dict()

        if self.tase_config_path is not None:
            tase_config = _get_config_from_file(self.tase_config_path)
            self.tase_config = tase_config
            if tase_config is not None:
                graph_db_config = tase_config.get('graph-config')
                elasticsearch_config = tase_config.get('elastic-config')
                self.database_client = DatabaseClient(
                    elasticsearch_config=elasticsearch_config,
                    graph_db_config=graph_db_config,
                )

                pyrogram_config = tase_config.get('pyrogram', None)
                # todo: what if it's None?

                pyrogram_workdir = None
                if pyrogram_config:
                    pyrogram_workdir = pyrogram_config.get('workdir', None)
                    print(pyrogram_workdir)

                for user_dict in tase_config.get('users', None).values():
                    pass
                    tg_client = TelegramClient._parse(ClientTypes.USER, user_dict, pyrogram_workdir)
                    client_manager = ClientManager(
                        telegram_client_name=tg_client.name,
                        telegram_client=tg_client,
                        task_queues=task_queues,
                        database_client=self.database_client
                    )
                    client_manager.start()
                    self.clients.append(tg_client)
                    self.client_managers.append(client_manager)

                for user_dict in tase_config.get('bots', None).values():
                    tg_client = TelegramClient._parse(ClientTypes.BOT, user_dict, pyrogram_workdir)
                    client_manager = ClientManager(
                        telegram_client_name=tg_client.name,
                        telegram_client=tg_client,
                        task_queues=task_queues,
                        database_client=self.database_client
                    )
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
