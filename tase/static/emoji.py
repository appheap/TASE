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
    _usa_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':United_States:']
    _tajikistan_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':Tajikistan:']
    _lithuania_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':Lithuania:']
    _iran_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':Iran:']
    _saudi_arabia_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':Saudi_Arabia:']
    _india_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':India:']
    _russia_flag = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':Russia:']
    _zap = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':zap:']
    _globe_showing_Americas = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':globe_showing_Americas:']

    # -------------Surprize--------------------------
    _party_popper = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':party_popper:']
    _confetti_ball = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':confetti_ball:']

    # -------------music--------------------------
    _headphone = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':headphone:']

    _studio_microphone = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':studio_microphone:']

    # -------------Utility and place--------------------------
    _round_pushpin = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':round_pushpin:']
    _pushpin = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':pushpin:']
    _search_emoji = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':mag_right:']
    _house_with_garden = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':house_with_garden:']
    _house = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':house:']
    _BACK_arrow = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':BACK_arrow:']
    _star_struck = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':star-struck:']
    _artist_palette = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':artist_palette:']
    _green_circle = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':green_circle:']
    _backhand_index_pointing_right = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':left_arrow_curving_right:']
    _exclamation_question_mark = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':exclamation_question_mark:']
    _mobile_phone_with_arrow = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':mobile_phone_with_arrow:']
    _chart_increasing = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':chart_increasing:']
    _bar_chart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':bar_chart:']
    _check_mark_button = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':white_check_mark:']
    _gear = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':gear:']
    _wrench = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':wrench:']
    _cross_mark = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':cross_mark:']
    _musical_note = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':musical_note:']
    _thumbs_up = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':thumbs_up:']
    _thumbs_down = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':thumbs_down:']
    _plus = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':heavy_plus_sign:']
    _fountain_pen = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':fountain_pen:']
    _traffic_light = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':traffic_light:']
    _checkmark_emoji = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':white_check_mark:']
    _floppy_emoji = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':floppy_disk:']
    _clock_emoji = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':hourglass_flowing_sand:']

    # -------------Books--------------------------
    _books = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':books:']
    _book_emoji = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':green_book:']

    # -------------Hearts--------------------------
    _red_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':red_heart:']
    _orange_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':orange_heart:']
    _yellow_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':yellow_heart:']
    _green_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':green_heart:']
    _blue_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':blue_heart:']

    # -------------Plants--------------------------
    _purple_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':purple_heart:']
    _seedling = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':seedling:']
    _evergreen_tree = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':evergreen_tree:']
    _deciduous_tree = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':deciduous_tree:']
    _palm_tree = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':palm_tree:']
    _sheaf_of_rice = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':sheaf_of_rice:']
    _herb = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':herb:']
    _shamrock = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':shamrock:']
    _four_leaf_clover = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':four_leaf_clover:']
    _fallen_leaf = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':fallen_leaf:']
    _leaf_fluttering_in_wind = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':leaf_fluttering_in_wind:']

    # -------------Fruits--------------------------
    _apple = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':apple:']
    _candy = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':candy:']
    _watermelon = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':watermelon:']
    _peach = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':peach:']
    _strawberry = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':strawberry:']
    _tea = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':tea:']
    _cherry_blossom = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':cherry_blossom:']
    _maple_leaf = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':maple_leaf:']
    _pineapple = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':pineapple:']
    _tangerine = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':tangerine:']
    _grapes = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':grapes:']
    _carrot = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':carrot:']
    _ear_of_corn = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':ear_of_corn:']
    _mushroom = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':mushroom:']
    _lemon = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':lemon:']
    _cherries = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':cherries:']

    # -------------Faces--------------------------
    _smiling_face_with_heart = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':smiling_face_with_heart-eyes:']
    _face_blowing_a_kiss = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':face_blowing_a_kiss:']
    _face_with_raised_eyebrow = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':face_with_raised_eyebrow:']
    _smiling_face_with_sunglasses = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':smiling_face_with_sunglasses:']
    _winking_face = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':winking_face:']

    # ------------Others-----------------------------------
    high_voltage = emoji.EMOJI_ALIAS_UNICODE_ENGLISH[':high_voltage:']

    # a list to randomly choose from
    fruit_list = [_grapes, _tangerine, _pineapple, _lemon, _cherries, _apple, _candy, _watermelon,
                  _peach, _strawberry, _tea, _cherry_blossom, _maple_leaf, _carrot, _ear_of_corn, _mushroom]

    heart_list = [_red_heart, _orange_heart, _yellow_heart, _green_heart, _blue_heart, _purple_heart]

    plants_list = [_seedling, _evergreen_tree, _deciduous_tree, _palm_tree, _sheaf_of_rice, _herb, _shamrock,
                   _four_leaf_clover, _maple_leaf, _fallen_leaf, _leaf_fluttering_in_wind]
