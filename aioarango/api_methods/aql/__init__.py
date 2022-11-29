from .clear_slow_aql_queries import ClearSlowAQLQueries
from .create_user_aql_function import CreateUserAQLFunction
from .delete_user_aql_function import DeleteUserAQLFunction
from .explain_aql_query import ExplainAQLQuery
from .get_all_aql_query_optimizer_rules import GetAllAQLQueryOptimizerRules
from .get_running_aql_queries import GetRunningAQLQueries
from .get_slow_aql_queries import GetSlowAQLQueries
from .get_user_registered_aql_functions import GetUserRegisteredAQLFunctions
from .kill_running_aql_query import KillRunningAQLQuery
from .parse_aql_query import ParseAQlQuery
from ..cursors import CreateCursor  # fixme: this class belongs to `cursor` api group!


class AQLMethods(
    ClearSlowAQLQueries,
    CreateUserAQLFunction,
    DeleteUserAQLFunction,
    ExplainAQLQuery,
    GetAllAQLQueryOptimizerRules,
    GetRunningAQLQueries,
    GetSlowAQLQueries,
    GetUserRegisteredAQLFunctions,
    KillRunningAQLQuery,
    CreateCursor,
    ParseAQlQuery,
):
    pass
