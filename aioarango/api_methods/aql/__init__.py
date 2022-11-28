from .parse_aql_query import ParseAQlQuery
from ..cursors import CreateCursor  # fixme: this class belongs to `cursor` api group!


class AQLMethods(
    CreateCursor,
    ParseAQlQuery,
):
    pass
