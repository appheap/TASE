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
    _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind, _smiling_face_with_sunglasses, \
    _winking_face, \
    _smiling_face_with_heart, _face_blowing_a_kiss, _face_with_raised_eyebrow

plants_list = [_seedling, _evergreen_tree, _deciduous_tree, _palm_tree, _sheaf_of_rice, _herb, _shamrock,
               _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind]

# ------Following three methods are specific to english.py module------
def inline_start_bot_title_text(*args, **kwargs) -> str:
    """
    Shows a call-to-start text to users who have not started the bot yet (Title)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    text = f"{_green_circle} Please start the Chromusic bot first"
    return text


def inline_start_bot_description_text(*args, **kwargs) -> str:
    """
    Shows a call-to-start text to users who have not started the bot yet (Description)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    hidden_character = "‏‏‎ ‎"
    text = f"{_headphone}To Enable this feature please hit the start button on Chromusic_bot{_thumbs_up}\n{_pushpin}@Chromusic_fa"
    return text


def inline_start_bot_content_text(*args, **kwargs) -> str:
    """
    Shows a call-to-start text to users who have not started the bot yet (When they click on the inline
        call-to-start result)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    plant = random.choice(plants_list)
    text = f"{_round_pushpin}To enable the search engine work for you please hit the <b>start</b> button on " \
           f"<b>@Chromusic_bot</b>{_smiling_face_with_sunglasses} page and <b>join</b> at least one of our channels:\n" \
           f"{_pushpin}@Chromusic_fa" \
           f"\nThank you for joining {plant}\n\n" \
           f"{_headphone}<a href='https://t.me/chromusic_bot'><b>Chromusic audio search engine</b></a>{_studio_microphone}"
    return text
# ------End of english.py specific modules------

def music_file_keyboard(*args: str, **kwargs: str) -> list[object]:
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


def playlist_keyboard(*args: list, **kwargs: object) -> list[object]:
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
        print("inp_message_content: ", inp_message_content)
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
            file_id = _audio_file["_id"]
            inp_message_content = f"/dl_{file_id}"
            _title = str(_audio_file["_source"]["title"]).replace("@", "")
            _title_line = "<b>Title:</b> " + str(_title) + "\n"
            _performer = str(_audio_file["_source"]["performer"]).replace("@", "")
            _performer_line = "<b>Performer:</b> " + str(_performer) + "\n"
            _filename = str(_audio_file["_source"]["file_name"]).replace("@", "")
            _filename_line = "<b>File name:</b> " + str(_filename) + "\n"
            if not _title == None:
                audio_title = _title
                description = _filename
            elif not _performer == None:
                audio_title = _performer
                description = _filename
            else:
                audio_title = _filename
                description = ""
            description = hidden_character + description
            results.append(InlineQueryResultArticle(
                title=hidden_character + str(list_length - index) + '. ' + audio_title,
                description=description,
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                input_message_content=InputTextMessageContent(inp_message_content, parse_mode="HTML"),

            ))
    else:
        description = "New Playlist"
        if add_new_pl_header:
            results.append(InlineQueryResultArticle(
                title="Add to a new playlist",
                description="A new playlist will be created and the file will be added to it",
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
                title=hidden_character + str(list_length - index) + '. ' + playlist["_source"]["title"],
                description=hidden_character + playlist["_source"]["description"],
                thumb_url="https://telegra.ph/file/cd08f00005cb527e6bcdb.jpg",
                input_message_content=InputTextMessageContent(inp_message_content, parse_mode="HTML"),

            ))
    return results


def playlists_buttons(*args, **kwargs) -> list[object]:
    """
    Generates an inline keyboard for the playlists
    :param args:
    :param kwargs:
    :return: Returns a list of buttons
    """
    markup = [
        [InlineKeyboardButton(f"My Downloads | {_mobile_phone_with_arrow}",
                              switch_inline_query_current_chat=f"#history"),
         InlineKeyboardButton(f"My Playlists | {_headphone}", switch_inline_query_current_chat=f"#myplaylists")],
        [InlineKeyboardButton(f"Home | {_house}", callback_data="home")]
    ]
    return markup


def mylists_menu_text(*args, **kwargs) -> str:
    """
    A Guid text for the user about the available lists to choose from:
        1. My Downloads
        2. My playlists
    :param args:
    :param kwargs:
    :return: Returns the generated text
    """
    text = f"<b>Please choose one of the lists below:</b>\n{34 * '-'}\n\n" \
           f"{_green_circle} <b>My Downloads:</b> your recently donwloaded audio files (up to 50)\n" \
           f"{_green_circle} <b>My playlists:</b> your current playlists (5 playlists at maximum and 20 audio files per playlist)\n"
    return text


def single_playlist_markup_list(*args: str, **kwargs) -> list[object]:
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
        [InlineKeyboardButton(f"Audio files | {_headphone}",
                              switch_inline_query_current_chat=f"#showfiles {playlist_id}"),
         InlineKeyboardButton(f"Get list | {_studio_microphone}", callback_data=f"get_list {playlist_id}")],
        [InlineKeyboardButton(f"Edit | {_gear}", callback_data=f"editpl {playlist_id}"),
         InlineKeyboardButton(f"Delete | {_cross_mark}", callback_data=f"delete {playlist_id}")],
        [InlineKeyboardButton(f"Home | {_house}", callback_data="home"),
         InlineKeyboardButton(f"Back | {_BACK_arrow}", callback_data=f"showmyplaylists {playlist_id}")]
    ]
    return markup


def edit_playlist_information_guide(*args: str, **kwargs) -> str:
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
        text = f"{_fountain_pen} Enter playlist name/description"
    elif field == "description":
        text = f"{_books} Please write new playlist information in the following text box "

    return text


def delete_audio_murkup_keyboard(*args: list, **kwargs) -> list[object]:
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

    markup.append([InlineKeyboardButton(f"Back | {_BACK_arrow}",
                                        callback_data=f"editpl {playlist_id}")])

    return markup


def delete_audio_file_text(*args, **kwargs) -> str:
    """
    The header text for the audio file deletion from the playlist
    :param args:
    :param kwargs:
    :return: Text containing the header text for the audtio file deletion message and keyboard
    """
    text = f"{_cross_mark} <b>Delete audio files from playlist</b>"
    return text


def delete_playlist_validation_keyboard(*args: list[object], **kwargs) -> list[object]:
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
        [InlineKeyboardButton(f"Yes | {_thumbs_up}", callback_data=f"ydelete {return_args}"),
         InlineKeyboardButton(f"No | {_thumbs_down}", callback_data=f"ndelete {return_args}")]
    ]
    return markup


def delete_playlist_validation_text(*args: list, **kwargs) -> list:
    """
    This message asks the user to verify the deletion. In case yes was chosen, it will return the ID of the feature,
    otherwise it will acts as back button.
    :param args:    type [str]: 1. playlist
                                2. audio_file
    :param kwargs:
    :return: Returns a call-to-action message with button to verify the deletion. The result contains the IDs for
    playlists and/or audio-files
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
        [InlineKeyboardButton(f"Yes | {_thumbs_up}", callback_data=f"ydelete {return_args}"),
         InlineKeyboardButton(f"No | {_thumbs_down}", callback_data=f"ndelete {return_args}")]
    ]


