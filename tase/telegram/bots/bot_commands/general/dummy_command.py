import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.errors import NotEnoughRamError
from tase.my_logger import logger
from tase.task_distribution import TargetWorkerType
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.tasks import DummyTask, ForwardMessageTask
from tase.telegram.update_handlers.base import BaseHandler


class DummyCommand(BaseCommand):
    """
    Publishes a dummy task to be executed. It is meant only for test purposes.
    """

    command_type: BotCommandType = Field(default=BotCommandType.DUMMY)
    command_description = "This is command for testing purposes"
    required_role_level: UserRole = UserRole.OWNER

    async def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        kwargs = {}
        # if message.command and len(message.command) > 1:
        #     kwargs = {f"key_{i}": arg for i, arg in enumerate(message.command[1:])}

        try:
            # status, created = await DummyTask(kwargs=kwargs).publish(handler.db)
            # kwargs["chat_id"] = -1001002402521  # kurdinus channel
            kwargs["chat_id"] = -1001452028875  # just_123_test
            # kwargs["message_ids"] = [12367, 12120, 12037]
            # kwargs["message_ids"] = [12367,]
            # kwargs["message_ids"] = [12367000,12367]
            kwargs["message_ids"] = [792]
            msgs = await client.get_messages(-1001452028875, message_ids=[792])
            for msg in msgs:
                if msg.audio:
                    f_msg = await client.send_audio(chat_id=-1001777852540, audio=msg.audio.file_id, caption=msg.caption)
                    logger.info(f_msg)

            # await client.forward_messages(chat_id=-1001777852540,from_chat_id=-1001452028875,message_ids=[792])
            # status, created = await ForwardMessageTask(kwargs=kwargs, target_worker_type=TargetWorkerType.ONE_TELEGRAM_BOT_CONSUMER_WORK,).publish(
            #     handler.db,
            #     target_queue_routing_key=handler.telegram_client.name,
            # )
        except NotEnoughRamError:
            await message.reply_text(
                f"`DummyTask` was cancelled due to high memory usage",
                quote=True,
                parse_mode=ParseMode.HTML,
            )
        # else:
        #     if status is None:
        #         await message.reply_text("internal error")
        #     else:
        #         if created:
        #             if status.is_active():
        #                 await message.reply_text("Added the task to be processed!")
        #         else:
        #             if status.is_active():
        #                 await message.reply_text("This task already being processed")
        #             else:
        #                 await message.reply_text("The task is already finished")
