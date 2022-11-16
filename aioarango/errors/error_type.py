from enum import Enum


class ErrorType(Enum):
    EMPTY_PLACEHOLDER = -2

    UNKNOWN = -1
    """
    Will be raised when the server error is not known to the client.
    """

    NO_ERROR = 0
    """
    No error has occurred.
    """

    FAILED = 1
    """
    Will be raised when a general error occurred.
    """

    SYS_ERROR = 2
    """
    Will be raised when operating system error occurred.
    """

    OUT_OF_MEMORY = 3
    """
    Will be raised when there is a memory shortage.
    """

    INTERNAL = 4
    """
    Will be raised when an internal error occurred.
    """

    ILLEGAL_NUMBER = 5
    """
    Will be raised when an illegal representation of a number was given.
    """

    NUMERIC_OVERFLOW = 6
    """
    Will be raised when a numeric overflow occurred.
    """

    ILLEGAL_OPTION = 7
    """
    Will be raised when an unknown option was supplied by the user.
    """

    DEAD_PID = 8
    """
    Will be raised when a PID without a living process was found.
    """

    NOT_IMPLEMENTED = 9
    """
    Will be raised when hitting an unimplemented feature.
    """

    BAD_PARAMETER = 10
    """
    Will be raised when the parameter does not fulfill the requirements.
    """

    FORBIDDEN = 11
    """
    Will be raised when you are missing permission for the operation.
    """

    OUT_OF_MEMORY_MMAP = 12
    """
    Will be raised when there is a memory shortage.
    """

    CORRUPTED_CSV = 13
    """
    Will be raised when encountering a corrupt csv line.
    """

    FILE_NOT_FOUND = 14
    """
    Will be raised when a file is not found.
    """

    CANNOT_WRITE_FILE = 15
    """
    Will be raised when a file cannot be written.
    """

    CANNOT_OVERWRITE_FILE = 16
    """
    Will be raised when an attempt is made to overwrite an existing file.
    """

    TYPE_ERROR = 17
    """
    Will be raised when a type error is encountered.
    """

    LOCK_TIMEOUT = 18
    """
    Will be raised when there’s a timeout waiting for a lock.
    """

    CANNOT_CREATE_DIRECTORY = 19
    """
    Will be raised when an attempt to create a directory fails.
    """

    CANNOT_CREATE_TEMP_FILE = 20
    """
    Will be raised when an attempt to create a temporary file fails.
    """

    REQUEST_CANCELED = 21
    """
    Will be raised when a request is canceled by the user.
    """

    DEBUG = 22
    """
    Will be raised intentionally during debugging.
    """

    IP_ADDRESS_INVALID = 25
    """
    Will be raised when the structure of an IP address is invalid.
    """

    FILE_EXISTS = 27
    """
    Will be raised when a file already exists.
    """

    LOCKED = 28
    """
    Will be raised when a resource or an operation is locked.
    """

    DEADLOCK = 29
    """
    Will be raised when a deadlock is detected when accessing collections.
    """

    SHUTTING_DOWN = 30
    """
    Will be raised when a call cannot succeed because a server shutdown is already in progress.
    """

    ONLY_ENTERPRISE = 31
    """
    Will be raised when an Enterprise Edition feature is requested from the Community Edition.
    """

    RESOURCE_LIMIT = 32
    """
    Will be raised when the resources used by an operation exceed the configured maximum value.
    """

    ARANGO_ICU_ERROR = 33
    """
    will be raised if icu operations failed
    """

    CANNOT_READ_FILE = 34
    """
    Will be raised when a file cannot be read.
    """

    INCOMPATIBLE_VERSION = 35
    """
    Will be raised when a server is running an incompatible version of ArangoDB.
    """

    DISABLED = 36
    """
    Will be raised when a requested resource is not enabled.
    """

    MALFORMED_JSON = 37
    """
    Will be raised when a JSON string could not be parsed.
    """

    STARTING_UP = 38
    """
    Will be raised when a call cannot succeed because the server startup phase is still in progress.
    """

    HTTP_BAD_PARAMETER = 400
    """
    Will be raised when the HTTP request does not fulfill the requirements.
    """

    HTTP_UNAUTHORIZED = 401
    """
    Will be raised when authorization is required but the user is not authorized.
    """

    HTTP_FORBIDDEN = 403
    """
    Will be raised when the operation is forbidden.
    """

    HTTP_NOT_FOUND = 404
    """
    Will be raised when an URI is unknown.
    """

    HTTP_METHOD_NOT_ALLOWED = 405
    """
    Will be raised when an unsupported HTTP method is used for an operation.
    """

    HTTP_NOT_ACCEPTABLE = 406
    """
    Will be raised when an unsupported HTTP content type is used for an operation
    """

    HTTP_REQUEST_TIMEOUT = 408
    """
    Will be raised when a timeout occured.
    """

    HTTP_CONFLICT = 409
    """
    Will be raised when a conflict occurs in an HTTP operation.
    """

    HTTP_GONE = 410
    """
    Will be raised when the requested content has been permanently deleted.
    """

    HTTP_PRECONDITION_FAILED = 412
    """
    Will be raised when a precondition for an HTTP request is not met.
    """

    HTTP_SERVER_ERROR = 500
    """
    Will be raised when an internal server is encountered.
    """

    HTTP_NOT_IMPLEMENTED = 501
    """
    Will be raised when an API is called this is not implemented in general
    """

    HTTP_SERVICE_UNAVAILABLE = 503
    """
    Will be raised when a service is temporarily unavailable.
    """

    HTTP_GATEWAY_TIMEOUT = 504
    """
    Will be raised when a service contacted by ArangoDB does not respond in a timely manner.
    """

    HTTP_CORRUPTED_JSON = 600
    """
    Will be raised when a string representation of a JSON object is corrupt.
    """

    HTTP_SUPERFLUOUS_SUFFICES = 601
    """
    Will be raised when the URL contains superfluous suffices.
    """

    ARANGO_ILLEGAL_STATE = 1000
    """
    Internal error that will be raised when the datafile is not in the required state.
    """

    ARANGO_READ_ONLY = 1004
    """
    Internal error that will be raised when trying to write to a read-only datafile or collection.
    """

    ARANGO_DUPLICATE_IDENTIFIER = 1005
    """
    Internal error that will be raised when a identifier duplicate is detected.
    """

    ARANGO_CORRUPTED_DATAFILE = 1100
    """
    Will be raised when a corruption is detected in a datafile.
    """

    ARANGO_ILLEGAL_PARAMETER_FILE = 1101
    """
    Will be raised if a parameter file is corrupted or cannot be read.
    """

    ARANGO_CORRUPTED_COLLECTION = 1102
    """
    Will be raised when a collection contains one or more corrupted data files.
    """

    ARANGO_FILESYSTEM_FULL = 1104
    """
    Will be raised when the filesystem is full.
    """

    ARANGO_DATADIR_LOCKED = 1107
    """
    Will be raised when the database directory is locked by a different process.
    """

    ARANGO_CONFLICT = 1200
    """
    Will be raised when updating or deleting a document and a conflict has been detected.
    """

    ARANGO_DOCUMENT_NOT_FOUND = 1202
    """
    Will be raised when a document with a given identifier is unknown.
    """

    ARANGO_DATA_SOURCE_NOT_FOUND = 1203
    """
    Will be raised when a collection or View with the given identifier or name is unknown.
    """

    ARANGO_COLLECTION_PARAMETER_MISSING = 1204
    """
    Will be raised when the collection parameter is missing.
    """

    ARANGO_DOCUMENT_HANDLE_BAD = 1205
    """
    Will be raised when a document identifier is corrupt.
    """

    ARANGO_DUPLICATE_NAME = 1207
    """
    Will be raised when a name duplicate is detected.
    """

    ARANGO_ILLEGAL_NAME = 1208
    """
    Will be raised when an illegal name is detected.
    """

    ARANGO_NO_INDEX = 1209
    """
    Will be raised when no suitable index for the query is known.
    """

    ARANGO_UNIQUE_CONSTRAINT_VIOLATED = 1210
    """
    Will be raised when there is a unique constraint violation.
    """

    ARANGO_INDEX_NOT_FOUND = 1212
    """
    Will be raised when an index with a given identifier is unknown.
    """

    ARANGO_CROSS_COLLECTION_REQUEST = 1213
    """
    Will be raised when a cross-collection is requested.
    """

    ARANGO_INDEX_HANDLE_BAD = 1214
    """
    Will be raised when a index identifier is corrupt.
    """

    ARANGO_DOCUMENT_TOO_LARGE = 1216
    """
    Will be raised when the document cannot fit into any datafile because of it is too large.
    """

    ARANGO_COLLECTION_NOT_UNLOADED = 1217
    """
    Will be raised when a collection should be unloaded
    """

    ARANGO_COLLECTION_TYPE_INVALID = 1218
    """
    Will be raised when an invalid collection type is used in a request.
    """

    ARANGO_ATTRIBUTE_PARSER_FAILED = 1220
    """
    Will be raised when parsing an attribute name definition failed.
    """

    ARANGO_DOCUMENT_KEY_BAD = 1221
    """
    Will be raised when a document key is corrupt.
    """

    ARANGO_DOCUMENT_KEY_UNEXPECTED = 1222
    """
    Will be raised when a user-defined document key is supplied for collections with auto key generation.
    """

    ARANGO_DATADIR_NOT_WRITABLE = 1224
    """
    Will be raised when the server’s database directory is not writable for the current user.
    """

    ARANGO_OUT_OF_KEYS = 1225
    """
    Will be raised when a key generator runs out of keys.
    """

    ARANGO_DOCUMENT_KEY_MISSING = 1226
    """
    Will be raised when a document key is missing.
    """

    ARANGO_DOCUMENT_TYPE_INVALID = 1227
    """
    Will be raised when there is an attempt to create a document with an invalid type.
    """

    ARANGO_DATABASE_NOT_FOUND = 1228
    """
    Will be raised when a non-existing database is accessed.
    """

    ARANGO_DATABASE_NAME_INVALID = 1229
    """
    Will be raised when an invalid database name is used.
    """

    ARANGO_USE_SYSTEM_DATABASE = 1230
    """
    Will be raised when an operation is requested in a database other than the system database.
    """

    ARANGO_INVALID_KEY_GENERATOR = 1232
    """
    Will be raised when an invalid key generator description is used.
    """

    ARANGO_INVALID_EDGE_ATTRIBUTE = 1233
    """
    will be raised when the _from or _to values of an edge are undefined or contain an invalid value.
    """

    ARANGO_INDEX_CREATION_FAILED = 1235
    """
    Will be raised when an attempt to create an index has failed.
    """

    ARANGO_COLLECTION_TYPE_MISMATCH = 1237
    """
    Will be raised when a collection has a different type from what has been expected.
    """

    ARANGO_COLLECTION_NOT_LOADED = 1238
    """
    Will be raised when a collection is accessed that is not yet loaded.
    """

    ARANGO_DOCUMENT_REV_BAD = 1239
    """
    Will be raised when a document revision is corrupt or is missing where needed.
    """

    ARANGO_INCOMPLETE_READ = 1240
    """
    Will be raised by the storage engine when a read cannot be completed.
    """

    ARANGO_EMPTY_DATADIR = 1301
    """
    Will be raised when encountering an empty server database directory.
    """

    ARANGO_TRY_AGAIN = 1302
    """
    Will be raised when an operation should be retried.
    """

    ARANGO_BUSY = 1303
    """
    Will be raised when storage engine is busy.
    """

    ARANGO_MERGE_IN_PROGRESS = 1304
    """
    Will be raised when storage engine has a datafile merge in progress and cannot complete the operation.
    """

    ARANGO_IO_ERROR = 1305
    """
    Will be raised when storage engine encounters an I/O error.
    """

    REPLICATION_NO_RESPONSE = 1400
    """
    Will be raised when the replication applier does not receive any or an incomplete response from the leader.
    """

    REPLICATION_INVALID_RESPONSE = 1401
    """
    Will be raised when the replication applier receives an invalid response from the leader.
    """

    REPLICATION_LEADER_ERROR = 1402
    """
    Will be raised when the replication applier receives a server error from the leader.
    """

    REPLICATION_LEADER_INCOMPATIBLE = 1403
    """
    Will be raised when the replication applier connects to a leader that has an incompatible version.
    """

    REPLICATION_LEADER_CHANGE = 1404
    """
    Will be raised when the replication applier connects to a different leader than before.
    """

    REPLICATION_LOOP = 1405
    """
    Will be raised when the replication applier is asked to connect to itself for replication.
    """

    REPLICATION_UNEXPECTED_MARKER = 1406
    """
    Will be raised when an unexpected marker is found in the replication log stream.
    """

    REPLICATION_INVALID_APPLIER_STATE = 1407
    """
    Will be raised when an invalid replication applier state file is found.
    """

    REPLICATION_UNEXPECTED_TRANSACTION = 1408
    """
    Will be raised when an unexpected transaction id is found.
    """

    REPLICATION_SHARD_SYNC_ATTEMPT_TIMEOUT_EXCEEDED = 1409
    """
    Will be raised when the synchronization of a shard takes longer than the configured timeout.
    """

    REPLICATION_INVALID_APPLIER_CONFIGURATION = 1410
    """
    Will be raised when the configuration for the replication applier is invalid.
    """

    REPLICATION_RUNNING = 1411
    """
    Will be raised when there is an attempt to perform an operation while the replication applier is running.
    """

    REPLICATION_APPLIER_STOPPED = 1412
    """
    Special error code used to indicate the replication applier was stopped by a user.
    """

    REPLICATION_NO_START_TICK = 1413
    """
    Will be raised when the replication applier is started without a known start tick value.
    """

    REPLICATION_START_TICK_NOT_PRESENT = 1414
    """
    Will be raised when the replication applier fetches data using a start tick
    """

    REPLICATION_WRONG_CHECKSUM = 1416
    """
    Will be raised when a new born follower submits a wrong checksum
    """

    REPLICATION_SHARD_NONEMPTY = 1417
    """
    Will be raised when a shard is not empty and the follower tries a shortcut
    """

    REPLICATION_REPLICATED_LOG_NOT_FOUND = 1418
    """
    Will be raised when a specific replicated log is not found
    """

    REPLICATION_REPLICATED_LOG_NOT_THE_LEADER = 1419
    """
    Will be raised when a participant of a replicated log is ordered to do something only the leader can do
    """

    REPLICATION_REPLICATED_LOG_NOT_A_FOLLOWER = 1420
    """
    Will be raised when a participant of a replicated log is ordered to do something only a follower can do
    """

    REPLICATION_REPLICATED_LOG_APPEND_ENTRIES_REJECTED = 1421
    """
    Will be raised when a follower of a replicated log rejects an append entries request
    """

    REPLICATION_REPLICATED_LOG_LEADER_RESIGNED = 1422
    """
    Will be raised when a leader instance of a replicated log rejects a request because it just resigned. This can also happen if the term changes (due to a configuration change)
    """

    REPLICATION_REPLICATED_LOG_FOLLOWER_RESIGNED = 1423
    """
    Will be raised when a follower instance of a replicated log rejects a request because it just resigned. This can also happen if the term changes (due to a configuration change)
    """

    REPLICATION_REPLICATED_LOG_PARTICIPANT_GONE = 1424
    """
    Will be raised when a participant instance of a replicated log is no longer available.
    """

    REPLICATION_REPLICATED_LOG_INVALID_TERM = 1425
    """
    Will be raised when a participant tries to change its term but found a invalid new term.
    """

    REPLICATION_REPLICATED_LOG_UNCONFIGURED = 1426
    """
    Will be raised when a participant is currently unconfigured
    """

    REPLICATION_REPLICATED_STATE_NOT_FOUND = 1427
    """
    Will be raised when a specific replicated state was not found.
    """

    CLUSTER_NOT_FOLLOWER = 1446
    """
    Will be raised when an operation is sent to a non-following server.
    """

    CLUSTER_FOLLOWER_TRANSACTION_COMMIT_PERFORMED = 1447
    """
    Will be raised when a follower transaction has already performed an intermediate commit and must be rolled back.
    """

    CLUSTER_CREATE_COLLECTION_PRECONDITION_FAILED = 1448
    """
    Will be raised when updating the plan on collection creation failed.
    """

    CLUSTER_SERVER_UNKNOWN = 1449
    """
    Will be raised on some occasions when one server gets a request from another
    """

    CLUSTER_TOO_MANY_SHARDS = 1450
    """
    Will be raised when the number of shards for a collection is higher than allowed.
    """

    CLUSTER_COULD_NOT_CREATE_COLLECTION_IN_PLAN = 1454
    """
    Will be raised when a Coordinator in a cluster cannot create an entry for a new collection in the Plan hierarchy in the Agency.
    """

    CLUSTER_COULD_NOT_CREATE_COLLECTION = 1456
    """
    Will be raised when a Coordinator in a cluster notices that some DB-Servers report problems when creating shards for a new collection.
    """

    CLUSTER_TIMEOUT = 1457
    """
    Will be raised when a Coordinator in a cluster runs into a timeout for some cluster wide operation.
    """

    CLUSTER_COULD_NOT_REMOVE_COLLECTION_IN_PLAN = 1458
    """
    Will be raised when a Coordinator in a cluster cannot remove an entry for a collection in the Plan hierarchy in the Agency.
    """

    CLUSTER_COULD_NOT_CREATE_DATABASE_IN_PLAN = 1460
    """
    Will be raised when a Coordinator in a cluster cannot create an entry for a new database in the Plan hierarchy in the Agency.
    """

    CLUSTER_COULD_NOT_CREATE_DATABASE = 1461
    """
    Will be raised when a Coordinator in a cluster notices that some DB-Servers report problems when creating databases for a new cluster wide database.
    """

    CLUSTER_COULD_NOT_REMOVE_DATABASE_IN_PLAN = 1462
    """
    Will be raised when a Coordinator in a cluster cannot remove an entry for a database in the Plan hierarchy in the Agency.
    """

    CLUSTER_COULD_NOT_REMOVE_DATABASE_IN_CURRENT = 1463
    """
    Will be raised when a Coordinator in a cluster cannot remove an entry for a database in the Current hierarchy in the Agency.
    """

    CLUSTER_SHARD_GONE = 1464
    """
    Will be raised when a Coordinator in a cluster cannot determine the shard that is responsible for a given document.
    """

    CLUSTER_CONNECTION_LOST = 1465
    """
    Will be raised when a Coordinator in a cluster loses an HTTP connection to a DB-Server in the cluster whilst transferring data.
    """

    CLUSTER_MUST_NOT_SPECIFY_KEY = 1466
    """
    Will be raised when a Coordinator in a cluster finds that the _key attribute was specified in a sharded collection the uses not only _key as sharding attribute.
    """

    CLUSTER_GOT_CONTRADICTING_ANSWERS = 1467
    """
    Will be raised if a Coordinator in a cluster gets conflicting results from different shards
    """

    CLUSTER_NOT_ALL_SHARDING_ATTRIBUTES_GIVEN = 1468
    """
    Will be raised if a Coordinator tries to find out which shard is responsible for a partial document
    """

    CLUSTER_MUST_NOT_CHANGE_SHARDING_ATTRIBUTES = 1469
    """
    Will be raised if there is an attempt to update the value of a shard attribute.
    """

    CLUSTER_UNSUPPORTED = 1470
    """
    Will be raised when there is an attempt to carry out an operation that is not supported in the context of a sharded collection.
    """

    CLUSTER_ONLY_ON_COORDINATOR = 1471
    """
    Will be raised if there is an attempt to run a Coordinator-only operation on a different type of node.
    """

    CLUSTER_READING_PLAN_AGENCY = 1472
    """
    Will be raised if a Coordinator or DB-Server cannot read the Plan in the Agency.
    """

    CLUSTER_COULD_NOT_TRUNCATE_COLLECTION = 1473
    """
    Will be raised if a Coordinator cannot truncate all shards of a cluster collection.
    """

    CLUSTER_AQL_COMMUNICATION = 1474
    """
    Will be raised if the internal communication of the cluster for AQL produces an error.
    """

    CLUSTER_ONLY_ON_DBSERVER = 1477
    """
    Will be raised if there is an attempt to run a DB-Server-only operation on a different type of node.
    """

    CLUSTER_BACKEND_UNAVAILABLE = 1478
    """
    Will be raised if a required DB-Server can’t be reached.
    """

    CLUSTER_AQL_COLLECTION_OUT_OF_SYNC = 1481
    """
    Will be raised if a collection/view needed during query execution is out of sync. This currently can happen when using SatelliteCollections
    """

    CLUSTER_COULD_NOT_CREATE_INDEX_IN_PLAN = 1482
    """
    Will be raised when a Coordinator in a cluster cannot create an entry for a new index in the Plan hierarchy in the Agency.
    """

    CLUSTER_COULD_NOT_DROP_INDEX_IN_PLAN = 1483
    """
    Will be raised when a Coordinator in a cluster cannot remove an index from the Plan hierarchy in the Agency.
    """

    CLUSTER_CHAIN_OF_DISTRIBUTESHARDSLIKE = 1484
    """
    Will be raised if one tries to create a collection with a distributeShardsLike attribute which points to another collection that also has one.
    """

    CLUSTER_MUST_NOT_DROP_COLL_OTHER_DISTRIBUTESHARDSLIKE = 1485
    """
    Will be raised if one tries to drop a collection to which another collection points with its distributeShardsLike attribute.
    """

    CLUSTER_UNKNOWN_DISTRIBUTESHARDSLIKE = 1486
    """
    Will be raised if one tries to create a collection which points to an unknown collection in its distributeShardsLike attribute.
    """

    CLUSTER_INSUFFICIENT_DBSERVERS = 1487
    """
    Will be raised if one tries to create a collection with a replicationFactor greater than the available number of DB-Servers.
    """

    CLUSTER_COULD_NOT_DROP_FOLLOWER = 1488
    """
    Will be raised if a follower that ought to be dropped could not be dropped in the Agency (under Current).
    """

    CLUSTER_SHARD_LEADER_REFUSES_REPLICATION = 1489
    """
    Will be raised if a replication operation is refused by a shard leader.
    """

    CLUSTER_SHARD_FOLLOWER_REFUSES_OPERATION = 1490
    """
    Will be raised if a replication operation is refused by a shard follower because it is coming from the wrong leader.
    """

    CLUSTER_SHARD_LEADER_RESIGNED = 1491
    """
    because it has resigned in the meantime
    """

    CLUSTER_AGENCY_COMMUNICATION_FAILED = 1492
    """
    Will be raised if after various retries an Agency operation could not be performed successfully.
    """

    CLUSTER_LEADERSHIP_CHALLENGE_ONGOING = 1495
    """
    Will be raised when servers are currently competing for leadership
    """

    CLUSTER_NOT_LEADER = 1496
    """
    Will be raised when an operation is sent to a non-leading server.
    """

    CLUSTER_COULD_NOT_CREATE_VIEW_IN_PLAN = 1497
    """
    Will be raised when a Coordinator in a cluster cannot create an entry for a new View in the Plan hierarchy in the Agency.
    """

    CLUSTER_VIEW_ID_EXISTS = 1498
    """
    Will be raised when a Coordinator in a cluster tries to create a View and the View ID already exists.
    """

    CLUSTER_COULD_NOT_DROP_COLLECTION = 1499
    """
    Will be raised when a Coordinator in a cluster cannot drop a collection entry in the Plan hierarchy in the Agency.
    """

    QUERY_KILLED = 1500
    """
    Will be raised when a running query is killed by an explicit admin command.
    """

    QUERY_PARSE = 1501
    """
    Will be raised when query is parsed and is found to be syntactically invalid.
    """

    QUERY_EMPTY = 1502
    """
    Will be raised when an empty query is specified.
    """

    QUERY_SCRIPT = 1503
    """
    Will be raised when a runtime error is caused by the query.
    """

    QUERY_NUMBER_OUT_OF_RANGE = 1504
    """
    Will be raised when a number is outside the expected range.
    """

    QUERY_INVALID_GEO_VALUE = 1505
    """
    Will be raised when a geo index coordinate is invalid or out of range.
    """

    QUERY_VARIABLE_NAME_INVALID = 1510
    """
    Will be raised when an invalid variable name is used.
    """

    QUERY_VARIABLE_REDECLARED = 1511
    """
    Will be raised when a variable gets re-assigned in a query.
    """

    QUERY_VARIABLE_NAME_UNKNOWN = 1512
    """
    Will be raised when an unknown variable is used or the variable is undefined the context it is used.
    """

    QUERY_COLLECTION_LOCK_FAILED = 1521
    """
    Will be raised when a read lock on the collection cannot be acquired.
    """

    QUERY_TOO_MANY_COLLECTIONS = 1522
    """
    Will be raised when the number of collections or shards in a query is beyond the allowed value.
    """

    QUERY_TOO_MUCH_NESTING = 1524
    """
    Will be raised when a query contains expressions or other constructs with too many objects or that are too deeply nested.
    """

    QUERY_INVALID_OPTIONS_ATTRIBUTE = 1539
    """
    Will be raised when an unknown attribute is used inside an OPTIONS clause.
    """

    QUERY_FUNCTION_NAME_UNKNOWN = 1540
    """
    Will be raised when an undefined function is called.
    """

    QUERY_FUNCTION_ARGUMENT_NUMBER_MISMATCH = 1541
    """
    expected number of arguments: minimum: %d
    """

    QUERY_FUNCTION_ARGUMENT_TYPE_MISMATCH = 1542
    """
    Will be raised when the type of an argument used in a function call does not match the expected argument type.
    """

    QUERY_INVALID_REGEX = 1543
    """
    Will be raised when an invalid regex argument value is used in a call to a function that expects a regex.
    """

    QUERY_BIND_PARAMETERS_INVALID = 1550
    """
    Will be raised when the structure of bind parameters passed has an unexpected format.
    """

    QUERY_BIND_PARAMETER_MISSING = 1551
    """
    Will be raised when a bind parameter was declared in the query but the query is being executed with no value for that parameter.
    """

    QUERY_BIND_PARAMETER_UNDECLARED = 1552
    """
    Will be raised when a value gets specified for an undeclared bind parameter.
    """

    QUERY_BIND_PARAMETER_TYPE = 1553
    """
    Will be raised when a bind parameter has an invalid value or type.
    """

    QUERY_INVALID_ARITHMETIC_VALUE = 1561
    """
    Will be raised when a non-numeric value is used in an arithmetic operation.
    """

    QUERY_DIVISION_BY_ZERO = 1562
    """
    Will be raised when there is an attempt to divide by zero.
    """

    QUERY_ARRAY_EXPECTED = 1563
    """
    Will be raised when a non-array operand is used for an operation that expects an array argument operand.
    """

    QUERY_COLLECTION_USED_IN_EXPRESSION = 1568
    """
    Will be raised when a collection is used as an operand in an AQL expression.
    """

    QUERY_FAIL_CALLED = 1569
    """
    Will be raised when the function FAIL() is called from inside a query.
    """

    QUERY_GEO_INDEX_MISSING = 1570
    """
    Will be raised when a geo restriction was specified but no suitable geo index is found to resolve it.
    """

    QUERY_FULLTEXT_INDEX_MISSING = 1571
    """
    Will be raised when a fulltext query is performed on a collection without a suitable fulltext index.
    """

    QUERY_INVALID_DATE_VALUE = 1572
    """
    Will be raised when a value cannot be converted to a date.
    """

    QUERY_MULTI_MODIFY = 1573
    """
    Will be raised when an AQL query contains more than one data-modifying operation.
    """

    QUERY_INVALID_AGGREGATE_EXPRESSION = 1574
    """
    Will be raised when an AQL query contains an invalid aggregate expression.
    """

    QUERY_COMPILE_TIME_OPTIONS = 1575
    """
    Will be raised when an AQL query contains OPTIONS that cannot be figured out at query compile time.
    """

    QUERY_FORCED_INDEX_HINT_UNUSABLE = 1577
    """
    Will be raised when forceIndexHint is specified
    """

    QUERY_DISALLOWED_DYNAMIC_CALL = 1578
    """
    Will be raised when a dynamic function call is made to a function that cannot be called dynamically.
    """

    QUERY_ACCESS_AFTER_MODIFICATION = 1579
    """
    Will be raised when collection data are accessed after a data-modification operation.
    """

    QUERY_FUNCTION_INVALID_NAME = 1580
    """
    Will be raised when a user function with an invalid name is registered.
    """

    QUERY_FUNCTION_INVALID_CODE = 1581
    """
    Will be raised when a user function is registered with invalid code.
    """

    QUERY_FUNCTION_NOT_FOUND = 1582
    """
    Will be raised when a user function is accessed but not found.
    """

    QUERY_FUNCTION_RUNTIME_ERROR = 1583
    """
    Will be raised when a user function throws a runtime exception.
    """

    QUERY_BAD_JSON_PLAN = 1590
    """
    Will be raised when an HTTP API for a query got an invalid JSON object.
    """

    QUERY_NOT_FOUND = 1591
    """
    Will be raised when an Id of a query is not found by the HTTP API.
    """

    QUERY_USER_ASSERT = 1593
    """
    Will be raised if and user provided expression fails to evaluate to true
    """

    QUERY_USER_WARN = 1594
    """
    Will be raised if and user provided expression fails to evaluate to true
    """

    QUERY_WINDOW_AFTER_MODIFICATION = 1595
    """
    Will be raised when a window node is created after a data-modification operation.
    """

    CURSOR_NOT_FOUND = 1600
    """
    Will be raised when a cursor is requested via its id but a cursor with that id cannot be found.
    """

    CURSOR_BUSY = 1601
    """
    Will be raised when a cursor is requested via its id but a concurrent request is still using the cursor.
    """

    VALIDATION_FAILED = 1620
    """
    Will be raised when a document does not pass schema validation.
    """

    VALIDATION_BAD_PARAMETER = 1621
    """
    Will be raised when the schema description is invalid.
    """

    TRANSACTION_INTERNAL = 1650
    """
    Will be raised when a wrong usage of transactions is detected. this is an internal error and indicates a bug in ArangoDB.
    """

    TRANSACTION_NESTED = 1651
    """
    Will be raised when transactions are nested.
    """

    TRANSACTION_UNREGISTERED_COLLECTION = 1652
    """
    Will be raised when a collection is used in the middle of a transaction but was not registered at transaction start.
    """

    TRANSACTION_DISALLOWED_OPERATION = 1653
    """
    Will be raised when a disallowed operation is carried out in a transaction.
    """

    TRANSACTION_ABORTED = 1654
    """
    Will be raised when a transaction was aborted.
    """

    TRANSACTION_NOT_FOUND = 1655
    """
    Will be raised when a transaction was not found.
    """

    USER_INVALID_NAME = 1700
    """
    Will be raised when an invalid user name is used.
    """

    USER_DUPLICATE = 1702
    """
    Will be raised when a user name already exists.
    """

    USER_NOT_FOUND = 1703
    """
    Will be raised when a user name is updated that does not exist.
    """

    USER_EXTERNAL = 1705
    """
    Will be raised when the user is authenticated by an external server.
    """

    SERVICE_DOWNLOAD_FAILED = 1752
    """
    Will be raised when a service download from the central repository failed.
    """

    SERVICE_UPLOAD_FAILED = 1753
    """
    Will be raised when a service upload from the client to the ArangoDB server failed.
    """

    LDAP_CANNOT_INIT = 1800
    """
    can not init a LDAP connection
    """

    LDAP_CANNOT_SET_OPTION = 1801
    """
    can not set a LDAP option
    """

    LDAP_CANNOT_BIND = 1802
    """
    can not bind to a LDAP server
    """

    LDAP_CANNOT_UNBIND = 1803
    """
    can not unbind from a LDAP server
    """

    LDAP_CANNOT_SEARCH = 1804
    """
    can not search the LDAP server
    """

    LDAP_CANNOT_START_TLS = 1805
    """
    can not star a TLS LDAP session
    """

    LDAP_FOUND_NO_OBJECTS = 1806
    """
    LDAP didn’t found any objects with the specified search query
    """

    LDAP_NOT_ONE_USER_FOUND = 1807
    """
    LDAP found zero ore more than one user
    """

    LDAP_USER_NOT_IDENTIFIED = 1808
    """
    but its not the desired one
    """

    LDAP_OPERATIONS_ERROR = 1809
    """
    LDAP returned an operations error
    """

    LDAP_INVALID_MODE = 1820
    """
    cant distinguish a valid mode for provided LDAP configuration
    """

    TASK_INVALID_ID = 1850
    """
    Will be raised when a task is created with an invalid id.
    """

    TASK_DUPLICATE_ID = 1851
    """
    Will be raised when a task id is created with a duplicate id.
    """

    TASK_NOT_FOUND = 1852
    """
    Will be raised when a task with the specified id could not be found.
    """

    GRAPH_INVALID_GRAPH = 1901
    """
    Will be raised when an invalid name is passed to the server.
    """

    GRAPH_INVALID_EDGE = 1906
    """
    Will be raised when an invalid edge id is passed to the server.
    """

    GRAPH_TOO_MANY_ITERATIONS = 1909
    """
    Will be raised when too many iterations are done in a graph traversal.
    """

    GRAPH_INVALID_FILTER_RESULT = 1910
    """
    Will be raised when an invalid filter result is returned in a graph traversal.
    """

    GRAPH_COLLECTION_MULTI_USE = 1920
    """
    an edge collection may only be used once in one edge definition of a graph.
    """

    GRAPH_COLLECTION_USE_IN_MULTI_GRAPHS = 1921
    """
    is already used by another graph in a different edge definition.
    """

    GRAPH_CREATE_MISSING_NAME = 1922
    """
    a graph name is required to create or drop a graph.
    """

    GRAPH_CREATE_MALFORMED_EDGE_DEFINITION = 1923
    """
    the edge definition is malformed. It has to be an array of objects.
    """

    GRAPH_NOT_FOUND = 1924
    """
    a graph with this name could not be found.
    """

    GRAPH_DUPLICATE = 1925
    """
    a graph with this name already exists.
    """

    GRAPH_VERTEX_COL_DOES_NOT_EXIST = 1926
    """
    the specified vertex collection does not exist or is not part of the graph.
    """

    GRAPH_WRONG_COLLECTION_TYPE_VERTEX = 1927
    """
    the collection is not a vertex collection.
    """

    GRAPH_NOT_IN_ORPHAN_COLLECTION = 1928
    """
    Vertex collection not in list of orphan collections of the graph.
    """

    GRAPH_COLLECTION_USED_IN_EDGE_DEF = 1929
    """
    The collection is already used in an edge definition of the graph.
    """

    GRAPH_EDGE_COLLECTION_NOT_USED = 1930
    """
    The edge collection is not used in any edge definition of the graph.
    """

    GRAPH_NO_GRAPH_COLLECTION = 1932
    """
    collection _graphs does not exist.
    """

    GRAPH_INVALID_NUMBER_OF_ARGUMENTS = 1935
    """
    Invalid number of arguments. Expected:
    """

    GRAPH_INVALID_PARAMETER = 1936
    """
    Invalid parameter type.
    """

    GRAPH_COLLECTION_USED_IN_ORPHANS = 1938
    """
    The collection is already used in the orphans of the graph.
    """

    GRAPH_EDGE_COL_DOES_NOT_EXIST = 1939
    """
    the specified edge collection does not exist or is not part of the graph.
    """

    GRAPH_EMPTY = 1940
    """
    The requested graph has no edge collections.
    """

    GRAPH_INTERNAL_DATA_CORRUPT = 1941
    """
    The _graphs collection contains invalid data.
    """

    GRAPH_CREATE_MALFORMED_ORPHAN_LIST = 1943
    """
    the orphan list argument is malformed. It has to be an array of strings.
    """

    GRAPH_EDGE_DEFINITION_IS_DOCUMENT = 1944
    """
    the collection used as a relation is existing
    """

    GRAPH_COLLECTION_IS_INITIAL = 1945
    """
    the collection is used as the initial collection of this graph and is not allowed to be removed manually.
    """

    GRAPH_NO_INITIAL_COLLECTION = 1946
    """
    during the graph creation process no collection could be selected as the needed initial collection. Happens if a distributeShardsLike or replicationFactor mismatch was found.
    """

    GRAPH_REFERENCED_VERTEX_COLLECTION_NOT_USED = 1947
    """
    the _from or _to collection specified for the edge refers to a vertex collection which is not used in any edge definition of the graph.
    """

    GRAPH_NEGATIVE_EDGE_WEIGHT = 1948
    """
    a negative edge weight was found during a weighted graph traversal or shortest path query
    """

    SESSION_UNKNOWN = 1950
    """
    Will be raised when an invalid/unknown session id is passed to the server.
    """

    SESSION_EXPIRED = 1951
    """
    Will be raised when a session is expired.
    """

    SIMPLE_CLIENT_UNKNOWN_ERROR = 2000
    """
    This error should not happen.
    """

    SIMPLE_CLIENT_COULD_NOT_CONNECT = 2001
    """
    Will be raised when the client could not connect to the server.
    """

    SIMPLE_CLIENT_COULD_NOT_WRITE = 2002
    """
    Will be raised when the client could not write data.
    """

    SIMPLE_CLIENT_COULD_NOT_READ = 2003
    """
    Will be raised when the client could not read data.
    """

    WAS_ERLAUBE = 2019
    """
    Will be raised if was erlaube?!
    """

    INTERNAL_AQL = 2200
    """
    Internal error during AQL execution
    """

    WROTE_TOO_FEW_OUTPUT_REGISTERS = 2201
    """
    An AQL block wrote too few output registers
    """

    WROTE_TOO_MANY_OUTPUT_REGISTERS = 2202
    """
    An AQL block wrote too many output registers
    """

    WROTE_OUTPUT_REGISTER_TWICE = 2203
    """
    An AQL block wrote an output register twice
    """

    WROTE_IN_WRONG_REGISTER = 2204
    """
    An AQL block wrote in a register that is not its output
    """

    INPUT_REGISTERS_NOT_COPIED = 2205
    """
    An AQL block did not copy its input registers
    """

    MALFORMED_MANIFEST_FILE = 3000
    """
    The service manifest file is not well-formed JSON.
    """

    INVALID_SERVICE_MANIFEST = 3001
    """
    The service manifest contains invalid values.
    """

    SERVICE_FILES_MISSING = 3002
    """
    The service folder or bundle does not exist on this server.
    """

    SERVICE_FILES_OUTDATED = 3003
    """
    The local service bundle does not match the checksum in the database.
    """

    INVALID_FOXX_OPTIONS = 3004
    """
    The service options contain invalid values.
    """

    INVALID_MOUNTPOINT = 3007
    """
    The service mountpath contains invalid characters.
    """

    SERVICE_NOT_FOUND = 3009
    """
    No service found at the given mountpath.
    """

    SERVICE_NEEDS_CONFIGURATION = 3010
    """
    The service is missing configuration or dependencies.
    """

    SERVICE_MOUNTPOINT_CONFLICT = 3011
    """
    A service already exists at the given mountpath.
    """

    SERVICE_MANIFEST_NOT_FOUND = 3012
    """
    The service directory does not contain a manifest file.
    """

    SERVICE_OPTIONS_MALFORMED = 3013
    """
    The service options are not well-formed JSON.
    """

    SERVICE_SOURCE_NOT_FOUND = 3014
    """
    The source path does not match a file or directory.
    """

    SERVICE_SOURCE_ERROR = 3015
    """
    The source path could not be resolved.
    """

    SERVICE_UNKNOWN_SCRIPT = 3016
    """
    The service does not have a script with this name.
    """

    SERVICE_API_DISABLED = 3099
    """
    The API for managing Foxx services has been disabled on this server.
    """

    MODULE_NOT_FOUND = 3100
    """
    The module path could not be resolved.
    """

    MODULE_SYNTAX_ERROR = 3101
    """
    The module could not be parsed because of a syntax error.
    """

    MODULE_FAILURE = 3103
    """
    Failed to invoke the module in its context.
    """

    NO_SMART_COLLECTION = 4000
    """
    The requested collection needs to be smart
    """

    NO_SMART_GRAPH_ATTRIBUTE = 4001
    """
    The given document does not have the SmartGraph attribute set.
    """

    CANNOT_DROP_SMART_COLLECTION = 4002
    """
    This smart collection cannot be dropped
    """

    KEY_MUST_BE_PREFIXED_WITH_SMART_GRAPH_ATTRIBUTE = 4003
    """
    In a smart vertex collection _key must be prefixed with the value of the SmartGraph attribute.
    """

    ILLEGAL_SMART_GRAPH_ATTRIBUTE = 4004
    """
    The given smartGraph attribute is illegal and cannot be used for sharding. All system attributes are forbidden.
    """

    SMART_GRAPH_ATTRIBUTE_MISMATCH = 4005
    """
    The SmartGraph attribute of the given collection does not match the SmartGraph attribute of the graph.
    """

    INVALID_SMART_JOIN_ATTRIBUTE = 4006
    """
    Will be raised when the smartJoinAttribute declaration is invalid.
    """

    KEY_MUST_BE_PREFIXED_WITH_SMART_JOIN_ATTRIBUTE = 4007
    """
    when using smartJoinAttribute for a collection
    """

    NO_SMART_JOIN_ATTRIBUTE = 4008
    """
    The given document does not have the required SmartJoin attribute set or it has an invalid value.
    """

    CLUSTER_MUST_NOT_CHANGE_SMART_JOIN_ATTRIBUTE = 4009
    """
    Will be raised if there is an attempt to update the value of the smartJoinAttribute.
    """

    INVALID_DISJOINT_SMART_EDGE = 4010
    """
    Will be raised if there is an attempt to create an edge between separated graph components.
    """

    UNSUPPORTED_CHANGE_IN_SMART_TO_SATELLITE_DISJOINT_EDGE_DIRECTION = 4011
    """
    Switching back and forth between Satellite and Smart in Disjoint SmartGraph is not supported within a single AQL statement. Split into multiple statements.
    """

    AGENCY_MALFORMED_GOSSIP_MESSAGE = 20001
    """
    Malformed gossip message.
    """

    AGENCY_MALFORMED_INQUIRE_REQUEST = 20002
    """
    Malformed inquire request.
    """

    AGENCY_INFORM_MUST_BE_OBJECT = 20011
    """
    The inform message in the Agency must be an object.
    """

    AGENCY_INFORM_MUST_CONTAIN_TERM = 20012
    """
    The inform message in the Agency must contain a uint parameter ‘term’.
    """

    AGENCY_INFORM_MUST_CONTAIN_ID = 20013
    """
    The inform message in the Agency must contain a string parameter ‘id’.
    """

    AGENCY_INFORM_MUST_CONTAIN_ACTIVE = 20014
    """
    The inform message in the Agency must contain an array ‘active’.
    """

    AGENCY_INFORM_MUST_CONTAIN_POOL = 20015
    """
    The inform message in the Agency must contain an object ‘pool’.
    """

    AGENCY_INFORM_MUST_CONTAIN_MIN_PING = 20016
    """
    The inform message in the Agency must contain an object ‘min ping’.
    """

    AGENCY_INFORM_MUST_CONTAIN_MAX_PING = 20017
    """
    The inform message in the Agency must contain an object ‘max ping’.
    """

    AGENCY_INFORM_MUST_CONTAIN_TIMEOUT_MULT = 20018
    """
    The inform message in the Agency must contain an object ‘timeoutMult’.
    """

    AGENCY_CANNOT_REBUILD_DBS = 20021
    """
    Will be raised if the readDB or the spearHead cannot be rebuilt from the replicated log.
    """

    AGENCY_MALFORMED_TRANSACTION = 20030
    """
    Malformed agency transaction.
    """

    SUPERVISION_GENERAL_FAILURE = 20501
    """
    General supervision failure.
    """

    QUEUE_FULL = 21003
    """
    Will be returned if the scheduler queue is full.
    """

    QUEUE_TIME_REQUIREMENT_VIOLATED = 21004
    """
    Will be returned if a request with a queue time requirement is set and it cannot be fulfilled.
    """

    ACTION_OPERATION_UNABORTABLE = 6002
    """
    This maintenance action cannot be stopped once it is started
    """

    ACTION_UNFINISHED = 6003
    """
    This maintenance action is still processing
    """

    HOT_BACKUP_INTERNAL = 7001
    """
    Failed to create hot backup set
    """

    HOT_RESTORE_INTERNAL = 7002
    """
    Failed to restore to hot backup set
    """

    BACKUP_TOPOLOGY = 7003
    """
    The hot backup set cannot be restored on non matching cluster topology
    """

    NO_SPACE_LEFT_ON_DEVICE = 7004
    """
    No space left on device
    """

    FAILED_TO_UPLOAD_BACKUP = 7005
    """
    Failed to upload hot backup set to remote target
    """

    FAILED_TO_DOWNLOAD_BACKUP = 7006
    """
    Failed to download hot backup set from remote source
    """

    NO_SUCH_HOT_BACKUP = 7007
    """
    Cannot find a hot backup set with this Id
    """

    REMOTE_REPOSITORY_CONFIG_BAD = 7008
    """
    The configuration given for upload or download operation to/from remote hot backup repositories is wrong.
    """

    LOCAL_LOCK_FAILED = 7009
    """
    Some of the DB-Servers cannot be reached for transaction locks.
    """

    LOCAL_LOCK_RETRY = 7010
    """
    Some of the DB-Servers cannot be reached for transaction locks.
    """

    HOT_BACKUP_CONFLICT = 7011
    """
    Conflict of multiple hot backup processes.
    """

    HOT_BACKUP_DBSERVERS_AWOL = 7012
    """
    One or more DB-Servers could not be reached for hot backup inquiry
    """

    CLUSTER_COULD_NOT_MODIFY_ANALYZERS_IN_PLAN = 7021
    """
    Plan could not be modified while creating or deleting Analyzers revision
    """

    AIR_EXECUTION_ERROR = 8001
    """
    During the execution of an AIR program an error occurred
    """

    LICENSE_EXPIRED_OR_INVALID = 9001
    """
    The license has expired or is invalid.
    """

    LICENSE_SIGNATURE_VERIFICATION = 9002
    """
    Verification of license failed.
    """

    LICENSE_NON_MATCHING_ID = 9003
    """
    The ID of the license does not match the ID of this instance.
    """

    LICENSE_FEATURE_NOT_ENABLED = 9004
    """
    The installed license does not cover this feature.
    """

    LICENSE_RESOURCE_EXHAUSTED = 9005
    """
    The installed license does not cover a higher number of this resource.
    """

    LICENSE_INVALID = 9006
    """
    The license does not hold features of an ArangoDB license.
    """

    LICENSE_CONFLICT = 9007
    """
    The license has one or more inferior features.
    """

    LICENSE_VALIDATION_FAILED = 9008
    """
    Could not verify the license’s signature.
    """
