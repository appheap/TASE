from numbers import Number
from typing import Optional, MutableMapping, Sequence, List, Union

from aioarango.api_methods import AQLMethods
from aioarango.connection import Connection
from aioarango.executor import API_Executor
from aioarango.typings import Result, Json, Jsons
from .cursor import Cursor
from ..errors import ArangoServerError, ErrorType
from ..models import AQLQuery, QueryOptimizerRule, AQLTrackingData


class AQL:
    """
    AQL (ArangoDB Query Language) API wrapper.
    """

    __slots__ = [
        "_connection",
        "_executor",
        "_api",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
    ):
        self._connection: Connection = connection
        self._executor: API_Executor = executor

        self._api: AQLMethods = AQLMethods(connection, executor)

    def __repr__(self) -> str:
        return f"<AQL in {self._connection.db_name}>"

    async def execute(
        self,
        query: str,
        count: Optional[bool] = False,
        batch_size: Optional[int] = None,
        ttl: Optional[int] = None,
        cache: Optional[bool] = None,
        memory_limit: int = 0,
        bind_vars: Optional[MutableMapping[str, str]] = None,
        full_count: Optional[bool] = None,
        fill_block_cache: Optional[bool] = None,
        max_plans: Optional[int] = None,
        max_nodes_per_call_stack: Optional[int] = None,
        max_warning_count: Optional[int] = None,
        fail_on_warning: Optional[bool] = None,
        stream: Optional[bool] = None,
        optimizer_rules: Optional[Sequence[str]] = None,
        profile: Optional[bool] = None,
        satellite_sync_wait: Optional[int] = None,
        max_runtime: Optional[Number] = None,
        max_transaction_size: Optional[int] = None,
        intermediate_commit_size: Optional[int] = None,
        intermediate_commit_count: Optional[int] = None,
        skip_inaccessible_cols: Optional[bool] = None,
        allow_dirty_read: bool = False,
    ) -> Result[Cursor]:
        """
        Execute the query and return the result cursor.

        Notes
        -----
        - The query details include the query string plus optional query options and
          bind parameters. These values need to be passed in a JSON representation in
          the body of the POST request.

        - **stream** parameter remarks:

            - The query will hold resources until it ends (such as RocksDB snapshots, which
              prevents compaction to some degree). Writes will be in memory until the query
              is committed.
            - If existing documents are modified, then write locks are held on these
              documents and other queries trying to modify the same documents will fail
              because of this conflict.
            - A streaming query may fail late because of a conflict or for other reasons
              after some batches were already returned successfully, possibly rendering the
              results up to that point meaningless.
            - The query options **cache**, **count** and **full_count** are not supported for streaming queries.
            - Query statistics, profiling data and warnings are delivered as part of the last batch.
              If the **stream** option is `false` (`default`), then the complete result of the
              query is calculated before any of it is returned to the client. The server
              stores the full result in memory (on the contacted Coordinator if in a cluster).
              All other resources are freed immediately (locks, RocksDB snapshots). The query
              will fail before it returns results in case of a conflict.

        Parameters
        ----------
        query : str
            Query to execute.
        count : bool, default : False
             Indicates whether the number of documents in the result set should be returned in the **count** attribute of the result.
             If set to `True`, the total document count is included in the result cursor.
        batch_size : int, optional
            Maximum number of result documents to be transferred from
            the server to the client in one roundtrip. If this attribute is
            not set, a server-controlled default value will be used. A **batch_size** value of
            `0` is disallowed.
        ttl : int, optional
            The time-to-live for the cursor (in seconds). If the result set is small enough
            (less than or equal to **batch_size**) then results are returned right away.
            Otherwise, they are stored in memory and will be accessible via the cursor with
            respect to the ttl. The cursor will be removed on the server automatically
            after the specified amount of time. This is useful to ensure garbage collection
            of cursors that are not fully fetched by clients. If not set, a server-defined
            value will be used (default: `30` seconds).
        cache : bool, optional
            Flag to determine whether the AQL query results cache
            shall be used. If set to `false`, then any query cache lookup will be skipped
            for the query. If set to `true`, it will lead to the query cache being checked
            for the query if the "query cache mode" is either `on` or `demand`.
        memory_limit : int, default : 0
            The maximum number of memory (measured in bytes) that the query is allowed to
            use. If set, then the query will fail with error "resource limit exceeded" in
            case it allocates too much memory. A value of `0` indicates that there is no
            memory limit.
        bind_vars : dict, optional
            Key/value pairs representing the bind parameters.
        full_count : bool, optional
            if set to `true` and the query contains a **LIMIT** clause, then the
            result will have an extra attribute with the sub-attributes stats
            and **full_count**, `{ ... , "extra": { "stats": { "fullCount": 123 } } }`.
            The **full_count** attribute will contain the number of documents in the result before the
            last top-level **LIMIT** in the query was applied. It can be used to count the number of
            documents that match certain filter criteria, but only return a subset of them, in one go.
            It is thus similar to `MySQL's SQL_CALC_FOUND_ROWS` hint.

            Note that setting the option will disable a few **LIMIT** optimizations and may lead to more documents being processed,
            and thus make queries run longer. Note that the **full_count** attribute may only
            be present in the result if the query has a top-level LIMIT clause and the LIMIT
            clause is actually used in the query.
        fill_block_cache : bool, optional
            if set to `true` or `not specified`, this will make the query store the data it
            reads via the RocksDB storage engine in the RocksDB block cache. This is usually
            the desired behavior. The option can be set to `false` for queries that are
            known to either read a lot of data which would thrash the block cache, or for queries
            that read data which are known to be outside the hot set. By setting the option
            to `false`, data read by the query will not make it into the RocksDB block cache if
            not already in there, thus leaving more room for the actual hot set.
        max_plans : int, optional
             Limits the maximum number of plans that are created by the AQL query optimizer.
        max_nodes_per_call_stack : int, optional
            The number of execution nodes in the query plan after that stack splitting is
            performed to avoid a potential stack overflow. Defaults to the configured value
            of the startup option `--query.max-nodes-per-callstack`.
            This option is only useful for testing and debugging and normally does not need
            any adjustment.
        max_warning_count : int, optional
            Limits the maximum number of warnings a query will return. The number of warnings
            a query will return is limited to `10` by default, but that number can be increased
            or decreased by setting this attribute.
        fail_on_warning : bool, optional
            When set to `true`, the query will throw an exception and abort instead of producing
            a warning. This option should be used during development to catch potential issues
            early. When the attribute is set to `false`, warnings will not be propagated to
            exceptions and will be returned with the query result.
            There is also a server configuration option `--query.fail-on-warning `for setting the
            default value for **fail_on_warning** so it does not need to be set on a per-query level.
        stream : bool, optional
            Can be enabled to execute the query lazily. If set to `true`, then the query is
            executed as long as necessary to produce up to **batch_size** results. These
            results are returned immediately and the query is suspended until the client
            asks for the next batch (if there are more results). Depending on the query
            this can mean that the first results will be available much faster and that
            less memory is needed because the server only needs to store a subset of
            results at a time. Read-only queries can benefit the most, unless `SORT`
            without `index` or `COLLECT` are involved that make it necessary to process all
            documents before a partial result can be returned. It is advisable to only use
            this option for "queries without exclusive locks".
        optimizer_rules : list of str
            A list of `to-be-included` or `to-be-excluded` optimizer rules can be put into this
            attribute, telling the optimizer to include or exclude specific rules. To disable
            a rule, prefix its name with a `-`, to enable a rule, prefix it with a `+`. There is
            also a pseudo-rule `all`, which matches all optimizer rules. `-all` disables all rules.
        profile : bool, optional
            If set to `true` or `1`, then the additional query profiling information will be returned
            in the sub-attribute **profile** of the **extra** return attribute, if the query result
            is not served from the query cache. Set to `2` the query will include execution stats
            per query plan node in sub-attribute **stats.nodes** of the **extra** return attribute.
            Additionally, the query plan is returned in the sub-attribute **extra.plan**.
        satellite_sync_wait : bool, optional
            This "Enterprise Edition" parameter allows to configure how long a DB-Server will have time
            to bring the `SatelliteCollections` involved in the query into sync.
            The default value is `60.0` (seconds). When the max time has been reached the query
            will be stopped.
        max_runtime : int, optional
            The query has to be executed within the given runtime, or it will be killed.
            The value is specified in seconds. The default value is `0.0` (no timeout).
        max_transaction_size : int, optional
            Transaction size limit in bytes.
        intermediate_commit_size : int, optional
            Maximum total size of operations after which an intermediate commit is performed automatically.
        intermediate_commit_count : int, optional
            Maximum number of operations after which an intermediate commit is performed automatically.
        skip_inaccessible_cols : bool, optional
            AQL queries (especially graph traversals) will treat collection to which a user has no access rights as if these collections were empty.
            Instead of returning a forbidden access error, your queries will execute normally. This is intended to help with certain use-cases: A graph contains several collections and different users execute AQL queries on that graph.
            You can now naturally limit the accessible results by changing the access rights of users on collections.
            This feature is only available in the "Enterprise Edition".
        allow_dirty_read : bool, default : False
            Allow reads from followers in a cluster.

        Returns
        -------
        Result
            A `Cursor` API wrapper object is returned if the operation was successful.

        Raises
        ------
        ValueError
            If `query` or `batch_size` have invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        cursor_body = await self._api.create_cursor(
            query=query,
            count=count,
            batch_size=batch_size,
            ttl=ttl,
            cache=cache,
            memory_limit=memory_limit,
            bind_vars=bind_vars,
            full_count=full_count,
            fill_block_cache=fill_block_cache,
            max_plans=max_plans,
            max_nodes_per_call_stack=max_nodes_per_call_stack,
            max_warning_count=max_warning_count,
            fail_on_warning=fail_on_warning,
            stream=stream,
            optimizer_rules=optimizer_rules,
            profile=profile,
            satellite_sync_wait=satellite_sync_wait,
            max_runtime=max_runtime,
            max_transaction_size=max_transaction_size,
            intermediate_commit_size=intermediate_commit_size,
            intermediate_commit_count=intermediate_commit_count,
            skip_inaccessible_cols=skip_inaccessible_cols,
            allow_dirty_read=allow_dirty_read,
        )

        return Cursor(
            self._connection,
            self._executor,
            cursor_body,
        )

    async def validate(
        self,
        query: str,
    ) -> Result[Json]:
        """
        Parse and validate the query without executing it.

        Parameters
        ----------
        query : str
            Query to validate.

        Returns
        -------
        Json
            Query details.

        Raises
        ------
        ValueError
            If query has invalid value.
        aioarango.errors.ArangoServerError
            If validation fails.
        """
        return await self._api.parse_aql_query(query)

    async def kill(
        self,
        query_id: str,
        kill_in_all_databases: Optional[bool] = None,
        ignore_missing: Optional[bool] = True,
    ) -> Result[bool]:
        """
        Kill a running query.

        Parameters
        ----------
        query_id : str
            ID of the query to kill.
        kill_in_all_databases : bool, optional
            If set to `true`, will attempt to kill the specified query in all databases, not just the selected one.
            Using the parameter is only allowed in the `system` database and with `superuser` privileges.
        ignore_missing : bool, default : True
            Whether to not throw errors in case the query does not exist.


        Returns
        -------
        bool
            `True` if the kill request was sent successfully. `False` if the query was not found and the `ignore_missing` parameter was set to `True`.

        Raises
        ------
        ValueError
            If `query_id` has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        try:
            response = await self._api.kill_running_aql_query(
                query_id=query_id,
                kill_in_all_databases=kill_in_all_databases,
            )
        except ArangoServerError as e:
            if e.response.status_code == 404 and ignore_missing:
                return False

            raise e
        else:
            return response

    async def slow_queries(
        self,
        get_from_all_databases: Optional[bool] = None,
    ) -> Result[List[AQLQuery]]:
        """
        Return a list of all slow AQL queries.


        Parameters
        ----------
        get_from_all_databases : bool, optional
            If set to `true`, will return the slow queries from all databases, not just the selected one.
            Using the parameter is only allowed in the system database and with superuser privileges.


        Returns
        -------
        Result
            List of slow AQL queries.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._api.get_slow_aql_queries(get_from_all_databases=get_from_all_databases)

    async def clear_slow_queries(
        self,
        clear_from_all_databases: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Clear the list of slow AQL queries in the currently selected database

        Parameters
        ----------
        clear_from_all_databases : bool, optional
            If set to `true`, will clear the slow query history in all databases, not just the selected one.
            Using the parameter is only allowed in the `system` database and with `superuser` privileges.

        Returns
        -------
        Result
            True if slow queries were cleared successfully.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._api.clear_slow_aql_queries(clear_from_all_databases=clear_from_all_databases)

    async def queries(
        self,
        get_from_all_databases: Optional[bool] = None,
    ) -> Result[List[AQLQuery]]:
        """
        Return the currently running AQL queries.


        Parameters
        ----------
        get_from_all_databases : bool, optional
            If set to `true`, will return the slow queries from all databases, not just the selected one.
            Using the parameter is only allowed in the system database and with superuser privileges.


        Returns
        -------
        Result
            Running AQL queries.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._api.get_running_aql_queries(get_from_all_databases=get_from_all_databases)

    async def explain(
        self,
        query: str,
        all_plans: bool = False,
        max_plans: Optional[int] = None,
        opt_rules: Optional[Sequence[str]] = None,
        bind_vars: Optional[MutableMapping[str, str]] = None,
    ) -> Result[Union[Json, Jsons]]:
        """
        Explain an AQL query.

        Parameters
        ----------
        query : str
            Query to explain.
        all_plans : bool, default : False
            If set to `True`, all possible execution plans are
            returned in the result. If set to `False`, only the optimal plan
            is returned.
        max_plans : int, optional
            Total number of plans generated by the optimizer.
        opt_rules : list of str, optional
            List of optimizer rules.
        bind_vars : MutableMapping, optional
            Bind variables for the query.

        Returns
        -------
        Result
            Execution plan, or plans if **all_plans** was set to `True`.

        Raises
        ------
        ValueError
            If the query has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._api.explain(
            query=query,
            all_plans=all_plans,
            max_plans=max_plans,
            opt_rules=opt_rules,
            bind_vars=bind_vars,
        )

    async def functions(
        self,
        namespace: Optional[str] = None,
    ) -> Result[Jsons]:
        """
        List the AQL functions defined in the database.

        # todo: result parsing of this endpoint should be investigated in more detail.


        Parameters
        ----------
        namespace : str, optional
            Returns all registered AQL user functions from namespace `namespace` under `result`.


        Returns
        -------
        Result
            AQL functions.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._api.get_user_registered_aql_functions(namespace=namespace)

    async def create_function(
        self,
        name: str,
        code: str,
        is_deterministic: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Create User AQL function.

        Parameters
        ----------
        name : str
            Name of the AQL function.
        code : str
            Function definition in Javascript.
        is_deterministic : bool, optional
            An optional `boolean` value to indicate whether the function
            results are fully deterministic (function return value solely depends on
            the input value and return value is the same for repeated calls with same
            input). The isDeterministic attribute is currently not used but may be
            used later for optimizations.

        Returns
        -------
        Result
           Whether the AQL function was newly created or an existing one was replaced.

        Raises
        ------
        ValueError
            If `name` or `code` parameters have invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._api.create_user_aql_function(
            name=name,
            code=code,
            is_deterministic=is_deterministic,
        )

    async def delete_function(
        self,
        name: str,
        group: Optional[bool] = None,
        ignore_missing: Optional[bool] = True,
    ) -> Result[int]:
        """
        Delete an AQL function.

        Parameters
        ----------
        name : str
            AQL function name.
        group : bool, optional
            If set to `True`, value of parameter **name** is treated
            as a namespace prefix, and all functions in the namespace are
            deleted. If set to `False`, the value of **name** must be a fully
            qualified function name including any namespaces.
        ignore_missing : bool, default : True
            Do not raise an exception on missing function.

        Returns
        -------
        Result
            Number of AQL functions deleted if operation was successful,
            `0` if function(s) was not found and **ignore_missing** was set
            to `True`.

        Raises
        ------
        ValueError
            If `name` has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        try:
            response = await self._api.delete_user_aql_function(name=name, group=group)
        except ArangoServerError as e:
            if e.arango_error == ErrorType.QUERY_FUNCTION_NOT_FOUND and ignore_missing:
                return 0

            raise e
        else:
            return response

    async def query_rules(self) -> Result[List[QueryOptimizerRule]]:
        """
        Return the available optimizer rules for AQL queries


        Returns
        -------
        Result
            The available optimizer rules for AQL queries

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        return await self._api.get_all_aql_query_optimizer_rules()

    async def tracking(self) -> Result[AQLTrackingData]:
        """
        Return the current query tracking configuration

        Returns
        -------
        AQLTrackingData
            An `AQLTrackingData` object is returned on success.


        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._api.get_aql_query_tracking_properties()

    async def set_tracking(
        self,
        enabled: Optional[bool] = None,
        max_slow_queries: Optional[int] = None,
        slow_query_threshold: Optional[int] = None,
        max_query_string_length: Optional[int] = None,
        track_bind_vars: Optional[bool] = None,
        track_slow_queries: Optional[bool] = None,
    ) -> Result[AQLTrackingData]:
        """
        Configure AQL query tracking properties


        Parameters
        ----------
        enabled : bool, optional
            Track queries if set to True.
        max_slow_queries : int, optional
            Max number of slow queries to track. Oldest entries are discarded first.
        slow_query_threshold : int, optional
            Runtime threshold (in seconds) for treating a query as slow.
        max_query_string_length : int, optional
            Max query string length (in bytes) tracked.
        track_bind_vars : bool, optional
            If set to `True`, track bind variables used in queries.
        track_slow_queries : bool, optional
            If set to `True`, track slow queries whose runtimes
            exceed **slow_query_threshold**. To use this, parameter **enabled** must
            be set to `True`.

        Returns
        -------
        AQLTrackingData
            An `AQLTrackingData` object is returned on success.


        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        return await self._api.change_aql_query_tracking_properties(
            enabled=enabled,
            max_slow_queries=max_slow_queries,
            slow_query_threshold=slow_query_threshold,
            max_query_string_length=max_query_string_length,
            track_bind_vars=track_bind_vars,
            track_slow_queries=track_slow_queries,
        )
