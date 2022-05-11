from jinja2 import Template

from .base import BaseTemplateData, BaseTemplate
from tase.utils import _trans


class NoResultsWereFoundData(BaseTemplateData):
    query: str
    s_no_results_were_found: str = _trans("No results were found for this query!")


class NoResultsWereFoundTemplate(BaseTemplate):
    template = Template(
        "{{emoji._traffic_light}}  {{s_no_results_were_found}}{{c_new_line}}<pre>{{query}}</pre>"
    )
