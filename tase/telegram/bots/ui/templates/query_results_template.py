import textwrap
from datetime import timedelta, datetime
from typing import Dict, Deque

from jinja2 import Template

from tase.common.preprocessing import clean_audio_item_text
from tase.common.utils import _trans
from tase.db.elasticsearchdb import models as elasticsearch_models
from .base_template import BaseTemplate, BaseTemplateData


class QueryResultsTemplate(BaseTemplate):
    name = "query_results_template"

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
        "{{c_dir}}      {{emoji._floppy_emoji}} {{item.file_size}} {{s_MB}} | {{c_dir}}{{emoji._clock_emoji}} {{item.time}}{{c_dir}} | {{emoji._cd}} {{item.quality_string}}"
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

    s_search_results_for: str = _trans("Search results for:")
    s_better_results: str = _trans("Better results are at the bottom of the list")
    s_download: str = _trans("Download:")
    s_MB: str = _trans("MB")

    @classmethod
    def process_item(
        cls,
        index: int,
        es_audio_doc: elasticsearch_models.Audio,
        hit_download_url: str,
    ) -> Dict[str, str]:
        _performer = clean_audio_item_text(es_audio_doc.raw_performer)
        _title = clean_audio_item_text(es_audio_doc.raw_title)
        _file_name = clean_audio_item_text(
            es_audio_doc.raw_file_name,
            is_file_name=True,
            remove_file_extension_=True,
        )
        if _title is None:
            _title = ""
        if _performer is None:
            _performer = ""
        if _file_name is None:
            _file_name = ""

        if len(_title) >= 2 and len(_performer) >= 2:
            name = f"{_performer} - {_title}"
        elif len(_performer) >= 2:
            name = f"{_performer} - {_file_name}"
        elif len(_title) >= 2:
            name = _title
        else:
            name = _file_name

        duration = timedelta(seconds=es_audio_doc.duration or 0)
        d = datetime(1, 1, 1) + duration
        if d.hour:
            _time = f"{d.hour:02}:{d.minute:02}:{d.second:02}"
        else:
            _time = f"{d.minute:02}:{d.second:02}"

        return {
            "index": f"{index + 1:02}",
            "name": textwrap.shorten(name, width=35, placeholder="..."),
            "file_size": round(es_audio_doc.file_size / 1_048_576, 1),
            "time": _time,
            "url": hit_download_url,
            "sep": f"{40 * '-' if index != 0 else ''}",
            "quality_string": es_audio_doc.estimated_bit_rate_type.get_bit_rate_string(),
        }

    @classmethod
    def parse_from_query(
        cls,
        query: str,
        lang_code: str,
        es_audio_docs: Deque[elasticsearch_models.Audio],
        hit_download_urls: Deque[str],
    ):
        items = [
            cls.process_item(index, es_audio_doc, hit_download_url)
            for index, (es_audio_doc, hit_download_url) in reversed(list(enumerate(zip(es_audio_docs, hit_download_urls))))
        ]

        return QueryResultsData(
            query=query,
            items=items,
            lang_code=lang_code,
        )
