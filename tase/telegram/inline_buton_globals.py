from tase.telegram.inline_buttons import AdvertisementInlineButton, BackInlineButton, DownloadHistoryInlineButton, \
    HelpCatalogInlineButton, MyPlaylistsInlineButton, HomeInlineButton, AddToPlaylistInlineButton, \
    GetPlaylistAudioInlineButton, DeletePlaylistInlineButton, EditPlaylistInlineButton, BackToPlaylistsInlineButton, \
    ChooseLanguageInlineButton, ShowLanguageMenuInlineButton

objs = [
    AdvertisementInlineButton(),
    BackInlineButton(),
    DownloadHistoryInlineButton(),
    HelpCatalogInlineButton(),
    MyPlaylistsInlineButton(),
    HomeInlineButton(),
    AddToPlaylistInlineButton(),
    GetPlaylistAudioInlineButton(),
    DeletePlaylistInlineButton(),
    EditPlaylistInlineButton(),
    BackToPlaylistsInlineButton(),
    ChooseLanguageInlineButton(),
    ShowLanguageMenuInlineButton(),
]

buttons = dict()

for obj in objs:
    buttons[obj.name] = obj

__all__ = [
    'buttons',
]
