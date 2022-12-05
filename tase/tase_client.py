import asyncio
import json
import sys
from typing import List, Optional

import uvloop
from decouple import config

from tase.configs import TASEConfig
from tase.db import DatabaseClient
from tase.errors import NotEnoughRamError
from tase.scheduler import SchedulerWorkerProcess
from tase.telegram.client import TelegramClient
from tase.telegram.client.telegram_client_manager import TelegramClientManager


class TASE:
    clients: List[TelegramClient]
    tase_config: Optional[TASEConfig]

    def __init__(
        self,
    ):
        self.tase_config = None
        self.database_client = None
        self.telegram_client_manager: Optional[TelegramClientManager] = None

    async def init_telegram_clients(self):
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
                self.telegram_client_manager = TelegramClientManager(tase_config)
                self.telegram_client_manager.start()

                self.database_client = DatabaseClient(
                    elasticsearch_config=tase_config.elastic_config,
                    arangodb_config=tase_config.arango_db_config,
                )
                await self.database_client.init_databases(update_arango_indexes=True)

                scheduler = SchedulerWorkerProcess(tase_config)
                scheduler.start()

                # cancel active task from the last run
                await self.database_client.document.cancel_all_active_tasks()

                try:
                    await asyncio.sleep(30)
                    # todo: do initial job scheduling in a proper way
                    # await DummyJob(kwargs={"key": 1}).publish(self.database_client)
                    await CountInteractionsJob().publish(self.database_client)
                    await CountHitsJob().publish(self.database_client)

                    await IndexAudiosJob().publish(self.database_client)
                    await ExtractUsernamesJob().publish(self.database_client)
                    await CheckUsernamesJob().publish(self.database_client)
                    await CheckUsernamesWithUncheckedMentionsJob().publish(self.database_client)
                except NotEnoughRamError as e:
                    raise e

            else:
                # todo: raise error (config file is invalid)
                pass

        else:
            # todo: raise error (empty config file path)
            pass

        if self.telegram_client_manager:
            self.telegram_client_manager.join()

        if scheduler:
            scheduler.join()


if __name__ == "__main__":
    tase = TASE()
    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            runner.run(tase.init_telegram_clients())
    else:
        uvloop.install()
        asyncio.run(tase.init_telegram_clients())
