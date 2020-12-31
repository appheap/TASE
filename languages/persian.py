"""####################################################################
# Copyright (C)                                                       #
# 2020 Soran Ghadri(soran.gdr.cs@gmail.com)                           #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
####################################################################"""

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
           f"پلی‌لیست‌های فعلی شما: (می‌توانید تا ۵ پلی‌لیست ایجاد کنید و به هرکدام تا ۲۰ فایل صوتی اضافه کنید)"
    return text


def single_playlist_markup_list(*args, **kwargs):
    """
    Generates a keyboard for each playlist; buttons:
        1. Audio files list (as an inline list)
        2. Get list (as a text message)
        3. Edit
        4. Delete
        5. Home
        6. Back
    :param args: args[0]: Playlist id
    :param kwargs:
    :return: A markup list containing mentioned buttons
    """
    playlist_id = args[0]
    markup = [
        [InlineKeyboardButton(f"فایل‌های صوتی | {_headphone}",
                              switch_inline_query_current_chat=f"#showfiles {playlist_id}"),
         InlineKeyboardButton(f"دریافت لیست | {_studio_microphone}", callback_data=f"get_list {playlist_id}")],
        [InlineKeyboardButton(f"ویرایش | {_gear}", callback_data=f"editpl {playlist_id}"),
         InlineKeyboardButton(f"حذف | {_cross_mark}", callback_data=f"delete {playlist_id}")],
        [InlineKeyboardButton(f"خانه | {_house}", callback_data="home"),
         InlineKeyboardButton(f"برگشت | {_BACK_arrow}", callback_data=f"showmyplaylists {playlist_id}")]
    ]
    return markup


def edit_playlist_information_guide(*args, **kwargs):
    """
    Guides the users how to edit their playlists. Two fields are available to edit:
        1. title
        2. description
    :param args: Field: the field that is going to be edited
    :param kwargs:
    :return: A text containing how to edit playlists
    """
    field = args[0]
    text = ""
    if field == "title":
        text = f"{_fountain_pen} " \
               f"اطلاعات را وارد کنید"
    elif field == "description":
        text = f"{_books} " \
               f"لطفا اطلاعات جدید را در ادامه‌ی متن زیر تایپ کنید"

    return text


def delete_audio_murkup_keyboard(*args, **kwargs):
    """
    Generates a keyboard for deleting single files from a specific playlist. This keyboard will be shown consecutive
     to "Edit" button being pressed in the previous step which was edit playlist.
     Buttons are:
        1. Crossmark to proceed with the deletion
        2. Back to cancel the process
    :param args:    1. Playlist_id = args[0]: The ID of the target playlist
                    2. Pl_audio_files = args[1]: A list of audio files withing this playlist
    :param kwargs:
    :return: A keyboard markup containing the above buttons
    """
    playlist_id = args[0]
    pl_audio_files = args[1]
    print("from delete audio_markup_keyboard - pl_audio_files: ", pl_audio_files)
    markup = []
    for _audio_file in pl_audio_files:
        _audio_file_id = _audio_file["_id"]
        markup.append([InlineKeyboardButton(f"{_cross_mark} | {_audio_file['_source']['title']}",
                                            callback_data=f"afdelete {playlist_id} {_audio_file_id}")])

    markup.append([InlineKeyboardButton(f"برگشت | {_BACK_arrow}",
                                        callback_data=f"editpl {playlist_id}")])

    return markup


def delete_audio_file_text(*args, **kwargs):
    """
    The header text for the audio file deletion from the playlist
    :param args:
    :param kwargs:
    :return: Text containing the header text for the audtio file deletion message and keyboard
    """
    text = f"{_cross_mark} <b>" \
           f"حذف فایل صوتی از پلی‌لیست" \
           f"</b>"
    return text


def delete_playlist_validation_keyboard(*args, **kwargs):
    """
    Generates a validation form for the user weather they want to proceed with the deletion of the audio file or the
     playlist itself. The buttons included in this keyboard are:
        1. Yes
        2. No
    :param args:    1. playlist_id
                    2. func: function type which means what do they want to delete
    :param kwargs:
    :return: The generated keyboard for deletion validation
    """
    playlist_id = args[0]
    func = args[1]
    return_args = ""
    if func == "playlist":
        return_args = f"{playlist_id}"
    elif func == "audio_file":
        audio_file_id = args[2]
        return_args = f"{playlist_id} {audio_file_id}"
    markup = [
        [InlineKeyboardButton(f"بله | {_thumbs_up}", callback_data=f"ydelete {return_args}"),
         InlineKeyboardButton(f"خیر | {_thumbs_down}", callback_data=f"ndelete {return_args}")]
    ]
    return markup

def delete_playlist_validation_text(*args: list, **kwargs) -> str:
    """
    This message asks the user to verify the deletion. In case yes was chosen, it will return the ID of the feature,
    otherwise it will acts as back button.
    :param args:    type [str]: 1. playlist
                                2. audio_file
    :param kwargs:
    :return: Returns a call-to-action message with button to verify the deletion. The result contains the IDs for
    playlists and/or audio-files
    """
    func = args[0]
    text = ""
    if func == "playlist":
        text = f"{_cross_mark} <b>" \
               f"آیا میخواهید پلی‌لیست برای همیشه حذف شود؟" \
               f"</b> {_studio_microphone}"
    elif func == "audio_file":
        text = f"{_cross_mark} <b>" \
               f"آیا میخواهید این فایل از پلی‌لیست فعلی حذف شود؟" \
               f"</b> {_headphone}"
    return text

