import json
import multiprocessing as mp
from typing import List, Optional

from tase.configs import TASEConfig
from tase.db.database_client import DatabaseClient
from tase.telegram import TelegramClient
from tase.telegram.client_manager import ClientManager


class TASE():
    clients: List['TelegramClient']
    tase_config: Optional[TASEConfig]

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
        task_queues = mgr.dict()

        if self.tase_config_path is not None:
            with open('../tase.json', 'r') as f:  # todo : fix me
                tase_config = TASEConfig.parse_obj(json.loads("".join(f.readlines())))  # todo: any improvement?

            self.tase_config = tase_config
            if tase_config is not None:
                self.database_client = DatabaseClient(
                    elasticsearch_config=tase_config.elastic_config,
                    arangodb_config=tase_config.arango_db_config,
                )

                for client_config in tase_config.clients_config:
                    tg_client = TelegramClient._parse(client_config, tase_config.pyrogram_config.workdir)
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


if __name__ == '__main__':
    tase = TASE('../tase.toml')
    tase.init_telegram_clients()
