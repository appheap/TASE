from tase.telegram.templates import QueryResultsTemplate, NoResultsWereFoundTemplate, AudioCaptionTemplate, \
    ChooseLanguageTemplate, WelcomeTemplate, HelpTemplate, HomeTemplate, PlaylistTemplate

query_results_template: QueryResultsTemplate = QueryResultsTemplate()
no_results_were_found_template: NoResultsWereFoundTemplate = NoResultsWereFoundTemplate()
audio_caption_template: AudioCaptionTemplate = AudioCaptionTemplate()
choose_language_template: ChooseLanguageTemplate = ChooseLanguageTemplate()
welcome_template: WelcomeTemplate = WelcomeTemplate()
help_template: HelpTemplate = HelpTemplate()
home_template: HomeTemplate = HomeTemplate()
playlist_template: PlaylistTemplate = PlaylistTemplate()

__all__ = [
    'query_results_template',
    'no_results_were_found_template',
    'audio_caption_template',
    'choose_language_template',
    'welcome_template',
    'help_template',
    'home_template',
    'playlist_template',

]
