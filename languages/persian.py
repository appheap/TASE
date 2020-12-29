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

    # markup = [
    #     [InlineKeyboardButton(f"{_house} Edit title",
    #                           switch_inline_query_current_chat=f"#edit_title {playlist_id} "),
    #      InlineKeyboardButton(f"{_house} Edit description",
    #                           switch_inline_query_current_chat=f"#edit_description {playlist_id} ")],
    #     [InlineKeyboardButton(f"{_house} Delete playlist", callback_data=f"delete {playlist_id}"),
    #      InlineKeyboardButton(f"{_house} Delete audio file", callback_data=f"adelete {playlist_id}")],
    #     [InlineKeyboardButton(f"{_house} Back", callback_data=f"showplaylist {playlist_id}")]
    # ]
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
    # query_id = args[1]
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
        # [InlineKeyboardButton("Docs", url="https://docs.pyrogram.org")]
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

