from .create_database import CreateDatabase
from .list_of_databases import ListOfDatabases


class DatabaseMethods(
    CreateDatabase,
    ListOfDatabases,
):
    pass
