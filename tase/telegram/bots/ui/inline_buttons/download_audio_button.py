from tase.common.utils import _trans, emoji
from .base import InlineButton, InlineButtonType, ButtonActionType


class DownloadAudioInlineButton(InlineButton):
    type = InlineButtonType.DOWNLOAD_AUDIO
    action = ButtonActionType.OPEN_URL

    s_download_audio = _trans("Download Audio")
    text = f"{s_download_audio} | {emoji._url}"
