from .create_database import CreateDatabase
from .drop_database import DropDatabase
from .list_accessible_databases import ListAccessibleDatabases
from .list_of_databases import ListOfDatabases


class DatabaseMethods(
    CreateDatabase,
    DropDatabase,
    ListAccessibleDatabases,
    ListOfDatabases,
):
    pass
