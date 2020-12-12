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
    for i in history_messages:
        try:
            audio = i.audio
            yield {
                "_index": "audio_files",
                "_id": str(audio.file_id[8:30:3]).replace("-", "d"),
                "_source": {
                    "chat_id": int(i.chat.id),  # important: telegram won't work with id if the client hasn't already
                    "chat_username": i.chat.username,
                    # important: telegram won't work with id if the client hasn't already
                    # indexed that chat peer itself --> this should be retieved from the
                    # channel index : retrieve the username and search by id --> if the
                    # retrieve client changed to something else
                    "message_id": int(i.message_id),
                    "file_id": audio.file_id,
                    "file_name": str(audio.file_name).replace("_", " ").replace("@", " "),
                    # re.sub(r'[^\w]', ' ', str(audio.file_name).replace("_", " "))
                    "file_size": audio.file_size,
                    "duration": audio.duration,
                    "performer": str(real_name_extractor(i, "performer")).replace("_",
                                                                                  " ") if not audio.performer == None else " ",
                    # re.sub(r'[^\w]', ' ', str(audio.performer).replace("_", " "))
                    "title": str(real_name_extractor(i, "title")).replace("_", " ") if not audio.title == None else " ",
                    # re.sub(r'[^\w]', ' ', str(audio.title).replace("_", " "))
                    "times_downloaded": 0,
                    "caption": str(caption_extractor(i)),
                    "copyright": False  # TODO: if set to True only return the source of the file not the file itself
                }
            }
        except Exception as e:
            print(f"Exception from audio data generator {e}")

