from .tase_error import TASEError


class UpdateRetryCountFailed(TASEError):
    """Update of retry count attribute of `BotTask` class failed"""

    MESSAGE = "Update of retry count attribute of `BotTask` class failed"
