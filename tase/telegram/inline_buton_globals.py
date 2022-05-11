from tase.telegram.inline_buttons import AdvertisementInlineButton, BackInlineButton, DownloadHistoryInlineButton, \
    HelpCatalogInlineButton, MyPlaylistsInlineButton

objs = [
    AdvertisementInlineButton(),
    BackInlineButton(),
    DownloadHistoryInlineButton(),
    HelpCatalogInlineButton(),
    MyPlaylistsInlineButton(),
]

buttons = dict()

for obj in objs:
    buttons[obj.name] = obj

__all__ = [
    'buttons',
]
