from .tase_error import TASEError


class NotEnoughRamError(TASEError):
    """There is not enough RAM available"""

    MESSAGE = """There is not enough RAM available. Threshold: `{}` percent"""
