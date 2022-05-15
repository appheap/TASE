from tase.telegram.inline_buttons import AdvertisementInlineButton, BackInlineButton, DownloadHistoryInlineButton, \
    HelpCatalogInlineButton, MyPlaylistsInlineButton, HomeInlineButton, AddToPlaylistInlineButton

objs = [
    AdvertisementInlineButton(),
    BackInlineButton(),
    DownloadHistoryInlineButton(),
    HelpCatalogInlineButton(),
    MyPlaylistsInlineButton(),
    HomeInlineButton(),
    AddToPlaylistInlineButton(),
]

buttons = dict()

for obj in objs:
    buttons[obj.name] = obj

__all__ = [
    'buttons',
]
