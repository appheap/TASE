from .clear_slow_aql_queries import ClearSlowAQLQueries
from .explain_aql_query import ExplainAQLQuery
from .get_running_aql_queries import GetRunningAQLQueries
from .get_slow_aql_queries import GetSlowAQLQueries
from .kill_running_aql_query import KillRunningAQLQuery
from .parse_aql_query import ParseAQlQuery
from ..cursors import CreateCursor  # fixme: this class belongs to `cursor` api group!


class AQLMethods(
    ClearSlowAQLQueries,
    ExplainAQLQuery,
    GetRunningAQLQueries,
    GetSlowAQLQueries,
    KillRunningAQLQuery,
    CreateCursor,
    ParseAQlQuery,
):
    pass
