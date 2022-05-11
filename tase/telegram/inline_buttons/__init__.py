from .advertisement_button import AdvertisementInlineButton
from .back_button import BackInlineButton
from .button import InlineButton
from .download_history_button import DownloadHistoryInlineButton
from .help_catalog import HelpCatalogInlineButton
from .my_playlists_button import MyPlaylistsInlineButton

buttons = dict()

objs = [
    AdvertisementInlineButton(),
    BackInlineButton(),
    DownloadHistoryInlineButton(),
    HelpCatalogInlineButton(),
    MyPlaylistsInlineButton(),
]

for obj in objs:
    buttons[obj.name] = obj

__all__ = [
    'buttons',
    'InlineButton',
    'DownloadHistoryInlineButton',
    'MyPlaylistsInlineButton',
]