def playlist_deleted_text(*args, **kwargs) -> str:
    """
    Deletion success text
    :param args:
    :param kwargs:
    :return: Generated text
    """
    text = f"{_check_mark_button} Playlist deleted successfully"
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
        [InlineKeyboardButton(f"Edit title | {_wrench}",
                              switch_inline_query_current_chat=f"#edit_title {playlist_id} "),
         InlineKeyboardButton(f"Edit description | {_wrench}",
                              switch_inline_query_current_chat=f"#edit_description {playlist_id} ")],
        [InlineKeyboardButton(f"Delete playlist | {_cross_mark}{_headphone}", callback_data=f"delete {playlist_id}"),
         InlineKeyboardButton(f"Delete audio file | {_cross_mark}{_musical_note}",
                              callback_data=f"adelete {playlist_id}")],
        [InlineKeyboardButton(f"Back | {_BACK_arrow}", callback_data=f"showplaylist {playlist_id}")]
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
    text = f"<b>Edit playlist | {_headphone}</b>\n{34 * '-'}\n\n" \
           f"<b>Title</b>: \"{playlist['_source']['title']}\"\n\n" \
           f"<b>Description</b>: {playlist['_source']['description']}"
    return text


def single_playlist_text(*args: list, **kwargs) -> str:
    """
    Creates a description about a specific playlist
    :param args: *[0] -> Playlist object
    :param kwargs:
    :return:
    """
    playlist = args[0]
    text = f"<b>Playlist menu | {_headphone}</b>" \
           f"\n{34 * '-'}\n\n" \
           f"<b>Title</b>: \"{playlist['title']}\"\n\n" \
           f"<b>Description</b>: {playlist['description']}"
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
    text = f"<b>Please choose your language:</b>\n\n" \
           f" {_en}<b> English </b> - /lang_en\n {34 * '-'} \n" \
           f" {_hi}<b> हिन्दी </b> (Hindi) - /lang_hi\n {34 * '-'} \n" \
           f" {_ru}<b> русский </b> (Russian) - /lang_ru\n {34 * '-'} \n" \
           f"&lrm; {_fa}<b> فارسی </b> (Persian) - /lang_fa\n {34 * '-'} \n" \
           f"&lrm; {_ar}<b> العربية </b> (Arabic) - /lang_ar\n\n" \
           f"{25 * '='} \nYou can change this later by sending <b>/lang</b>"
    return text


