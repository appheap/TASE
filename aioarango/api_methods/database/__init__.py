from .create_database import CreateDatabase
from .list_accessible_databases import ListAccessibleDatabases
from .list_of_databases import ListOfDatabases


class DatabaseMethods(
    CreateDatabase,
    ListAccessibleDatabases,
    ListOfDatabases,
):
    pass
