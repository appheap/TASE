from jinja2 import Template

from tase.common.utils import _trans
from .base_template import BaseTemplate, BaseTemplateData


class NoResultsWereFoundData(BaseTemplateData):
    query: str
    s_no_results_were_found: str = _trans("No results were found for this query!")


class NoResultsWereFoundTemplate(BaseTemplate):
    name = "no_results_were_found_template"

    template = Template("{{emoji._traffic_light}}  {{s_no_results_were_found}}{{c_new_line}}<pre>{{query}}</pre>")
