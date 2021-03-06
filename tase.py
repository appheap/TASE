"""####################################################################
# Copyright (C)                                                       #
# 2021 Soran Ghaderi(soran.gdr.cs@gmail.com)                          #
# Website: soran-ghaderi.github.io                                    #
# Follow me on social media                                           #
# Twitter: twitter.com/soranghadri                                    #
# Linkedin: https://www.linkedin.com/in/soran-ghaderi/                #
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

import schedule
from elasticsearch import Elasticsearch, helpers
from pyrogram import Client, Filters, InlineKeyboardMarkup, \
    InputTextMessageContent, InlineQueryResultArticle
# from search_module.search_handling import file_retrieve_handler
from pyrogram.api import functions, types
from pyrogram.errors import FloodWait, SlowmodeWait
from static.emoji import _floppy_emoji, _clock_emoji
from index.analyzer import Analyzer
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

    indexer_bot_id = "api_id_0"
    indexer_bot_hash = "api_hash_0"

    # Create as many clients as you want (requires phone numbers and api hash and ID)
    # To get API hash and ID go to Telegram website
    # TODO: these clients must be used within a list and should be dynamic

    api_id_1 = "api_id_1"
    api_hash_1 = "api_hash_1"

    api_id_2 = "api_id_2"
    api_hash_2 = "api_hash_2"

    api_id_3 = "api_id_3"
    api_hash_3 = "api_hash_3"

    BOT_TOKEN = "Your bot toke here"  # bot_name_bot bot token

    # app_me = client_connect("admin", indexer_bot_id, indexer_bot_hash)
    app = client_connect("bot_name_1", api_id_1, api_hash_1)
    app2 = client_connect("bot_name_2", api_id_2, api_hash_2)
    client_1 = client_connect("client_1", api_id_3, api_hash_3)

    # adbot = adbot_connect(BOT_TOKEN, api_hash, api_id)
    bot = bot_connect("bot_name_bot", indexer_bot_id, indexer_bot_hash, BOT_TOKEN)
    indexer_list.append(client_1)


def client_connect(
        session_name: str = "bot_name",
        api_id: Union[int, str] = None,
        api_hash: Union[int, str] = None):
    """
    Connect the client to Telegram servers. [Client API]
    :param session_name: [str] (defaults to 'bot_name')
            Pass a string of your choice to give a name to the client session, e.g.: "*bot_name*". This name will be
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
        session_name: str = "bot_name_bot",
        api_id: Union[int, str] = None,
        api_hash: Union[int, str] = None,
        bot_token: str = None):
    """
    Connect the client to Telegram servers. [Bot API]
    :param session_name: [str] (defaults to 'bot_name_bot')
            Pass a string of your choice to give a name to the client session, e.g.: "*bot_name*". This name will be
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
        res = get_admin_log(channel_id)  # bot_name channel ID
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
        func: str = None,
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


def get_admin_log(peer: Union[int, str] = None) -> list:
    """
    Get a list of logs from the admin-logs. This method gets 'Join' and 'Leave'  events by default, but you can
    uncomment the commented items and add them to your result list.

    :param peer: Union: [id, username]. Peer username or ID.
    ex. get_admin_log("bot_name")
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


