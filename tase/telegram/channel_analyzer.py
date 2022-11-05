import math

from pydantic import BaseModel
from pyrogram.enums import MessagesFilter

from tase.my_logger import logger
from tase.telegram.client import TelegramClient


class ChannelAnalyzer(BaseModel):
    """
    This class is used to calculate importance scores for telegram channels based on different factors
    """

    @staticmethod
    def calculate_score(
        telegram_client: TelegramClient,
        telegram_chat_id: int,
        chat_members_count: int,
    ) -> float:
        """
        Calculate score for a channel

        Parameters
        ----------
        telegram_client : tase.telegram.TelegramClient
            Telegram client being used to get statistics about the channel
        telegram_chat_id : int
            Channel ID that the score is being calculated for
        chat_members_count : int
            Total number of chat's members

        Returns
        -------
        Calculated score for the channel
        """
        all_messages_count = telegram_client._client.get_chat_history_count(telegram_chat_id)
        audio_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.AUDIO)
        photo_video_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.PHOTO_VIDEO)
        document_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.DOCUMENT)
        audio_video_note_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.AUDIO_VIDEO_NOTE)
        gif_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.ANIMATION)
        link_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.URL)
        location_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.LOCATION)
        # phone_call_count = telegram_client._client.search_messages_count(
        #     chat.id, filter=MessagesFilter.PHONE_CALL
        # )
        chat_photo_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.CHAT_PHOTO)
        contact_count = telegram_client._client.search_messages_count(telegram_chat_id, filter=MessagesFilter.CONTACT)

        media_count = (
            audio_count
            + photo_video_count
            + document_count
            + audio_video_note_count
            + gif_count
            + link_count
            + location_count
            # + phone_call_count
            + chat_photo_count
            + contact_count
        )

        deleted_message_count = all_messages_count - media_count

        try:
            audio_density = audio_count / (all_messages_count - deleted_message_count - link_count)
        except ZeroDivisionError:
            audio_density = 0.0

        member_density = math.log(chat_members_count if chat_members_count is not None and chat_members_count > 0 else 1, 10_000_000_000)

        logger.debug(f"audio_density: {audio_density}")
        logger.debug(f"member_density: {member_density}")

        return (2 * audio_density + 1 * member_density) / 3
