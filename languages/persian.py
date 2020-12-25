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
    _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind, _smiling_face_with_heart, \
    _face_blowing_a_kiss, _face_with_raised_eyebrow, _smiling_face_with_sunglasses, _winking_face, _artist_palette

# _traffic_light = emoji.EMOJI_ALIAS_UNICODE[':traffic_light:']
# _checkmark_emoji = emoji.EMOJI_ALIAS_UNICODE[':white_check_mark:']
# _floppy_emoji = emoji.EMOJI_ALIAS_UNICODE[':floppy_disk:']
# _clock_emoji = emoji.EMOJI_ALIAS_UNICODE[':hourglass_flowing_sand:']
#
# _lemon = emoji.EMOJI_ALIAS_UNICODE[':lemon:']
# _cherries = emoji.EMOJI_ALIAS_UNICODE[':cherries:']
# _apple = emoji.EMOJI_ALIAS_UNICODE[':apple:']
# _candy = emoji.EMOJI_ALIAS_UNICODE[':candy:']
# _watermelon = emoji.EMOJI_ALIAS_UNICODE[':watermelon:']
# _peach = emoji.EMOJI_ALIAS_UNICODE[':peach:']
# _strawberry = emoji.EMOJI_ALIAS_UNICODE[':strawberry:']
# _tea = emoji.EMOJI_ALIAS_UNICODE[':tea:']
# _cherry_blossom = emoji.EMOJI_ALIAS_UNICODE[':cherry_blossom:']
# _maple_leaf = emoji.EMOJI_ALIAS_UNICODE[':maple_leaf:']
# _pineapple = emoji.EMOJI_ALIAS_UNICODE[':pineapple:']
# _tangerine = emoji.EMOJI_ALIAS_UNICODE[':tangerine:']
# _grapes = emoji.EMOJI_ALIAS_UNICODE[':grapes:']
# _carrot = emoji.EMOJI_ALIAS_UNICODE[':carrot:']
# _ear_of_corn = emoji.EMOJI_ALIAS_UNICODE[':ear_of_corn:']
# _mushroom = emoji.EMOJI_ALIAS_UNICODE[':mushroom:']
# fruit_list = [_grapes, _tangerine, _pineapple, _lemon, _cherries, _apple, _candy, _watermelon,
#               _peach, _strawberry, _tea, _cherry_blossom, _maple_leaf, _carrot, _ear_of_corn, _mushroom]
#
# # -------------Country Flags--------------------
# _en = emoji.EMOJI_ALIAS_UNICODE[':United_States:']
# _fa = emoji.EMOJI_ALIAS_UNICODE[':Iran:']
# _ar = emoji.EMOJI_ALIAS_UNICODE[':Saudi_Arabia:']
# _hi = emoji.EMOJI_ALIAS_UNICODE[':India:']
# _ru = emoji.EMOJI_ALIAS_UNICODE[':Russia:']
# _zap = emoji.EMOJI_ALIAS_UNICODE[':zap:']
# _globe_showing_Americas = emoji.EMOJI_ALIAS_UNICODE[':globe_showing_Americas:']
#
# # -------------Surprize--------------------------
# _party_popper = emoji.EMOJI_ALIAS_UNICODE[':party_popper:']
# _confetti_ball = emoji.EMOJI_ALIAS_UNICODE[':confetti_ball:']
#
# # -------------music--------------------------
# _headphone = emoji.EMOJI_ALIAS_UNICODE[':headphone:']
# _studio_microphone = emoji.EMOJI_ALIAS_UNICODE[':studio_microphone:']
#
# # -------------Utility and place--------------------------
# _round_pushpin = emoji.EMOJI_ALIAS_UNICODE[':round_pushpin:']
# _pushpin = emoji.EMOJI_ALIAS_UNICODE[':pushpin:']
# _search_emoji = emoji.EMOJI_ALIAS_UNICODE[':mag_right:']
# _house_with_garden = emoji.EMOJI_ALIAS_UNICODE[':house_with_garden:']
# _house = emoji.EMOJI_ALIAS_UNICODE[':house:']
# _BACK_arrow = emoji.EMOJI_ALIAS_UNICODE[':BACK_arrow:']
# _star_struck = emoji.EMOJI_ALIAS_UNICODE[':star-struck:']
# _artist_palette = emoji.EMOJI_ALIAS_UNICODE[':artist_palette:']
# _green_circle = emoji.EMOJI_ALIAS_UNICODE[':green_circle:']
# _backhand_index_pointing_right = emoji.EMOJI_ALIAS_UNICODE[':left_arrow_curving_right:']
# _exclamation_question_mark = emoji.EMOJI_ALIAS_UNICODE[':exclamation_question_mark:']
# _mobile_phone_with_arrow = emoji.EMOJI_ALIAS_UNICODE[':mobile_phone_with_arrow:']
# _chart_increasing = emoji.EMOJI_ALIAS_UNICODE[':chart_increasing:']
# _bar_chart = emoji.EMOJI_ALIAS_UNICODE[':bar_chart:']
# _check_mark_button = emoji.EMOJI_ALIAS_UNICODE[':white_check_mark:']
# _gear = emoji.EMOJI_ALIAS_UNICODE[':gear:']
# _wrench = emoji.EMOJI_ALIAS_UNICODE[':wrench:']
# _cross_mark = emoji.EMOJI_ALIAS_UNICODE[':cross_mark:']
# _musical_note = emoji.EMOJI_ALIAS_UNICODE[':musical_note:']
# _thumbs_up = emoji.EMOJI_ALIAS_UNICODE[':thumbs_up:']
# _thumbs_down = emoji.EMOJI_ALIAS_UNICODE[':thumbs_down:']
# _fountain_pen = emoji.EMOJI_ALIAS_UNICODE[':fountain_pen:']
# _plus = emoji.EMOJI_ALIAS_UNICODE[':heavy_plus_sign:']
#
# # -------------Books--------------------------
# _books = emoji.EMOJI_ALIAS_UNICODE[':books:']
# _book_emoji = emoji.EMOJI_ALIAS_UNICODE[':green_book:']
#
# # -------------Hearts--------------------------
# _red_heart = emoji.EMOJI_ALIAS_UNICODE[':red_heart:']
# _orange_heart = emoji.EMOJI_ALIAS_UNICODE[':orange_heart:']
# _yellow_heart = emoji.EMOJI_ALIAS_UNICODE[':yellow_heart:']
# _green_heart = emoji.EMOJI_ALIAS_UNICODE[':green_heart:']
# _blue_heart = emoji.EMOJI_ALIAS_UNICODE[':blue_heart:']
# _purple_heart = emoji.EMOJI_ALIAS_UNICODE[':purple_heart:']
#
# heart_list = [_red_heart, _orange_heart, _yellow_heart, _green_heart, _blue_heart, _purple_heart]
#
# # -------------Plants--------------------------
# _seedling = emoji.EMOJI_ALIAS_UNICODE[':seedling:']
# _evergreen_tree = emoji.EMOJI_ALIAS_UNICODE[':evergreen_tree:']
# _deciduous_tree = emoji.EMOJI_ALIAS_UNICODE[':deciduous_tree:']
# _palm_tree = emoji.EMOJI_ALIAS_UNICODE[':palm_tree:']
# _sheaf_of_rice = emoji.EMOJI_ALIAS_UNICODE[':sheaf_of_rice:']
# _herb = emoji.EMOJI_ALIAS_UNICODE[':herb:']
# _shamrock = emoji.EMOJI_ALIAS_UNICODE[':shamrock:']
# _four_leaf_clover = emoji.EMOJI_ALIAS_UNICODE[':four_leaf_clover:']
# _maple_leaf = emoji.EMOJI_ALIAS_UNICODE[':maple_leaf:']
#
# # -------------Faces--------------------------
# # ============================================================================
# _house_emoji = emoji.EMOJI_ALIAS_UNICODE[':house_with_garden:']