def download_guide(user):
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
            help_keyboard_text = language_handler("example_message", lang_code)
            help_markup_keyboard = language_handler("example_message_keyboard", user_data["lang_code"])
            bot.send_message(chat_id=user.id, text=help_keyboard_text,
                             reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
                             parse_mode='HTML')
    except FloodWait as e:
        res = bot.set_slow_mode(user.id, 2)
        text = f"floodwait occured in the download_guide! \n\n{e}\n\nresult: {res}"
        app.send_message(bot_name_log_id, text)
        time.sleep(e.x)
    except SlowmodeWait as e:
        res = bot.set_slow_mode(user.id, 2)
        text = f"SlowmodeWait occured in the download_guide! \n\n{e}\n\nresult: {res}"
        app.send_message(bot_name_log_id, text)
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
            app.send_message(bot_name_log_id, text)
            time.sleep(e.x)
        except SlowmodeWait as e:
            res = bot.set_slow_mode(user.id, 2)
            text = f"SlowmodeWait occured in the search handler! \n\n{e}\n\nresult: {res}"
            app.send_message(bot_name_log_id, text)
            time.sleep(e.x)
        except Exception as e:
            print(f"from search handler exception: {e}")


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
                # bot.send_audio("admin", audio_track.audio.file_id,
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
                # bot.send_audio("admin", audio_track.audio.file_id,
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

                    # bot.send_audio("me", audio_track.audio.file_id,
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
                    # bot.send_audio("me", audio_track.audio.file_id,
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
                app.send_message(bot_name_log_id, error_text)
    except Exception as e:
        text = f"outer exception from file retrieve: {e}"
        app.send_message(bot_name_log_id, text)


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
        resc = es.update(index="channel", id=bot_name_users_files_id, body={
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
        tokens = re.split(":|,| |\n|-|;|??", text)
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
                client.send_message(bot_name_log_id, text)
                # continue
            finally:
                time.sleep(30)
    except Exception as e:
        text = f"exception handled from out of while in daily_gathered_channels_controller() function: \n\n{e}"
        client.send_message(bot_name_log_id, text)
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
                        client.send_message(bot_name_log_id, text)
                        time.sleep(15)

            except Exception as e:
                text = f"exception handled form existing_channels_handler_by_importance() function: \n\n{e}"
                client.send_message(bot_name_log_id, text)
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
        client.send_message(bot_name_log_id, text)
    finally:
        time.sleep(15)
        existing_channels_handler_by_importance(client, importance)


def existing_channels_handler_by_importance_recent_messages(client: object, importance: int):
    """
    This function retrieves channels from DB by importance and updates their indexing in reverse mode (from recent
    to previous).
    :param client: Telegram client
    :param importance: The target importance of the channels to be retrieved from DB
    :return: -
    """
    try:
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
                                # break

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
                        client.send_message(bot_name_log_id, text)
                    finally:
                        time.sleep(15)

            except Exception as e:
                text = f"exception handled form existing_channels_handler_by_importance_recent_messages() function: \n\n{e}"
                client.send_message(bot_name_log_id, text)
            finally:
                text = f"existing_channels_handler_by_importance_recent_messages finished and will start again soon\n\n" \
                       f"importance: {importance}"
                # client.send_message("me", text)
                time.sleep(30)
    except Exception as e:
        text = f"out of the while in the existing_channels_handler_by_importance_recent_messages handled and will revoked again in 15 sec.\n\n" \
               f"importance: {importance}\n\n" \
               f"exception details:\n" \
               f"{e}"
        client.send_message(bot_name_log_id, text)
    finally:
        time.sleep(15)
        existing_channels_handler_by_importance_recent_messages(client, importance)


def existing_channel_indexer(client: object, channel_id: int, *args: list) -> bool:
    """
    This function indexes channels that already exist in the database and updates their last indexing status
    :param client: Telegram client
    :param channel_id: ID of the previously stored target channel to continue its indexing
    :param args: Other arguments to pass
    :return: True on success otherwise, False
    """
    try:
        print("existing channel indexer started ...")
        _ch_from_es = es.get(index="channel", id=channel_id)
        print(f"_ch_from_es: {_ch_from_es}")
        current_channel_offset_date = int(_ch_from_es['_source']['last_indexed_offset_date'])
        importance = int(_ch_from_es['_source']['importance'])
        channel_username = _ch_from_es['_source']['username']
        lenth_of_history = len(client.get_history(channel_username))
        text = f"channel_id: {channel_id}\n\n" \
               f"ch from es: {_ch_from_es}\n\n" \
               f"importance: {importance}\n\n" \
               f"channel_username: {channel_username}\n\n" \
               f"len of history: {lenth_of_history}"
        # print(f"text: after using client: {text}") # works until here!
        time.sleep(3)
        # client.send_message("admin", text)
        if importance > 0:
            # print("current_channel_offset_date: ", current_channel_offset_date)
            # print(f"indexing existing channel: {_ch_from_es['_source']['title']} started ...")
            # print(f"indexing existing channel: {_ch_from_es['_source']['username']} started ...")
            # print(f"works_until here {channel_username}")
            if lenth_of_history < 100:
                # print(f"works_until here less than 100 {channel_username}")
                # print("channel_with_less_than_100_posts_deleted: ", es.get(index="channel", id=channel))
                res = es.delete(index="channel", id=channel_id, ignore=[409, 400])
                # print("deleted_with_less_than_100: ", res)

            else:
                audio_file_indexer(client, channel_id, current_channel_offset_date, *args)
                # print(f"works_until here after audio file indexer:{channel_username}")
                # print(f"indexing existing channel: {_ch_from_es['_source']['title']} finished ...")
        print("existing channel indexer finished ...")
        time.sleep(3)
        return True
    except Exception as e:
        text = f"exception handled form existing_channel_indexer() function: \n\n{e}"
        if not (str(e).__contains__("NotFoundError(404,") or
                str(e).__contains__("not supported")):
            client.send_message(bot_name_log_id, text)
        return False


def new_channel_indexer(client: object, channels_username: list, db_index: str):
    """
    Index brand new channels (not existing in the database)
    :param client: Telegram client
    :param channels_username: A list of channels' usernames to be indexed
    :param db_index: Database index (Either from 'future_channel' or 'channel_buffer')
    :return: -
    """
    try:
        if len(channels_username) > 0:
            print(f"new channel indexer started ... {channels_username}")
            starting_time = int(time.time())
            for channel_username in channels_username:
                print(f"channel_username: {channel_username}")
                # Every time only lets the crawler to work 3 hours at max
                try:
                    # channel_id = es.get(index=db_index, id=channel_username)["_source"]["id"]
                    if int(time.time()) - starting_time > timedelta(hours=4).total_seconds():
                        delay = timedelta(minutes=13).total_seconds()
                        time.sleep(delay)
                        # break
                    # print("in the new indexer")

                    if int(es.count(index="channel", body={"query": {
                        "match": {
                            "username": channel_username
                        }
                    }})['count']) == 0:

                        # print("sleeping for 5 seconds after getting channel info ...")
                        time.sleep(4)
                        try:
                            members_count = client.get_chat_members_count(channel_username)

                            # continue
                        except Exception as e:
                            es.delete(db_index, id=channel_username, ignore=404)
                            print(f"couldn't find the username in {db_index} index")
                            continue

                        try:
                            time.sleep(5)
                            chat = client.get_chat(channel_username)
                            time.sleep(5)
                        except Exception as e:

                            print(f"handled exception from new_channel_indexer(): {e}")
                            try:
                                es.delete(db_index, id=channel_username, ignore=404)
                                # continue
                            except Exception as e:

                                print(f"couldn't find the username in {db_index} index")
                                # continue

                        # app.send_message("me", f"time spent indexing {chat} " # up
                        #                        f"channel is {starting_time - int(time.time())} seconds")
                        print(f"indexing: {chat.username}")

                        # analyze it
                        # print("sleeping for 1 seconds after getting channel members ...")
                        time.sleep(1)
                        channel_analyse = Analyzer(client.get_history(channel_username), members_count)
                        importance = channel_analyse.channel_analyzer()
                        if len(client.get_history(chat.id)) > 99:
                            es.indices.refresh(index="channel")
                            res = es.create("channel", id=chat.id, body={
                                "title": chat.title,
                                "username": chat.username,
                                "importance": importance,
                                "indexed_from_audio_count": 0,
                                "last_indexed_offset_date": 0,
                                "downloaded_from_count": 0,
                            }, refresh=True, ignore=409)
                            # time.sleep(3)
                            if importance > 0:
                                # ----------- new_changes -----------------
                                try:
                                    es.indices.refresh(index="global_control")
                                    status_res = es.get(index="global_control", doc_type="indexing_flag",
                                                        id=chat.id)
                                    is_being_indexed = status_res["_source"]["indexing"]
                                    print("is being indexed: ", is_being_indexed)
                                    if is_being_indexed == True:
                                        continue
                                    else:
                                        flag_update_res = es.update(index="global_control", doc_type="indexing_flag",
                                                                    id=chat.id, body={
                                                "script": {
                                                    "inline": "ctx._source.indexing = params.indexing;",
                                                    "lang": "painless",
                                                    "params": {
                                                        "indexing": True,
                                                    }
                                                }
                                            }, ignore=409)
                                except Exception as e:
                                    es.create(index="global_control", doc_type="indexing_flag", id=chat.id,
                                              body={
                                                  "indexing": True,
                                                  "name": chat.username,
                                                  "importance": importance
                                              }, refresh=True, ignore=409)
                                # ----------- new_changes -----------------
                                audio_file_indexer(client, chat.id, offset_date=0)
                                # ----------- new_changes -----------------
                                flag_update_res = es.update(index="global_control", doc_type="indexing_flag",
                                                            id=chat.id, body={
                                        "script": {
                                            "inline": "ctx._source.indexing = params.indexing;",
                                            "lang": "painless",
                                            "params": {
                                                "indexing": False,
                                            }
                                        }
                                    }, ignore=409)
                                # ----------- new_changes ----------------
                            else:
                                try:
                                    es.delete(db_index, id=channel_username, ignore=404)
                                    # continue
                                except Exception as e:
                                    text = f"it's not in the {db_index} two to the last except in the main if in the for loop \n\n{e}"
                                    client.send_message(bot_name_log_id, text)
                                    print(
                                        "it's not in the future_channel/channel_buffer two to the fffflast except in the main if in the for loop")
                                    # continue

                        else:
                            # print("The number of the shared posts is less than 100")
                            try:
                                es.delete(db_index, id=channel_username, ignore=404)
                                # continue
                            except Exception as e:
                                text = f"it's not in the future_channel/channel_buffer one to the last except in the main if in the for loop \n\n{e}"
                                client.send_message(bot_name_log_id, text)
                                print(
                                    f"it's not in the future_channel/channel_buffer one to the last except in the main if in the for loop")
                                # continue
                            # print("channel successfully deleted from future_channe/channel_bufferl")
                    else:
                        # print("this is an existing channel")
                        try:
                            es.delete(db_index, id=channel_username, ignore=404)
                            # continue
                        except Exception as e:
                            text = f"it's not in the future_channel/channel_buffer last except in the main if in the for loop \n\n{e}"
                            client.send_message(bot_name_log_id, text)
                            # print(f"it's not in the future_channel/channel_buffer last except in the main if in the for loop")
                            # continue
                        # print("channel successfully deleted from future_channe/channel_bufferl")
                except Exception as e:
                    text = f"exception handled form new_channel_indexer() function <b>for loop</b>: \n\n{e}"
                    if not (str(e).__contains__("NotFoundError(404,") or
                            str(e).__contains__("not supported")):
                        client.send_message(bot_name_log_id, text)
                    # continue
                finally:
                    time.sleep(5)
    except Exception as e:
        text = f"exception handled form new_channel_indexer() function: \n\n{e}"
        app.send_message(bot_name_log_id, text)
    finally:
        text = f"new_channel_indexer() finished and will start again ..."
        # client.send_message(bot_name_log_id, text)
        time.sleep(30)


def audio_file_indexer(client: object, channel_id: int, offset_date: int, *args: str) -> bool:
    """
    Crawl and index audio files within channels
    :param client: Telegram client
    :param channel_id: ID of the current channel being indexed
    :param offset_date: Offset date of the last indexed message from the current channel
    :param args: Extra arguments: Possibly contains "recently": whether to index from recent messages(reversed) or not
    :return: True on success; otherwise False
    """
    try:

        _messages = []
        s = int(time.time())
        _last_message = None
        _counter = 0
        speed_limiter_counter = 0
        limit = 0
        reverse_index = True

        _ch_from_es = es.get(index="channel", id=channel_id)
        channel_username = _ch_from_es['_source']['username']
        if len(args) > 0:
            if args[0] == "recently":
                # print("from_bottom_up_indexing", es.get(index="channel", id=channel))
                limit = 20
                offset_date = 0
                reverse_index = False
                # _ch_from_es = es.get(index="channel", id=channel_id)
                # channel_username = _ch_from_es['_source']['username']
                if len(client.get_history(channel_username)) < 100:
                    print("channel_with_less_than_100_posts_deleted: ", es.get(index="channel", id=channel_id))
                    res = es.delete("channel", id=channel_id, ignore=404)
                    # print("deleted_with_less_than_100", res)
                    return None
        indexed_from_counter = 0
        # print("from audio, indexing: ", client.get_chat(channel_username))
        for message in client.iter_history(channel_username, limit=limit, offset_date=offset_date,
                                           reverse=reverse_index):
            try:
                _date = int(message.date)
                # sleep 2 seconds every 35 iteration
                if speed_limiter_counter > 99:
                    speed_limiter_counter = 0
                    time.sleep(2)
                if _counter > 9:
                    # client.send_message("admin", f"https://t.me/{_last_message.chat.username}/{_last_message.message_id}")
                    # client.send_message("admin", f"{_last_message.message_id}")
                    # print("in counter 34 ...")
                    try:
                        # print("before getting _date ...")
                        if reverse_index and not _last_message == None:
                            # _date = int(_last_message.date)
                            # print("date: ", _date)
                            response = es.update(index="channel", id=channel_id, body={
                                "script": {
                                    "inline": "ctx._source.last_indexed_offset_date = params.last_indexed_offset_date;",
                                    "lang": "painless",
                                    "params": {
                                        "last_indexed_offset_date": _date,
                                    }
                                }
                            }, ignore=409)
                            # print("response: ", response)
                        # print(es.get("channel", id=channel))
                    except Exception as e:
                        print(f"exception from counter: {e}")
                    # print(f"from counter if: {response}")
                    # this if is meant to slow down the indexing rate to 35 messages per sec. at max
                    if len(_messages) > 0:
                        # if not reverse_index:
                        #     print("len(_messages) > 0: ", _messages)
                        helpers.bulk(es, audio_data_generator(_messages))
                        # print("after bulk", _messages[0])

                        response = es.update(index="channel", id=channel_id, body={
                            "script": {
                                "inline": "ctx._source.indexed_from_audio_count += params.indexed_from_audio_count",
                                "lang": "painless",
                                "params": {
                                    "indexed_from_audio_count": len(_messages)
                                }
                            }
                        }, ignore=409)

                        try:
                            if es.exists("future_channel", id=channel_username):
                                es.delete("future_channel", id=channel_username, ignore=404)
                            if es.exists("channel_buffer", id=channel_username):
                                es.delete("channel_buffer", id=channel_username, ignore=404)
                                # print(f"deleted {channel} from database successfully")
                        except Exception as e:
                            print("query didn't match any document id --> from future_channel - new channel indexer")
                            print(f"exact exception: \n{e}")
                        # print(es.get("channel", id=channel))

                        time.sleep(1)

                    _messages = []
                    _counter = 0
                    # time.sleep(1)

                if message.audio:
                    # if limit == 20:
                    # print("from_bottom_up_indexing message added", message.chat.username,
                    #       es.count(index="audio", body={"query": {
                    #           "match": {
                    #               "file_id": message.audio.file_id
                    #           }}}), message.audio.title)
                    # --> following if is as an alternative
                    # if not es.exists(index="audio", id=str(message.audio.file_id[8:30:3]).replace("-", "d"))
                    if int(es.count(index="audio_files", body={"query": {
                        "match": {
                            "file_id": message.audio.file_id
                        }
                    }})['count']) == 0:
                        _messages.append(message)
                        # if limit == 20:
                        # print("message appended", len(_messages))
                    # ----- following 3 ifs are for extracting channels: ----------
                    if message.forward_from_chat:
                        forwarded_from_channel_extractor(client, message)  # this func will extract channels' IDs
                    if message.caption_entities:
                        caption_entities_channel_extractor(client, message)
                    if message.text:
                        channel_name_extractor(client, message.text)
                    if message.caption:
                        channel_name_extractor(client, message.caption)
                _counter += 1
                _last_message = message
                speed_limiter_counter += 1

            except FloodWait as e:
                text = f"FloodWait from audio_file_indexer: \n\n{e}"
                client.send_message(bot_name_log_id, text)
                # print("from audio file indexer: Flood wait exception: ", e)
                time.sleep(e.x)
            except SlowmodeWait as e:
                text = f"SlowmodeWait from audio_file_indexer: \n\n{e}"
                client.send_message(bot_name_log_id, text)
                # print("from audio file indexer: Slowmodewait exception: ", e)
                time.sleep(e.x)
            except TimeoutError as e:
                text = f"TimeoutError from audio_file_indexer: \n\n{e}"
                client.send_message(bot_name_log_id, text)
                # print("Timeout error: sleeping for 20 seconds: ", e)
                time.sleep(20)
                # pass
            except ConnectionError as e:
                text = f"ConnectionError from audio_file_indexer: \n\n{e}"
                client.send_message(bot_name_log_id, text)
                # print("Connection error - sleeping for 40 seconds: ", e)
            except Exception as e:
                client.send_message(bot_name_log_id,
                                    f"from audio_file_indexer: maybe encountered a service message in the for loop\n\n {e}")
                print("from audio file indexer: ", e)

        return True
    except FloodWait as e:
        text = f"FloodWait from audio_file_indexer. outer try/except: \n\n{e}"
        client.send_message(bot_name_log_id, text)
        # print("from audio file indexer: Flood wait exception: ", e)
        time.sleep(e.x)
        return False
    except SlowmodeWait as e:
        text = f"SlowmodeWait from audio_file_indexer. outer try/except: \n\n{e}"
        client.send_message(bot_name_log_id, text)
        # print("from audio file indexer: Slowmodewait exception: ", e)
        time.sleep(e.x)
        return False
    except TimeoutError as e:
        text = f"TimeoutError from audio_file_indexer. outer try/except: \n\n{e}"
        client.send_message(bot_name_log_id, text)
        # print("Timeout error: sleeping for 20 seconds: ", e)
        time.sleep(20)
        return False
    except ConnectionError as e:
        text = f"ConnectionError from audio_file_indexer. outer try/except: \n\n{e}"
        client.send_message(bot_name_log_id, text)
        # print("Connection error - sleeping for 40 seconds: ", e)
        return False
    except Exception as e:
        client.send_message(bot_name_log_id,
                            f" outer try/except from audio_file_indexer: maybe encountered a service message\n\n {e}")
        print("from audio file indexer: ", e)
        return False


def main_join_left_checker_controller():
    """
    Control members' joining actions and handle exceptions
    :return: -
    """

    try:
        while 1:
            try:
                delay = random.randint(5, 7)
                # check_new_member_join_count(bot_name_id)
                time.sleep(1)
                check_new_member_join_count(bot_name_fa_id)
                time.sleep(delay)
            except Exception as e:
                text = f"exception handled form main_join_left_checker_controller() function <b>for loop</b>: \n\n{e}"
                app.send_message(bot_name_log_id, text)


    except Exception as e:
        text = f"exception handled form main_join_left_checker_controller() function <b>for loop</b>: \n\n{e}"
        app.send_message(bot_name_log_id, text)
        main_join_left_checker_controller()
    finally:
        text = f"join/left checker controller has stopped: \n\n"
        app.send_message("admin", text)


def main_index_scheduler_controller():
    """
    Manually schedule to index channels
    :return: -
    """
    try:
        print("index scheduler controller")
        # schedule.every(5).to(7).seconds.do(check_new_member_join_count, bot_name_id)
        schedule.every(5).to(7).seconds.do(check_new_member_join_count, bot_name_fa_id)
        schedule.every(1).seconds.do(check_new_member_join_count, bot_name_id)
        schedule.every(1).seconds.do(check_new_member_join_count, bot_name_fa_id)

        # -------------------------- Daily new gathered channels ------------------------
        schedule.every(1).day.at("00:00").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("03:30").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("07:00").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("10:30").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("14:00").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("17:30").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("21:00").do(daily_gathered_channels_controller)
        schedule.every(1).day.at("01:30").do(existing_channels_handler_by_importance, 6)
        # importance 5 channels schedule: sat, sun, mon, tue, fri
        schedule.every(1).minutes.do(daily_gathered_channels_controller)

        schedule.every(30).minutes.do(daily_gathered_channels_controller)
        schedule.every(3).hours.do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every(6).hours.do(existing_channels_handler_by_importance_recent_messages, 4)
        schedule.every(10).hours.do(existing_channels_handler_by_importance_recent_messages, 3)
        schedule.every(15).hours.do(existing_channels_handler_by_importance_recent_messages, 2)
        schedule.every(24).hours.do(existing_channels_handler_by_importance_recent_messages, 1)
        schedule.every(30).minutes.do(existing_channels_handler_by_importance, 5)
        schedule.every(1).hours.do(existing_channels_handler_by_importance, 4)
        schedule.every(3).hours.do(existing_channels_handler_by_importance, 3)
        schedule.every(5).hours.do(existing_channels_handler_by_importance, 2)
        schedule.every(10).hours.do(existing_channels_handler_by_importance, 1)

        schedule.every().saturday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().saturday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().saturday.at("04:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().saturday.at("04:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().saturday.at("09:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().saturday.at("14:30").do(existing_channels_handler_by_importance, 5)

        schedule.every().sunday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().sunday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().sunday.at("04:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().sunday.at("09:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().sunday.at("09:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().sunday.at("14:30").do(existing_channels_handler_by_importance, 5)

        schedule.every().monday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().monday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().monday.at("04:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().monday.at("09:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().monday.at("14:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().monday.at("14:30").do(existing_channels_handler_by_importance_recent_messages, 5)

        schedule.every().tuesday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().tuesday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().tuesday.at("04:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().tuesday.at("09:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().tuesday.at("09:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().tuesday.at("14:30").do(existing_channels_handler_by_importance, 5)

        schedule.every().wednesday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().wednesday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().wednesday.at("04:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().wednesday.at("09:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().wednesday.at("14:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().wednesday.at("14:30").do(existing_channels_handler_by_importance_recent_messages, 5)

        schedule.every().thursday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().thursday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().thursday.at("04:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().thursday.at("09:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().thursday.at("14:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().thursday.at("14:30").do(existing_channels_handler_by_importance_recent_messages, 5)

        schedule.every().friday.at("01:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().friday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        schedule.every().friday.at("04:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().friday.at("09:30").do(existing_channels_handler_by_importance, 5)
        schedule.every().friday.at("14:30").do(existing_channels_handler_by_importance, 5)
        # schedule.every().friday.at("14:30").do(existing_channels_handler_by_importance_recent_messages, 5)
        # ---------------------end-----------------------------

        # importance 4 channels schedule: sat , mon, wed, thr
        schedule.every().saturday.at("07:30").do(existing_channels_handler_by_importance, 4)
        schedule.every(1).hours.do(existing_channels_handler_by_importance_recent_messages, 4)
        # schedule.every().saturday.at("07:30").do(existing_channels_handler_by_importance_recent_messages, 4)
        schedule.every().saturday.at("11:30").do(existing_channels_handler_by_importance, 4)
        schedule.every().saturday.at("15:30").do(existing_channels_handler_by_importance, 4)

        schedule.every().monday.at("07:30").do(existing_channels_handler_by_importance, 4)
        # schedule.every().monday.at("07:30").do(existing_channels_handler_by_importance_recent_messages, 4)
        schedule.every().monday.at("11:30").do(existing_channels_handler_by_importance, 4)
        schedule.every().monday.at("15:30").do(existing_channels_handler_by_importance, 4)

        schedule.every().wednesday.at("07:30").do(existing_channels_handler_by_importance, 4)
        # schedule.every().wednesday.at("07:30").do(existing_channels_handler_by_importance_recent_messages, 4)
        schedule.every().wednesday.at("11:30").do(existing_channels_handler_by_importance, 4)
        schedule.every().wednesday.at("15:30").do(existing_channels_handler_by_importance, 4)

        schedule.every().thursday.at("07:30").do(existing_channels_handler_by_importance, 4)
        # schedule.every().thursday.at("07:30").do(existing_channels_handler_by_importance_recent_messages, 4)
        schedule.every().thursday.at("11:30").do(existing_channels_handler_by_importance, 4)
        schedule.every().thursday.at("15:30").do(existing_channels_handler_by_importance, 4)
        # ---------------------end-----------------------------

        # importance 3 channels schedule: sun , tue, thr
        schedule.every().sunday.at("07:30").do(existing_channels_handler_by_importance, 3)
        schedule.every(3).hours.do(existing_channels_handler_by_importance_recent_messages, 3)
        # schedule.every().sunday.at("07:30").do(existing_channels_handler_by_importance_recent_messages, 3)
        schedule.every().sunday.at("11:30").do(existing_channels_handler_by_importance, 3)
        schedule.every().sunday.at("15:30").do(existing_channels_handler_by_importance, 3)

        schedule.every().tuesday.at("07:30").do(existing_channels_handler_by_importance, 3)
        # schedule.every().tuesday.at("07:30").do(existing_channels_handler_by_importance_recent_messages, 3)
        schedule.every().tuesday.at("11:30").do(existing_channels_handler_by_importance, 3)
        schedule.every().tuesday.at("15:30").do(existing_channels_handler_by_importance, 3)

        schedule.every().thursday.at("01:30").do(existing_channels_handler_by_importance, 3)
        # schedule.every().thursday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 3)
        schedule.every().thursday.at("11:30").do(existing_channels_handler_by_importance, 3)
        schedule.every().thursday.at("15:30").do(existing_channels_handler_by_importance, 3)
        # ---------------------end-----------------------------

        # importance 2 channels schedule: tue, fri
        schedule.every().tuesday.at("10:30").do(existing_channels_handler_by_importance, 2)
        schedule.every(10).hours.do(existing_channels_handler_by_importance_recent_messages, 2)
        schedule.every().tuesday.at("10:30").do(existing_channels_handler_by_importance_recent_messages, 2)
        schedule.every().friday.at("07:30").do(existing_channels_handler_by_importance, 2)
        # ---------------------end-----------------------------

        # importance 1 channels schedule: wed
        schedule.every().wednesday.at("01:30").do(existing_channels_handler_by_importance, 1)
        schedule.every(20).hours.do(existing_channels_handler_by_importance_recent_messages, 1)
        schedule.every().wednesday.at("01:30").do(existing_channels_handler_by_importance_recent_messages, 1)
        # ---------------------end-----------------------------

        # importance 1 channels schedule: wed
        schedule.every(15).days.at("14:30").do(existing_channels_handler_by_importance, 0)
        # ---------------------end-----------------------------

        while 1:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        app.send_message(bot_name_log_id, f"exception from scheduler \n {e}")
        # main_index_scheduler_controller()


def reset_last_index_offset_date():
    """
    Reset the last index date and the number of indexed files for channels after finishing indexing
    :return: True on success
    """
    res = helpers.scan(es,
                       query={"query": {"match_all": {}}},
                       index="channel", size=10000,
                       scroll='2m', )
    for hit in res:
        channel_id = hit["_id"]
        response = es.update(index="channel", id=channel_id, body={
            "script": {
                "inline": "ctx._source.last_indexed_offset_date = params.last_indexed_offset_date;"
                          "ctx._source.indexed_from_audio_count = params.indexed_from_audio_count;",
                "lang": "painless",
                "params": {
                    "last_indexed_offset_date": 0,
                    "indexed_from_audio_count": 0,
                }
            }
        }, ignore=409)

    return True


def buffer_gathered_channels_controller(client):
    """
    Check the gathered channel candidates in the buffer and indexes the valid ones.
    notice: usernames are gathered optimistically (they may or may not be valid usernames)
    :param client: Telegram client
    :return: -
    """
    try:
        while 1:
            try:
                _channels_list_username = []
                print("existing channels now running  ...")
                res = helpers.scan(es,
                                   query={"query": {"match_all": {}}},
                                   index="channel_buffer")

                for buffered_candidate_channel in res:
                    _channel_username = _channels_list_username.append(buffered_candidate_channel["_id"])
                try:
                    new_channel_indexer(client, _channels_list_username, "channel_buffer")
                except FloodWait as e:
                    text = f"FloodWait from buffer_gathered_channels_controller \n\n{e}"
                    client.send_message(bot_name_log_id, text)
                    # print("from audio file indexer: Flood wait exception: ", e)
                    time.sleep(e.x)
                except SlowmodeWait as e:
                    text = f"SlowmodeWait from buffer_gathered_channels_controller \n\n{e}"
                    client.send_message(bot_name_log_id, text)
                    # print("from audio file indexer: Slowmodewait exception: ", e)
                    time.sleep(e.x)
                except TimeoutError as e:
                    text = f"TimeoutError from buffer_gathered_channels_controller \n\n{e}"
                    client.send_message(bot_name_log_id, text)
                    # print("Timeout error: sleeping for 20 seconds: ", e)
                    time.sleep(20)
                    # pass
                except ConnectionError as e:
                    text = f"ConnectionError from buffer_gathered_channels_controller\n\n{e}"
                    client.send_message(bot_name_log_id, text)
                    # print("Connection error - sleeping for 40 seconds: ", e)
                except Exception as e:
                    print(f"got exception in buffer_gathered_channels_controller(): {_channel_username} \n\n{e}")
                    es.delete(index="channel_buffer", id=_channel_username, ignore=404)
                time.sleep(30)
                # print("new indexing channels started ... !")
            except Exception as e:
                text = f"exception handled form buffer_gathered_channels_controller() function: \n\n{e}"
                client.send_message(bot_name_log_id, text)
                # continue
            finally:
                time.sleep(30)
    except Exception as e:
        text = f"Exception handled out of the while in the buffer_gathered_channels_controller() \n\n{e}"
        client.send_message(bot_name_log_id, text)
        buffer_gathered_channels_controller(client)


def invalid_title_performer_remover(client):
    """
    Detect and remove fake audio-title and audio-performer information. (In case they were channel's username or title).
    :param client: Telegram client
    :return: -
    """
    try:
        while 1:
            try:
                res = es.search(index="audio_files", body={
                    "query": {
                        "match_all": {}
                    },
                    "sort": {
                        "last_indexed_offset_date": "desc"
                    }
                })
                starting_time = int(time.time())
                for audio_file in res["hits"]["hits"]:
                    audio = audio_file["_source"]
                    # print(f"_channel: {_channel}")
                    # Every time only lets the crawler to work 3 hours at max
                    try:
                        if str(audio["chat_username"]).replace("_", " ") in audio["performer"]:
                            es.update(index="audio_files", )
                            es.update(index="audio_files", id=audio_file["_id"], body={
                                "script": {
                                    "inline": "ctx._source.performer = params.performer;",
                                    "lang": "painless",
                                    "params": {
                                        "performer": " "
                                    }
                                }
                            })
                        elif str(audio["chat_username"]).replace("_", " ") in audio["title"]:
                            es.update(index="audio_files", id=audio_file["_id"], body={
                                "script": {
                                    "inline": "ctx._source.title = params.title;",
                                    "lang": "painless",
                                    "params": {
                                        "title": " "
                                    }
                                }
                            })
                    except Exception as e:
                        text = f"Exception in the for loop from invalid_title_performer_remover() \n\n{e}"
                        client.send_message(bot_name_log_id, text)
            except Exception as e:
                text = f"Exception in the while loop from invalid_title_performer_remover() \n\n{e}"
                client.send_message(bot_name_log_id, text)

    except Exception as e:
        text = f"encountered exception out of the while loop in the invalid_title_performer_remover()\n\n{e}"
        print(text)
        client.send_message(bot_name_log_id, text)


def audio_file_forwarder(client):
    """
    Forward audio files to a channel as backup (* optional to use)
    :param client: Telegram client
    :return: -
    """
    i = 0
    for file in client.iter_history(-1001381641403, reverse=True):
        try:
            if file.audio:
                if i % 5000 == 0:
                    print(f"{i} audio files forwarded so far!")
                if i % 65 == 0:
                    time.sleep(2)
                client.forward_messages("Audiowarehouse", -1001381641403, file.message_id)
                i += 1
        except FloodWait as e:
            text = f"FloodWait from audio_file_forwarder: \n\n{e}"
            client.send_message(bot_name_log_id, text)
            # print("from audio file indexer: Flood wait exception: ", e)
            time.sleep(e.x)
        except SlowmodeWait as e:
            text = f"SlowmodeWait from audio_file_forwarder: \n\n{e}"
            client.send_message(bot_name_log_id, text)
            # print("from audio file indexer: Slowmodewait exception: ", e)
            time.sleep(e.x)
        except TimeoutError as e:
            text = f"TimeoutError from audio_file_forwarder: \n\n{e}"
            client.send_message(bot_name_log_id, text)
            # print("Timeout error: sleeping for 20 seconds: ", e)
            time.sleep(20)
            # pass
        except ConnectionError as e:
            text = f"ConnectionError from audio_file_forwarder: \n\n{e}"
            client.send_message(bot_name_log_id, text)
            # print("Connection error - sleeping for 40 seconds: ", e)
        except Exception as e:
            client.send_message(bot_name_log_id,
                                f"from audio_file_forwarder: \n\n {e}")
            print("from audio file indexer: ", e)


def main():
    """
    Main function of the search engine. Create and initiate indexes and create necessary docs and flags.
    Revoke main_functions_revoker()
    :return: -
    """
    # executor.submit(daily_gathered_channels_controller)
    # executor.submit(main_index_scheduler_controller)

    # -1001007590017
    starting_time = int(time.time())
    # res = es.indices.delete(index="to_index")
    # res = es.indices.delete(index="audio_files")
    # res = es.indices.delete(index="channel")
    # es.indices.delete("admin_log_control")

    # res = es.count(index="channel_buffer", body={
    #     "query": {
    #         "match_all": {}
    #     }
    # })["count"]
    # print(f"count of channel_buffer: {res}")
    for i in es.indices.get("*"):
        print("index name: ", i)
    #     res = es.indices.delete(index=i)
    to_index = es.indices.create(
        index="to_index",
        body=to_index_mapping,
        ignore=400  # ignore 400 already exists code
    )
    future_channel = es.indices.create(
        index="future_channel",
        body=future_channel_mapping,
        ignore=400  # ignore 400 already exists code
    )
    channel_buffer = es.indices.create(
        index="channel_buffer",
        body=channel_buffer_mapping,
        ignore=400  # ignore 400 already exists code
    )
    # audio = es.indices.create(
    #     index="audio",
    #     body=audio_files_mapping,
    #     ignore=400  # ignore 400 already exists code
    # )
    audio_files = es.indices.create(
        index="audio_files",
        body=audio_files_mapping,
        ignore=400  # ignore 400 already exists code
    )
    channel = es.indices.create(
        index="channel",
        body=channel_mapping,
        ignore=400  # ignore 400 already exists code
    )
    user = es.indices.create(
        index="user",
        body=channel_mapping,
        ignore=400  # ignore 400 already exists code
    )
    admin_log = es.indices.create(
        index="admin_log_control",
        body=admin_log_control_mapping,
        ignore=400
    )
    # es.indices.delete("user_lists")
    # es.indices.delete("playlist")
    user_lists = es.indices.create(
        index="user_lists",
        body=user_list_mapping,
        ignore=400
    )
    playlists = es.indices.create(
        index="playlist",
        body=playlist_mapping,
        ignore=400
    )

    res = es.create(index="admin_log_control", id=bot_name_id, body={  # bot_name channel ID: -1001357823954
        "last_offset_date": 0,
        "members_count": 0
    }, ignore=409)
    # print(f"from main: ", res)
    es.create(index="admin_log_control", id=bot_name_fa_id, body={  # bot_name channel ID: -1001357823954
        "last_offset_date": 0,
        "members_count": 0
    }, ignore=409)
    # es.delete("user", id=165802777)
    es.create(index="user", id=165802777, body={  # my ID: 165802777 --> username: admin
        "first_name": "Soran",
        "username": "admin",
        "date_joined": int(time.time()),
        "downloaded_audio_count": 0,
        "lang_code": "en",
        "limited": False,
        "role": "owner",
        "coins": 0,
        "last_active_date": int(time.time()),
        "is_admin": True,
        "sex": "neutral",
        "country": "US"
    }, ignore=409)
    es.update(index="user", id=165802777, body={
        "script": {
            "inline": "ctx._source.role = params.role;",
            "lang": "painless",
            "params": {
                "role": "owner"
            }
        }
    }, ignore=409)

    try:
        res = helpers.scan(es,
                           query={"query": {"match": {
                               "indexing": True
                           }}},
                           index="global_control",
                           )

        for _channel in res:
            flag_update_res = es.update(index="global_control", doc_type="indexing_flag", id=_channel["_id"], body={
                "script": {
                    "inline": "ctx._source.indexing = params.indexing;",
                    "lang": "painless",
                    "params": {
                        "indexing": False,
                    }
                }
            }, ignore=409)
    except Exception as e:
        print(e)
    print("before revoker() ...")

    main_functions_revoker()


def main_functions_revoker():
    """
    Revoke indexers, joining-status handlers, etc. and associate respective clients (manually) (* needs to be
    re-written dynamically.
    :return: -
    """

    executor.submit(main_join_left_checker_controller)
    executor.submit(daily_gathered_channels_controller, app)
    executor.submit(daily_gathered_channels_controller, app2)
    # executor.submit(buffer_gathered_channels_controller, app2)
    for app_instance in indexer_list:
        executor.submit(buffer_gathered_channels_controller, app_instance)
        executor.submit(daily_gathered_channels_controller, app_instance)
        # executor.submit(audio_file_forwarder, app_instance)

    executor.submit(existing_channels_handler_by_importance, app, 5)
    executor.submit(existing_channels_handler_by_importance, app2, 4)
    executor.submit(existing_channels_handler_by_importance, app_instance, 4)
    executor.submit(existing_channels_handler_by_importance, app, 3)
    executor.submit(existing_channels_handler_by_importance, app2, 2)
    # executor.submit(existing_channels_handler_by_importance, app_instance, 2)
    executor.submit(existing_channels_handler_by_importance, app2, 1)
    executor.submit(existing_channels_handler_by_importance_recent_messages, app, 5)
    # executor.submit(existing_channels_handler_by_importance_recent_messages, app_instance, 5)
    executor.submit(existing_channels_handler_by_importance_recent_messages, app2, 4)
    executor.submit(existing_channels_handler_by_importance_recent_messages, app_instance, 4)
    executor.submit(existing_channels_handler_by_importance_recent_messages, app, 3)
    executor.submit(existing_channels_handler_by_importance_recent_messages, app2, 2)
    # executor.submit(existing_channels_handler_by_importance_recent_messages, app_instance, 2)
    executor.submit(existing_channels_handler_by_importance_recent_messages, app, 1)
    # time.sleep(20)
    # executor.submit(daily_gathered_channels_controller)
    # time.sleep(20)
    # executor.submit(daily_gathered_channels_controller)


def initialize():
    """
    Define and initialize global variables and run the main function.
    :return: True on success
    """
    global editing_flag
    global executor
    global bot_name_id
    global bot_name_fa_id
    global datacenter_id
    global bot_name_log_id
    global bot_name_users_files_id
    global speed_limiter

    speed_limiter = 0
    bot_name_log_id = "your channel ID or username to which the logs are sent"
    datacenter_id = "your channel ID or username; used as a warehouse channel"
    editing_flag = False
    bot_name_users_files_id = "your channel id or username which is used as a warehouse for " \
                              "user-sent audio files"
    bot_name_id = "your channel ID or username [num 1]"
    bot_name_fa_id = "your channel ID or username [num 2]"

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=27)
    telegramAPI_connect()
    # print(app.get_me())
    db_connect()

    try:
        executor.submit(main)
    except Exception as e:
        app.send_message(bot_name_log_id, str(e))

    return True


if __name__ == '__main__':
    initialize()


def choose_language(bot, message):
    """
    Ask users to choose a language among a menu shows a list of available languages.
    :param bot: Telegram bot client
    :param message: Telegram message object
    :return: True on success
    """
    try:
        user_data = es.get(index="user", id=message.from_user.id)["_source"]
        lang_code = user_data["lang_code"]
    except Exception as e:
        lang_code = "en"
        print("exception from choose language", e)
        pass

    markup_list = language_handler("button_language_list", lang_code)
    text = language_handler("choose_language_text", lang_code, message.from_user.first_name)
    exception_handler(bot.send_message(chat_id=message.from_user.id,
                                       text=text,
                                       reply_markup=InlineKeyboardMarkup(markup_list),
                                       parse_mode='HTML'))

    return True


@bot.on_inline_query()
def inine_res(bot: object, query: object) -> object:
    """
    Handle the coming inline messages.
    options:
        1. more_results: Return more results (up to 40 items)
        2. addtopl: Add audio file to a playlist (using "more" button in the bottom of
         each search result
        3. history: Show the last 50 searched audio files (using "history" button in "home" and "help" menu)
        4. myplaylists: Show a list of user's playlists (using "my playlists" button in "home" and "help" menu)
        5. showfiles: Show audio files within a playlist (using "show files" button in "playlist" menu)
        6. edit_title: Edit the title of a playlist (using "Edit title" button in "playlist" menu)
        7. edit_description: Edit the description of a playlist (using "Edit description" button in "playlist" menu)
        8. help_catalog: Return a list of URLs which tutorial contents can be placed
        9. Search audio files: Search audio files (requested by users without any prefix)

    :param bot: Telegram bot client
    :param query: Telegram query object
    :return: Query answers on success, report the problem otherwise
    """
    print("got inline")
    results = []
    user = query.from_user
    # if str(query.query).split(":")[1] == "playlists":
    # print(query)
    hidden_character = "????????? ???"

    try:
        lang_code = es.get("user", id=user.id)["_source"]["lang_code"]
        if es.get("user", id=user.id)["_source"]["role"] == "searcher":
            item_title = language_handler("inline_join_channel_title_text", lang_code)
            item_description = language_handler("inline_join_channel_description_text", lang_code)
            item_content = language_handler("inline_join_channel_content_text", lang_code)
            results.append(InlineQueryResultArticle(
                title=item_title,
                # description=res["_source"]["performer"],
                description=item_description,
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                # "https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                input_message_content=InputTextMessageContent(item_content, parse_mode="HTML")))
            exception_handler(
                bot.answer_inline_query(query.id, results=results,
                                        cache_time=10, switch_pm_text="bot_name",
                                        switch_pm_parameter="back_to_the_bot"))
    except Exception as e:
        try:
            item_title = language_handler("inline_start_bot_title_text", "en")
            item_description = language_handler("inline_start_bot_description_text", "en")
            item_content = language_handler("inline_start_bot_content_text", "en")
            content = f"<a href ='https://t.me/bot_name_bot'><b>bot_name bot:</b> audio file search engine</a>\n\n" \
                      f"Channel: @bot_name\n" \
                      f"Persian channel: @bot_name_fa"
            results.append(InlineQueryResultArticle(
                title=item_title,
                # description=res["_source"]["performer"],
                description=item_description,
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                # "https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                input_message_content=InputTextMessageContent(item_content, parse_mode="HTML")))
            exception_handler(
                bot.answer_inline_query(query.id, results=results,
                                        cache_time=10, switch_pm_text="Start", switch_pm_parameter="back_to_the_bot"))
        except Exception as e:
            # exception_handler(
            #     bot.answer_inline_query(query.id, results=results,
            #                             cache_time=10))
            print(f"exception from first inline result exception handler: {e}")

    back_text = language_handler("back_to_the_bot", lang_code)

    if str(query.query).__contains__("#more_results:"):

        # -------------- Setting No. 1 -----------------
        # results_list = es.search(index="audio_files", body={"query": {
        #     "multi_match": {
        #         "query": str(query.query).split("#more_results:")[-1].replace("_", ""),
        #         "fields": ["title", "performer", "file_name"],
        #         "fuzziness": "AUTO",
        #         "tie_breaker": 0.5
        #     }}}, from_=10, size=40)

        # -------------- Setting No. 2 -----------------
        # es.search(index="audio_files", body={"query": {
        #     "multi_match": {
        #         "query": processed_query,
        #         "type": "best_fields",
        #         "fields": ["title", "file_name", "performer"],  # , "caption"],
        #         # "fuzziness": "AUTO",
        #         # "tie_breaker": 0.5,
        #         "minimum_should_match": "60%"
        #     }}})
        processed_query = str(str(query.query).split("#more_results:")[-1]).replace("_", " ")

        # -------------- Setting No. 3 -----------------
        results_list = es.search(index="audio_files", body={"query": {
            "multi_match": {
                "query": processed_query,
                "type": "best_fields",
                "fields": ["title", "file_name", "performer"],  # , "caption"],
                # "fuzziness": "AUTO",
                # "tie_breaker": 0.5,
                "minimum_should_match": "60%"
            }}}, from_=0, size=50)
        res_len = int(results_list["hits"]["total"]["value"])
        if res_len > 10:
            first_index_subtract_from = 10
        else:
            first_index_subtract_from = res_len

        for index, hit in enumerate(results_list["hits"]["hits"]):
            if index + 1 > first_index_subtract_from:
                duration = timedelta(seconds=int(hit['_source']['duration']))
                d = datetime(1, 1, 1) + duration
                temp_perf_res = hit["_source"]["performer"]
                temp_titl_res = hit["_source"]["title"]
                temp_filnm_res = hit["_source"]["file_name"]
                # _title = hit["_source"]["title"]
                _performer = temp_perf_res if len(temp_perf_res) > 1 else temp_filnm_res
                _performer = textwrap.shorten(_performer, width=34, placeholder='...')
                _title = temp_titl_res if len(temp_titl_res) > 1 else temp_filnm_res
                _title = textwrap.shorten(_title, width=34, placeholder='...')

                _caption_content = language_handler("inline_file_caption", lang_code, hit)
                item_describtion = f"{hidden_character}???{_performer}\n" \
                                   f"{hidden_character}{_floppy_emoji} | {round(int(hit['_source']['file_size']) / 1_048_576, 1)} MB  " \
                                   f"{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}"  # 1000_000 MB
                item_title = hidden_character + str(index + 1) + '. ' + _title

                results.append(InlineQueryResultArticle(
                    title=item_title,
                    # description=res["_source"]["performer"],
                    description=item_describtion,
                    thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                    # "https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    # input_message_content=InputTextMessageContent(_caption_content, parse_mode="HTML")))
                    input_message_content=InputTextMessageContent(f"??????/dl_{hit['_id']}", parse_mode="HTML")))

        if res_len < 40:
            """
            If the previous search results count was less than 40 then do a fuzzy search to suggrst more results
            """
            results_list = es.search(index="audio_files", body={"query": {
                "multi_match": {
                    "query": processed_query,
                    "type": "best_fields",
                    "fields": ["title", "file_name", "performer"],  # , "caption"],
                    "fuzziness": "AUTO",
                    # "tie_breaker": 0.5,
                    "minimum_should_match": "50%"
                }}}, size=50 - res_len)

            for index, hit in enumerate(results_list["hits"]["hits"]):
                duration = timedelta(seconds=int(hit['_source']['duration']))
                d = datetime(1, 1, 1) + duration

                temp_perf_res = hit["_source"]["performer"]
                temp_titl_res = hit["_source"]["title"]
                temp_filnm_res = hit["_source"]["file_name"]
                # _title = hit["_source"]["title"]
                _performer = temp_perf_res if len(temp_perf_res) > 0 else temp_filnm_res
                _performer = textwrap.shorten(_performer, width=34, placeholder='...')
                _title = temp_titl_res if len(temp_titl_res) > 1 else temp_filnm_res
                _title = textwrap.shorten(_title, width=34, placeholder='...')

                _caption_content = language_handler("inline_file_caption", lang_code, hit)
                item_describtion = f"{hidden_character}???{_performer}\n" \
                                   f"{hidden_character}{_floppy_emoji} | {round(int(hit['_source']['file_size']) / 1_048_576, 1)} MB  " \
                                   f"{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}"  # 1000_000 MB
                item_title = hidden_character + str(index + res_len + 1) + '. ' + _title

                results.append(InlineQueryResultArticle(
                    title=item_title,
                    # description=res["_source"]["performer"],
                    description=item_describtion,
                    thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                    # "https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    input_message_content=InputTextMessageContent(_caption_content, parse_mode="HTML")))

        exception_handler(
            bot.answer_inline_query(query.id, results=results,
                                    cache_time=10, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot"))

    elif str(query.query).__contains__("#addtopl:"):
        try:
            file_id = str(query.query).split(" ")[1]
            audio_file = es.get("audio_files", id=file_id)
            print("audio file in on_inline:", audio_file)
            number_of_playlists = es.count(index="playlist", body={
                "query": {
                    "match": {
                        "author_id": user.id
                    }
                }
            })["count"]
            new_pl_header = True
            if number_of_playlists > 4:
                new_pl_header = False
            # playlists = es.get("user_lists", id=user.id)["_source"]["playlists"]
            playlists_result = es.search(index="playlist", body={
                "query": {
                    "match": {
                        "author_id": user.id
                    }
                }
            })["hits"]["hits"]
            playlists = []
            for pl in playlists_result:
                playlists.append(pl)
            print("\n\n\n\n\nplaylists", playlists)
            func = "addpl"
            playlist_inline_keyboard = language_handler("playlist_keyboard", lang_code, playlists, audio_file,
                                                        new_pl_header, func)
            bot.answer_inline_query(query.id, results=playlist_inline_keyboard,
                                    cache_time=1, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot")
            print("playlists:", playlists)
        except Exception as e:
            print("from inline query- #addtopl: ", e)

    elif str(query.query) == ("#history"):
        download_history = []
        history_result = es.get(index="user_lists", id=user.id)["_source"]["downloaded_audio_id_list"]
        for index, pl in enumerate(history_result):
            try:
                audio_file = es.get(index="audio_files", id=pl)
                download_history.append(audio_file)
                print(audio_file)
            except Exception as e:
                print("exception from get_history ", e)
                continue

        func = "history"
        show_add_pl_header = False
        playlist_inline_keyboard = language_handler("playlist_keyboard", lang_code, download_history, "audio_file",
                                                    show_add_pl_header, func)
        bot.answer_inline_query(query.id, results=playlist_inline_keyboard,
                                cache_time=1, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot")

    elif str(query.query) == ("#myplaylists"):
        playlists_result = es.search(index="playlist", body={
            "query": {
                "match": {
                    "author_id": user.id
                }
            }
        })["hits"]["hits"]
        playlists = []
        for pl in playlists_result:
            playlists.append(pl)

        func = "playlists"
        show_add_pl_header = False
        playlist_inline_keyboard = language_handler("playlist_keyboard", lang_code, playlists, "audio_file",
                                                    show_add_pl_header, func)
        bot.answer_inline_query(query.id, results=playlist_inline_keyboard,
                                cache_time=1, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot")

    elif str(query.query).__contains__("#showfiles"):
        try:
            playlist_id = str(query.query).split(" ")[1]
            results_list = es.get(index="playlist", id=playlist_id)["_source"]

            for index, file_id in enumerate(results_list["list"]):
                res = es.get(index="audio_files", id=file_id)["_source"]
                item_title = f"{str(index + 1)}. {res['title']}"
                item_title = hidden_character + item_title
                item_description = f"{hidden_character}{res['performer']}"
                results.append(InlineQueryResultArticle(
                    title=item_title,
                    description=item_description,
                    thumb_url="https://telegra.ph/file/6e6831bdd89011688bddb.jpg",
                    input_message_content=InputTextMessageContent(f"/dl_{file_id}", parse_mode="HTML")))
            exception_handler(
                bot.answer_inline_query(query.id, results=results,
                                        cache_time=10, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot"))
        except Exception as e:
            print("print from show files: ", e)

    elif str(query.query).__contains__("#edit_title"):

        try:
            result = []

            playlist_id = str(query.query).split(" ")[1]

            # query_id = str(query.query).split(" ")[1].split(":")[1]
            def unpack(s):
                return " ".join(map(str, s))

            print("from edit title:", query)
            if len(str(query.query).split(" ")) > 2:
                args = str(query.query).split(' ')[2:]
                new_title = f"{hidden_character}{unpack(args)}"
                results.append(InlineQueryResultArticle(
                    title="Save",
                    description=new_title,
                    thumb_url="https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    input_message_content=InputTextMessageContent(f"/edit_pl_title {playlist_id} {new_title}",
                                                                  parse_mode="HTML")))
                exception_handler(
                    bot.answer_inline_query(query.id, results=results,
                                            cache_time=1, switch_pm_text=back_text,
                                            switch_pm_parameter="back_to_the_bot"))

            else:
                title = language_handler("edit_playlist_information_guide", lang_code, "title")
                description = language_handler("edit_playlist_information_guide", lang_code, "description")
                results.append(InlineQueryResultArticle(
                    title=title,
                    description=description,
                    thumb_url="https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    input_message_content=InputTextMessageContent(f"/edit_pl_title {playlist_id} default title",
                                                                  parse_mode="HTML")))
                exception_handler(
                    bot.answer_inline_query(query.id, results=results,
                                            cache_time=1, switch_pm_text=back_text,
                                            switch_pm_parameter="back_to_the_bot"))
        except:
            print("from #editfile inline: ", e)

    elif str(query.query).__contains__("#edit_description"):

        result = []

        try:
            print("query    ", query.query)
            playlist_id = str(query.query).split(" ")[1]

            # query_id = str(query.query).split(" ")[1].split(":")[1]

            def unpack(s):
                return " ".join(map(str, s))

            if len(str(query.query).split(" ")) > 2:
                args = str(query.query).split(' ')[2:]
                new_title = f"{hidden_character}{unpack(args)}"
                results.append(InlineQueryResultArticle(
                    title="Save",
                    description=new_title,
                    thumb_url="https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    input_message_content=InputTextMessageContent(f"/edit_pl_description {playlist_id} {new_title}",
                                                                  parse_mode="HTML")))
                exception_handler(
                    bot.answer_inline_query(query.id, results=results,
                                            cache_time=1, switch_pm_text=back_text,
                                            switch_pm_parameter="back_to_the_bot"))
            else:
                title = language_handler("edit_playlist_information_guide", lang_code, "title")
                description = language_handler("edit_playlist_information_guide", lang_code, "description")
                results.append(InlineQueryResultArticle(
                    title=title,
                    description=description,
                    thumb_url="https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    input_message_content=InputTextMessageContent(f"/edit_pl_title {playlist_id} default description",
                                                                  parse_mode="HTML")))
                exception_handler(
                    bot.answer_inline_query(query.id, results=results,
                                            cache_time=1, switch_pm_text=back_text,
                                            switch_pm_parameter="back_to_the_bot"))
        except Exception as e:
            print("from #editfile inline: ", e)

    elif str(query.query) == "#help_catalog":
        print("got help_catalog")
        try:
            help_inline_keyboard = language_handler("help_inline_keyboard_list", lang_code)
            bot.answer_inline_query(query.id, results=help_inline_keyboard,
                                    cache_time=1, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot")
        except Exception as e:
            print("exception from help_catalog: ", e)

    else:
        # results_list = es.search(index="audio_files", body={"query": {
        #     "multi_match": {
        #         "query": str(query.query).split("#more_results:")[-1],
        #         "fields": ["file_name", "title", "performer"],
        #         "fuzziness": "AUTO",
        #         "tie_breaker": 0.5
        #     }}}, from_=10, size=10)

        results_list = es.search(index="audio_files", body={"query": {
            "multi_match": {
                "query": str(query.query).split("#more_results:")[-1],
                "type": "best_fields",
                "fields": ["title", "file_name", "performer"],  # , "caption"],
                # "fuzziness": "AUTO",
                # "tie_breaker": 0.5,
                "minimum_should_match": "70%"
            }}}, from_=1, size=50)

        for index, hit in enumerate(results_list["hits"]["hits"]):
            duration = timedelta(seconds=int(hit['_source']['duration']))
            d = datetime(1, 1, 1) + duration

            temp_perf_res = hit["_source"]["performer"]
            temp_titl_res = hit["_source"]["title"]
            temp_filnm_res = hit["_source"]["file_name"]
            # _title = hit["_source"]["title"]
            _performer = temp_perf_res if len(temp_perf_res) > 0 else temp_filnm_res
            _performer = textwrap.shorten(_performer, width=34, placeholder='...')
            _title = temp_titl_res if len(temp_titl_res) > 0 else temp_filnm_res
            _title = textwrap.shorten(_title, width=34, placeholder='...')

            _caption_content = language_handler("inline_file_caption", lang_code, hit)
            item_describtion = f"{hidden_character}???{_performer}\n" \
                               f"{hidden_character}{_floppy_emoji} | {round(int(hit['_source']['file_size']) / 1_048_576, 1)} MB  " \
                               f"{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}"  # 1000_000 MB
            item_title = hidden_character + str(index + 1) + '. ' + _title

            results.append(InlineQueryResultArticle(
                title=item_title,
                # description=res["_source"]["performer"],
                description=item_describtion,
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                # "https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                input_message_content=InputTextMessageContent(_caption_content, parse_mode="HTML")))
            # input_message_content=InputTextMessageContent(f"??????/dl_{hit['_id']}", parse_mode="HTML")))

            # results.append(InlineQueryResultArticle(
            #     title=str(index + 1) + '. ' + res["_source"]["title"],
            #     description=res["_source"]["performer"],
            #     thumb_url="https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
            #     input_message_content=InputTextMessageContent(f"/dl_{res['_id']}", parse_mode="HTML")))

        res_len = int(results_list["hits"]["total"])
        if res_len < 50:
            """
            If the previous search results count was less than 40 then do a fuzzy search to suggrst more results
            """
            results_list = es.search(index="audio_files", body={"query": {
                "multi_match": {
                    "query": str(query.query).split("#more_results:")[-1],
                    "type": "best_fields",
                    "fields": ["title", "file_name", "performer"],  # , "caption"],
                    "fuzziness": "AUTO",
                    # "tie_breaker": 0.5,
                    "minimum_should_match": "50%"
                }}}, size=50 - res_len)
            for index, hit in enumerate(results_list["hits"]["hits"]):
                duration = timedelta(seconds=int(hit['_source']['duration']))
                d = datetime(1, 1, 1) + duration

                temp_perf_res = hit["_source"]["performer"]
                temp_titl_res = hit["_source"]["title"]
                temp_filnm_res = hit["_source"]["file_name"]
                # _title = hit["_source"]["title"]
                _performer = temp_perf_res if len(temp_perf_res) > 0 else temp_filnm_res
                _performer = textwrap.shorten(_performer, width=34, placeholder='...')
                _title = temp_titl_res if len(temp_titl_res) > 0 else temp_filnm_res
                _title = textwrap.shorten(_title, width=34, placeholder='...')

                _caption_content = language_handler("inline_file_caption", lang_code, hit)
                item_describtion = f"{hidden_character}???{_performer}\n" \
                                   f"{hidden_character}{_floppy_emoji} | {round(int(hit['_source']['file_size']) / 1_048_576, 1)} MB  " \
                                   f"{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}"  # 1000_000 MB
                item_title = hidden_character + str(index + 1) + '. ' + _title

                results.append(InlineQueryResultArticle(
                    title=item_title,
                    # description=res["_source"]["performer"],
                    description=item_describtion,
                    thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                    # "https://www.howtogeek.com/wp-content/uploads/2017/09/img_59b89568ec308.jpg",
                    input_message_content=InputTextMessageContent(_caption_content, parse_mode="HTML")))

        exception_handler(
            bot.answer_inline_query(query.id, results=results,
                                    cache_time=10, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot"))


@bot.on_callback_query()
def callback_query_handler(bot, query):
    """
    Handle callback queries.
    options:
        1. "lang": Show a list of available languages
        2. [language code]: Choose language
        3. [Check joining status]: Check if the user has already joined your Telegram channel
        4. get_list: Get a list of audio files within the current playlist (first part splitted by space)
        5. delete: Remove an audio file from the current playlist after 2-step verification
        6. edit: Edit playlist meta-data
        7. showplaylist: Show an options for single playlist using a keyboard
        8. showmyplaylists: Show a list of playlists created by the user
        9. home: Show "Home" menu
        10. help: Show "Help" menu

    :param bot: Telegram bot object
    :param query: Telegram query object
    :return: True on success
    """
    user = query.from_user
    user_data = es.get(index="user", id=user.id)["_source"]
    lang_code = user_data["lang_code"]
    # bot.answer_callback_query(
    #     query.id,
    #     text=f"{query.data} language registered for you.\n\nYou can always change it using /lang command",
    #     show_alert=True
    # )
    joined_status = ["joined"]
    lang_list = ["en", "fa", "hi", "ru", "ar"]

    if query.data == "lang":
        choose_language(bot, query)

    if query.data in lang_list:
        print("got query")
        if query.data == "en":
            lang_code = "en"
        elif query.data == "fa":
            lang_code = "fa"
        elif query.data == "hi":
            lang_code = "hi"
        elif query.data == "ru":
            lang_code = "ru"
        elif query.data == "ar":
            lang_code = "ar"

        es.update("user", id=query.from_user.id, body={
            "script":
                {
                    "inline": "ctx._source.lang_code = params.lang_code;",
                    "lang": "painless",
                    "params": {
                        "lang_code": lang_code
                    }
                }
        }, ignore=409)

        text = language_handler("lang_register_alert", lang_code, query.from_user.first_name)
        # text = language_handler("send_in_1_min", lang_code, query.from_user.first_name)
        exception_handler(bot.answer_callback_query(
            query.id,
            text=text,  # f"{query.data} language registered for you.\n\nYou can always change it using /lang command",
            show_alert=True
        ))

        query.message.delete()

        try:
            prev_message = bot.get_messages(query.from_user.id, int(query.message.message_id) - 1)
            if prev_message.text:
                print("before contains:", prev_message.text)
                if str(prev_message.text).__contains__("Take your audio searching to the speed"):
                    print("after contains:", prev_message.text)
                    text = language_handler("welcome", lang_code, query.from_user.first_name)
                    exception_handler(prev_message.edit_text(text))

            # apl[1].edit_message_text(query.from_user.id, int(query.message.message_id)-1, "new text")
            print(bot.get_messages(query.from_user.id, int(query.message.message_id) - 1))
        except Exception as e:
            print("from editing welcome message: ", e)
            pass

        print(query)

    elif query.data in joined_status:
        if query.data == "joined":
            try:
                # user_data = es.get(index="user", id=query.from_user.id)["_source"]
                if user_data["lang_code"] == "fa":
                    user = exception_handler(app.get_chat_member(bot_name_fa_id, query.from_user.id))

                else:
                    user = exception_handler(app.get_chat_member(bot_name_id, query.from_user.id))

                es.update("user", id=query.from_user.id, body={
                    "script":
                        {
                            "inline": "ctx._source.role = params.role;"
                                      "ctx._source.limited = params.limited;",
                            "lang": "painless",
                            "params": {
                                "role": "subscriber",
                                "limited": False
                            }
                        }
                }, ignore=409)
                # text = "ok you're right"
                user_data = es.get("user", id=query.from_user.id)["_source"]
                text = language_handler("has_joined", user_data["lang_code"], user_data["first_name"])
                # text = language_handler("not_joined", user_data["lang_code"], user_data["first_name"])
            except:
                user_data = es.get("user", id=query.from_user.id)["_source"]
                text = language_handler("not_joined", user_data["lang_code"], user_data["first_name"])
                # text = "you're not joined :("

            exception_handler(bot.answer_callback_query(
                query.id,
                text=text,
                # f"{query.data} language registered for you.\n\nYou can always change it using /lang command",
                show_alert=True
            ))

        else:
            exception_handler(bot.answer_callback_query(
                query.id,
                text=""
                # f"{query.data} language registered for you.\n\nYou can always change it using /lang command",
                # show_alert=True
            ))

    elif str(query.data).__contains__("get_list"):
        playlist_id = str(query.data).split(" ")[1]
        results_list = es.get(index="playlist", id=playlist_id)["_source"]
        back_text = language_handler("back_to_the_bot", lang_code)
        results = []

        for index, file_id in enumerate(results_list["list"]):
            res = es.get(index="audio_files", id=file_id)
            # file = app.get_chat(res["_source"]["chat_id"])["username"]
            # print(file)
            # audio_file = app.get_messages(res["_source"]["chat_id"], res["_source"]["message_id"])
            # caption = file_retrieve_handler(audio_file)
            # captions.append(caption)
            results.append(res)
            print("\n\nresults\n", res)

        text = language_handler("playlist_result_list_handler", lang_code, results, results_list["title"])
        print("text", text)
        exception_handler(bot.answer_callback_query(
            query.id,
            text=''
            # f"{query.data} language registered for you.\n\nYou can always change it using /lang command",
            # show_alert=True
        ))
        exception_handler(bot.send_message(query.from_user.id, text=text, parse_mode="HTML"))
        # exception_handler(
        #     bot.answer_inline_query(query.id, results=results,
        #                             cache_time=10, switch_pm_text=back_text, switch_pm_parameter="back_to_the_bot"))

    elif str(query.data).__contains__("delete"):
        print(query)
        operation = str(query.data).split(" ")[0]
        playlist_id = str(query.data).split(" ")[1]
        if operation == "delete":
            result = es.get(index="playlist", id=playlist_id)
            func = "playlist"
            text = language_handler("delete_playlist_validation_text", lang_code, func)
            markup_list = language_handler("delete_playlist_validation_keyboard", lang_code, playlist_id, func)
            # exception_handler(bot.send_message(chat_id=query.from_user.id,
            #                                    text=f"<b>{text}</b>",
            #                                    reply_markup=InlineKeyboardMarkup(markup_list),
            #                                    parse_mode='HTML'))
            exception_handler(query.edit_message_text(
                text=f"<b>{text}</b>",
                reply_markup=InlineKeyboardMarkup(markup_list),
                parse_mode='HTML'))

        elif operation == "ydelete":
            # try:
            playlist_id = str(query.data).split(" ")[1]
            try:
                file_retrieve_id = str(query.data).split(" ")[2]
                # is_audio_file = True
                res = es.update(index="playlist", id=playlist_id, body={
                    "script": {
                        "source": "if (ctx._source.list.contains(params.file_id)) "
                                  "{ctx._source.list.remove(ctx._source.list.indexOf(params.file_id))} "
                                  "else {ctx.op = 'none'}",
                        "lang": "painless",
                        "params": {
                            "file_id": file_retrieve_id
                        }
                    }
                }, ignore=409)
                text = language_handler("file_deleted_from_playlist", user_data["lang_code"])
                exception_handler(query.answer(
                    text=text,
                    show_alert=True))
                bot.delete_messages(user.id, query.message.message_id)

            except:
                is_audio_file = False
                res = es.delete(index="playlist", id=playlist_id)
                text = language_handler("playlist_deleted_text", lang_code)
                exception_handler(query.answer(
                    text=f"{text}",
                    show_alert=True))
                bot.delete_messages(user.id, query.message.message_id)

        elif operation == "ndelete":
            playlist_files = es.get(index="playlist", id=playlist_id)["_source"]
            single_playlist_markup_list = language_handler("single_playlist_markup_list", user_data["lang_code"],
                                                           playlist_id)
            single_playlist_text = language_handler("single_playlist_text", user_data["lang_code"], playlist_files)
            exception_handler(query.edit_message_text(text=single_playlist_text,
                                                      reply_markup=InlineKeyboardMarkup(single_playlist_markup_list),
                                                      parse_mode='HTML'))

        elif operation == "adelete":
            results_list = es.get(index="playlist", id=playlist_id)
            back_text = language_handler("back_to_the_bot", lang_code)
            results = []
            for _audio_file_id in results_list["_source"]["list"]:
                results.append(es.get(index="audio_files", id=_audio_file_id))

            print("result list:", results_list)
            print("results:", results)
            text = language_handler("delete_audio_file_text", lang_code)  # , results,
            delete_audio_guide_text = language_handler("delete_audio_guide_text", lang_code)
            exception_handler(bot.answer_callback_query(
                query.id,
                text=delete_audio_guide_text,
                # f"{query.data} language registered for you.\n\nYou can always change it using /lang command",
                show_alert=True
            ))
            # results_list["_source"]["title"])
            da_markup_keyborad = language_handler("delete_audio_murkup_keyboard", lang_code, playlist_id, results)
            print("da_markup_keyborad", da_markup_keyborad)
            exception_handler(query.edit_message_text(text=text, parse_mode="HTML",
                                                      reply_markup=InlineKeyboardMarkup(da_markup_keyborad)))

        elif operation == "afdelete":
            playlist_id = str(query.data).split(" ")[1]
            audio_file_id = str(query.data).split(" ")[2]
            _message_id = query.message.message_id
            print("got delete query: ", query)
            func = "audio_file"

            text = language_handler("delete_playlist_validation_text", lang_code, func)
            markup_list = language_handler("delete_playlist_validation_keyboard", lang_code, playlist_id, func,
                                           audio_file_id)
            # exception_handler(bot.send_message(chat_id=query.from_user.id,
            #                                    text=f"<b>{text}</b>",
            #                                    reply_markup=InlineKeyboardMarkup(markup_list),
            #                                    parse_mode='HTML'))
            exception_handler(query.edit_message_text(
                text=f"<b>{text}</b>",
                reply_markup=InlineKeyboardMarkup(markup_list),
                parse_mode='HTML'))


        elif str(query.data).__contains__("edit"):
            _query = str(query.data).split(" ")[0]
            playlist_id = str(query.data).split(" ")[1]
            if _query == "editpl":
                try:
                    print(query)
                    playlist_id = str(query.data).split(" ")[1]
                    playlist = es.get(index="playlist", id=playlist_id)
                    print(playlist)
                    text = language_handler("edit_playlist_text", lang_code, playlist)
                    markup_list = language_handler("edit_playlist_keyboard", lang_code, playlist_id)
                    # exception_handler(bot.send_message(chat_id=query.from_user.id,
                    #                                    text=f"<b>{text}</b>",
                    #                                    reply_markup=InlineKeyboardMarkup(markup_list),
                    #                                    parse_mode='HTML'))
                    exception_handler(query.edit_message_text(
                        text=f"{text}",
                        reply_markup=InlineKeyboardMarkup(markup_list),
                        parse_mode='HTML'))
                except Exception as e:
                    print("exception from edit playlist: ", e)


        elif str(query.data).__contains__("showplaylist"):
            show_playlist(query, user_data)


        elif str(query.data).__contains__("showmyplaylists"):
            playlist_id = str(query.data).split(" ")[1]
            playlist_files = es.get(index="playlist", id=playlist_id)["_source"]

            markup_list = language_handler("playlists_buttons", user_data["lang_code"])
            mylists_menu_text = language_handler("mylists_menu_text", user_data["lang_code"])
            print(playlist_files)

            exception_handler(query.edit_message_text(text=mylists_menu_text,
                                                      reply_markup=InlineKeyboardMarkup(markup_list),
                                                      parse_mode='HTML'))

        elif str(query.data) == "home":
            home_markup_keyboard = language_handler("home_markup_keyboard", user_data["lang_code"])
            home_keyboard_text = language_handler("home_keyboard_text", user_data["lang_code"])

            exception_handler(query.edit_message_text(text=home_keyboard_text,
                                                      reply_markup=InlineKeyboardMarkup(home_markup_keyboard),
                                                      parse_mode='HTML'))

        elif str(query.data) == "help":
            help_markup_keyboard = language_handler("help_markup_keyboard", user_data["lang_code"])
            help_keyboard_text = language_handler("help_keyboard_text", user_data["lang_code"])

            exception_handler(query.edit_message_text(text=help_keyboard_text,
                                                      reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
                                                      parse_mode='HTML'))

    elif str(query.data).__contains__("edit"):
        _query = str(query.data).split(" ")[0]
        playlist_id = str(query.data).split(" ")[1]
        if _query == "editpl":
            try:
                print(query)
                playlist_id = str(query.data).split(" ")[1]
                playlist = es.get(index="playlist", id=playlist_id)
                print(playlist)
                text = language_handler("edit_playlist_text", lang_code, playlist)
                markup_list = language_handler("edit_playlist_keyboard", lang_code, playlist_id)
                # exception_handler(bot.send_message(chat_id=query.from_user.id,
                #                                    text=f"<b>{text}</b>",
                #                                    reply_markup=InlineKeyboardMarkup(markup_list),
                #                                    parse_mode='HTML'))
                exception_handler(query.edit_message_text(
                    text=f"{text}",
                    reply_markup=InlineKeyboardMarkup(markup_list),
                    parse_mode='HTML'))
            except Exception as e:
                print("exception from edit playlist: ", e)

    elif str(query.data).__contains__("showplaylist"):
        show_playlist(query, user_data)

    elif str(query.data).__contains__("showmyplaylists"):
        # try:
        playlist_id = str(query.data).split(" ")[1]
        playlist_files = es.get(index="playlist", id=playlist_id)["_source"]
        # single_playlist_markup_list = language_handler("single_playlist_markup_list", user_data["lang_code"], playlist_id, query.message.message_id)
        # single_playlist_text = language_handler("single_playlist_text", user_data["lang_code"], playlist_files)
        markup_list = language_handler("playlists_buttons", user_data["lang_code"])
        mylists_menu_text = language_handler("mylists_menu_text", user_data["lang_code"])
        print(playlist_files)
        # exception_handler(bot.send_message(chat_id=user.id,
        #                                     text=mylists_menu_text,
        #                                    reply_markup=InlineKeyboardMarkup(markup_list),
        #                                    parse_mode='HTML'))
        exception_handler(query.edit_message_text(text=mylists_menu_text,
                                                  reply_markup=InlineKeyboardMarkup(markup_list),
                                                  parse_mode='HTML'))

    elif str(query.data) == "home":
        home_markup_keyboard = language_handler("home_markup_keyboard", user_data["lang_code"])
        home_keyboard_text = language_handler("home_keyboard_text", user_data["lang_code"])
        # exception_handler(bot.send_message(chat_id=user.id,
        #                                     text=mylists_menu_text,
        #                                    reply_markup=InlineKeyboardMarkup(markup_list),
        #                                    parse_mode='HTML'))
        exception_handler(query.edit_message_text(text=home_keyboard_text,
                                                  reply_markup=InlineKeyboardMarkup(home_markup_keyboard),
                                                  parse_mode='HTML'))

    elif str(query.data) == "help":
        help_markup_keyboard = language_handler("help_markup_keyboard", user_data["lang_code"])
        help_keyboard_text = language_handler("help_keyboard_text", user_data["lang_code"])
        # exception_handler(bot.send_message(chat_id=user.id,
        #                                     text=mylists_menu_text,
        #                                    reply_markup=InlineKeyboardMarkup(markup_list),
        #                                    parse_mode='HTML'))
        exception_handler(query.edit_message_text(text=help_keyboard_text,
                                                  reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
                                                  parse_mode='HTML'))

    return True


def show_playlist(query, user_data):
    """
    Generates a keyboard for each playlist; buttons:
        1. Audio files list (as an inline list)
        2. Get list (as a text message)
        3. Edit
        4. Delete
        5. Home
        6. Back
    :param query: Query containing the "show playlist" data
    :param user_data: User data within database
    :return: True on success; False otherwise
    """

    try:
        query.answer(f"Back to the playlist ...")
        playlist_id = str(query.data).split(" ")[1]
        playlist_files = es.get(index="playlist", id=playlist_id)["_source"]
        single_playlist_markup_list = language_handler("single_playlist_markup_list", user_data["lang_code"],
                                                       playlist_id)
        single_playlist_text = language_handler("single_playlist_text", user_data["lang_code"], playlist_files)
        print(playlist_files)
        exception_handler(query.edit_message_text(text=single_playlist_text,
                                                  reply_markup=InlineKeyboardMarkup(single_playlist_markup_list),
                                                  parse_mode='HTML'))

        return True
    except Exception as e:
        print("from showplaylist:", e)
        return False


@bot.on_message(Filters.command(["users", "promote", "reset_channel", "index"]))
def users_log(bot, message):
    """
    Some useful functionalities and options for the owner/admin of the bot:
        1. "users": Generates a summary log of the database status only for the admin/owner of the bot. This is a
         static function and not a formal part of the bot (meant just for simplification; otherwise you can use Kibana).
        2. "promote": promotes the rank of a channel in the indexer waiting list
        3. "reset_channel": Reset the indexing information of a channel in the database
        4. "index": Index a channel immediately without waiting in the indexer queue

    :param bot: Telegram bot object
    :param message: Telegram message object
    :return: True on success
    """
    user = message.from_user
    user_data = es.get(index="user", id=user.id)["_source"]
    if user_data["role"] == "owner":

        if message.command[0] == "users":
            res = es.count(index="audio", body={
                "query": {
                    "match_all": {}
                }
            })
            audio_files = es.count(index="audio_files", body={
                "query": {
                    "match_all": {}
                }
            })
            users_count = es.count(index="user", body={
                "query": {
                    "match_all": {}
                }
            })
            uen = es.count(index="user", body={
                "query": {
                    "match": {
                        "lang_code": "en"
                    }
                }
            })
            uhi = es.count(index="user", body={
                "query": {
                    "match": {
                        "lang_code": "hi"
                    }
                }
            })
            uru = es.count(index="user", body={
                "query": {
                    "match": {
                        "lang_code": "ru"
                    }
                }
            })
            ufa = es.count(index="user", body={
                "query": {
                    "match": {
                        "lang_code": "fa"
                    }
                }
            })
            uar = es.count(index="user", body={
                "query": {
                    "match": {
                        "lang_code": "ar"
                    }
                }
            })
            channels = es.count(index="channel", body={
                "query": {
                    "match_all": {}
                }
            })
            imp0 = es.count(index="channel", body={
                "query": {
                    "match": {
                        "importance": 0
                    }
                }
            })
            imp1 = es.count(index="channel", body={
                "query": {
                    "match": {
                        "importance": 1
                    }
                }
            })
            imp2 = es.count(index="channel", body={
                "query": {
                    "match": {
                        "importance": 2
                    }
                }
            })
            imp3 = es.count(index="channel", body={
                "query": {
                    "match": {
                        "importance": 3
                    }
                }
            })
            imp4 = es.count(index="channel", body={
                "query": {
                    "match": {
                        "importance": 4
                    }
                }
            })
            imp5 = es.count(index="channel", body={
                "query": {
                    "match": {
                        "importance": 5
                    }
                }
            })
            to_index = es.count(index="to_index", body={
                "query": {
                    "match_all": {}
                }
            })
            future_channel = es.count(index="future_channel", body={
                "query": {
                    "match_all": {}
                }
            })
            channel_buffer = es.count(index="channel_buffer", body={
                "query": {
                    "match_all": {}
                }
            })
            user_lists = helpers.scan(
                client=es,
                query={"query": {"match_all": {}}},
                size=10000,
                scroll='2m',
                index="user_lists"
            )
            # print("audio files:", res)
            audio_count = res["count"]
            audio_files_count = audio_files["count"]
            users_count = users_count["count"]
            # print("channels:", channels)
            channel_count = channels["count"]
            imp0_count = imp0["count"]
            imp1_count = imp1["count"]
            imp2_count = imp2["count"]
            imp3_count = imp3["count"]
            imp4_count = imp4["count"]
            imp5_count = imp5["count"]
            uen_count = uen["count"]
            uhi_count = uhi["count"]
            uru_count = uru["count"]
            ufa_count = ufa["count"]
            uar_count = uar["count"]
            # print("to_index:", to_index)
            to_index_count = to_index["count"]
            future_channel_count = future_channel["count"]
            channel_buffer_count = channel_buffer["count"]
            # print("user_lists:", user_lists)
            counts_text = f"<b>Number of indexed docs in each index</b>\n\n" \
                          f"<b>1. Audio:</b> {audio_count}\n" \
                          f"<b>   Audio_files:</b> {audio_files_count}\n\n" \
                          f"<b>2. Users:</b> {users_count}\n" \
                          f"    users by language:\n" \
                          f"            en: {uen_count}\n" \
                          f"            hi: {uhi_count}\n" \
                          f"            ru: {uru_count}\n" \
                          f"            fa: {ufa_count}\n" \
                          f"            ar: {uar_count}\n\n" \
                          f"<b>3. To_index:</b> {to_index_count}\n\n" \
                          f"<b>3. future_channel:</b> {future_channel_count}\n\n" \
                          f"<b>3. channel_buffer:</b> {channel_buffer_count}\n\n" \
                          f"<b>4. Channels:</b> {channel_count}\n" \
                          f"    channel by importance:\n" \
                          f"            0: {imp0_count}\n" \
                          f"            1: {imp1_count}\n" \
                          f"            2: {imp2_count}\n" \
                          f"            3: {imp3_count}\n" \
                          f"            4: {imp4_count}\n" \
                          f"            5: {imp5_count}\n\n"

            # es.indices.delete("channel")
            # es.indices.delete("audio")
            # es.indices.delete("to_index")
            exception_handler(bot.send_message(user.id, counts_text, parse_mode="html"))

        elif message.command[0] == "promote":
            try:
                channel_username = message.command[1]
                new_importance = message.command[2]
                _channel_instance_db = es.search(index="channel", body={
                    "query": {
                        "match": {
                            "username": channel_username
                        }
                    }
                })

                if len(_channel_instance_db["hits"]["hits"]) > 0:
                    res_text = f"search results: \n\n{_channel_instance_db}"
                    exception_handler(bot.send_message(user.id, res_text, parse_mode="html"))
                    _channel_id = _channel_instance_db["hits"]["hits"][0]["_id"]

                    res = es.update(index="channel", id=_channel_id, body={
                        "script": {
                            "inline": "ctx._source.importance = params.importance;",
                            "lang": "painless",
                            "params": {
                                "importance": new_importance
                            }
                        }
                    }, ignore=409)
                    result_text = f"the result of promoting @{channel_username} to importance {new_importance}:\n\n" \
                                  f"{res['result']}"
                    exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                else:
                    result_text = f"Channel with this username doesn't exist in the database\n\n" \
                                  f"Channel username: @{channel_username}\n" \
                                  f"New importance: {new_importance}"
                    exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))

            except Exception as e:
                text = f"exception occurred while trying to promote channels: \n\n{e}"
                exception_handler(bot.send_message(user.id, text, parse_mode="html"))

        elif message.command[0] == "reset_channel":
            try:
                channel_username = message.command[1]
                # new_importance = message.command[2]
                _channel_instance_db = es.search(index="channel", body={
                    "query": {
                        "match": {
                            "username": channel_username
                        }
                    }
                })

                if len(_channel_instance_db["hits"]["hits"]) > 0:
                    res_text = f"search results: \n\n{_channel_instance_db}"
                    exception_handler(bot.send_message(user.id, res_text, parse_mode="html"))
                    _channel_id = _channel_instance_db["hits"]["hits"][0]["_id"]

                    res = es.update(index="channel", id=_channel_id, body={
                        "script": {
                            "inline": "ctx._source.last_indexed_offset_date = params.last_indexed_offset_date;",
                            "lang": "painless",
                            "params": {
                                "last_indexed_offset_date": 0
                            }
                        }
                    }, ignore=409)
                    result_text = f"the result of resetting @{channel_username}:\n\n" \
                                  f"{res['result']}"
                    exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                else:
                    result_text = f"Channel with this username doesn't exist in the database\n\n" \
                                  f"Channel username: @{channel_username}"
                    exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))

            except Exception as e:
                text = f"exception occurred while trying to promote channels: \n\n{e}"
                exception_handler(bot.send_message(user.id, text, parse_mode="html"))

        elif message.command[0] == "index":
            try:
                channel_username = message.command[1]
                urgent_index(channel_username, user)
            except Exception as e:
                text = f"exception occurred while trying to indexing channels: \n\n{e}"
                exception_handler(bot.send_message(user.id, text, parse_mode="html"))

    return True


def urgent_index(channel_username: str, user: object):
    """
    Index requested channel by the owner/admin immediately. Start from the first message if the channel was
     new, update otherwise.
    :param channel_username: Channel username [*str]
    :param user: Telegram user object
    :return: True on success
    """

    _channel_instance_db = es.search(index="channel", body={
        "query": {
            "match": {
                "username": channel_username
            }
        }
    })

    if len(_channel_instance_db["hits"]["hits"]) > 0:
        res_text = f"This channel has already been indexed\n\nSearch results: \n\n{_channel_instance_db}"
        exception_handler(bot.send_message(user.id, res_text, parse_mode="html"))
        # db_importance = _channel_instance_db["hits"]["hits"][0]["_source"]["importance"]
        db_downloaded_from_count = _channel_instance_db["hits"]["hits"][0]["_source"]["indexed_from_audio_count"]
        if db_downloaded_from_count == 0:
            _channel_id = _channel_instance_db["hits"]["hits"][0]["_id"]
            starting_text = f"Indexing @{channel_username} started ...\n\nIt might take several minutes."
            exception_handler(bot.send_message(user.id, starting_text, parse_mode="html"))
            #
            audio_file_indexer(app, _channel_id, 0)
            #
            finishing_text = f"Indexing @{channel_username} finished successfully"
            exception_handler(bot.send_message(user.id, finishing_text, parse_mode="html"))

    else:
        result_text = f"Channel with this username doesn't exist in the database.\n" \
                      f"Checking it on telegram...\n\n" \
                      f"Channel username: @{channel_username}"
        exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
        try:
            # time.sleep(10)
            # current_chat = app2.get_chat(channel_username)
            # time.sleep(3)
            # if current_chat.type == "channel":
            starting_text = f"Indexing @{channel_username} started ...\n\nIt might take several minutes."
            exception_handler(bot.send_message(user.id, starting_text, parse_mode="html"))

            # audio_file_indexer(app2, current_chat.id, 0)
            # random_indexer = random.choice([app, app2, indexer_list[0]])
            new_channel_indexer(app, [channel_username], "future_channel")

            finishing_text = f"Indexing @{channel_username} finished successfully"
            exception_handler(bot.send_message(user.id, finishing_text, parse_mode="html"))
        except FloodWait as e:
            result_text = f"FloodWait from manual indexer: \n\n{e}"
            exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
            # print("from audio file indexer: Flood wait exception: ", e)
            time.sleep(e.x)
        except SlowmodeWait as e:
            result_text = f"SlowmodeWait from manual indexer: \n\n{e}"
            exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
            # print("from audio file indexer: Slowmodewait exception: ", e)
            time.sleep(e.x)
        except TimeoutError as e:
            result_text = f"TimeoutError from manual indexer: \n\n{e}"
            exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
            # print("Timeout error: sleeping for 20 seconds: ", e)
            time.sleep(20)
            # pass
        except ConnectionError as e:
            result_text = f"ConnectionError from manual indexer: \n\n{e}"
            exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
            # print("Connection error - sleeping for 40 seconds: ", e)
        except Exception as e:
            result_text = f"Channel with this username doesn't seem to be valid\n\n" \
                          f"Channel username: @{channel_username}\n\n{e}"
            exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
    time.sleep(5)
    return True


@bot.on_message(Filters.private & Filters.command("start"))
def index_user(bot, message):
    """
    Add new users after sending "start" if did not exist; check if they have joined the channel and update their status
    respectively
    :param bot: Telegram bot object
    :param message: Telegram message object
    :return: -
    """
    # different roles: searcher, subscriber, recom_subscriber, admin, CEO, maintainer
    # es.bulk({ "create" : user_data_generator(message)})
    print("start")
    print(message)

    if "back_to_the_bot" in message.command:
        message.delete()
    else:
        try:
            user = message.from_user

            # if es.exists(index="user", id=user.id):
            #     es.delete("user", id=user.id)

            if not es.exists(index="user", id=user.id):
                res_u = es.create(index="user", id=user.id, body={
                    "first_name": user.first_name,
                    "username": user.username,
                    "date_joined": int(time.time()),
                    "downloaded_audio_count": 0,
                    "lang_code": "en",
                    "limited": False,
                    "role": "searcher",
                    "coins": 0,
                    "last_active_date": int(time.time()),
                    "is_admin": False,
                    "sex": "neutral",
                    "country": "-"
                }, ignore=409)
                # print(res)
                # es.delete(index="user_lists", id=user.id)
            res_ul = es.create(index="user_lists", id=user.id, body={
                "downloaded_audio_id_list": [],
                "playlists": []
            }, ignore=409)
            welcome_en = language_handler("welcome", "en", user.first_name)
            print(welcome_en)
            exception_handler(bot.send_message(message.chat.id, welcome_en, parse_mode="html"))

            choose_language(bot, message)

            es.indices.refresh("user")
            user_data = es.get(index="user", id=user.id)["_source"]
            try:
                # apt = apl[0]
                lang_code = user_data["lang_code"]
                if lang_code == "fa":
                    user_status = app.get_chat_member(bot_name_fa_id, user.id)
                else:
                    user_status = app.get_chat_member(bot_name_id, user.id)

                if user_data["role"] == "searcher":
                    es.update(index="user", id=user.id, body={
                        "script": {
                            "inline": "ctx._source.limited = params.limited;"
                                      "ctx._source.role = params.role;",
                            "lang": "painless",
                            "params": {
                                "limited": False,
                                "role": "subscriber"
                            }
                        }
                    }, ignore=409)



            except Exception as e:
                print(e)

            time.sleep(15)
            es.indices.refresh("user")
            user_data = es.get(index="user", id=user.id)["_source"]
            lang_code = user_data["lang_code"]
            example_message = language_handler("example_message", lang_code, user.first_name)
            exception_handler(bot.send_message(message.chat.id, example_message, parse_mode="html"))

        except Exception as e:
            print(f"Exception from index_user: {e}")
        finally:
            check_joining_status(bot_name_id)
            check_joining_status(bot_name_fa_id)


@bot.on_message(Filters.command(["lang", "help", "home"]))
def commands_handler(bot, message):
    """
    Show following keyboards on request:
        1. Lang
        2. Help
        3. Home
    :param bot: Bot object
    :param message: Message object
    :return: True on success; False otherwise
    """

    if message.command[0] == "lang":
        # english.languages_list()
        message.delete()
        choose_language(bot, message)

    elif message.command[0] == "help":
        try:
            user_data = es.get(index="user", id=message.chat.id)["_source"]
            help_markup_keyboard = language_handler("help_markup_keyboard", user_data["lang_code"])
            help_keyboard_text = language_handler("help_keyboard_text", user_data["lang_code"])

            message.delete()
            exception_handler(bot.send_message(message.chat.id, text=help_keyboard_text,
                                               reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
                                               parse_mode='HTML'))
        except Exception as e:
            print("from search on_message: ", e)
            return False

    elif message.command[0] == "home":
        try:
            user_data = es.get(index="user", id=message.chat.id)["_source"]
            home_markup_keyboard = language_handler("home_markup_keyboard", user_data["lang_code"])
            home_keyboard_text = language_handler("home_keyboard_text", user_data["lang_code"])

            message.delete()

            exception_handler(bot.send_message(message.chat.id, text=home_keyboard_text,
                                               reply_markup=InlineKeyboardMarkup(home_markup_keyboard),
                                               parse_mode='HTML'))
        except Exception as e:
            print("from on_message: ", e)
            return False

    return True


@bot.on_message(Filters.command(["addnewpl", "addtoexistpl", "myplaylists",
                                 "showplaylist", "edit_pl_title", "edit_pl_description"]))
def playlist_commands_handler(bot, message):
    """
    Handle following commands:
        1. "addnewpl": Create a new playlist and add the audio file to it
        2. "addtoexistpl": Add the audio file to an existing playlist
        3. "myplaylists": Show all playlists for the current user
        4. "showplaylist": Show all audio files within the chosen playlist
        5. "edit_pl_title": Edit the chosen playlist's title
        6. "edit_pl_description": Edit the chosen playlist's description
    :param bot: Telegram bot object
    :param message: Telegram message object
    :return: True on success; False on exception
    """

    user = message.from_user
    user_data = es.get(index="user", id=user.id)["_source"]
    lang_code = user_data["lang_code"]
    if message.command[0] == "addnewpl":
        try:
            file_ret_id = str(message.text).split(" ")[1]
            playlist_id = str(uuid4())[:6].replace("-", "d")
            print("playlist id: ", playlist_id)
            audio_file_db_data = es.get("audio_files", id=file_ret_id)["_source"]
            data = {"id": playlist_id,
                    "title": audio_file_db_data["title"],
                    "description": "New Playlist",
                    "list": []}
            func = "addnewpl"
            added_success_text = language_handler("added_to_playlist_success_text", lang_code, func, data)
            markup_keyboard = language_handler("playlists_buttons", lang_code)
            message.reply_text(text=added_success_text, quote=False, parse_mode="HTML",
                               reply_markup=InlineKeyboardMarkup(markup_keyboard))
            playlist_title = audio_file_db_data["title"] if not audio_file_db_data["title"] == None else \
                audio_file_db_data["performer"] if not audio_file_db_data["performer"] == None \
                    else audio_file_db_data["file_name"]
            # resl = es.update(index="user_lists", id=user.id, body={
            #     "script": {
            #         "source": "if (ctx._source.playlists.contains(params.file_id)) {ctx.op = 'none'} else "
            #                   "{if (ctx._source.downloaded_audio_id_list.size()>49) "  #
            #                   "{ctx._source.downloaded_audio_id_list.remove(0);"
            #                   "ctx._source.downloaded_audio_id_list.add(params.file_id);} "
            #                   "else {ctx._source.downloaded_audio_id_list.add(params.file_id);}}",  # ctx.op = 'none'}",
            #         "lang": "painless",
            #         "params": {
            #             "file_id": file_ret_id
            #         }
            #     }
            # })
            base64urlsafe_playlist_id = secrets.token_urlsafe(6)
            print("generated id", base64urlsafe_playlist_id)
            # res = es.create(index="playlist", )
            number_of_user_playlists = es.count(index="playlist", body={
                "query": {
                    "match": {
                        "author_id": user.id
                    }
                }
            })
            print("number_of_user_playlists", number_of_user_playlists)
            if int(number_of_user_playlists["count"]) < 5:
                create_new_playlist_res = es.create(index="playlist", id=base64urlsafe_playlist_id, body={
                    "author_id": user.id,
                    "title": playlist_title,
                    "description": "New playlist",
                    "list": [file_ret_id]
                })
                print("create_new_playlist_res", create_new_playlist_res)
                res = es.update(index="user_lists", id=user.id, body={
                    "script": {
                        "inline": "ctx._source.playlists.add(params.playlist_id);",
                        "lang": "painless",
                        "params": {
                            "playlist_id": base64urlsafe_playlist_id
                        }
                    }
                }, ignore=409)
            message.delete()
            return True

        except Exception as e:
            print("from playlists handling: ", e)
            return False

    elif message.command[0] == "addtoexistpl":
        try:
            playlist_id = message.command[1]
            file_retrieve_id = message.command[2]
            # print("playlist id: ", playlist_id)
            audio_file_db_data = es.get("audio_files", id=file_retrieve_id)["_source"]
            data = {"id": playlist_id,
                    "title": audio_file_db_data["title"],
                    "description": "New Playlist",
                    "list": []}
            playlist = es.get(index="playlist", id=playlist_id)
            print(playlist)
            res = es.update(index="playlist", id=playlist_id, body={
                "script": {
                    "source": "if (ctx._source.list.contains(params.file_id)) {ctx.op = 'none'} else "
                              "{if (ctx._source.list.size()>14) "
                              "{ctx.op = 'none'}"
                              "else {ctx._source.list.add(params.file_id);}}",

                    # "if (ctx._source.list.size()<20){"
                    #         "if (ctx._source.list.contains(params.file_id))"
                    #             "{ctx.op = 'none';} "
                    #         "else {ctx._source.list.add(params.file_id);}}"
                    #       "else{ctx.op = 'none'}",
                    "lang": "painless",
                    "params": {
                        "file_id": file_retrieve_id
                    }
                }
            }, ignore=409)
            func = "addtoexistpl"
            added_success_text = language_handler("added_to_playlist_success_text", lang_code, func, data, playlist)
            markup_keyboard = language_handler("playlists_buttons", lang_code)
            message.reply_text(text=added_success_text, quote=False, parse_mode="HTML",
                               reply_markup=InlineKeyboardMarkup(markup_keyboard))
            # bot.send_message(user.id, str(playlist))
            message.delete()
            return True

        except Exception as e:
            print("from playlists - adding to existing playlist: ", e)
            return False

    elif message.command[0] == "myplaylists":
        print(message)
        user = message.from_user
        pl_results = es.search(index="playlist", body={
            "query": {
                "match": {
                    "author_id": user.id
                }
            }
        })
        # print(pl_results)
        for pl in pl_results["hits"]["hits"]:
            print(pl)
        markup_list = language_handler("playlists_buttons", user_data["lang_code"])
        playlist_text = language_handler("mylists_menu_text", user_data["lang_code"])
        exception_handler(message.reply_text(text=playlist_text, reply_markup=InlineKeyboardMarkup(markup_list),
                                             parse_mode='HTML'))
        message.delete()
        return True

    elif message.command[0] == "showplaylist":
        try:
            playlist_id = message.command[1]
            playlist_files = es.get(index="playlist", id=playlist_id)["_source"]
            single_playlist_markup_list = language_handler("single_playlist_markup_list", user_data["lang_code"],
                                                           playlist_id, message.message_id)
            single_playlist_text = language_handler("single_playlist_text", user_data["lang_code"], playlist_files)
            print(playlist_files)
            exception_handler(message.reply_text(text=single_playlist_text,
                                                 reply_markup=InlineKeyboardMarkup(single_playlist_markup_list),
                                                 parse_mode='HTML'))

            message.delete()
            return True
        except Exception as e:
            print("from showplaylist:", e)
            return False

    elif message.command[0] == "edit_pl_title":
        playlist_id = str(message.command[1])
        # prev_query_id = str(message.command[1]).split(":")[1]
        new_title = message.command[2:]
        print(message.command)

        def unpack(s):
            return " ".join(map(str, s))

        new_title = unpack(new_title)

        res = es.update(index="playlist", id=playlist_id, body={
            "script": {
                "source": "ctx._source.title = params.new_title",
                "lang": "painless",
                "params": {
                    "new_title": new_title
                }
            }
        }, ignore=409)
        func = "title_update"
        text = language_handler("playlist_updated_text", user_data["lang_code"], func)
        exception_handler(bot.send_message(user.id, text))
        # bot.answer_callback_query(callback_query_id=prev_query_id, text=text, show_alert=True)
        message.delete()
        return True

    elif message.command[0] == "edit_pl_description":
        playlist_id = str(message.command[1])
        # prev_query_id = str(message.command[1]).split(":")[1]
        new_description = message.command[2:]
        print("commands", message.command)

        def unpack(s):
            return " ".join(map(str, s))

        new_description = unpack(new_description)

        res = es.update(index="playlist", id=playlist_id, body={
            "script": {
                "source": "ctx._source.description = params.new_description",
                "lang": "painless",
                "params": {
                    "new_description": new_description
                }
            }
        }, ignore=409)
        func = "description_update"
        text = language_handler("playlist_updated_text", user_data["lang_code"], func)
        exception_handler(bot.send_message(user.id, text))
        # bot.answer_callback_query(callback_query_id=prev_query_id, text=text, show_alert=True)
        message.delete()
        return True


@bot.on_message(Filters.private & Filters.regex("dl_"))
def download_handler(bot, message):
    """
    Check if the message is coming from a Telegram client and contains "dl_" regex, and then submit a thread to
    retrieve the searched audio file
    :param bot: Telegram bot object
    :param message: Telegram message object
    :return: True on success
    """
    executor.submit(file_retrieve_handler, message)
    return True


@bot.on_message(~Filters.via_bot & ~Filters.bot &
                Filters.private & (Filters.forwarded | Filters.regex("@") | Filters.web_page | Filters.regex("https")))
def get_channel(bot, message):
    """
    Index requested channel by the owner/admin immediately. Start from the first message if the channel was
     new, update otherwise.
    :param bot: Telegram bot API
    :param message: Telegram message object
    :return: True on success
    """
    channels_username = []
    user_data = es.get(index="user", id=message.chat.id)
    user = message.from_user
    # print(message.text)

    if user_data["_source"]["role"] == "owner":
        channels_usernames = caption_entities_channel_extractor(app, message)
        for _channel_username in channels_usernames:
            try:
                urgent_index(_channel_username, user)
            except FloodWait as e:
                result_text = f"FloodWait from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("from audio file indexer: Flood wait exception: ", e)
                time.sleep(e.x)
            except SlowmodeWait as e:
                result_text = f"SlowmodeWait from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("from audio file indexer: Slowmodewait exception: ", e)
                time.sleep(e.x)
            except TimeoutError as e:
                result_text = f"TimeoutError from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("Timeout error: sleeping for 20 seconds: ", e)
                time.sleep(20)
                # pass
            except ConnectionError as e:
                result_text = f"ConnectionError from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("Connection error - sleeping for 40 seconds: ", e)
            except Exception as e:
                result_text = f"Channel with this username doesn't seem to be valid\n\n" \
                              f"Channel username: @{_channel_username}\n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
        if message.text:
            channels_usernames = channel_name_extractor(app, message.text)
        elif message.caption:
            channels_usernames = channel_name_extractor(app, message.caption)

        for _channel_username in channels_usernames:
            try:
                urgent_index(_channel_username, user)
            except FloodWait as e:
                result_text = f"FloodWait from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("from audio file indexer: Flood wait exception: ", e)
                time.sleep(e.x)
            except SlowmodeWait as e:
                result_text = f"SlowmodeWait from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("from audio file indexer: Slowmodewait exception: ", e)
                time.sleep(e.x)
            except TimeoutError as e:
                result_text = f"TimeoutError from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("Timeout error: sleeping for 20 seconds: ", e)
                time.sleep(20)
                # pass
            except ConnectionError as e:
                result_text = f"ConnectionError from manual indexer: \n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))
                # print("Connection error - sleeping for 40 seconds: ", e)
            except Exception as e:
                result_text = f"Channel with this username doesn't seem to be valid\n\n" \
                              f"Channel username: @{_channel_username}\n\n{e}"
                exception_handler(bot.send_message(user.id, result_text, parse_mode="html"))

        if message.forward_from_chat:
            forwarded_from_channel_extractor(app, message)

    else:
        check_message = bot.send_message(message.chat.id,
                                         language_handler("checking_items_started", user_data["_source"]["lang_code"]))
        if message.text:
            channels_username = channel_name_extractor(app, message.text)
        elif message.caption:
            channels_username = channel_name_extractor(app, message.caption)
        if message.forward_from_chat:
            forwarded_from_channel_extractor(app, message)
        t = caption_extractor(message)
        print("caption: ", t)
        count = 0

        for _channel_username in channels_username:
            # if not es.exists(index="channel", id=_channel):
            if es.count(index="channel", body={
                "query": {
                    "match": {
                        "username": _channel_username
                    }
                }
            })["count"] == 0:
                if not es.exists(index="future_channel", id=_channel_username):
                    count += 1

        if count > 0:
            registered = True
            check_message.edit_text(
                language_handler("contribution_thanks", user_data["_source"]["lang_code"], message.chat.first_name,
                                 registered, count))
        else:
            registered = False
            check_message.edit_text(language_handler("contribution_thanks", user_data["_source"]["lang_code"],
                                                     message.chat.first_name, registered))
    return True


@bot.on_message(Filters.private & Filters.audio & ~Filters.bot)
def save_audio(bot, message):
    """
    Store audio files sent by users if it did not already exist in the database, ignore otherwise and reply to the
     user respectively
    :param bot: Telegram bot API
    :param message: Telegram message object
    :return: True on success
    """
    audio = message.audio
    print(message, caption_extractor(message))
    user_data = es.get("user", id=message.chat.id)["_source"]
    print("from file ret - lang code:")
    lang_code = user_data["lang_code"]
    if message.caption:
        channels_username = channel_name_extractor(app, message.caption)

    if not es.exists(index="audio_files", id=str(audio.file_id[8:30:3]).replace("-", "d")):
        print(es.exists(index="audio_files", id=str(audio.file_id[8:30:3]).replace("-", "d")))
        # try:
        # print("before")
        # _caption = language_handler("file_caption", lang_code, audio_track, audio_track.message_id, bot_name_users_files_id)
        # app.send_message(chat_id=bot_name_users_files_id, text=" test chrome")
        sent_to_user_sent_channel = bot.forward_messages(bot_name_users_files_id, message.chat.id, message.message_id)
        sender_info = f"Sender: \n{message.chat.first_name} \n@{message.chat.username}"
        bot.send_message(bot_name_users_files_id, sender_info,
                         reply_to_message_id=sent_to_user_sent_channel.message_id)
        # bot.forward_messages(bot_name_users_files_id, audio_track.chat.id, audio_track.message_id)
        print("sent file: ", sent_to_user_sent_channel)

        res = es.create(index="audio_files", id=str(audio.file_id[8:30:3]).replace("-", "d"), body={
            "chat_id": sent_to_user_sent_channel.chat.id,
            "chat_username": sent_to_user_sent_channel.chat.username,
            "message_id": int(sent_to_user_sent_channel.message_id),
            "file_id": audio.file_id,
            "file_name": str(audio.file_name).replace("_", " ").replace("@", " "),
            "file_size": audio.file_size,
            "duration": audio.duration,
            "performer": str(audio.performer).replace("_", " ").replace("@", " "),
            "title": str(audio.title).replace("_", " ").replace("@", " "),
            "times_downloaded": 0,
            "caption": str(caption_extractor(message)),
            "copyright": False
        }, ignore=409)
        es.indices.refresh("audio_files")

        # res = helpers.bulk(es, audio_data_generator([sent_to_user_sent_channel]))
        print("registered: ", res, sent_to_user_sent_channel)
        print(es.get(index="audio_files", id=str(audio.file_id[8:30:3]).replace("-", "d")))
        registered = True
        user_data = es.get(index="user", id=message.chat.id)
        bot.send_message(message.chat.id, language_handler("contribution_thanks", user_data["_source"]["lang_code"],
                                                           message.chat.first_name, registered))
        # message_id = sent_to_user_sent_channel.message_id
        # audio_track = bot.get_messages(datacenter_id, message_id)
        # except Exception as e:
        #     print("from save audio: ", e)
    else:
        # es.delete(index="audio", id=str(audio.file_id[8:30:3]).replace("-", "d"))
        registered = False
        user_data = es.get(index="user", id=message.chat.id)
        bot.send_message(message.chat.id, language_handler("contribution_thanks", user_data["_source"]["lang_code"],
                                                           message.chat.first_name, registered))

    return True


@bot.on_message(Filters.private & Filters.text & ~Filters.edited & ~Filters.bot & ~Filters.via_bot)
def message_handler(bot, message):
    """
    Handle received messages from the user. If it was a valid text submit it to the search handler otherwise send
     "Help" menu.
    :param bot: Telegram bot API
    :param message: Telegram message object
    :return: True on success
    """
    # print('got ur search query')
    # speed_limiter +=1
    if message.text and message.entities == None:
        if len(message.text) > 1:
            # adbot.send_message(message.chat.id, "it works")
            executor.submit(search_handler, bot, message)
    else:
        try:
            user_data = es.get(index="user", id=message.chat.id)["_source"]
            help_markup_keyboard = language_handler("help_markup_keyboard", user_data["lang_code"])
            help_keyboard_text = language_handler("help_keyboard_text", user_data["lang_code"])
            # exception_handler(bot.send_message(chat_id=user.id,
            #                                     text=mylists_menu_text,
            #                                    reply_markup=InlineKeyboardMarkup(markup_list),
            #                                    parse_mode='HTML'))
            exception_handler(bot.send_message(message.chat.id, text=help_keyboard_text,
                                               reply_markup=InlineKeyboardMarkup(help_markup_keyboard),
                                               parse_mode='HTML'))
        except Exception as e:
            print("from search on_message: ", e)

    return True


# @app.on_message()
def client_handler(app, message):
    """
    This is for development purposes and not a part of the bot. (uncomment the hooker in case you wanted to conduct
    tests)
    :param app: Telegram app API
    :param message: Telegram message object
    :return: -
    """
    pool_id = 'poolmachinelearning_x123'  # ID to get command from: Here is the pool channel admins
    commands = ["/f", "/sf", "/d", "/v", "/clean", "/i", "/s"]
    supported_message_types = ["text", "photo", "video", "document", "audio", "animation",
                               "voice", "poll", "sticker", "web_page"]
    valid_usernames = ["admin", "cmusic_self"]  # , pool_id]  # , "Pudax"]
    destinations = {"ce": "cedeeplearning", "pool": pool_id, "me": "admin"}

    # if message.chat.id == "61709467":
    #     message_handler(app, message)
    try:
        if message.chat.username in valid_usernames:
            # print(apl[0].get_users(34497745))

            # print(message)
            app.send_message("cmusic_self", str(message))
            # h = app.get_history("shanbemag", limit=1)
            # print(h[0])
            # for i in app.iter_history('BBC_6_Minute', limit=10):
            #     if i.audio:
            #         print(i)

            if str(message.text).split(' ')[0] == 'ch':
                # print(es.search(index="channel", body={
                #     "query": {
                #         "match_all": {}
                #     }
                # }))
                # es.bulk({ "create" : audio_data_generator() })
                # res = es.get(index="channel", id=app.get_chat('cedeeplearning').id)
                # print(res)
                res = es.search(index="channel", body={
                    "query": {
                        "match": {"importance": 5}
                    },
                    "sort": {
                        "last_indexed_offset_date": "asc"
                    }
                })
                print("started...")
                # print("his mes ", [ i for i in app.iter_history("me", limit=1)])#, datetime(app.get_history("me", limit=1)[-1].date).timestamp())

                # app.send_message("me", "indexing started ...")
                # app.terminate()
                # bot.restart()
                # es.get(index="future_channel", id=app.get_chat("kurdi4").id)
                # es.get(index="future_channel", id=app.get_chat("ahangify").id)
                # channel_to_index_set_consume = channel_to_index_set
                # [channel_to_index_set_consume.add(ch) for ch in list(channel_to_index_set)]
                # _channels_list = list(channel_to_index_set_consume)
                # print("cunsume set before: ", channel_to_index_set_consume)
                # new_channel_indexer(_channels_list)
                # app.send_message("me", res["hits"]["hits"])
                for item in res["hits"]["hits"]:
                    print(item)
                # res = helpers.scan(
                #     client=es,
                #     query={"query": {"match_all": {}}},
                #     size=10000,
                #     scroll='2m',
                #     index="channel"
                # )
                # for i in res:
                #     print(f"indexing: {i}")
                #     existing_channel_indexer(channel=int(i['_id']))
                #
                # app.send_message("me", "existing channels indexed successfully ")
                # caption_entities_channel_extractor(message)

            elif str(message.text).split(' ')[0] == 'delete':
                try:
                    es.indices.delete('audio')
                    es.indices.delete('channel')
                    # app.send_message("admin", text=f"deleted 2 indexes:\n1. audio\n2. channel")
                    # audio = es.indices.create(
                    #     index="audio",
                    #     body=audio_mapping,
                    #     ignore=400  # ignore 400 already exists code
                    # )
                    channel = es.indices.create(
                        index="channel",
                        body=channel_mapping,
                        ignore=400  # ignore 400 already exists code
                    )

                    app.send_message('admin', 'created again')
                except:
                    app.send_message('admin', "There's no audio index!")
                    # for index in es.indices.get('*'):
                    #     print(index)
                    print(es.search(index="datacenter", body={
                        "query": {"match_all": {}}
                    }))

                # elif str(message.text).split(' ')[0] == 'create':
                #     audio = es.indices.create(
                #         index="audio",
                #         body=audio_mapping,
                #         ignore=400  # ignore 400 already exists code
                #     )
                #     user = es.indices.create(
                #         index="user",
                #         body=audio_mapping,
                #         ignore=400  # ignore 400 already exists code
                #     )
                #     channel = es.indices.create(
                #         index="channel",
                #         body=audio_mapping,
                #         ignore=400  # ignore 400 already exists code
                #     )
                response = es.update(index="user", id=165802777, body={
                    "script": {
                        "source": "ctx._source.role = params.role_p",
                        "lang": "painless",
                        "params": {
                            "role_p": "owner"
                        }
                    }
                }, refresh=True, ignore=409)
                # app.send_message("admin",
                #                  text=f"created 3 indexes:\n\n1. audio: {audio}\n2. user: {user}\n\n3. channel: {channel}\n\n4. update responce: {response}")
                print(es.get(index="user_role", id=165802777))

            elif str(message.text).split(' ')[0] == 'index':
                time.sleep(3)
                current_chat = app.get_chat(str(message.text).split(' ')[1])
                time.sleep(3)
                if current_chat.type == "channel":
                    audio_file_indexer(app, current_chat, 0)

            elif str(message.text).split(' ')[0] == 'count':
                print(es.count(index='audio_files'))
    except Exception as e:
        print(f"from client handler: {e}")