def playlist_deleted_text(*args, **kwargs) -> str:
    """
    Deletion success text
    :param args:
    :param kwargs:
    :return: Generated text
    """
    text = f"{_check_mark_button}" \
           f"پلی‌لیست با موفقیت حذف شد"
    return text

def edit_playlist_keyboard(*args: list, **kwargs) -> list:
    """
    Generates a keyboard for playlists editing. Buttons are:
        1. Edit title
        2. Edit decription
        3. Delete playlist
        4. Delete audio-file
        5. Back
    :param args: Contains the playlist ID
    :param kwargs:
    :return:
    """
    playlist_id = args[0]
    markup = [
        [InlineKeyboardButton(f"ویرایش نام | {_wrench}",
                              switch_inline_query_current_chat=f"#edit_title {playlist_id} "),
         InlineKeyboardButton(f"ویرایش توضیحات | {_wrench}",
                              switch_inline_query_current_chat=f"#edit_description {playlist_id} ")],
        [InlineKeyboardButton(f"حذف پلی‌لیست | {_cross_mark}{_headphone}", callback_data=f"delete {playlist_id}"),
         InlineKeyboardButton(f"حذف فایل از پلی‌لیست | {_cross_mark}{_musical_note}",
                              callback_data=f"adelete {playlist_id}")],
        [InlineKeyboardButton(f"برگشت | {_BACK_arrow}", callback_data=f"showplaylist {playlist_id}")]
    ]
    return markup

def edit_playlist_text(*args: list, **kwargs) -> str:
    """
    Generates a text about the current attributes of the chosen playlist in the edit window
    :param args: Chosen playlist object
    :param kwargs:
    :return:
    """
    playlist = args[0]
    text = f"<b>" \
           f"ویرایش پلی‌لیست | {_headphone}" \
           f"</b>" \
           f"\n&rlm;{34 * '-'}\n\n" \
           f"&rlm;<b>" \
           f"نام:" \
           f"</b> " \
           f"\"{playlist['_source']['title']}\"\n\n" \
           f"&rlm;<b>" \
           f"توضیحات:" \
           f"</b> {playlist['_source']['description']}"
    return text

def single_playlist_text(*args: list, **kwargs) -> str:
    """
    Creates a description about a specific playlist
    :param args:    *[0] -> Playlist object
    :param kwargs:
    :return:
    """
    playlist = args[0]
    text = f"<b>" \
           f"منوی پلی‌لیست‌ها | {_headphone}" \
           f"</b>" \
           f"\n&rlm;{34 * '-'}\n\n" \
           f"&rlm;<b>" \
           f"نام:" \
           f"</b> \"{playlist['title']}\"\n\n" \
           f"&rlm;<b>" \
           f"توضیحات:" \
           f"</b> {playlist['description']}"

    return text

def languages_list(*args, **kwargs) -> str:
    """
    Generates a text containing a list of available languages (both in english and native writing system). Contains:
        1. English
        2. Hindi
        3. Russian
        4. Persian
        5. Arabic
    :param args:
    :param kwargs:
    :return: The generated text
    """
    text = f"<b>لطفا زبان مورد نظرت رو انتخاب کن:</b>\n\n" \
           f" {_en}<b> English </b> - /lang_en\n {34 * '-'} \n" \
           f" {_hi}<b> हिन्दी </b> (Hindi) - /lang_hi\n {34 * '-'} \n" \
           f" {_ru}<b> русский </b> (Russian) - /lang_ru\n {34 * '-'} \n" \
           f"&lrm; {_fa}<b> فارسی </b> (Persian) - /lang_fa\n {34 * '-'} \n" \
           f"&lrm; {_ar}<b> العربية </b> (Arabic) - /lang_ar\n\n" \
           f"{25 * '='} \n" \
           f"هر موقع خواستی میتونی عبارت دستوری " \
           f"<b>/lang</b>" \
           f" رو بفرستی و زبان رو تغییر بدی"
    return text

def choose_language_text(*args: list, **kwargs) -> str:
    """
    A call-to-action message for choosing the preferred language; plus a mini-guide on how to change the language later
    :param args: *[0] User's first name -> str
    :param kwargs:
    :return: A text containing the information
    """
    first_name = args[0]
    text = f"<b>" \
           f"لطفا زبان مورد نظرت رو انتخاب کن {first_name}" \
           f"</b> | {_globe_showing_Americas}\n\n" \
           f"بعدا هم با روش های زیر میتونی زبان رو تغییر بدی\n" \
           f"   ۱. فرستادن کد دستوری" \
           f" <b>/lang</b>\n" \
           f"   ۲. با مراجعه به " \
           f"<b>" \
           f"خانه | {_house}" \
           f"</b>"
    return text

def button_language_list(*args, **kwargs) -> list:
    """
    A keyboard containing the available languages. You Add your language name here to be included in the menu.
    Current languages:
        1. English
        2. Persian
        # not implemented yet:
        3. Hindi
        4. Russian
        5. Arabic
    :param args:
    :param kwargs:
    :return: A keyboard containing the mentioned buttons
    """
    markup = []
    stringList = {f" {_en} English": f"en", f" {_hi} हिन्दी (Hindi)": f"hi",
                  f" {_ru} русский (Russian)": f"ru", f"{_fa} فارسی (Persian)": f"fa",
                  f"{_ar} العربية (Arabic)": f"ar"}
    for key, value in stringList.items():
        markup.append([InlineKeyboardButton(text=key,
                                            callback_data=value)])
    return markup

