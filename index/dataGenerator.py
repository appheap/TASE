import time
import re


def user_data_generator(message):
    """
    A generator for user-data based on the message
    :param message: The message containing the user, chat, etc. data
    :return:
    """
    try:
        user = message.from_user
        yield {
            "_index": "user",
            "_id": user.id,
            "_source": {
                "first_name": user.first_name,
                "username": user.username,
                "date_joined": int(time.time()),
                "downloaded_audio_id_list": [],
                "favorite_audio_id_list": [], # when added to this list it'll be deleted from downloaded list
                "downloaded_audio_count": 0,
                "lang_code": "en",
                "limited": False,  # after 5 songs users should wait 1 min till receive the file
                "role": "searcher",
                "coins": 0,
                "last_active_date": int(time.time()),
                "is_admin": False,
                "sex": "neutral",
                "country": "-",
                "other": [],
            }
        }
    except Exception as e:
        print(f"Exception from data generator {e}")


def caption_extractor(audio):
    """
    Extracts the captions from audio files
    :param audio: Audio object from the whole message file
    :return: The caption extracted from the file and returned as string
    """
