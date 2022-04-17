import time
from typing import List

import pyrogram

from tase.db.database_client import DatabaseClient
from tase.models import TelegramClient, ClientTypes, UserClientRoles
from tase.my_logger import logger
from tase.utils import _get_config_from_file


class TASE():
    clients: List['TelegramClient']

    def __init__(
            self,
            tase_config_path: str = './tase.toml',
    ):
        self.clients = []
        self.tase_config_path = tase_config_path
        self.tase_config = None
        self._init_telegram_clients()

    def _init_telegram_clients(self):
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
                    tg_client = TelegramClient._parse(ClientTypes.USER, user_dict, pyrogram_workdir)
                    self.clients.append(tg_client)

                for user_dict in tase_config.get('bots', None).values():
                    tg_client = TelegramClient._parse(ClientTypes.BOT, user_dict, pyrogram_workdir)
                    self.clients.append(tg_client)
            else:
                # todo: raise error (config file is invalid)
                pass

        else:
            # todo: raise error (empty config file path)
            pass

    def connect_clients(self):
        for client in self.clients:
            client.connect()


if __name__ == '__main__':
    # toml_dict = get_toml_from_file('./tast.toml')
    tase = TASE('../tase.toml')
    tase.connect_clients()
    pass
