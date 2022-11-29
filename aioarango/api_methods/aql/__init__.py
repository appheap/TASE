from .get_slow_aql_queries import GetSlowAQLQueries
from .kill_running_aql_query import KillRunningAQLQuery
from .parse_aql_query import ParseAQlQuery
from ..cursors import CreateCursor  # fixme: this class belongs to `cursor` api group!


class AQLMethods(
    GetSlowAQLQueries,
    KillRunningAQLQuery,
    CreateCursor,
    ParseAQlQuery,
):
    pass
