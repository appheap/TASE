from numbers import Number
from typing import Optional, MutableMapping, Sequence

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Json


class CreateCursor(Endpoint):
    error_codes = (
        ErrorType.RESOURCE_LIMIT,
        ErrorType.ARANGO_ILLEGAL_NAME,
        ErrorType.QUERY_BIND_PARAMETER_MISSING,
        ErrorType.QUERY_ARRAY_EXPECTED,
    )
    status_codes = (
        201,
        # is returned if the result set can be created by the server.
        400,  # 1200, 1551, 1563
        # is returned if the JSON representation is malformed or the query specification is
        # missing from the request.
        # If the JSON representation is malformed or the query specification is
        # missing from the request, the server will respond with HTTP 400.
        # The body of the response will contain a JSON object with additional error
        # details.
        500,  # 32
    )

    async def create_cursor(
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
    ) -> Result[Json]:
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
            A `Json` object is returned if the operation was successful.

        Raises
        ------
        ValueError
            If `query` or `batch_size` have invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if query is None or not len(query):
            raise ValueError(f"`query` has invalid value: `{query}`")

        if batch_size is not None and batch_size == 0:
            raise ValueError(f"`batch_size` value cannot be `0`")

        data: Json = {"query": query, "count": count}
        if batch_size is not None:
            data["batchSize"] = batch_size
        if ttl is not None:
            data["ttl"] = ttl
        if cache is not None:
            data["cache"] = cache
        if memory_limit is not None:
            data["memoryLimit"] = memory_limit
        if bind_vars is not None:
            data["bindVars"] = bind_vars

        options: Json = {}
        if full_count is not None:
            options["fullCount"] = full_count
        if fill_block_cache is not None:
            options["fillBlockCache"] = fill_block_cache
        if max_plans is not None:
            options["maxNumberOfPlans"] = max_plans
        if max_nodes_per_call_stack is not None:
            options["maxNodesPerCallstack"] = max_nodes_per_call_stack
        if max_warning_count is not None:
            options["maxWarningCount"] = max_warning_count
        if fail_on_warning is not None:
            options["failOnWarning"] = fail_on_warning
        if stream is not None:
            options["stream"] = stream
        if optimizer_rules is not None:
            options["optimizer"] = {"rules": optimizer_rules}
        if profile is not None:
            options["profile"] = profile
        if satellite_sync_wait is not None:
            options["satelliteSyncWait"] = satellite_sync_wait
        if max_runtime is not None:
            options["maxRuntime"] = max_runtime
        if max_transaction_size is not None:
            options["maxTransactionSize"] = max_transaction_size
        if intermediate_commit_size is not None:
            options["intermediateCommitSize"] = intermediate_commit_size
        if intermediate_commit_count is not None:
            options["intermediateCommitCount"] = intermediate_commit_count
        if skip_inaccessible_cols is not None:
            options["skipInaccessibleCollections"] = skip_inaccessible_cols

        if options:
            data["options"] = options

        data.update(options)

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/cursor",
            data=data,
            headers={"x-arango-allow-dirty-read": "true"} if allow_dirty_read else None,
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body

        return await self.execute(request, response_handler)
