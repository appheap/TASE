import random
import textwrap
import unicodedata as UD
from datetime import timedelta, datetime
import emoji
from pyrogram import InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

from static.emoji import _traffic_light, _checkmark_emoji, _floppy_emoji, _clock_emoji, fruit_list, _en, _fa, _ar, _hi, \
    _ru, _zap, _globe_showing_Americas, _party_popper, _confetti_ball, _headphone, _studio_microphone, _round_pushpin, \
    _pushpin, _search_emoji, _house, _BACK_arrow, _star_struck, _green_circle, _backhand_index_pointing_right, \
    _exclamation_question_mark, _mobile_phone_with_arrow, _chart_increasing, _bar_chart, _check_mark_button, _gear, \
    _wrench, _cross_mark, _musical_note, _thumbs_up, _thumbs_down, _plus, _fountain_pen, _books, _red_heart, \
    _green_heart, heart_list, _seedling, _evergreen_tree, _deciduous_tree, _palm_tree, _sheaf_of_rice, _herb, _shamrock, \
    _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind, _smiling_face_with_sunglasses, \
    _winking_face, \
    _smiling_face_with_heart, _face_blowing_a_kiss, _face_with_raised_eyebrow

plants_list = [_seedling, _evergreen_tree, _deciduous_tree, _palm_tree, _sheaf_of_rice, _herb, _shamrock,
               _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind]


def music_file_keyboard(*args: str, **kwargs: str) -> list:
    """
    Generates a keyboard for the returned audio files
    :param args: Contains query = args[0] which is file id
    :param kwargs:
    :return: Generated keyboard
    """

    query = args[0]
    keyboard = [
        [InlineKeyboardButton(text=f"Add to playlist | {_plus}", switch_inline_query_current_chat=f"#addtopl: {query}"),
         InlineKeyboardButton(text=f"Home | {_house}", callback_data="home")]

    ]
    return keyboard


def back_to_the_bot(*args: str, **kwargs: str) -> str:
    """
    Returns the "back to the button" on top of the inline results
    :param args:
    :param kwargs:
    :return: A text contains the desired string
    """
    back_text = f"Back to the bot {_backhand_index_pointing_right}"
    return back_text

def playlist_keyboard(*args, **kwargs):
    """
    The necessary buttons for playlists
    :param args:
    :param kwargs:
    :return:
    """
