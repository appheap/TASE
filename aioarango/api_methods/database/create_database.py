from typing import Optional, Sequence, Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType, ShardingMethod
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, User
from aioarango.typings import Json, Result


class CreateDatabase(Endpoint):
    error_codes = (
        ErrorType.ARANGO_USE_SYSTEM_DATABASE,
        ErrorType.ARANGO_DUPLICATE_NAME,
        ErrorType.ARANGO_DATABASE_NAME_INVALID,
    )
    status_codes = (
        201,
        # is returned if the database was created successfully.
        400,  # 1229
        # is returned if the request parameters are invalid or if a database with the specified name already exists.
        403,  # 1230
        # is returned if the request was not executed in the _system database.
        409,  # 1207
        # is returned if a database with the specified name already exists.
    )

    async def create_database(
        self,
        name: str,
        users: Optional[Sequence[User]] = None,
        replication_factor: Union[int, str, None] = None,
        write_concern: Optional[int] = None,
        sharding: Optional[ShardingMethod] = None,
    ) -> Result[bool]:
        """
        Create a new database.

        Notes
        -----
        - The response is a JSON object with the attribute **result** set to true.
        -  creating a new database is only possible from within the **_system** database.


        Parameters
        ----------
        name : str
            Database name.

        users : list of User
            List of users with access to the new database, where each
            user is a dictionary with fields "username", "password", "active"
            and "extra" (see below for example). If not set, only the admin and
            current user are granted access.

        replication_factor : int or str, optional
            Default replication factor for collections
            created in this database. Special values include "satellite" which
            replicates the collection to every DBServer, and 1 which disables
            replication. Used for clusters only.

        write_concern : int, optional
            Default write concern for collections created in
            this database. Determines how many copies of each shard are
            required to be in sync on different DBServers. If there are less
            than these many copies in the cluster a shard will refuse to write.
            Writes to shards with enough up-to-date copies will succeed at the
            same time, however. Value of this parameter can not be larger than
            the value of **replication_factor**. Used for clusters only.

        sharding : ShardingMethod, optional
            Sharding method used for new collections in this
            database. Allowed values are: "", "flexible" and "single". The
            first two are equivalent. Used for clusters only.

        Returns
        -------
        Result
            True if database was created successfully.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If insert fails.

        """
        data: Json = {"name": name}

        options: Json = {}
        if replication_factor is not None:
            options["replicationFactor"] = replication_factor
        if write_concern is not None:
            options["writeConcern"] = write_concern
        if sharding is not None:
            options["sharding"] = sharding
        if options:
            data["options"] = options

        if users is not None:
            data["users"] = [user.json() for user in users]

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/database",
            data=data,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 201
            return True

        return await self.execute(request, response_handler)
