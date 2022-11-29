from .kill_running_aql_query import KillRunningAQLQuery
from .parse_aql_query import ParseAQlQuery
from ..cursors import CreateCursor  # fixme: this class belongs to `cursor` api group!


class AQLMethods(
    KillRunningAQLQuery,
    CreateCursor,
    ParseAQlQuery,
):
    pass