plants_list = [_seedling, _evergreen_tree, _deciduous_tree, _palm_tree, _sheaf_of_rice, _herb, _shamrock,
               _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind]


def music_file_keyboard(*args, **kwargs):
    """
    Generates a keyboard for the returned audio files
    :param args: Contains query = args[0] which is file id
    :param kwargs:
    :return: Generated keyboard
    """
    query = args[0]
    keyboard = [
        [InlineKeyboardButton(text=f"اضافه به پلی‌لیست | {_plus}",
                              switch_inline_query_current_chat=f"#addtopl: {query}"),
         InlineKeyboardButton(text=f"خانه | {_house}", callback_data="home")]

    ]
    return keyboard

def back_to_the_bot(*args, **kwargs):
    """
    Returns the "back to the button" on top of the inline results
    :param args:
    :param kwargs:
    :return: A text contains the desired string
    """
    back_text = f"برگشت به بات {_backhand_index_pointing_right}"
    return back_text

def playlist_keyboard(*args, **kwargs):
    """
    The necessary buttons for playlists
    :param args: 1. playlists, 2. audio_file, 3. add_new_pl_header, 4. function
    :param kwargs:
    :return: Generated keyboard
    """
    playlists = args[0]
    audio_file = args[1]
    add_new_pl_header = args[2]
    func = args[3]
    inp_message_content = ""
    if func == "addpl":
        inp_message_content = f"/addnewpl {audio_file['_id']}"
    elif func == "playlists":
        add_new_pl_header = False
        # inp_message_content = f"/showplaylist"
    elif func == "history":
        add_new_pl_header = False
    hidden_character = "‏‏‎ ‎"
    results = []
    list_length = len((list(enumerate(playlists))))
    if func == "history":

        for index, _audio_file in reversed(list(enumerate(playlists))):
            print("audio_file", _audio_file)
            file_id = _audio_file["_id"]
            inp_message_content = f"/dl_{file_id}"
            _title = str(_audio_file["_source"]["title"]).replace("@", "")
            _title_line = "<b>نام:</b> " + str(_title) + "\n"
            _performer = str(_audio_file["_source"]["performer"]).replace("@", "")
            _performer_line = "<b>اجرا کننده:</b> " + str(_performer) + "\n"
            _filename = str(_audio_file["_source"]["file_name"]).replace("@", "")
            _filename_line = "<b>نام فایل:</b> " + str(_filename) + "\n"
            # _title = str(_audio_file["_source"]["title"]).replace("@", "")
            # _title_line = "<b>Title:</b> " + str(_title) + "\n"
            # _performer = str(_audio_file["_source"]["performer"]).replace("@", "")
            # _performer_line = "<b>Performer:</b> " + str(_performer) + "\n"
            # _filename = str(_audio_file["_source"]["file_name"]).replace("@", "")
            # _filename_line = "<b>File name:</b> " + str(_filename) + "\n"
            if not len(_title) < 2:
                audio_title = _title
                description = _filename
            elif not len(_performer) < 2:
                audio_title = _performer
                description = _filename
            else:
                audio_title = _filename
                description = ""
            audio_title = hidden_character + audio_title
            description = hidden_character + description
            results.append(InlineQueryResultArticle(
                title=str(list_length - index) + '. ' + audio_title,
                description=description,
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                input_message_content=InputTextMessageContent(inp_message_content, parse_mode="HTML"),

            ))
    else:
        description = "پلی‌لیست جدید"
        if add_new_pl_header:
            results.append(InlineQueryResultArticle(
                title="اضافه کردن به پلی‌لیست جدید",
                description="یک پلی‌لیست جدید ایجاد شده و فایل به آن اضافه می‌شود",
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                input_message_content=InputTextMessageContent(inp_message_content, parse_mode="HTML"),

            ))
        for index, playlist in reversed(list(enumerate(playlists))):

            pl_id = playlist["_id"]
            if func == "addpl":
                inp_message_content = f"/addtoexistpl {pl_id} {audio_file['_id']}"
            elif func == "playlists":
                inp_message_content = f"/showplaylist {pl_id}"

            results.append(InlineQueryResultArticle(
                title=str(list_length - index) + '. ' + playlist["_source"]["title"],
                description=playlist["_source"]["description"],
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                input_message_content=InputTextMessageContent(inp_message_content, parse_mode="HTML"),

            ))
    return results

