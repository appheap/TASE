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
from index.analyzer import channel_analyzer # Change this
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


def get_admin_log(peer):
    """

    :param peer:
    :return:
    """