def button_joining_request_keyboard(*args, **kwargs) -> str:
    """
    A keyboard containing buttons to join or announce if they are already joined
    :param args:
    :param kwargs:
    :return: Generated keyboard markup
    """
    markup = [
        [InlineKeyboardButton("همین الان عضو هستم", callback_data="joined"),
         InlineKeyboardButton("باشه الان عضو میشم", url="https://t.me/chromusic_fa")]  #
    ]
    return markup

def welcome(*args: list, **kwargs) -> str:
    """
    Shows a welcome message to the user after hitting 'start'
    :param args: *[0] -> user's first name
    :param kwargs:
    :return: Generated welcome message
    """
    name = args[0]
    text = f"{_headphone}" \
           f"<b>جستجوی انواع فایل های صوتی با بالاترین سرعت ممکن در تلگرام</b>{_headphone}\n\n" \
           f"به " \
           f" <b>Chromusic</b> " \
           f"خوش اومدی" \
           f", <b>{name}</b>.&rlm;" \
           f" خوشحالم که اینجایی.{_party_popper}" \
           f" الان میتونی خیلی ساده و بدون محدودیت سرچ کنی.{_zap}\n\n\n" \
           f"{_studio_microphone}" \
           f"هر نوع فایل صوتی رو (آهنگ, پادکست و ...) زیر ۱ ثانیه پیدا کن" \
           f" {_smiling_face_with_sunglasses}\n\n" \
           f"&rlm;{_green_circle} " \
           f"راهنمایی خواستی روی " \
           f"&lrm;/help " \
           f"کلیک کن" \
           f" {_winking_face}"
    return text

def file_caption(*args: list, **kwargs) -> str:
    """
    Generates caption for the retrieved audio files. Each caption contains:
        1. Title
        2. Performer
        3. File name (In case above fields were not available)
        4. File source (source channel username + message_id)

    :param args:    1. *[0] -> Audio track
                    2. *[1] -> Message id
    :param kwargs:
    :return: A caption containing audio file information
    """
    audio_track = args[0]
    message_id = args[1]
    chromusic_users_files_id = 165802777
    include_source = True
    _heart = random.choice(heart_list)
    _plant = random.choice(plants_list)
    if len(args) == 3 or audio_track.chat.id == chromusic_users_files_id:
        include_source = False
        user_files_id = args[2]
        print("its_from_file_caption")

    _title = str(audio_track.audio.title).replace("@", "")
    _title_line = "<b>نام:</b> " + str(_title) + "\n"
    _performer = str(audio_track.audio.performer).replace("@", "")
    _performer_line = "<b>اجرا کننده:</b> " + str(_performer) + "\n"
    _filename = str(audio_track.audio.file_name).replace("@", "")
    _filename_line = "<b>نام فایل:</b> " + str(_filename) + "\n"
    _source = f"<a href ='https://t.me/{audio_track.chat.username}/{message_id}'>{audio_track.chat.username}</a>"
    text = ""
    try:

        text = f"{_title_line if not _title == 'None' else ''}" \
               f"{_performer_line if not _performer == 'None' else ''}" \
               f"{_filename_line if (_title == 'None' and not _filename == 'None') else ''}" \
               f"{_round_pushpin}منبع: {_source if include_source else 'Sent by Chromusic users'}\n" \
               f"\n{_search_emoji} | <a href ='https://t.me/chromusic_bot'><b>کروموزیک</b>: جستجوی فایل‌های صوتی</a>\n" \
               f"&rlm;{_plant}"
    except Exception as e:
        print(f"from file caption: {e}")
    return text

def inline_file_caption(*args: list, **kwargs) -> str:
    """
    Generates caption for the retrieved audio files from inline searches. Each caption contains:
        1. Title
        2. Performer
        3. File name (In case above fields were not available)
        4. File source (source channel username + message_id)
    :param args:    1. *[0] -> Audio track
                    2. *[1] -> Message id
    :param kwargs:
    :return: A caption containing audio file information
    """
    audio_track = args[0]
    message_id = audio_track["_source"]["message_id"]

    # temp_perf_res = audio_track["_source"]["performer"]
    # temp_titl_res = audio_track["_source"]["title"]
    # temp_filnm_res = audio_track["_source"]["file_name"]
    # chromusic_users_files_id = 165802777
    chromusic_users_files_id = -1001288746290
    include_source = True
    _heart = random.choice(heart_list)
    _plant = random.choice(plants_list)
    text = f""
    if len(args) == 3 or audio_track["_source"]["chat_id"] == chromusic_users_files_id:
        include_source = False

        print("its_from_file_caption")
        return f"اگه در صفحه‌ی ربات نیستی, برای دریافت فایل این پیام رو برای ربات کروموزیک فوروارد کن" \
               f"\n<a href ='https://t.me/chromusic_bot'><b>ربات کروموزیک:</b> جستجوی فایل‌های صوتی</a>\n" \
               f"{_round_pushpin} | " \
               f"کانال فارسی: " \
               f"@Chromusic_fa\n" \
               f"{_round_pushpin} | " \
               f"کانال بین‌المللی: " \
               f"@Chromusic_fa" \
               f"\n\n{_headphone} | dl_{audio_track['_id']}\n" \
               f"{_plant}"

    try:
        _title = audio_track["_source"]["title"]
        _title_line = "<b>نام:</b> " + str(_title) + "\n"
        _performer = audio_track["_source"]["performer"]
        _performer_line = "<b>اجرا کننده:</b> " + str(_performer) + "\n"
        _filename = audio_track["_source"]["file_name"]
        _filename_line = "<b>نام فایل:</b> " + str(_filename) + "\n"
        _source = f"<a href ='https://t.me/{audio_track['_source']['chat_username']}/{message_id}'>{audio_track['_source']['chat_username']}</a>"
        text = f"{_title_line if not _title == None else ''}" \
               f"{_performer_line if not _performer == None else ''}" \
               f"{_filename_line if (_title == None and not _filename == None) else ''}" \
               f"{_round_pushpin}منبع: {_source if include_source else 'فرستاده شده توسط کاربران کروموزیک'}\n" \
               f"\n{_search_emoji} | <a href ='https://t.me/chromusic_bot'><b>کروموزیک:</b> جستجوی فایل‌های صوتی</a>\n" \
               f"&rlm;{_plant}"
    except Exception as e:
        print(f"from file caption: {e}")
    return text

