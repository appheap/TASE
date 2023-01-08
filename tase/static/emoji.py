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

"""
This module provides the necessary emojis used by the agent (bot)
"""
import emoji
from pydantic import BaseModel


class Emoji(BaseModel):
    # -------------Country Flags--------------------
    _usa_flag = emoji.emojize(":United_States:", language="alias")
    _tajikistan_flag = emoji.emojize(":Tajikistan:", language="alias")
    _lithuania_flag = emoji.emojize(":Lithuania:", language="alias")
    _italy_flag = emoji.emojize(":Italy:", language="alias")
    _spain_flag = emoji.emojize(":Spain:", language="alias")
    _iran_flag = emoji.emojize(":Iran:", language="alias")
    _saudi_arabia_flag = emoji.emojize(":Saudi_Arabia:", language="alias")
    _india_flag = emoji.emojize(":India:", language="alias")
    _russia_flag = emoji.emojize(":Russia:", language="alias")
    _germany_flag = emoji.emojize(":Germany:", language="alias")
    _netherlands_flag = emoji.emojize(":Netherlands:", language="alias")
    _portugal_flag = emoji.emojize(":Portugal:", language="alias")
    _zap = emoji.emojize(":zap:", language="alias")
    _globe_showing_Americas = emoji.emojize(":globe_showing_Americas:", language="alias")

    # -------------Surprise--------------------------
    _party_popper = emoji.emojize(":party_popper:", language="alias")
    _confetti_ball = emoji.emojize(":confetti_ball:", language="alias")

    # -------------music--------------------------
    _headphone = emoji.emojize(":headphone:", language="alias")
    _bell = emoji.emojize(":bell:", language="alias")
    _no_bell = emoji.emojize(":no_bell:", language="alias")
    _link = emoji.emojize(":link:", language="alias")
    _cd = emoji.emojize(":optical_disk:", language="alias")

    _studio_microphone = emoji.emojize(":studio_microphone:", language="alias")

    # -------------Utility and place--------------------------
    _round_pushpin = emoji.emojize(":round_pushpin:", language="alias")
    _pushpin = emoji.emojize(":pushpin:", language="alias")
    _search_emoji = emoji.emojize(":mag_right:", language="alias")
    _house_with_garden = emoji.emojize(":house_with_garden:", language="alias")
    _house = emoji.emojize(":house:", language="alias")
    _BACK_arrow = emoji.emojize(":BACK_arrow:", language="alias")
    _star_struck = emoji.emojize(":star-struck:", language="alias")
    _artist_palette = emoji.emojize(":artist_palette:", language="alias")
    _green_circle = emoji.emojize(":green_circle:", language="alias")
    _backhand_index_pointing_right = emoji.emojize(":left_arrow_curving_right:", language="alias")
    _exclamation_question_mark = emoji.emojize(":exclamation_question_mark:", language="alias")
    _mobile_phone_with_arrow = emoji.emojize(":mobile_phone_with_arrow:", language="alias")
    _chart_increasing = emoji.emojize(":chart_increasing:", language="alias")
    _bar_chart = emoji.emojize(":bar_chart:", language="alias")
    _check_mark_button = emoji.emojize(":white_check_mark:", language="alias")
    _gear = emoji.emojize(":gear:", language="alias")
    _wrench = emoji.emojize(":wrench:", language="alias")
    _cross_mark = emoji.emojize(":cross_mark:", language="alias")
    _musical_note = emoji.emojize(":musical_note:", language="alias")
    _thumbs_up = emoji.emojize(":thumbs_up:", language="alias")
    _thumbs_down = emoji.emojize(":thumbs_down:", language="alias")
    _plus = emoji.emojize(":heavy_plus_sign:", language="alias")
    _minus = emoji.emojize(":heavy_minus_sign:", language="alias")
    _fountain_pen = emoji.emojize(":fountain_pen:", language="alias")
    _traffic_light = emoji.emojize(":traffic_light:", language="alias")
    _checkmark_emoji = emoji.emojize(":white_check_mark:", language="alias")
    _floppy_emoji = emoji.emojize(":floppy_disk:", language="alias")
    _inbox_tray = emoji.emojize(":inbox_tray:", language="alias")
    _outbox_tray = emoji.emojize(":outbox_tray:", language="alias")
    _url = emoji.emojize(":link:", language="alias")
    _clock_emoji = emoji.emojize(":hourglass_flowing_sand:", language="alias")
    _information = emoji.emojize(":information:", language="alias")

    # -------------Books--------------------------
    _books = emoji.emojize(":books:", language="alias")
    _book_emoji = emoji.emojize(":green_book:", language="alias")

    # -------------Hearts--------------------------
    _red_heart = emoji.emojize(":red_heart:", language="alias")
    _white_heart = emoji.emojize(":white_heart:", language="alias")
    _orange_heart = emoji.emojize(":orange_heart:", language="alias")
    _yellow_heart = emoji.emojize(":yellow_heart:", language="alias")
    _green_heart = emoji.emojize(":green_heart:", language="alias")
    _blue_heart = emoji.emojize(":blue_heart:", language="alias")

    # -----------------------------------------------------------
    _dark_thumbs_up = emoji.emojize(":thumbs_up_dark_skin_tone:")
    _light_thumbs_up = emoji.emojize(":thumbs_up_light_skin_tone:")
    _dark_thumbs_down = emoji.emojize(":thumbs_down_dark_skin_tone:")
    _light_thumbs_down = emoji.emojize(":thumbs_down_light_skin_tone:")

    # -------------Plants--------------------------
    _purple_heart = emoji.emojize(":purple_heart:", language="alias")
    _seedling = emoji.emojize(":seedling:", language="alias")
    _evergreen_tree = emoji.emojize(":evergreen_tree:", language="alias")
    _deciduous_tree = emoji.emojize(":deciduous_tree:", language="alias")
    _palm_tree = emoji.emojize(":palm_tree:", language="alias")
    _sheaf_of_rice = emoji.emojize(":sheaf_of_rice:", language="alias")
    _herb = emoji.emojize(":herb:", language="alias")
    _shamrock = emoji.emojize(":shamrock:", language="alias")
    _four_leaf_clover = emoji.emojize(":four_leaf_clover:", language="alias")
    _fallen_leaf = emoji.emojize(":fallen_leaf:", language="alias")
    _leaf_fluttering_in_wind = emoji.emojize(":leaf_fluttering_in_wind:", language="alias")

    # -------------Fruits--------------------------
    _apple = emoji.emojize(":apple:", language="alias")
    _candy = emoji.emojize(":candy:", language="alias")
    _watermelon = emoji.emojize(":watermelon:", language="alias")
    _peach = emoji.emojize(":peach:", language="alias")
    _strawberry = emoji.emojize(":strawberry:", language="alias")
    _tea = emoji.emojize(":tea:", language="alias")
    _cherry_blossom = emoji.emojize(":cherry_blossom:", language="alias")
    _maple_leaf = emoji.emojize(":maple_leaf:", language="alias")
    _pineapple = emoji.emojize(":pineapple:", language="alias")
    _tangerine = emoji.emojize(":tangerine:", language="alias")
    _grapes = emoji.emojize(":grapes:", language="alias")
    _carrot = emoji.emojize(":carrot:", language="alias")
    _ear_of_corn = emoji.emojize(":ear_of_corn:", language="alias")
    _mushroom = emoji.emojize(":mushroom:", language="alias")
    _lemon = emoji.emojize(":lemon:", language="alias")
    _cherries = emoji.emojize(":cherries:", language="alias")

    # -------------Faces--------------------------
    _smiling_face_with_heart = emoji.emojize(":smiling_face_with_heart-eyes:", language="alias")
    _face_blowing_a_kiss = emoji.emojize(":face_blowing_a_kiss:", language="alias")
    _face_with_raised_eyebrow = emoji.emojize(":face_with_raised_eyebrow:", language="alias")
    _smiling_face_with_sunglasses = emoji.emojize(":smiling_face_with_sunglasses:", language="alias")
    _winking_face = emoji.emojize(":winking_face:", language="alias")

    # ------------Others-----------------------------------
    high_voltage = emoji.emojize(":high_voltage:", language="alias")

    # a list to randomly choose from
    fruit_list = [
        _grapes,
        _tangerine,
        _pineapple,
        _lemon,
        _cherries,
        _apple,
        _candy,
        _watermelon,
        _peach,
        _strawberry,
        _tea,
        _cherry_blossom,
        _maple_leaf,
        _carrot,
        _ear_of_corn,
        _mushroom,
    ]

    heart_list = [
        _red_heart,
        _orange_heart,
        _yellow_heart,
        _green_heart,
        _blue_heart,
        _purple_heart,
    ]

    plants_list = [
        _seedling,
        _evergreen_tree,
        _deciduous_tree,
        _palm_tree,
        _sheaf_of_rice,
        _herb,
        _shamrock,
        _four_leaf_clover,
        _maple_leaf,
        _fallen_leaf,
        _leaf_fluttering_in_wind,
    ]