def playlists_buttons(*args, **kwargs):
    """
    Generates an inline keyboard for the playlists
    :param args:
    :param kwargs:
    :return: Returns a list of buttons
    """
    markup = [
        [InlineKeyboardButton(f"دانلود‌های من | {_mobile_phone_with_arrow}",
                              switch_inline_query_current_chat=f"#history"),
         InlineKeyboardButton(f"پلی‌لیست‌های من | {_headphone}", switch_inline_query_current_chat=f"#myplaylists")],
        [InlineKeyboardButton(f"خانه | {_house}", callback_data="home")]
    ]
    return markup

def mylists_menu_text(*args, **kwargs):
    """
    A Guid text for the user about the available lists to choose from:
        1. My Downloads
        2. My playlists
    :param args:
    :param kwargs:
    :return: Returns the generated text
    """
    text = f"<b>لطفا یکی از لیست‌های زیر را انتخاب کنید:</b>\n&rlm;{34 * '-'}\n\n" \
           f"&rlm;{_green_circle}<b>" \
           f" دانلود‌های من: " \
           f"</b>" \
           f"&rlm;" \
           f" لیست دانلود‌های اخیر شما (تا حداکثر ۵۰ فایل)" \
           f"\n" \
           f"&rlm;{_green_circle} <b>" \
           f"پلی‌لیست‌های من: " \
           f"</b> " \
           f"پلی‌لیست‌های فعلی شما: (می‌توانید تا ۵ پلی‌لیست ایجاد کنید و به هرکدام تا ۲۰ فایل صوتی اضافه کنید)