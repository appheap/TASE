import time
import re


def user_data_generator(message):
    """
    A generator for user-data based on the message object
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

    result = f""
    try:
        if audio.caption:
            text = audio.caption

            tokens = re.split(":|,| |\n|-|;|؛", text)
            for token in tokens:
                if (not "@" in token) and (not str(token).__contains__("https://")):
                    result += str(token.replace("-", " ")) + " "
        else:
            return "-"
    except Exception as e:
        print(f"Exception from data generator caption extractor {e}")
    finally:
        if len(result) < 2:
            result = " "
    return result

def real_name_extractor(audio_message, field):
    """
    Finds whether the audio title and performer are real or channel name
    :param audio_message: Audio object from the whole message object
    :param field: Fields of the audio object (i.e. title, performer)
    :return: Extracted real-name from the specified field
    """
    result = f""
    try:
        if audio_message.audio:
            audio = audio_message.audio
            if field == "title":
                if audio.title:
                    text = audio.title

                    tokens = re.split(":|,| |\n|-|;|؛", text)
                    for token in tokens:
                        if (not "@" in token) and (not str(token).__contains__("https://")):
                            if not (token == audio_message.chat.username or token == audio_message.chat.title):
                                result += str(token.replace("-", " ")) + " "
                else:
                    return " "
            elif field == "performer":
                if audio.performer:
                    text = audio.performer

                    tokens = re.split(":|,| |\n|-|;|؛", text)
                    for token in tokens:
                        if (not "@" in token) and (not str(token).__contains__("https://")):
                            if not (token == audio_message.chat.username or token == audio_message.chat.title):
                                result += str(token.replace("-", " ")) + " "
                else:
                    return " "


    except Exception as e:
        print(f"Exception from data generator caption extractor {e}")
    finally:
        if len(result) < 2:
            result = " "
    return result

def audio_data_generator(history_messages):
    """
    A generator for audio-data based on the message object
    :param history_messages:
    :return:
    """

