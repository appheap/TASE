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


def playlist_keyboard(*args: list, **kwargs: object) -> list:
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


def playlists_buttons(*args, **kwargs) -> list:
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


def single_playlist_markup_list(*args: str, **kwargs) -> list:
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
    :return:
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


def delete_audio_murkup_keyboard(*args: list, **kwargs) -> list(object):
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


def delete_playlist_validation_keyboard(*args: list(object), **kwargs) -> list(object):
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
