"""####################################################################
# Copyright (C)                                                       #
# 2020 Soran Ghadri(soran.gdr.cs@gmail.com)                           #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
####################################################################"""

import concurrent.futures
import random
import secrets
import textwrap
from typing import Union, List, Any
from datetime import timedelta, datetime
from uuid import uuid4

# import emoji
import schedule
from elasticsearch import Elasticsearch, helpers
from pyrogram import Client, Filters, InlineKeyboardMarkup, \
    InputTextMessageContent, InlineQueryResultArticle
# from search_module.search_handling import file_retrieve_handler
from pyrogram.api import functions, types
from pyrogram.errors import FloodWait, SlowmodeWait

from static.emoji import _floppy_emoji, _clock_emoji
from index.analyzer import channel_analyzer  # Change this
from index.dataGenerator import *
# from languages.persian import result_list_handler
from languages import english, persian
from mapping import *


def telegramAPI_connect():
    """
    This function makes multiple telegram app clients and their respective global variables to make them accessible
    through the entire module.
    You can customise this function and make app clients as much as you want.

    Obtaining api_id and api_hash (Telegram guides):
    In order to obtain an API id and develop your own application using the Telegram API you need to do the following:
        1. Sign up for Telegram using any application.
        2. Log in to your Telegram core: https://my.telegram.org.
        3. Go to 'API development tools' and fill out the form.
        4. You will get basic addresses as well as the api_id and api_hash parameters required for user authorization.
        5. For the moment each number can only have one api_id connected to it.
    :return:
    """
    global executor, app, app2, bot, adbot, indexer_list
    indexer_list = []

    chromusic_indexer_7693_api_id = "api_id_1"
    chromusic_indexer_7693_api_hash = "api_hash_1"

    shelbycobra2016_api_id = "api_id_2"
    shelbycobra2016_api_hash = "api_hash_2"

    api_id_0762 = "api_id_3"
    api_hash_0762 = "api_hash_3"

    api_id_0765 = "api_id_4"
    api_hash_0765 = "api_hash_4"

    BOT_TOKEN = "Your bot toke here"  # chromusic_bot bot token

    # app_me = client_connect("shelbycobra2016", shelbycobra2016_api_id, shelbycobra2016_api_hash)
    app = client_connect("Chromusic_1", api_id_0762, api_hash_0762)
    app2 = client_connect("Chromusic_2", api_id_0765, api_hash_0765)
    chromusic_indexer_7693 = client_connect("Chromusic_indexer_7693", chromusic_indexer_7693_api_id,
                                            chromusic_indexer_7693_api_hash)

    # adbot = adbot_connect(BOT_TOKEN, api_hash, api_id)
    # bot = bot_connect("soranpythonbot", BOT_TOKEN, shelbycobra2016_api_hash, shelbycobra2016_api_id)
    bot = bot_connect("chromusic_bot", shelbycobra2016_api_id, shelbycobra2016_api_hash, BOT_TOKEN)
    indexer_list.append(chromusic_indexer_7693)


def client_connect(
        session_name: str = "chromusic",
        api_id: Union[int, str] = None,
        api_hash: Union[int, str] = None):
    """
    Connect the client to Telegram servers. [Client API]
    :param session_name: [str] (defaults to 'chromusic')
            Pass a string of your choice to give a name to the client session, e.g.: "*chromusic*". This name will be
            used to save a file on disk that stores details needed to reconnect without asking again for credentials.
            Alternatively, if you don't want a file to be saved on disk, pass the special name "**:memory:**" to start
            an in-memory session that will be discarded as soon as you stop the Client. In order to reconnect again
            using a memory storage without having to login again, you can use
            :meth:`~pyrogram.Client.export_session_string` before stopping the client to get a session string you can
            pass here as argument.
    :param api_id: [int/str]
            The *api_id* part of your Telegram API Key, as integer. E.g.: "12345".
            This is an alternative way to pass it if you don't want to use the *config.ini* file.
    :param api_hash:  [str]
            The *api_hash* part of your Telegram API Key, as string. E.g.: "0123456789abcdef0123456789abcdef".
            This is an alternative way to set it if you don't want to use the *config.ini* file.
    :return: Connected client
    :raises: ConnectionError: In case you try to connect an already connected client.
    """
    client = Client(session_name, api_id, api_hash)
    client.start()
    # apl.append(app)
    print(f"Client {session_name} session running ...")
    return client


def bot_connect(
        session_name: str = "chromusic_bot",
        api_id: Union[int, str] = None,
        api_hash: Union[int, str] = None,
        bot_token: str = None):
    """
    Connect the client to Telegram servers. [Bot API]
    :param session_name: [str] (defaults to 'chromusic_bot')
            Pass a string of your choice to give a name to the client session, e.g.: "*chromusic*". This name will be
            used to save a file on disk that stores details needed to reconnect without asking again for credentials.
            Alternatively, if you don't want a file to be saved on disk, pass the special name "**:memory:**" to start
            an in-memory session that will be discarded as soon as you stop the Client. In order to reconnect again
            using a memory storage without having to login again, you can use
            :meth:`~pyrogram.Client.export_session_string` before stopping the client to get a session string you can
            pass here as argument.
    :param api_id: [int/str]
            The *api_id* part of your Telegram API Key, as integer. E.g.: "12345".
            This is an alternative way to pass it if you don't want to use the *config.ini* file.
    :param api_hash:  [str]
            The *api_hash* part of your Telegram API Key, as string. E.g.: "0123456789abcdef0123456789abcdef".
            This is an alternative way to set it if you don't want to use the *config.ini* file.
    :param bot_token:  [str]
            Pass your Bot API token to create a bot session, e.g.: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            Only applicable for new sessions.
            This is an alternative way to set it if you don't want to use the *config.ini* file.
    :return: Connected bot object
    :raises: ConnectionError - In case you try to connect an already connected client.
    """
    bot = Client(session_name, api_id, api_hash, bot_token=bot_token)
    bot.start()
    # apl.append(bot)
    print(f"Bot: {session_name} session running ...")
    return bot


