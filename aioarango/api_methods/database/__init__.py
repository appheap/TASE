from .create_database import CreateDatabase
from .drop_database import DropDatabase
from .get_database_info import GetDatabaseInfo
from .list_accessible_databases import ListAccessibleDatabases
from .list_of_databases import ListOfDatabases


class DatabaseMethods(
    CreateDatabase,
    DropDatabase,
    GetDatabaseInfo,
    ListAccessibleDatabases,
    ListOfDatabases,
):
    pass
