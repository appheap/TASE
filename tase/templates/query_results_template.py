from jinja2 import Template

from .base import BaseTemplate, BaseTemplateData
from tase.utils import _trans


class QueryResultsTemplate(BaseTemplate):
    template = Template(
        "<b>{{emoji._search_emoji}} {{s_search_results_for}} {{query}}</b>"
        "{{c_new_line}}"
        "{{emoji._checkmark_emoji}} {{s_better_results}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{% for item in items %}"
        "{{c_dir}}<b>{{item.index}}. {{c_dir}}{{emoji._headphone_emoji}} </b><b>{{item.name}}</b>"
        "{{c_new_line}}"
        "{{c_dir}}      {{emoji._floppy_emoji}} | {{item.file_size}} {{s_MB}} {{c_dir}}{{emoji._clock_emoji}} | {{item.time}}{{c_dir}}"
        "{{c_new_line}}"
        "{{c_dir}}       {{s_download}} /dl_{{item.url}}"
        "{{c_new_line}}"
        "{{c_dir}}{{item.sep}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{% endfor %}"
    )


class QueryResultsData(BaseTemplateData):
    query: str
    items: list[dict]

    s_search_results_for: str = _trans('Search results for:')
    s_better_results: str = _trans("Better results are at the bottom of the list")
    s_download: str = _trans("Download:")
    s_MB: str = _trans("MB")