def db_connect():
    """
    Connect to elasticsearch API
    Creates a global variable for elasticsearch object
    :return: -
    """
    global es
    es = Elasticsearch([{"host": "localhost", "port": 9200}])
    print("Elasticsearch database running ...")


def exception_handler(func: Any) -> object:
    """
    Wraps a function and handles non-handled exceptions
    :param func: Input function
    :return: Input function's output
    """
    try:
        func
    except SlowmodeWait as e:
        time.sleep(e.x)
        return func
    except FloodWait as e:
        time.sleep(e.x)
        return func
    except Exception as e:
        time.sleep(10)
        return func


def check_new_member_join_count(channel_id: int):
    """
    Check if any changes has happened in the number of subscribers
    :param channel_id: Channel ID in which this client is an admin
    :return: -
    """
    try:
        current_db_members_count = int(es.get("admin_log_control", id=channel_id)["_source"]["members_count"])
        current_members_count = int(app.get_chat_members_count(channel_id))
        # print("check_new_member: ", channel_id)
        if not current_db_members_count == current_members_count:
            check_joining_status(channel_id)
            res = es.update(index="admin_log_control", id=channel_id, body={
                "script":
                    {
                        "source": "ctx._source.members_count = params.count",
                        "lang": "painless",
                        "params": {
                            "count": int(current_members_count)
                        }
                    }
            }, ignore=409)
            # print("check_new_member: ", res)
    except FloodWait as e:
        print("floodwait from check_new_member:", e)
        print("sleeping for", e.x)
        time.sleep(e.x)
    except Exception as e:
        print("exception from check_new_member:", e)


def check_joining_status(channel_id):
    """
    Check if a user is a subscriber or not
    :param channel_id: Channel ID in which this client is an admin
    :return: -
    """
    try:
        res = get_admin_log(channel_id)  # chromusic channel ID
        # print("admin log: ", res)
        current_last_date = es.get("admin_log_control", id=channel_id)["_source"]["last_offset_date"]
        _last_event = None
        # print("this action contains join")
        for event in reversed(res["events"]):
            # print("this is the event: ", event)
            if event["date"] > current_last_date:
                # print("event_single: ", current_last_date)
                if es.exists("user", id=event["user_id"]):
                    # print("user_exists")
                    if str(event["action"]).__contains__("Leave"):
                        # print("this action contains leave")
                        # app.send_message(chat_id="me", text="leave")
                        try:
                            es.update("user", id=event["user_id"], body={
                                "script":
                                    {
                                        "inline": "ctx._source.role = params.role; ctx._source.limited = params.limited;",
                                        "lang": "painless",
                                        "params": {
                                            "role": "searcher",
                                            "limited": True
                                        }
                                    }
                            }, ignore=409)
                        except Exception as e:
                            print("exception from updating join/leave check joining status: ", e)
                            # pass
                    elif str(event["action"]).__contains__("Join"):
                        # print("this action contains join")
                        # app.send_message(chat_id="me", text="Join")
                        es.update("user", id=event["user_id"], body={
                            "script":
                                {
                                    "inline": "ctx._source.role = params.role; ctx._source.limited = params.limited;",
                                    "lang": "painless",
                                    "params": {
                                        "role": "subscriber",
                                        "limited": False
                                    }
                                }
                        }, ignore=409)
                _last_event = event
        if _last_event:
            # print("last date: ", _last_event["date"])
            es.update(index="admin_log_control", id=channel_id, body={
                "script":
                    {
                        "source": "ctx._source.last_offset_date = params.date_offset",
                        "lang": "painless",
                        "params": {
                            "date_offset": int(_last_event["date"])
                        }
                    }
            }, ignore=409)
    except Exception as e:
        print("from check joining status:", e)


def language_handler(
        func: object = None,
        lang: str = "en",
        *args: list,
        **kwargs: dict):
    """
    Routes the functions to their respective languages.
    :param func: Input function to be routed
    :param lang: Language to return results in
    :param args: [list] Other arguments
    :param kwargs: [dict] Other key-value arguments
    :return: The result of the queried function in 'lang' language
    """
    text = ""
    if lang == "en":
        text = getattr(english, func)(*args, **kwargs)
    elif lang == "fa":
        text = getattr(persian, func)(*args, **kwargs)
    else:
        text = getattr(english, func)(*args, **kwargs)

    return text


