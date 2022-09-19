from .tase_error import TASEError


class InvalidAudioForInlineMode(TASEError):
    """`Audio` vertex does not have valid audio type for inline mode"""

    MESSAGE = """`Audio` vertex with key `{}` does not have valid audio type for inline mode"""
