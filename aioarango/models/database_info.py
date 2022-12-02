from typing import Union, Optional

from pydantic import BaseModel

from aioarango.enums import ShardingMethod


class DatabaseInfo(BaseModel):
    """
    Basic Database information.

    Attributes
    ----------
    id : str
        ID of the current database.
    name : str
        Name of the current database
    path : str
        Filesystem path of the current database
    isSystem : bool
        Whether the current database is the _system database or not.
    sharding : ShardingMethod, optional
        Default sharding method for collections created in this database.
    replicationFactor : int or str, optional
        Default replication factor for collections in this database.
    writeConcern : int, optional
        Default write concern for collections in this database.
    """

    id: str
    name: str
    path: str
    isSystem: bool
    sharding: Optional[ShardingMethod]
    replicationFactor: Union[int, str, None]
    writeConcern: Optional[int]