def get_admin_log(peer: Union[int, str] = None) -> list[object]:
    """
    Get a list of logs from the admin-logs. This method gets 'Join' and 'Leave'  events by default, but you can
    uncomment the commented items and add them to your result list.

    :param peer: Union: [id, username]. Peer username or ID.
    ex. get_admin_log("chromusic")
    :return: list[object] - A list of recent join/leave activities
    """
    res = app.send(functions.channels.GetAdminLog(
        channel=app.resolve_peer(peer),
        q='',
        max_id=0,
        min_id=0,
        limit=10000,
        # events_filter=types.ChannelAdminLogEventsFilter()
        events_filter=types.ChannelAdminLogEventsFilter(
            join=True,
            leave=True
            # invite=False,
            # ban=False,
            # unban=False,
            # kick=False,
            # unkick=False,
            # promote=False,
            # demote=False,
            # info=False,
            # settings=False,
            # pinned=False,
            # edit=False
        )
    ))
    return res


def download_guide(user: object):
    """
    Send a 'How to search and download' example to new users. Automatically picks the user's language and returns
     the example with respect to their languages.
    :param user: User object
    :return:
    """
    try:
        user_data = es.get("user", id=user.id)["_source"]
        if user_data["downloaded_audio_count"] == 0:
            lang_code = user_data["lang_code"]
            help_keyboard_text = language_handler("example_message", lang_code, user.first_name, 15)
            help_markup_keyboard = language_handler("example_message_keyboard", user_data["lang_code"])
            bot.send_message(chat_id=user.id, text=help_keyboard_text,
                             reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
            # parse_mode='HTML')
    except FloodWait as e:
        res = bot.set_slow_mode(user.id, 2)
        text = f"floodwait occured in the download_guide! \n\n{e}\n\nresult: {res}"
        app.send_message(chromusic_log_id, text)
        time.sleep(e.x)
    except SlowmodeWait as e:
        res = bot.set_slow_mode(user.id, 2)
        text = f"SlowmodeWait occured in the download_guide! \n\n{e}\n\nresult: {res}"
        app.send_message(chromusic_log_id, text)
        time.sleep(e.x)
    except Exception as e:
        print(f"from download_guide exception: {e}")


def search_handler(bot: object, message: object):
    """
    1. Search the query among the elasticsearch documents
    2. Handles the activity and membership status of users
    :param bot: Bot object - Connects to and deals with Telegram servers
    :param message: Message object containing the query
    :return: A message containing the results, in case there were any result in the database; otherwise a 'no result'
     text
    """
    if len(str(message.text)) > 1:
        user = message.from_user
        try:
            is_member(user)
            query = message.text
            processed_query = str(query).replace("_", " ")

            res = es.search(index="audio_files", body={"query": {
                "multi_match": {
                    "query": processed_query,
                    "type": "best_fields",
                    "fields": ["title", "file_name", "performer"],  # , "caption"],
                    # "fuzziness": "AUTO", # play with search parameters to satisfy your desired results
                    # "tie_breaker": 0.5,
                    "minimum_should_match": "60%"
                }}})

            user_data = es.get("user", id=user.id)["_source"]
            lang_code = user_data["lang_code"]
            last_active_date = int(time.time()) - int(user_data["last_active_date"])
            if last_active_date > timedelta(days=7).total_seconds():
                help_markup_keyboard = language_handler("help_markup_keyboard", user_data["lang_code"])

                if last_active_date > timedelta(days=14).total_seconds():
                    help_keyboard_text = language_handler("long_time_not_active", lang_code, user.first_name, 15)
                else:
                    help_keyboard_text = language_handler("long_time_not_active", lang_code, user.first_name, 5)

                exception_handler(bot.send_message(chat_id=user.id, text=help_keyboard_text,
                                                   reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
                                                   parse_mode='HTML'))
            _text = language_handler("result_list_handler", lang_code, query, res)
            search_list_keyboard = language_handler("search_list_keyboard", lang_code, processed_query)
            exception_handler(
                bot.send_message(message.chat.id, _text, parse_mode='html', disable_web_page_preview=True,
                                 reply_to_message_id=message.message_id,
                                 reply_markup=InlineKeyboardMarkup(search_list_keyboard)))
            es.update(index="user", id=user.id, body={
                "script": {
                    "source": "ctx._source.last_active_date = params.last_active_date",
                    "lang": "painless",
                    "params": {
                        "last_active_date": int(time.time())
                    }
                }
            }, ignore=409)
            return _text


        except FloodWait as e:
            res = bot.set_slow_mode(user.id, 2)
            text = f"floodwait occured in the search handler! \n\n{e}\n\nresult: {res}"
            app.send_message(chromusic_log_id, text)
            time.sleep(e.x)
        except SlowmodeWait as e:
            res = bot.set_slow_mode(user.id, 2)
            text = f"SlowmodeWait occured in the search handler! \n\n{e}\n\nresult: {res}"
            app.send_message(chromusic_log_id, text)
            time.sleep(e.x)
        except Exception as e:
            print(f"from search handler exception: {e}")


def result_list_handler(
        query: str,
        search_res: str,
        lang: str = 'en') -> str:
    """
    Language hub function. This function routes each text and function request to its requested language file and
     returns the results from language files.
    :param query: Search query
    :param search_res: Search results including the links in case any result were returned
    :param lang: Requested language to route to
    :return: Results from requested language functions
    """
    # TODO: Remove this function after implementing the global language handler function
    if lang == "fa":
        text = persian.result_list_handler(query, search_res)
    elif lang == "en":
        text = english.result_list_handler(query, search_res)
    else:
        text = english.result_list_handler(query, search_res)

    return text


def is_member(user: object):
    """
    Check if a user is already a member in the channel; in case was not member and exceeded five downloads, update
     their 'limited' status to 'True'
    :param user: User object
    :return:
    """
    try:
        user_data = es.get("user", id=user.id)["_source"]
        if user_data["role"] == "searcher":
            print("he is a searcher")
            if user_data["limited"] == False:
                if user_data["downloaded_audio_count"] > 4:
                    es.update(index="user", id=user.id, body={
                        "script": {
                            "inline": "ctx._source.limited = params.limited;"
                                      "ctx._source.role = params.role;",
                            "lang": "painless",
                            "params": {
                                "limited": True,
                                "role": "searcher"
                            }
                        }
                    }, ignore=409)
    except FloodWait as e:
        time.sleep(e.x + 5)
    except Exception as e:
        print(f"from is member: {e}")


def file_retrieve_handler(message: object) -> str:
    """
    Retrieve audio file from source channels after getting ID of the audio file chosen by the user from the
     result list.
    :param message: Message object containing the ID of the audio file
    :return: On success returns Generated audio-file caption
    """
    try:
        # important: telegram won't work with id if the client hasn't already
        # indexed that chat peer itself --> this should be retrieved from the
        # channel index : retrieve the username and search by id --> in case the
        # retrieve client changed to something else

        # A Problem: if chat_id s get converted to chat_username --> it may loose those files from chat's
        # that have changed their username

        # one way: each time a file is retrieved -> check if exists in the channel index --> if it's already
        # integer then it exists otherwise it's converted to username

        query = str(message.text).split("dl_")[1]
        if len(query) < 8:
            query = str(message.text)[4:]

        user = message.from_user
        is_member(user)
        res = es.search(index="audio_files", body={
            "query": {
                "match": {
                    "_id": query
                }
            }
        })
        chat_id = int(res['hits']['hits'][0]['_source']['chat_id'])
        chat_username = res['hits']['hits'][0]['_source']['chat_username']
        message_id = int(res['hits']['hits'][0]['_source']['message_id'])
        print(f"{40 * '='}", chat_id, ' &&  ', message.chat)

        try:
            try:
                audio_track = bot.get_messages(chat_username, message_id)  # message_id)
            except Exception as e:
                audio_track = bot.get_messages(chat_id, message_id)  # message_id)

            user_data = es.get("user", id=user.id)["_source"]
            lang_code = user_data["lang_code"]

            collaboration_request_message = language_handler("collaboration_request", lang_code)
            probability = 0
            if random.random() > 0.8:
                probability = 1

            _caption = language_handler("file_caption", lang_code, audio_track, audio_track.message_id)
            music_file_keyboard = language_handler("music_file_keyboard", lang_code, query)
            if user_data["limited"] == False:
                exception_handler(bot.send_audio(message.chat.id, audio_track.audio.file_id,
                                                 caption=_caption,  # reply_to_message_id=message.message_id,
                                                 reply_markup=InlineKeyboardMarkup(music_file_keyboard),
                                                 parse_mode="HTML"))
                if user_data["role"] == "subscriber":
                    if probability == 1:
                        sent_collaboration_request_message = bot.send_message(message.chat.id,
                                                                              collaboration_request_message)
                # bot.send_audio("shelbycobra2016", audio_track.audio.file_id,
                #                caption=_caption)  # , file_ref=audio_track.audio.file_ref)
                # print("before_retrieve_updater")
                retrieve_updater(query, user, chat_id)
                # print("after_retrieve_updater")
            else:
                keyboard = language_handler("button_joining_request_keyboard", lang=lang_code)
                text = language_handler("send_in_1_min", user_data["lang_code"], user_data["first_name"])
                send1min = bot.send_message(message.chat.id, text,  # reply_to_message_id=message.message_id,
                                            reply_markup=InlineKeyboardMarkup(keyboard))
                # exception_handler(bot.send_message(message.chat.id, text,
                #                                           # reply_to_message_id=message.message_id,
                #                                           reply_markup=InlineKeyboardMarkup(keyboard)))

                time.sleep(60)

                exception_handler(bot.send_audio(message.chat.id, audio_track.audio.file_id,
                                                 caption=_caption,  # reply_to_message_id=message.message_id,
                                                 reply_markup=InlineKeyboardMarkup(music_file_keyboard),
                                                 parse_mode="HTML"))
                send1min.delete()
                # bot.send_audio("shelbycobra2016", audio_track.audio.file_id,
                #                caption=_caption)
                retrieve_updater(query, user, chat_id)
            # print(es.get("user", id=user.id))
            # print(es.get("user_lists", id=user.id))
            return _caption
        except Exception as e:
            # print("exception from file_ret_handler: ", e)
            try:
                try:
                    audio_track = app.get_messages(chat_username, message_id)
                except Exception as e:
                    audio_track = app.get_messages(chat_id, message_id)
                user_data = es.get("user", id=user.id)["_source"]
                # print("from file ret - lang code:", audio_track)
                lang_code = user_data["lang_code"]
                music_file_keyboard = language_handler("music_file_keyboard", lang_code, query)
                # _caption = caption_handler(audio_track, message_id, lang_code)
                _caption = language_handler("file_caption", lang_code, audio_track, audio_track.message_id)
                sent_to_datacenter = app.send_audio(datacenter_id, audio_track.audio.file_id,
                                                    audio_track.audio.file_ref,
                                                    caption=_caption)

                message_id = sent_to_datacenter.message_id
                audio_track = bot.get_messages(datacenter_id, message_id)
                if user_data["limited"] == False:
                    exception_handler(bot.send_audio(message.chat.id, audio_track.audio.file_id,
                                                     caption=_caption,  # reply_to_message_id=message.message_id,
                                                     reply_markup=InlineKeyboardMarkup(music_file_keyboard),
                                                     parse_mode="HTML"))

                    if user_data["role"] == "subscriber":
                        if probability == 1:
                            sent_collaboration_request_message = bot.send_message(message.chat.id,
                                                                                  collaboration_request_message)

                    # bot.send_audio("shelbycobra2016", audio_track.audio.file_id,
                    #                caption=_caption)
                    retrieve_updater(query, user, chat_id)
                else:
                    keyboard = language_handler("button_joining_request_keyboard", lang=lang_code)
                    text = language_handler("send_in_1_min", user_data["lang_code"], user_data["first_name"])
                    send1min = bot.send_message(message.chat.id, text,  # reply_to_message_id=message.message_id,
                                                reply_markup=InlineKeyboardMarkup(keyboard))
                    # exception_handler(
                    # bot.send_message(message.chat.id, text,  # reply_to_message_id=message.message_id,
                    #                  reply_markup=InlineKeyboardMarkup(keyboard)))

                    time.sleep(60)
                    exception_handler(bot.send_audio(message.chat.id, audio_track.audio.file_id,
                                                     caption=_caption,  # reply_to_message_id=message.message_id,
                                                     reply_markup=InlineKeyboardMarkup(music_file_keyboard),
                                                     parse_mode="HTML"))
                    send1min.delete()
                    # bot.send_audio("shelbycobra2016", audio_track.audio.file_id,
                    #                caption=_caption)
                    retrieve_updater(query, user, chat_id)
                sent_to_datacenter.delete()
                return _caption
            except Exception as e:
                try:
                    finale_ex = ""
                    bot.send_message(message.chat.id, f"Hey {message.from_user.first_name}, unfortunately, the source "
                                                      f"channel has removed the file or the channel has converted "
                                                      f"to a private channel")
                except Exception as e:
                    finale_ex = f"last exception occured as well {e}"
                error_text = f"Exception from exception from file retriever .. maybe file has been removed:\n\n{e}\n\n" \
                             f"File ID: {message.text}\n" \
                             f"Sender: {user.first_name} - {user.username}\n" \
                             f"Channel username: {chat_username}\n\n" \
                             f"{finale_ex}"
                app.send_message(chromusic_log_id, error_text)
    except Exception as e:
        text = f"outer exception from file retrieve: {e}"
        app.send_message(chromusic_log_id, text)


def retrieve_updater(query: str, user: object, channel: str) -> bool:
    """
    Update database indices on file retrieving.
    :param query: Audio-file ID to update its information
    :param user: User object to update its information
    :param channel: ChannelID to update its information
    :return: True on success
    """
    resu = es.update(index="user", id=user.id, body={
        "script": {
            "inline": "ctx._source.downloaded_audio_count+=params.count_inc;",
            "lang": "painless",
            "params": {
                "count_inc": 1,
            }
        }
    }, ignore=409)

    resl = es.update(index="user_lists", id=user.id, body={
        "script": {
            "source": "if (ctx._source.downloaded_audio_id_list.contains(params.file_id)) {ctx.op = 'none'} else "
                      "{if (ctx._source.downloaded_audio_id_list.size()>49) "
                      "{ctx._source.downloaded_audio_id_list.remove(0);"
                      "ctx._source.downloaded_audio_id_list.add(params.file_id);} "
                      "else {ctx._source.downloaded_audio_id_list.add(params.file_id);}}",  # ctx.op = 'none'}",
            "lang": "painless",
            "params": {
                "file_id": query
            }
        }
    }, ignore=409)
    # print("user_lists update:", resl)
    # for res in resl:
    #     print(res)

    resa = es.update(index="audio_files", id=query, body={
        "script": {
            "inline": "ctx._source.times_downloaded+=params.count_inc;",
            "lang": "painless",
            "params": {
                "count_inc": 1,
            }
        }
    }, ignore=409)

    try:
        resc = es.update(index="channel", id=channel, body={
            "script": {
                "inline": "ctx._source.downloaded_from_count+=params.count_inc;",
                "lang": "painless",
                "params": {
                    "count_inc": 1,
                }
            }
        }, ignore=409)
        return True
    except Exception as e:
        try:
            time.sleep(3)
            chat = app.get_chat(channel)
            time.sleep(3)
            res = es.create("channel", id=chat.id, body={
                "title": chat.title,
                "username": chat.username,
                "importance": 5,
                "indexed_from_audio_count": 0,
                "last_indexed_offset_date": 0,
                "downloaded_from_count": 0,
            }, refresh=True, ignore=409)
        except Exception as e:
            print(f"chat: {e}")
        resc = es.update(index="channel", id=chromusic_users_files_id, body={
            "script": {
                "inline": "ctx._source.downloaded_from_count+=params.count_inc;",
                "lang": "painless",
                "params": {
                    "count_inc": 1,
                }
            }
        }, ignore=409)
        return True

def channel_name_extractor(client: object, text: str) -> list:
    """
    Extract channel names if any from the text.
    Optimistic channel name extraction [first it will be added to the elasticsearch index,
     later when it was its turn, it will be checked if it is a channel or not] -> Reduce get_chat requests, hence,
     avoid getting banned by the Telegram.
    :param client: Telegram client
    :param text: Text to be checked. Maybe caption, file name, etc.
    :return: A list of extracted channel names or empty list if there were no channel name in the text.
    """
    try:
        wrong_characters = ["?", "-", "%", "#", "*", "+", "$", "^", ".", "=", "!", "/"]
        import re
        if not str(text).__contains__("@"):
            return []
        tokens = re.split(":|,| |\n|-|;|؛", text)
        channels_username = []

        for token in tokens:
            if "@" in token:
                _token = token.replace("@", "")
                if _token.__len__() > 4:
                    try:
                        if not any(x in _token for x in wrong_characters):
                            if es.count(index="channel", body={
                                "query": {
                                    "match": {
                                        "username": _token
                                    }
                                }
                            })["count"] == 0:
                                res = es.create(index="channel_buffer", id=_token,
                                                body={},
                                                ignore=[409, 400])
                                print(f"from channel_name_extractor to channel_buffer: {res} ")
                                # time.sleep(3)  # since get_chat() has been revoked above
                                channels_username.append(_token)
                                # print("from channel extractor: ", res)
                    except Exception as e:
                        print(f"exception from caption_entities_channel_extractor() function inside"
                              f" if _token.__len__() > 4: {e}")
        return channels_username
    except Exception as e:
        print(f"exception from caption_entities_channel_extractor() function {e}")
        return []

def forwarded_from_channel_extractor(client: object, message: object) -> bool:
    """
    Extract channels' IDs from messages with forwarded_from_chat field and adds them to the set
    :param client: Telegram client
    :param message: Message object containing the ID of the audio file
    :return: True on success; otherwise False
    """
    try:
        temp_channel = message.forward_from_chat
        if temp_channel.type == "channel":

            if not es.exists(index="channel", id=temp_channel.id):
                # es.get(index="future_channel", id=temp_channel.username)
                es.create(index="future_channel", id=temp_channel.username, body={"id": temp_channel.id}, ignore=409)
        return True
    except Exception as e:
        print(f"exception from forwarded_from_channel_extractor() function: it may swapped to private "
              f"though unavailable: {e}")
        return False

def caption_entities_channel_extractor(client: object, message: object) -> list:
    """
    Extract channels' IDs from messages with caption_entities field
    :param client: Telegram client
    :param message: Message object containing the caption of the audio file
    :return: A list of extracted channel usernames on success; otherwise an empty list
    """
    try:
        channels_username = []
        entities = message.caption_entities
        wrong_characters = ["?", "-", "%", "#", "*", "+", "$", "^", ".", "=", "!", "/"]
        # temp_channel = ""
        if entities == None:
            entities = message.entities

        for entity in entities:
            if entity.type == "text_link":
                try:

                    url = str(entity.url).split("/")
                    if url.__len__() == 4:
                        # time.sleep(3)  # since get_chat() has been revoked above

                        # temp_channel = client.get_chat(url[-1])
                        # time.sleep(3)  # since get_chat() has been revoked above
                        # if temp_channel.type == "channel":

                        if not any(x in url[-1] for x in wrong_characters):
                            if es.count(index="channel", body={
                                "query": {
                                    "match": {
                                        "username": url[-1]
                                    }
                                }
                            })["count"] == 0:
                                # if not es.exists(index="channel", id=temp_channel.id):
                                # es.create(index="future_channel", id=temp_channel.username, body={"id": temp_channel.id}, ignore=409)
                                res = es.create(index="channel_buffer", id=url[-1],
                                                body={},
                                                ignore=[409, 400])
                                channels_username.append(url[-1])
                                print(f"from caption_entities_channel_extractor to channel_buffer: {res} ")
                                # es.get(index="future_channel", id=temp_channel.username)
                    elif url.__len__() == 5:
                        # time.sleep(3)  # since get_chat() has been revoked above
                        # temp_channel = client.get_chat(url[-2])
                        # time.sleep(3)  # since get_chat() has been revoked above
                        # if temp_channel.type == "channel":
                        if not any(x in url[-1] for x in wrong_characters):
                            if es.count(index="channel", body={
                                "query": {
                                    "match": {
                                        "username": url[-2]
                                    }
                                }
                            })["count"] == 0:
                                # if not es.exists(index="channel", id=temp_channel.id):
                                # es.create(index="future_channel", id=temp_channel.username, body={"id": temp_channel.id}, ignore=409)
                                res = es.create(index="channel_buffer", id=url[-2],
                                                body={},
                                                ignore=[409, 400])
                                channels_username.append(url[-2])
                                print(f"from caption_entities_channel_extractor to channel_buffer: {res} ")
                                # es.get(index="future_channel", id=temp_channel.username)
                        # print(temp_channel)
                except Exception as e:
                    print(
                        f"exception from caption_entities_channel_extractor() function entity.type == 'text_link': part: {e}")
                # channel_to_index_set.append(temp.id)
        if message.web_page:
            try:

                url = str(message.web_page.url).split("/")
                if url.__len__() == 4:
                    # time.sleep(3)  # since get_chat() has been revoked above
                    # temp_channel = client.get_chat(url[-1])
                    # time.sleep(3)  # since get_chat() has been revoked above
                    if not any(x in url[-1] for x in wrong_characters):
                        if es.count(index="channel", body={
                            "query": {
                                "match": {
                                    "username": url[-1]
                                }
                            }
                        })["count"] == 0:
                            # if not es.exists(index="channel", id=temp_channel.id):
                            # es.create(index="future_channel", id=temp_channel.username, body={"id": temp_channel.id}, ignore=409)
                            res = es.create(index="channel_buffer", id=url[-1],
                                            body={},
                                            ignore=[409, 400])
                            channels_username.append(url[-1])
                            print(f"from caption_entities_channel_extractor to channel_buffer: {res} ")
                elif url.__len__() == 5:
                    # time.sleep(3)  # since get_chat() has been revoked above
                    # temp_channel = client.get_chat(url[-2])
                    # time.sleep(3)  # since get_chat() has been revoked above
                    if not any(x in url[-1] for x in wrong_characters):
                        if es.count(index="channel", body={
                            "query": {
                                "match": {
                                    "username": url[-2]
                                }
                            }
                        })["count"] == 0:
                            # if not es.exists(index="channel", id=temp_channel.id):
                            # es.create(index="future_channel", id=temp_channel.username, body={"id": temp_channel.id}, ignore=409)
                            res = es.create(index="channel_buffer", id=url[-2],
                                            body={},
                                            ignore=[409, 400])
                            channels_username.append(url[-2])
                            print(f"from caption_entities_channel_extractor to channel_buffer: {res} ")
                    # print(temp_channel)
            except Exception as e:
                print(f"exception from caption_entities_channel_extractor() function message.web_page part: {e}")
        return channels_username
    except Exception as e:
        print(f"exception from caption_entities_channel_extractor() function: {e}")
        return []
    # print(channel_to_index_set)

def channel_re_analyzer() -> list:
    """
    Re-analyze channels and re-score their importance
    :return: Re-analysed channels list (still not completed)
    """
    res = None
    for imp in range(1):
        # es.indices.refresh("channel")
        # res = helpers.scan(es, query={"query": {"match": {"importance": imp}}},
        #                    index="channel")

        res = helpers.scan(
            client=es,
            query={"query": {"match": {"importance": imp}}},
            size=10000,
            scroll='5m',
            index="channel"
        )
        for _channel in res:
            # Do the re-scoring stuff here
            _channel

    return res

def daily_gathered_channels_controller(client: object) -> bool:
    """
    This function calls prepares the list and calls "new_channel_indexer" function 2 sets has been used in order to
    keep one of them intact until the channel is indexed and then remove from both of them (second set acts like a
    buffer).
    :param client: Telegram client
    :return: True on success otherwise False
    """
    try:
        while 1:
            try:
                _channels_list_username = []
                print("existing channels now running  ...")
                es.indices.refresh("future_channel")
                res = helpers.scan(es,
                                   query={"query": {"match_all": {}}},
                                   index="future_channel")

                for future_channel_instance in res:
                    _channels_list_username.append(future_channel_instance["_id"])
                # print("new indexing channels started ... !")
                new_channel_indexer(client, _channels_list_username, "future_channel")
                return True
            except Exception as e:
                text = f"exception handled form daily_gathered_channels_controller() function: \n\n{e}"
                client.send_message(chromusic_log_id, text)
                # continue
            finally:
                time.sleep(30)
    except Exception as e:
        text = f"exception handled from out of while in daily_gathered_channels_controller() function: \n\n{e}"
        client.send_message(chromusic_log_id, text)
        daily_gathered_channels_controller(client)
        return False

def existing_channels_handler_by_importance(client: object, importance: int):
    """
    This function retrieves channels from DB by importance and updates their indexing status
    :param client: Telegram client
    :param importance: The target importance of the channels to be retrieved from DB
    :return: -
    """
    try:
        while 1:
            try:
                res = es.search(index="channel", body={
                    "query": {
                        "match": {"importance": importance}
                    },
                    "sort": {
                        "last_indexed_offset_date": "asc"
                    }
                })
                starting_time = int(time.time())
                for _channel in res["hits"]["hits"]:
                    print(f"_channel: {_channel}")
                    # Every time only lets the crawler to work 3 hours at max
                    try:
                        if int(time.time()) - starting_time > timedelta(hours=2).total_seconds():
                            if importance > 0:
                                delay = timedelta(minutes=15).total_seconds()
                                time.sleep(delay)
                                starting_time = int(time.time())
                        try:
                            es.indices.refresh(index="global_control")
                            status_res = es.get(index="global_control", doc_type="indexing_flag", id=_channel["_id"])
                            is_being_indexed = status_res["_source"]["indexing"]
                            print("is being indexed: ", is_being_indexed)
                            if is_being_indexed == True:
                                continue
                            else:
                                flag_update_res = es.update(index="global_control", doc_type="indexing_flag",
                                                            id=_channel["_id"], body={
                                        "script": {
                                            "inline": "ctx._source.indexing = params.indexing;",
                                            "lang": "painless",
                                            "params": {
                                                "indexing": True,
                                            }
                                        }
                                    }, ignore=409)
                                es.index(index="global_control", doc_type="indexing_flag", id=_channel["_id"],
                                         body={
                                             "indexing": True,
                                             "name": _channel["_source"]["username"],
                                             "importance": _channel["_source"]["importance"]
                                         }, refresh=True)
                        except Exception as e:
                            es.create(index="global_control", doc_type="indexing_flag", id=_channel["_id"], body={
                                "indexing": True,
                                "name": _channel["_source"]["username"],
                                "importance": _channel["_source"]["importance"]
                            }, refresh=True, ignore=409)
                        existing_channel_indexer(client, channel_id=int(_channel["_id"]))
                        flag_update_res = es.update(index="global_control", doc_type="indexing_flag",
                                                    id=_channel["_id"], body={
                                "script": {
                                    "inline": "ctx._source.indexing = params.indexing;",
                                    "lang": "painless",
                                    "params": {
                                        "indexing": False,
                                    }
                                }
                            }, ignore=409)

                        time.sleep(10)
                    except Exception as e:
                        text = f"exception handled form existing_channels_handler_by_importance() function <b>for loop</b>: \n\n{e}"
                        client.send_message(chromusic_log_id, text)
                        time.sleep(15)

            except Exception as e:
                text = f"exception handled form existing_channels_handler_by_importance() function: \n\n{e}"
                client.send_message(chromusic_log_id, text)
            finally:
                text = f"existing_channels_handler_by_importance finished and will start again soon\n\n" \
                       f"importance: {importance}"
                # client.send_message("me", text)
                time.sleep(30)
    except Exception as e:
        text = f"out of the while in the existing_channels_handler_by_importance handled and will revoked again in 15 sec.\n\n" \
               f"importance: {importance}\n\n" \
               f"exception details:\n" \
               f"{e}"
        client.send_message(chromusic_log_id, text)
    finally:
        time.sleep(15)
        existing_channels_handler_by_importance(client, importance)

def existing_channels_handler_by_importance_recent_messages(client, importance):
    """

    :param client:
    :param importance:
    :return:
    """
    while 1:
        try:
            print("existing_channels_handler_by_importance_recent_messages started ...")

            res = es.search(index="channel", body={
                "query": {
                    "match": {"importance": importance}
                },
                "sort": {
                    "last_indexed_offset_date": "asc"
                }
            })
            starting_time = int(time.time())
            args = "recently"
            for _channel in res["hits"]["hits"]:
                try:
                    # Every time only lets the crawler to work 3 hours at max
                    if int(time.time()) - starting_time > timedelta(hours=2).total_seconds():
                        if importance > 0:
                            delay = timedelta(minutes=20).total_seconds()
                            time.sleep(delay)

                    channel_db = es.get('channel', id=_channel['_id'], ignore=404)
                    print(f"after existing indexer with client {client}\n{channel_db}")
                    if int(channel_db["_source"]["importance"]) > 0:
                        try:
                            es.indices.refresh(index="global_control")
                            status_res = es.get(index="global_control", doc_type="indexing_flag",
                                                id=_channel["_id"])
                            is_being_indexed = status_res["_source"]["indexing"]
                            print("is being indexed: ", is_being_indexed)
                            if is_being_indexed == True:
                                continue
                            else:
                                flag_update_res = es.update(index="global_control", doc_type="indexing_flag",
                                                            id=_channel["_id"], body={
                                        "script": {
                                            "inline": "ctx._source.indexing = params.indexing;",
                                            "lang": "painless",
                                            "params": {
                                                "indexing": True,
                                            }
                                        }
                                    }, ignore=409)
                                es.index(index="global_control", doc_type="indexing_flag", id=_channel["_id"],
                                         body={
                                             "indexing": True,
                                             "name": _channel["_source"]["username"],
                                             "importance": _channel["_source"]["importance"]
                                         }, refresh=True)
                        except Exception as e:
                            es.create(index="global_control", doc_type="indexing_flag", id=_channel["_id"], body={
                                "indexing": True,
                                "name": _channel["_source"]["username"],
                                "importance": _channel["_source"]["importance"]
                            }, refresh=True, ignore=409)
                        existing_channel_indexer(client, int(_channel["_id"]), args)
                        flag_update_res = es.update(index="global_control", doc_type="indexing_flag",
                                                    id=_channel["_id"], body={
                                "script": {
                                    "inline": "ctx._source.indexing = params.indexing;",
                                    "lang": "painless",
                                    "params": {
                                        "indexing": False,
                                    }
                                }
                            }, ignore=409)
                    time.sleep(20)
                except Exception as e:
                    text = f"exception handled form existing_channels_handler_by_importance_recent_messages() function <b>for loop</b>: \n\n{e}"
                    client.send_message(chromusic_log_id, text)
                    # continue
                finally:
                    time.sleep(15)
        except Exception as e:
            text = f"exception handled form existing_channels_handler_by_importance_recent_messages() function: \n\n{e}"
            client.send_message(chromusic_log_id, text)
            # continue
        finally:
            text = f"existing_channels_handler_by_importance_recent_messages finished and will start again soon\n\n" \
                   f"importance: {importance}"
            # client.send_message("shelbycobra2016", text)
            time.sleep(30)