def choose_language_text(*args: list, **kwargs) -> str:
    """
    A call-to-action message for choosing the preferred language; plus a mini-guide on how to change the language later
    :param args: *[0] User's first name -> str
    :param kwargs:
    :return: A text containing the information
    """
    first_name = args[0]
    text = f"<b>Please choose your language {first_name} |</b> {_globe_showing_Americas}\n\nYou can change this later by :\n" \
           f"   1. Sending <b>/lang</b>\n" \
           f"   2. Go to <b>Home | {_house}</b>"
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
        # InlineKeyboardButton(text=value,
        #                      callback_data="['key', '" + key + "']")])

    return markup


def button_joining_request_keyboard(*args, **kwargs) -> str:
    """
    A keyboard containing buttons to join or announce if they are already joined
    :param args:
    :param kwargs:
    :return: Generated keyboard markup
    """
    markup = [
        [InlineKeyboardButton(f"I've already joined | {_check_mark_button}", callback_data="joined"),
         InlineKeyboardButton(f"Ok I'll join | {_thumbs_up}", url="https://t.me/chromusic_fa")]
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
    text = f"{_headphone}<b>Take your audio searching to the speed</b>{_headphone}\n\n" \
           f"Welcome to <b>Chromusic</b>, <b>{name}</b>. It's great to have you!{_party_popper} Here are a bunch of features that will " \
           f"get your searching up to <b>#speed</b>.{_zap}\n" \
           f"\n\n{_studio_microphone} <b>#Find</b> your audio (music, podcast, etc.) in <b>#milliseconds</b> {_smiling_face_with_sunglasses}" \
           f"\n\n{_green_circle} Any question? then press /help {_winking_face}"
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
    text = f""
    if len(args) == 3 or audio_track.chat.id == chromusic_users_files_id:
        include_source = False
        user_files_id = args[2]
        print("its_from_file_caption")
    try:

        _title = str(audio_track.audio.title).replace("@", "")
        _title_line = "<b>Title:</b> " + str(_title) + "\n"
        _performer = str(audio_track.audio.performer).replace("@", "")
        _performer_line = "<b>Performer:</b> " + str(_performer) + "\n"
        _filename = str(audio_track.audio.file_name).replace("@", "")
        _filename_line = "<b>File name:</b> " + str(_filename) + "\n"
        _source = f"<a href ='https://t.me/{audio_track.chat.username}/{message_id}'>{audio_track.chat.username}</a>"
        text = f"{_title_line if not _title == 'None' else ''}" \
               f"{_performer_line if not _performer == 'None' else ''}" \
               f"{_filename_line if (_title == 'None' and not _filename == 'None') else ''}" \
               f"{_round_pushpin}Source: {_source if include_source else 'Sent by Chromusic users'}\n" \
               f"\n{_search_emoji} | <a href ='https://t.me/chromusic_bot'><b>Chromusic bot:</b> Audio search engine</a>\n" \
               f"{_plant}"
        # f"{_pushpin} | <a href ='https://t.me/chromusic'>Chromusic channel</a>\n" \
        # f"{_pushpin} | <a href ='https://t.me/chromusic'>Persian Chromusic channel</a>\n" \
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
    :return:
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
        return f"If you are not in the bot's chat, please forward this message to the bot: \n" \
               f"<a href ='https://t.me/chromusic_bot'><b>Chromusic bot:</b> Audio search engine</a>\n" \
               f"{_round_pushpin} | Channel: @Chromusic_fa" \
               f"\n\n{_headphone} | dl_{audio_track['_id']}\n" \
               f"{_plant}"

    try:

        _title = audio_track["_source"]["title"]
        _title_line = "<b>Title:</b> " + str(_title) + "\n"
        _performer = audio_track["_source"]["performer"]
        _performer_line = "<b>Performer:</b> " + str(_performer) + "\n"
        _filename = audio_track["_source"]["file_name"]
        _filename_line = "<b>File name:</b> " + str(_filename) + "\n"
        _source = f"<a href ='https://t.me/{audio_track['_source']['chat_username']}/{message_id}'>{audio_track['_source']['chat_username']}</a>"
        text = f"{_title_line if not _title == None else ''}" \
               f"{_performer_line if not _performer == None else ''}" \
               f"{_filename_line if (_title == None and not _filename == None) else ''}" \
               f"{_round_pushpin}Source: {_source if include_source else 'Sent by Chromusic users'}\n" \
               f"\n{_search_emoji} | <a href ='https://t.me/chromusic_bot'><b>Chromusic bot:</b> Audio search engine</a>\n" \
               f"{_plant}"
        # f"{_pushpin} | <a href ='https://t.me/chromusic'>Chromusic channel</a>\n" \
        # f"{_pushpin} | <a href ='https://t.me/chromusic'>Persian Chromusic channel</a>\n" \
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
    text = f"{_headphone}To Enable this feature please join Chromusic channel first{_thumbs_up}\n{_pushpin}@Chromusic_fa"
    return text


def inline_join_channel_title_text(*args, **kwargs) -> str:
    """
    Shows a call-to-action text to users who have not Joined the channel yet (Title)
    :param args:
    :param kwargs:
    :return: Generated a text requiring users to start the bot first
    """
    text = f"{_green_circle} Please join Chromusic"
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
    text = f"{_round_pushpin}Please join @Chromusic_fa channel {_smiling_face_with_sunglasses}\nThank you for joining {plant}\n\n" \
           f"{_headphone}<a href='https://t.me/chromusic_bot'><b>Chromusic audio search engine:</b></a> @chromusic_bot{_studio_microphone}"
    return text



def example_message(*args, **kwargs) -> str:
    """
    Mini-tutorial for the first time the users starts the bot. This is a sample message on how to search
        audio files in the bot.
    :param args:
    :param kwargs:
    :return: Generated text
    """
    text = f"{_search_emoji}<b>1. Send the audio name or the performer:</b>\n" \
           f"{_checkmark_emoji}<b>Example:</b> Blank Space - Taylor Swift\n\n<b>2.Click on the links starting " \
           f"with \"/ dl_\"</b>\n" \
           f"<b>Example:</b> /dl_7DzuE_Rg"
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
    text = f"{_red_heart}{plant} <b>Please support us by introducing this service to your friends</b>\n\n" \
           f"{plant2} Since our servers contain monthly charges, please <b>share</b> this service with your friends" \
           f" to keep Chromusic running. Thanks {plant3}\n" \
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
    text = f"Thanks {message.from_user.first_name} for your contribution. {_heart}{_plant}"
    return text


def lang_register_alert(*args: list, **kwargs) -> str:
    """
    An alert validating the user's preferred language has been saved
    :param args:
    :param kwargs:
    :return: Generated alert
    """
    first_name = args[0]
    text = f"OK {first_name}, {_en} English language saved for you {_confetti_ball}{_party_popper}\n\n" \
           f"You can always change your language using\n" \
           f"{_green_circle} 1. \"/lang\" command\n" \
           f"{_green_circle} 2. Bottom keyboard"
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
    text = f"{_green_circle} I'm super excited you like our service, <b>{first_name}</b> {_smiling_face_with_heart}. If you want to access the " \
           f"full #speed, <b>please #join our channel: @chromusic_fa</b> {_headphone}\n\n " \
           f"However, you will still receive the file (in 1 minute). {_winking_face}"
    return text


def has_joined(*args: list, **kwargs) -> str:
    """
    Validates the user's joining the channel after being required to join.
    :param args: *[0] -> first name
    :param kwargs:
    :return: Generated validation message
    """
    first_name = args[0]
    text = f"{_star_struck}{_smiling_face_with_heart} Ok <b>{first_name}</b>, Now you have full access{_party_popper}{_confetti_ball}\n\n" \
           f"Love from @chromusic_fa {_red_heart}{_face_blowing_a_kiss}\n"
    return text


def not_joined(*args, **kwargs) -> str:
    """
    This will be shown when users claim to already have joined and they are lying
    :param args:
    :param kwargs:
    :return: Generated message for rejecting user's claim
    """
    text = f"{_face_with_raised_eyebrow} I checked, you haven't joined our channel.\n\n " \
           f"{_green_heart} Join @chromusic_fa to access all features for #FREE {_green_heart}"
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
    print("search res from res list handler", search_res)
    if int(search_res["hits"]["total"]["value"]) > 0:
        text = f"<b>{_search_emoji} Search results for: {textwrap.shorten(query, width=100, placeholder='...')}</b>\n"
        text += f"{_checkmark_emoji} Better results are at the bottom of the list\n\n\n"
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

            # name = f"{_file_name if ((_performer == 'None' or _performer == '.mp3') and (_title == 'None' or _title == '.mp3')) else (_performer if (_title == 'None' or _title == '.mp3') else _title)}".replace(
            #     ".mp3", "")
            # if not _title == None:
            #     name += f" - {_title}"

            text += f"<b>{str(index + 1)}. {dir_str} {_headphone_emoji} {fruit if index == 0 else ''}</b>" \
                    f"<b>{textwrap.shorten(name, width=35, placeholder='...')}</b>\n" \
                    f"{dir_str}     {_floppy_emoji} | {round(int(hit['_source']['file_size']) / 1000_000, 1)} MB  " \
                    f"{dir_str}{_clock_emoji} | {str(d.hour) + ':' if d.hour > 0 else ''}{d.minute}:{d.second}\n{dir_str}" \
                    f"{dir_str}      Download: /dl_{hit['_id']}\n" \
                    f"      {34 * '-' if not index == 0 else ''}{dir_str} \n\n"
    else:
        text = f"{_traffic_light}  No results were found!" \
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
        text = f"{_check_mark_button} <b>Title updated successfully</b>"
    elif func == "description_update":
        text = f"{_check_mark_button} <b>Description updated successfully</b>"
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
    text = f""
    if func == "addnewpl":
        print("data from english:", data)
        text = f"<b>1. A new playlist created successfully | {_check_mark_button}</b>\n" \
               f"       Default name: {data['title']}\n" \
               f"       Default description: {data['description']}\n" \
               f"       You can change these information in edit section:\n" \
               f"            my playlists -> edit -> ...\n" \
               f"<b>2. Audio file added to the new playlist | {_check_mark_button}</b>\n{34 * '-'}\n\n" \
               f"You can access your playlists and your download history using <b>Home</b> button"
    elif func == "addtoexistpl":
        playlist = args[2]
        text = f"<b>1. Audio file added to the playlist | {_check_mark_button}</b>\n" \
               f"       Audio file Name: {data['title']}\n" \
               f"       Playlist name: {playlist['_source']['title']}\n" \
               f"       You can change these information in edit section:\n" \
               f"            my playlists -> edit -> ...\n{34 * '-'}\n\n" \
               f"You can access your playlists and your download history using <b>Home</b> button | {_green_circle}"
    return text

def delete_audio_guide_text(*args, **kwargs) -> str:
    """
    Guides users how to delete an audio-file from the current playlist.
    :param args:
    :param kwargs:
    :return: Deletion mini-guide message
    """
    text = f"{_green_circle} By clicking on each button you can remove that file from the current playlist | {_cross_mark}"
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
        [InlineKeyboardButton(f"My Downloads | {_mobile_phone_with_arrow}",
                              switch_inline_query_current_chat=f"#history"),
         InlineKeyboardButton(f"My Playlists | {_headphone}", switch_inline_query_current_chat=f"#myplaylists")],
        [InlineKeyboardButton(f"Language | {_globe_showing_Americas}", callback_data="lang")],
        [InlineKeyboardButton(f"Advertisement | {_chart_increasing}{_bar_chart}", url="https://t.me/chromusic_ads"),
         InlineKeyboardButton(f"How to | {_exclamation_question_mark}",
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
        [InlineKeyboardButton(f"My Downloads | {_mobile_phone_with_arrow}",
                              switch_inline_query_current_chat=f"#history"),
         InlineKeyboardButton(f"My Playlists | {_headphone}", switch_inline_query_current_chat=f"#myplaylists")],
        [InlineKeyboardButton(f"Back | {_BACK_arrow}", callback_data="home")],
        [InlineKeyboardButton(f"Advertisement | {_chart_increasing}{_bar_chart}", url="https://t.me/chromusic_ads")
            , InlineKeyboardButton(f"Help | {_exclamation_question_mark}",
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
    text = f"<b>Help menu | {_exclamation_question_mark}</b>\n{34 * '-'}\n\n" \
           f"Our channels:\n" \
           f"Channel: <b>@chromusic_fa</b> | {_pushpin}\n{34 * '-'}\n\n" \
           f"Our Instagram accounts:\n" \
           f"<a href='https://www.instagram/chromusic.official'>Chromusic</a> | {_round_pushpin}\n" \
           f"<a href='https://www.instagram/chromusic_fa'>Persian Chromusic</a> | {_round_pushpin}\n\n" \
           f"&lrm;{_plant}{_heart}"
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
    text = f"<b>Main menu | {_house}</b>\n{34 * '-'}\n\n" \
           f"Our channels:\n" \
           f"{_pushpin} | Channel: <b>@chromusic_fa</b> \n{34 * '-'}\n\n" \
           f"Our Instagram accounts:\n" \
           f"<a href='https://www.instagram.com/chromusic_official/'><b>Chromusic</b></a> | {_round_pushpin}\n" \
           f"<a href='https://www.instagram.com/chromusic_fa'><b>Persian Chromusic</b></a> | {_round_pushpin}\n\n" \
           f"&rlm;{_plant}{_heart}"
    return text

def file_deleted_from_playlist(*args, **kwargs) -> str:
    """
    Audio-file deletion validation message
    :param args:
    :param kwargs:
    :return: Generated validation message
    """
    text = f"{_check_mark_button} Audio file deleted from playlist"
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
        title="*. <b>Soran Ghadri</b>",
        description="To see author's <b>github</b> and social media, click here",
        thumb_url="https://telegra.ph/file/6e6831bdd89011688bddb.jpg",
        input_message_content=InputTextMessageContent(f"Everything you need to know before promoting your business: \n"
                                                      f"<a href='https://github.com/soran-ghadri/'>"
                                                      f"<b>Chromusic Advertising</b></a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="1. How to advertise?",
        description="If you need advertising, click here",
        thumb_url="https://telegra.ph/file/6e6831bdd89011688bddb.jpg",
        input_message_content=InputTextMessageContent(f"Everything you need to know before promoting your business: \n"
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"<b>Chromusic Advertising</b></a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="2. How to search for and download an audio track",
        description="You can easily send your audio file and get indexed by Chromusic bot",
        thumb_url="https://telegra.ph/file/36fc0478a793bd6db8c4e.jpg",
        input_message_content=InputTextMessageContent(f"Read searching tutorial on this page: \n"
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"<b>Optimal search</b></a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="3. How to register my own audio track?",
        description="You can simply send your audio file and have it indexed by Chromusic",
        thumb_url="https://telegra.ph/file/36fc0478a793bd6db8c4e.jpg",
        input_message_content=InputTextMessageContent(f"Here is a complete guide on "
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"<b>how to add my audio track</b></a> (music, podcast, etc.)"
                                                      f" to be shown in the results", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="4. How to add my channel to Chromusic",
        description="if you feel your channel has not been indexed",
        thumb_url="https://pbs.twimg.com/profile_images/1306684220232945665/5i_q4pCx_400x400.jpg",
        input_message_content=InputTextMessageContent(f"Here is a complete guide on "
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>"
                                                      f"<b>how to add my channel</b></a>  to be shown by Chromusic",
                                                      parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="5. Contact us",
        description="If you need to contact Chromusic admins then hit this item",
        thumb_url="https://pbs.twimg.com/profile_images/1306684220232945665/5i_q4pCx_400x400.jpg",
        input_message_content=InputTextMessageContent(f"you can be in touch with us through @[Admin username]\n"
                                                      f"For further information please read "
                                                      f"<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>Contact Chromusic</a>", parse_mode="HTML")))
    results.append(InlineQueryResultArticle(
        title="6. About us",
        description="If you like to find out more about us, click on this link",
        thumb_url="https://pbs.twimg.com/profile_images/1306684220232945665/5i_q4pCx_400x400.jpg",
        input_message_content=InputTextMessageContent(
            f"<b>Read more about us on the following page:\n<a href='https://github.com/soran-ghadri/Chromusic_search_engine'>About Chromusic</a></b>",
            parse_mode="HTML")
    ))
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
            temp = f"{count} items registered"
        else:
            temp = ''
    else:
        temp = ''

    if registered:
        _plant = random.choice(plants_list)
        _heart = random.choice(heart_list)
        text = f"Special thanks for your contribution <b>{first_name}</b>. {_heart}{_plant}.\n\n" \
               f"{temp}"
    else:
        _plant = random.choice(plants_list)
        _heart = random.choice(heart_list)
        text = f"Special thanks for your contribution <b>{first_name}</b>. {_heart}{_plant}."
        # text = f"Thank you <b>{first_name};</b> However, this file/channel has already been registered. {_heart}{_plant}\n\n"
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
    text = f""
    if not_active_since > 14:
        text = f"Hey <b>{first_name}</b>, long time no see! \nQuestions about our services? " \
               f"I'm happy to <b>#help</b>."
    else:
        text = f"Glad to see you again <b>{first_name}</b>.\n press <b>#help</b> button from the following keyboard if " \
               f"you think you need it"
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
    text = f"Checking off items started ... {_clock_emoji}.\n" \
           f"I will let you know after the process is complete. {_plant}{_heart}"
    return text