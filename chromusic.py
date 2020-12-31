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