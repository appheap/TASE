import json
import multiprocessing as mp
from typing import List, Optional

from decouple import config

from tase.configs import TASEConfig
from tase.db import DatabaseClient
from tase.errors import NotEnoughRamError
from tase.scheduler import SchedulerWorkerProcess
from tase.scheduler.jobs import (
    CountInteractionsJob,
    CountHitsJob,
    CheckUsernamesWithUncheckedMentionsJob,
    CheckUsernamesJob,
    ExtractUsernamesJob,
    IndexAudiosJob,
)
from tase.telegram.client import TelegramClient
from tase.telegram.client.telegram_client_manager import TelegramClientManager


class TASE:
    clients: List[TelegramClient]
    tase_config: Optional[TASEConfig]

    def __init__(
        self,
    ):
        self.clients = []
        self.tase_config = None
        self.database_client = None
        self.telegram_manager: Optional[TelegramClientManager] = None

    def init_telegram_clients(self):
        mgr = mp.Manager()
        client_worker_queues = mgr.dict()
        scheduler = None

        debug = config(
            "DEBUG",
            cast=bool,
            default=True,
        )

        tase_config_file_name = config("TASE_CONFIG_FILE_NAME_DEBUG") if debug else config("TASE_CONFIG_FILE_NAME_PRODUCTION")

        if tase_config_file_name is not None:
            with open(f"../{tase_config_file_name}", "r") as f:
                tase_config = TASEConfig.parse_obj(json.loads("".join(f.readlines())))  # todo: any improvement?

            self.tase_config = tase_config
            if tase_config is not None:
                self.telegram_manager = TelegramClientManager(tase_config)
                self.telegram_manager.start()

                self.database_client = DatabaseClient(
                    elasticsearch_config=tase_config.elastic_config,
                    arangodb_config=tase_config.arango_db_config,
                    update_arango_indexes=True,
                )

                scheduler = SchedulerWorkerProcess(tase_config)
                scheduler.start()

                # cancel active task from the last run
                self.database_client.document.cancel_all_active_tasks()
                try:
                    # todo: do initial job scheduling in a proper way
                    CountInteractionsJob().publish(self.database_client)
                    CountHitsJob().publish(self.database_client)

                    IndexAudiosJob().publish(self.database_client)
                    ExtractUsernamesJob().publish(self.database_client)
                    CheckUsernamesJob().publish(self.database_client)
                    CheckUsernamesWithUncheckedMentionsJob().publish(self.database_client)
                except NotEnoughRamError as e:
                    raise e

            else:
                # todo: raise error (config file is invalid)
                pass

        else:
            # todo: raise error (empty config file path)
            pass

        if self.telegram_manager:
            self.telegram_manager.join()

        if scheduler:
            scheduler.join()

    def connect_clients(self):
        for client in self.clients:
            client.start()


if __name__ == "__main__":
    tase = TASE()
    tase.init_telegram_clients()
