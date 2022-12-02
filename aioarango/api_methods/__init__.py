from .administration import AdministrationMethods
from .analyzers import AnalyzersMethods
from .aql import AQLMethods, AQLCacheMethods
from .backup_restore import BackupRestoreMethods
from .bulk import BulkMethods
from .cluster import ClusterMethods
from .collections import CollectionsMethods
from .cursors import CursorsMethods
from .database import DatabaseMethods
from .documents import DocumentsMethods
from .foxx import FoxxMethods
from .graph import GraphMethods
from .graph_edges import GraphEdgesMethods
from .indexes import IndexesMethods
from .job import JobMethods
from .pregel import PregelMethods
from .replication import ReplicationMethods
from .transactions import TransactionsMethods
from .user_management import UserManagementMethods
from .views import ViewsMethods


class APIMethods(
    AdministrationMethods,
    AnalyzersMethods,
    AQLMethods,
    BackupRestoreMethods,
    BulkMethods,
    ClusterMethods,
    CollectionsMethods,
    CursorsMethods,
    DatabaseMethods,
    DocumentsMethods,
    FoxxMethods,
    GraphMethods,
    GraphEdgesMethods,
    IndexesMethods,
    JobMethods,
    PregelMethods,
    ReplicationMethods,
    TransactionsMethods,
    UserManagementMethods,
    ViewsMethods,
):
    pass
