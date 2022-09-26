from tase.common.utils import _trans, emoji
from .base import InlineButton, InlineButtonType


class DownloadAudioInlineButton(InlineButton):
    name = "download_audio"
    type = InlineButtonType.DOWNLOAD_AUDIO

    s_download_audio = _trans("Download Audio")
    text = f"{s_download_audio} | {emoji._url}"
    is_inline = False
    is_url = True
