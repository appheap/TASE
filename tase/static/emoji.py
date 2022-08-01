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
    _usa_flag = emoji.emojize(":United_States:")
    _tajikistan_flag = emoji.emojize(":Tajikistan:")
    _lithuania_flag = emoji.emojize(":Lithuania:")
    _italy_flag = emoji.emojize(":Italy:")
    _spain_flag = emoji.emojize(":Spain:")
    _iran_flag = emoji.emojize(":Iran:")
    _saudi_arabia_flag = emoji.emojize(":Saudi_Arabia:")
    _india_flag = emoji.emojize(":India:")
    _russia_flag = emoji.emojize(":Russia:")
    _germany_flag = emoji.emojize(":Germany:")
    _netherlands_flag = emoji.emojize(":Netherlands:")
    _portugal_flag = emoji.emojize(":Portugal:")
    _zap = emoji.emojize(":zap:")
    _globe_showing_Americas = emoji.emojize(":globe_showing_Americas:")

    # -------------Surprise--------------------------
    _party_popper = emoji.emojize(":party_popper:")
    _confetti_ball = emoji.emojize(":confetti_ball:")

    # -------------music--------------------------
    _headphone = emoji.emojize(":headphone:")

    _studio_microphone = emoji.emojize(":studio_microphone:")

    # -------------Utility and place--------------------------
    _round_pushpin = emoji.emojize(":round_pushpin:")
    _pushpin = emoji.emojize(":pushpin:")
    _search_emoji = emoji.emojize(":mag_right:")
    _house_with_garden = emoji.emojize(":house_with_garden:")
    _house = emoji.emojize(":house:")
    _BACK_arrow = emoji.emojize(":BACK_arrow:")
    _star_struck = emoji.emojize(":star-struck:")
    _artist_palette = emoji.emojize(":artist_palette:")
    _green_circle = emoji.emojize(":green_circle:")
    _backhand_index_pointing_right = emoji.emojize(":left_arrow_curving_right:")
    _exclamation_question_mark = emoji.emojize(":exclamation_question_mark:")
    _mobile_phone_with_arrow = emoji.emojize(":mobile_phone_with_arrow:")
    _chart_increasing = emoji.emojize(":chart_increasing:")
    _bar_chart = emoji.emojize(":bar_chart:")
    _check_mark_button = emoji.emojize(":white_check_mark:")
    _gear = emoji.emojize(":gear:")
    _wrench = emoji.emojize(":wrench:")
    _cross_mark = emoji.emojize(":cross_mark:")
    _musical_note = emoji.emojize(":musical_note:")
    _thumbs_up = emoji.emojize(":thumbs_up:")
    _thumbs_down = emoji.emojize(":thumbs_down:")
    _plus = emoji.emojize(":heavy_plus_sign:")
    _minus = emoji.emojize(":heavy_minus_sign:")
    _fountain_pen = emoji.emojize(":fountain_pen:")
    _traffic_light = emoji.emojize(":traffic_light:")
    _checkmark_emoji = emoji.emojize(":white_check_mark:")
    _floppy_emoji = emoji.emojize(":floppy_disk:")
    _clock_emoji = emoji.emojize(":hourglass_flowing_sand:")

    # -------------Books--------------------------
    _books = emoji.emojize(":books:")
    _book_emoji = emoji.emojize(":green_book:")

    # -------------Hearts--------------------------
    _red_heart = emoji.emojize(":red_heart:")
    _orange_heart = emoji.emojize(":orange_heart:")
    _yellow_heart = emoji.emojize(":yellow_heart:")
    _green_heart = emoji.emojize(":green_heart:")
    _blue_heart = emoji.emojize(":blue_heart:")

    # -------------Plants--------------------------
    _purple_heart = emoji.emojize(":purple_heart:")
    _seedling = emoji.emojize(":seedling:")
    _evergreen_tree = emoji.emojize(":evergreen_tree:")
    _deciduous_tree = emoji.emojize(":deciduous_tree:")
    _palm_tree = emoji.emojize(":palm_tree:")
    _sheaf_of_rice = emoji.emojize(":sheaf_of_rice:")
    _herb = emoji.emojize(":herb:")
    _shamrock = emoji.emojize(":shamrock:")
    _four_leaf_clover = emoji.emojize(":four_leaf_clover:")
    _fallen_leaf = emoji.emojize(":fallen_leaf:")
    _leaf_fluttering_in_wind = emoji.emojize(":leaf_fluttering_in_wind:")

    # -------------Fruits--------------------------
    _apple = emoji.emojize(":apple:")
    _candy = emoji.emojize(":candy:")
    _watermelon = emoji.emojize(":watermelon:")
    _peach = emoji.emojize(":peach:")
    _strawberry = emoji.emojize(":strawberry:")
    _tea = emoji.emojize(":tea:")
    _cherry_blossom = emoji.emojize(":cherry_blossom:")
    _maple_leaf = emoji.emojize(":maple_leaf:")
    _pineapple = emoji.emojize(":pineapple:")
    _tangerine = emoji.emojize(":tangerine:")
    _grapes = emoji.emojize(":grapes:")
    _carrot = emoji.emojize(":carrot:")
    _ear_of_corn = emoji.emojize(":ear_of_corn:")
    _mushroom = emoji.emojize(":mushroom:")
    _lemon = emoji.emojize(":lemon:")
    _cherries = emoji.emojize(":cherries:")

    # -------------Faces--------------------------
    _smiling_face_with_heart = emoji.emojize(":smiling_face_with_heart-eyes:")
    _face_blowing_a_kiss = emoji.emojize(":face_blowing_a_kiss:")
    _face_with_raised_eyebrow = emoji.emojize(":face_with_raised_eyebrow:")
    _smiling_face_with_sunglasses = emoji.emojize(":smiling_face_with_sunglasses:")
    _winking_face = emoji.emojize(":winking_face:")

    # ------------Others-----------------------------------
    high_voltage = emoji.emojize(":high_voltage:")

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