def inline_join_channel_description_text(*args, **kwargs) -> str:
    """
    Shows a call-to-action text to users who have not Joined the channel yet (Description)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    hidden_character = "‏‏‎ ‎"
    text = f"{_headphone}" \
           f"لطفا ابتدا توی کانال کروموزیک عضو شوید" \
           f"{_thumbs_up}\n" \
           f"{_pushpin}آدرس: " \
           f"@Chromusic_fa"
    return text

def inline_join_channel_title_text(*args, **kwargs) -> str:
    """
    Shows a call-to-action text to users who have not Joined the channel yet (Title)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    text = f"{_green_circle} لطفا وارد کروموزیک شوید"
    return text

def inline_join_channel_content_text(*args, **kwargs) -> str:
    """
    Shows a call-to-action text to users who have not Joined the channel (When they click on the inline
        call-to-join result)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    plant = random.choice(plants_list)
    text = f"{_round_pushpin} " \
           f"به " \
           f"&lrm;<b>@Chromusic_fa</b> " \
           f"&rlm;" \
           f"بپیوندید " \
           f"{_smiling_face_with_sunglasses}\n" \
           f"تشکر بابت همکاریت با کروموزیک" \
           f" {plant}\n\n" \
           f"ضمنا یه کانال انگلیسی هم داریم خوشحال میشم تشریف بیارید" \
           f"\n" \
           f"آدرس کانال: " \
           f"&lrm;<b>@Chromusic\n" \
           f"&rlm;{_headphone}<a href='https://t.me/chromusic_bot'><b>جستجوی فایل‌های صوتی در کروموزیک:</b></a> &lrm;@chromusic_bot{_studio_microphone}"
    return text

def example_message(*args, **kwargs) -> str:
    """
    Mini-tutorial for the first time the users starts the bot. This is a sample message on how to search
        audio files in the bot.
    :param args:
    :param kwargs:
    :return: Generated text
    """
    text = f"{_search_emoji}&rlm;<b>۱. " \
           f"نام آهنگ و یا اجراکننده رو بفرست:" \
           f"</b>\n" \
           f"{_checkmark_emoji}<b>" \
           f"مثال:" \
           f"</b> " \
           f"معین - آواز جدایی" \
           f"\n\n&rlm;<b>" \
           f"۲. برای دریافت هر کدام از آهنگ‌ها روی لینک‌های مقابل آنها که با " \
           f"\"/ dl_\"" \
           f"شروع می‌شوند کلیک کنید" \
           f"\n" \
           f"مثال:" \
           f"</b> " \
           f"/dl_8AEVX0ux"
    return text


def collaboration_request(*args, **kwargs) -> str:
    """
    Requires the user for collaboration
    :param args:
    :param kwargs:
    :return: returns the inquiry text message
    """
    plant = random.choice(plants_list)
    plant2 = random.choice(plants_list)
    plant3 = random.choice(plants_list)
    text = f"&rlm;{_red_heart}{plant} " \
           f"<b>" \
           f"لطفا ما را با دوستان خود به اشتراک بگذارید" \
           f"</b>\n\n" \
           f"{plant2} " \
           f"با توجه به اینکه هرماه هزینه‌ای برای سرورهای کروموزیک تخصیص داده‌ شده, لطفا برای حمایت از ما این سرویس جستجوی موزیک را با دوستانتان به" \
           f" <b>" \
           f"اشتراک" \
           f"</b> " \
           f"بگذارید تا همچنان این سرویس به صورت رایگان به فعالیت خود ادامه دهد. با تشکر" \
           f" {plant3}\n" \
           f"@chromusic_bot"
    return text

def thanks_new_channel(*args: list, **kwargs) -> str:
    """
    Thanks a user for his/her collaboration
        1. Sending channel name
        2. Sending Music file
    :param args:
    :param kwargs:
    :return: Generated result
    """
    message = args[0]
    _heart = random.choice(heart_list)
    _plant = random.choice(plants_list)
    text = f"متشکرم" \
           f" {message.from_user.first_name} " \
           f"برای همکاریت با کرومیوزیک" \
           f" {_heart}{_plant}"
    return text

def lang_register_alert(*args: list, **kwargs) -> str:
    """
    An alert validating the user's preferred language has been saved
    :param args:
    :param kwargs:
    :return: Generated alert
    """
    first_name = args[0]
    dir = "&rlm;"
    text = f"بسیار خب {first_name} زبان فارسی برات ثبت شد {_confetti_ball}{_party_popper}\n\n" \
           f"هرموقع خواستی میتونی با استفاده از\n کد دستوری \"lang/\" زبان رو دوباره انتخاب کنی"
    return text

def send_in_1_min(*args: list, **kwargs) -> str:
    """
    A message notifying users when they are not joined the channel and have surpassed the maximum free download. It
        alerts them about sending the audio file after one minumte
    :param args: *[0] -> first name
    :param kwargs:
    :return: Generated message
    """
    first_name = args[0]
    text = f"&rlm;{_green_circle} بسیار خوشحالم که کار با این سرویس رو دوست داری, " \
           f"<b>{first_name}</b> {_smiling_face_with_heart}. " \
           f"اگه دوست داری #سرعت سرویس همچنان بالا باشه " \
           f"<b>" \
           f"لطفا توی کانال" \
           f" &lrm;@chromusic_fa {_headphone}{_artist_palette}" \
           f" عضو شو\n\n" \
           f"</b>" \
           f" کانال انگلیسی ما: &lrm;@chromusic {_headphone}{_artist_palette}\n\n " \
           f"هرچند که فایل رو همچنان دریافت خواهی کرد (در ۱ دقیقه)" \
           f"  {_winking_face}"
    return text

def has_joined(*args: list, **kwargs) -> str:
    """
    Validates the user's joining the channel after being required to join.
    :param args: *[0] -> first name
    :param kwargs:
    :return: Generated validation message
    """
    first_name = args[0]
    text = f"{_star_struck}{_smiling_face_with_heart} بسیار خب " \
           f"<b>{first_name}</b> " \
           f", حالا تمام دسترسی ها رو داری{_party_popper}{_confetti_ball}\n\n" \
           f"تبریک از طرف @chromusic_fa {_red_heart}\n" \
           f"با خیال راحت هر فایل صوتی رو سرچ کن {_face_blowing_a_kiss}"
    return text

def not_joined(*args, **kwargs) -> str:
    """
    This will be shown when users claim to already have joined and they are lying
    :param args:
    :param kwargs:
    :return: Generated message for rejecting user's claim
    """
    text = f"{_face_with_raised_eyebrow} الان نگاه کردم, هنوز عضو کانال فارسی نیستی.\n\n " \
           f"{_green_heart} عضو @chromusic_fa شو" \
           f" تا تمام قابلیت ها به صورت کاملا #رایگان برات فعال شه {_red_heart}"
    return text

def result_list_handler(*args: list, **kwargs) -> str:
    """
    Handles the main search result for each query. It checks whether there are any result for this qeury or not.
        1. If there was results, then it sorts and decorates the them.
        2 Otherwise it shows a message containing there were no results for this query
    :param args:    1. *[0] -> query
                    2. *[1] -> a list of search results objects
    :param kwargs:
    :return: Final decorated search results
    """
    query = args[0]
    search_res = args[1]

    print(UD.bidirectional(u'\u0688'))
    x = len([None for ch in query if UD.bidirectional(ch) in ('R', 'AL')]) / float(len(query))
    # print('{t} => {c}'.format(t=query.encode('utf-8'), c='RTL' if x > 0.5 else 'LTR'))
    # print(UD.bidirectional("dds".decode('utf-8')))
    # direction = 'RTL' if x > 0.5 else 'LTR'
    dir_str = "&rlm;" if x > 0.5 else '&lrm;'
    fruit = random.choice(fruit_list)
    print(search_res)
    if int(search_res["hits"]["total"]["value"]) > 0:
        text = f"<b>{_search_emoji} نتایج جستجو برای: {textwrap.shorten(query, width=100, placeholder='...')}</b>\n"
        text += f"{_checkmark_emoji} نتایج بهتر پایین لیست هستند.\n\n\n"
        _headphone_emoji = emoji.EMOJI_ALIAS_UNICODE[':headphone:']
        for index, hit in reversed(list(enumerate(search_res['hits']['hits']))):
            duration = timedelta(seconds=int(hit['_source']['duration']))
            d = datetime(1, 1, 1) + duration
            _performer = hit['_source']['performer']
            _title = hit['_source']['title']
            _file_name = hit['_source']['file_name']
            if not (len(_title) < 2 or len(_performer) < 2):
                name = f"{_performer} - {_title}"
            elif not len(_performer) < 2:
                name = f"{_performer} - {_file_name}"
            else:
                name = _file_name

            # name = f"{_file_name if (_performer == 'None' and _title == 'None') else (_performer if _title == 'None' else _title)}".replace(
            #     ".mp3", "")

            text += f"<b>{str(index + 1)}. {dir_str} {_headphone_emoji} {fruit if index == 0 else ''}</b>" \
                    f"<b>{textwrap.shorten(name, width=35, placeholder='...')}</b>\n" \
                    f"{dir_str}     {_floppy_emoji} | {round(int(hit['_source']['file_size']) / 1000_000, 1)} {'مگابایت' if x > 0.5 else 'MB'}  " \
                    f"{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}\n{dir_str}" \
                    f"      دانلود: " \
                    f" /dl_{hit['_id']} \n" \
                    f"      {34 * '-' if not index == 0 else ''}{dir_str} \n\n"
    else:
        text = f"{_traffic_light}  هیچ نتیجه ای برای این عبارت پیدا نشد:" \
               f"\n<pre>{textwrap.shorten(query, width=200, placeholder='...')}</pre>"
    return text

def playlist_updated_text(*args: list, **kwargs) -> str:
    """
    Playlist update validation message on success
    :param args: *[0] -> function
    :param kwargs:
    :return: Validation-on-success message
    """
    func = args[0]
    text = ""
    if func == "title_update":
        text = f"<b> {_check_mark_button} " \
               f"نام جدید پلی‌لیست با موفقیت ذخیره شد" \
               f"</b>"
    elif func == "description_update":
        text = f"<b> {_check_mark_button} " \
               f"توضیحات جدید پلی‌لیست با موفقیت ذخیره شد" \
               f"</b>"
    return text

def added_to_playlist_success_text(*args: list, **kwargs) -> str:
    """
    Shows a success message for audio-file addition to a playlist
    :param args:    1. *[0] -> function
                    2. *[1] -> audio-file data
    :param kwargs:
    :return: A message on success containing the results and a mini-guide about how to change these
        default information later
    """
    func = args[0]
    data = args[1]
    text = ""
    if func == "addnewpl":
        print("data from english:", data)
        text = f"<b>۱. پلی‌لیست جدید با موفقیت ایجاد شد | {_check_mark_button}</b>\n" \
               f"       نام پیشفرض: " \
               f"{data['title']}\n" \
               f"توضیحات پیشفرض: " \
               f"{data['description']}\n" \
               f"       با استفاده از دکمه ویرایش می‌توانید اطلاعات پیشفرض را تغییر دهید:" \
               f"\n&rlm;" \
               f"            my playlists -> edit -> ...\n" \
               f"<b>۲. فایل صوتی به پلی‌لیست اضافه شد | {_check_mark_button}</b>\n&rlm;{34 * '-'}\n\n" \
               f"&rlm;" \
               f"{_green_circle} با استفاده از دکمه  " \
               f"<b>\"خانه | {_house}\"</b>" \
               f"می‌توانید پلی‌لیست‌ها و لیست دانلود‌های اخیرتان را ببینید"
    elif func == "addtoexistpl":
        playlist = args[2]
        text = f"<b>۱. فایل صوتی به پلی‌لیست اضافه شد | {_check_mark_button}</b></b>\n" \
               f"       نام فایل: " \
               f"{data['title']}\n" \
               f"       نام پلی‌لیست: " \
               f"{playlist['_source']['title']}\n" \
               f"       با استفاده از دکمه ویرایش می‌توانید اطلاعات پیشفرض را تغییر دهید:" \
               f"\n&rlm;" \
               f"            my playlists -> edit\n&rlm;{34 * '-'}\n\n" \
               f"&rlm;" \
               f"{_green_circle} با استفاده از دکمه  " \
               f"<b>\"خانه | {_house}\"</b>" \
               f"می‌توانید پلی‌لیست‌ها و لیست دانلود‌های اخیرتان را ببینید"
    return text

def delete_audio_guide_text(*args, **kwargs) -> str:
    """
    Guides users how to delete an audio-file from the current playlist.
    :param args:
    :param kwargs:
    :return: Deletion mini-guide message
    """
    text = f"{_green_circle}" \
           f"با کلیک روی هرکدام از دکمه‌های زیر می‌توانید فایل صوتی را از پلی‌لیست فعلی حذف کنید"
    return text

def home_markup_keyboard(*args, **kwargs) -> list:
    """
    The main keyboard of the bot. It contains following buttons:
        1. My Downloads: A list of last 50 downloads
        2. My Playlists: A list of user's playlists
        3. Language: Returns the language choosing keyboard
        4. Advertisement: Redirects to the advertisement channel
        5. How To: Shows an inline list of tutorials [website urls]
    :param args:
    :param kwargs:
    :return: Final markup result
    """
    markup = [
        [InlineKeyboardButton(f"دانلودهای من | {_mobile_phone_with_arrow}",
                              switch_inline_query_current_chat=f"#history"),
         InlineKeyboardButton(f"پلی‌لیست‌های من | {_headphone}", switch_inline_query_current_chat=f"#myplaylists")],
        [InlineKeyboardButton(f"زبان | {_globe_showing_Americas}", callback_data="lang")],
        [InlineKeyboardButton(f"تبلیغات | {_chart_increasing}{_bar_chart}", url="https://t.me/chromusic_ads"),
         # callback_data="ads"),
         InlineKeyboardButton(f"راهنمایی | {_exclamation_question_mark}",
                              switch_inline_query_current_chat=f"#help_catalog")]
    ]
    return markup

def help_markup_keyboard(*args, **kwargs) -> list:
    """
    The help keyboard of the bot. It contains following buttons:
        1. My Downloads: A list of last 50 downloads
        2. My Playlists: A list of user's playlists
        3. Back: Returns back to the 'Home' keyboard
        4. Advertisement: Redirects to the advertisement channel
        5. Help: Shows an inline list of tutorials [website urls]
    :param args:
    :param kwargs:
    :return: Final markup result
    """
    markup = [
        [InlineKeyboardButton(f"دانلودهای من | {_mobile_phone_with_arrow}",
                              switch_inline_query_current_chat=f"#history"),
         InlineKeyboardButton(f"پلی‌لیست‌های من | {_headphone}", switch_inline_query_current_chat=f"#myplaylists")],
        [InlineKeyboardButton(f"برگشت | {_BACK_arrow}", callback_data="home")],
        [InlineKeyboardButton(f"تبلیغات | {_chart_increasing}{_bar_chart}", url="https://t.me/chromusic_ads")
            , InlineKeyboardButton(f"راهنمایی | {_exclamation_question_mark}",
                                   switch_inline_query_current_chat=f"#help_catalog")]
    ]
    return markup

def help_keyboard_text(*args, **kwargs) -> str:
    """
    Help message showing on top of the 'Help' menu
    :param args:
    :param kwargs:
    :return: Generated results
    """
    _heart = random.choice(heart_list)
    _plant = random.choice(plants_list)
    text = f"&rlm;<b>راهنمایی‌ | {_exclamation_question_mark}</b>\n&rlm;{34 * '-'}\n\n" \
           f"کانال‌های ما:\n" \
           f"{_pushpin} | " \
           f"کانال انگلیسی: " \
           f"<b>@chromusic</b>\n" \
           f"{_pushpin} | " \
           f"کانال فارسی: " \
           f"<b>@chromusic_fa</b> \n&rlm;{34 * '-'}\n\n" \
           f"پیج‌های اینستاگرام کروموزیک:\n" \
           f"<a href='https://www.instagram/chromusic.official'>کروموزیک</a> | {_round_pushpin}\n" \
           f"<a href='https://www.instagram/chromusic_fa'>کروموزیک فارسی</a> | {_round_pushpin}\n\n" \
           f"&rlm;{_plant}{_heart}"
    return text

def home_keyboard_text(*args, **kwargs) -> str:
    """
    Home message showing on top of the 'Home' Menu
    :param args:
    :param kwargs:
    :return: Generated results
    """
    _heart = random.choice(heart_list)
    _plant = random.choice(plants_list)
    text = f"&rlm;<b>خانه | {_house}</b>\n&rlm;{34 * '-'}\n\n" \
           f"کانال‌های ما:\n" \
           f"{_pushpin} | &rlm;" \
           f"کانال انگلیسی: " \
           f"<b>&lrm;@chromusic</b>\n" \
           f"{_pushpin} | &rlm;" \
           f"کانال فارسی: " \
           f"<b>&lrm;@chromusic_fa</b>\n&rlm;{34 * '-'}\n\n" \
           f"پیج‌های اینستاگرام کروموزیک:\n" \
           f"<a href='https://www.instagram.com/chromusic_official/'><b>کروموزیک</b></a> | {_round_pushpin}\n" \
           f"<a href='https://www.instagram.com/chromusic_fa'><b>کروموزیک فارسی</b></a> | {_round_pushpin}\n\n" \
           f"&rlm;{_plant}{_heart}"
    return text


def file_deleted_from_playlist(*args, **kwargs) -> str:
    """
    Audio-file deletion validation message
    :param args:
    :param kwargs:
    :return: Generated validation message
    """
    text = f"{_check_mark_button} " \
           f"فایل با موفقیت حذف شد"
    return text

def help_inline_keyboard_list(*args, **kwargs) -> list:
    """
    An inline list including necessary features. Will be shown after requesting "How To" or "Help" button in "Home" and
        "Help" menus.
    Current items:
        1. How to advertise?
        2. How to search for and download an audio track
        3. How to register my own audio track?
        4. How to add my channel to Chromusic
        5. Contact us
        6. About us
    This feature acts like a blog for a website. To add blogs we recommend using telegra.ph website which is related to
        Telegram itself
    :param args:
    :param kwargs:
    :return: Generated inline list of blogs
    """
    results = []
    results.append(InlineQueryResultArticle(
        title="*. سوران قادری",
        description="کدهای برنامه و پروفایل برنامه‌نویس",
        thumb_url="https://telegra.ph/file/6e6831bdd89011688bddb.jpg",
        input_message_content=InputTextMessageContent(f"&rlm;"
                                                      f"برای دیدن کدها روی گیتهاب, اینچا کلیک کنید:\n"
                                                      f"<a href='https://github.com/soran-ghadri/'><b>"
                                                      f"گیتهاب"
                                                      f"</b></a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="۱. نحوه تبلیغات در کروموزیک",
        description="اگه میخوای تبلیغات کنی این گزینه رو بزن",
        thumb_url="https://telegra.ph/file/6e6831bdd89011688bddb.jpg",
        input_message_content=InputTextMessageContent(f"&rlm;"
                                                      f"هرآنچه رو قبل از تبلیغات باید بدونی:\n"
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'><b>"
                                                      f"تبلیغات کروموزیک"
                                                      f"</b></a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="۲. نحوه جستجو و دانلود موزیک و فایل‌های صوتی",
        description="به آسانی میتونید فایل‌های دلخواهت رو در چند میلی‌ثانیه پیدا و دانلود کنی",
        thumb_url="https://telegra.ph/file/36fc0478a793bd6db8c4e.jpg",
        input_message_content=InputTextMessageContent(f"&rlm;"
                                                      f"آموزش جستجوی موزیک رو در این متلب بخونید: \n"
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'><b>&rlm;"
                                                      f"جستجوی بهینه"
                                                      f"</b></a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="۳. ثبت موزیک و فایل‌های صوتی خودم در کروموزیک",
        description="برای آگاهی از نحوه ثبت موزیک و فایل‌های صوتی این گزینه رو انتخاب کنید",
        thumb_url="https://telegra.ph/file/36fc0478a793bd6db8c4e.jpg",
        input_message_content=InputTextMessageContent(f"&rlm;"
                                                      f"در این مقاله راهنمای کامل "
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"<b>چگونه موزیک و فایل صوتی خودم رو در کروموزیک ثبت کنم</b></a> "
                                                      f"(موزیک, پادکست, کتاب صوتی و ...),"
                                                      f" بخوان", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="۴. ثبت کانال خودم در کروموزیک",
        description="اگه میخوای فایل‌های صوتی کانالت در کروموزیک ثبت شه این گزینه رو انتخاب کن",
        thumb_url="https://telegra.ph/file/36fc0478a793bd6db8c4e.jpg",
        input_message_content=InputTextMessageContent(f"&rlm;"
                                                      f"انیجا میتونی یک راهنمایی کامل در باره‌ی"
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"<b>"
                                                      f"ثبت کانال"
                                                      f"</b></a>"
                                                      f" خودم در کروموزیک بخوانی\n"
                                                      f"<b>&rlm;{_check_mark_button} "
                                                      f"توجه: نام کانال شما همراه فایل صوتی نمایش داده میشود "
                                                      f"</b>\n", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="۵. تماس با ما",
        description="برای تماس با تیم ما اینجا کلین کنید",
        thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
        input_message_content=InputTextMessageContent(f"می توانید با از طریق آی‌دی "
                                                      f"@[your admin username]\n"
                                                      f"در ارتباط با"
                                                      f"\n"
                                                      f"برای اطلاعات بیشتر روی لینک زیر کلیک کنید"
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"تماس با ما"
                                                      f"</a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="۶. درباره ما",
        description="درباره تیم ما بیشتر بدانید",
        thumb_url="https://telegra.ph/file/17ea2995a5146d4c32e7b.jpg",
        input_message_content=InputTextMessageContent(f"<b>&rlm;"
                                                      f"در اینجا لینک‌های ارتباطی با بخش پشتیبانی و همنیطور بیشتر درباره‌ی ما بخوانید"
                                                      f"</b>\n&rlm;<a href='https://github.com/soran-ghadri/'>"
                                                      f"درباره‌ی تیم ما"
                                                      f"</a>", parse_mode="HTML")))
    return results

def contribution_thanks(*args: list, **kwargs) -> str:
    """
    Shows a thank you message to the contributing users
    :param args:    1. *[0] -> first name
                    2. *[1] -> is the file registered or not
    :param kwargs:
    :return: Thank you message
    """
    first_name = args[0]
    registered = args[1]
    if len(args) == 3:
        if args[2] > 1:
            count = args[2]
            temp = f"&rlm;{count}" \
                   f"آیتم ثبت شد"
        else:
            temp = ''
    else:
        temp = ''

    if registered:
        _plant = random.choice(plants_list)
        _heart = random.choice(heart_list)
        text = f"تشکر" \
               f"<b>{first_name}</b>. " \
               f"بابت همکاریت با کروموزیک" \
               f"{_heart}{_plant}.\n\n" \
               f"{temp}"
    else:
        _plant = random.choice(plants_list)
        _heart = random.choice(heart_list)
        text = f"تشکر " \
               f"<b>{first_name}</b> " \
               f"بابت همکاریت با کروموزیک. " \
               f"{_heart}{_plant}\n\n"
    return text

def long_time_not_active(*args: list, **kwargs) -> str:
    """
    This message will be shown to users being inactive more than 5 days and 14 days (as the longer period)
    :param args:    1. *[0] -> firstname
                    2. *[1] -> number of days being inactive
    :param kwargs:
    :return: The welcome again message
    """
    first_name = args[0]
    not_active_since = args[1]
    _plant = random.choice(plants_list)
    _heart = random.choice(heart_list)
    if not_active_since > 14:
        text = f"سلام " \
               f"<b>{first_name}</b>" \
               f"خیلی وقته نا پیدایی!" \
               f"\nاگه هر سوالی در مورد سرویس‌های ما داری خوشحال میشم " \
               f"<b>#راهنماییت</b>" \
               f" کنم. " \
               f"{_heart}{_plant}"
    else:
        text = f"سلام مجدد " \
               f"<b>{first_name}</b>.\n " \
               f"هرموقع " \
               f"<b>#راهنمایی</b> " \
               f"لازم داشتی میتونی از صفحه کلید زیر دکمه راهنمایی رو بزنی " \
               f"{_heart}{_plant}"
    return text

def checking_items_started(*args, **kwargs) -> str:
    """
    This will appear after sending channel names to be indexed
    :param args:
    :param kwargs:
    :return: A text notifying users that the bot is already checking their sent channel usernames
    """
    _plant = random.choice(plants_list)
    _heart = random.choice(heart_list)
    text = f"بررسی آیتم‌ها شروع شد ... {_clock_emoji}\n" \
           f"تموم شد بهت خبر میدم. " \
           f"{_plant}{_heart}"
    return text

