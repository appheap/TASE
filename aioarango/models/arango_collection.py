from __future__ import annotations

from typing import Optional, List, Union

from pydantic import BaseModel

from aioarango.enums import CollectionStatus, CollectionType
from aioarango.typings import Json
from .computed_value import ComputedValue
from .key_options import KeyOptions


class ArangoCollection(BaseModel):
    """
    Defines a ArangoDB collection.

    Attributes
    ----------
    id : str
        unique identifier of the collection; **deprecated**
    name : str
        Literal name of this collection.
    status : CollectionStatus
        Status of the collection.
    type : CollectionType
        Type of the collection
    is_system : bool
        `True` if this is a system collection; usually name will start with an `underscore`.
    globally_unique_id : str
        Unique identifier of the collection.
    wait_for_sync: bool, optional
        If true then creating, changing or removing documents will wait until the data has been synchronized to disk.
    collection_schema : Json, optional
        The collection level schema for documents.
    computed_values : list of ComputedValue, optional
        A list of objects, each representing a computed value.
    key_options : KeyOptions, optional
        Key options object defining the type of the key used in the collection.
    is_cache_enabled : bool, optional
        Whether the in-memory hash cache for documents is enabled for this collection.
    number_of_shards : int, optional
        The number of shards of the collection. (cluster only)
    shard_keys : list of str, optional
        contains the names of document attributes that are used to determine the target shard for documents. (cluster only)
    replication_factor : int or str, optional
        contains how many copies of each shard are kept on different DB-Servers.
        It is an integer number in the range of 1-10 or the string "satellite"
    write_concern : int, optional
        determines how many copies of each shard are required to be
        in sync on the different DB-Servers. If there are less then these many copies
        in the cluster a shard will refuse to write. Writes to shards with enough
        up-to-date copies will succeed at the same time. however, The value of
        `writeConcern` cannot be larger than `replicationFactor`. (cluster only)
    sharding_strategy : ShardingStrategy, optional
        Sharding strategy selected for the collection. One of 'hash' or 'enterprise-hash-smart-edge'. (cluster only)
    is_smart : bool, optional
        Whether the collection is used in a SmartGraph (Enterprise Edition only). (cluster only)
    is_smart_child : bool, optional
        # fixme
    smart_graph_attribute : str, optional
        Attribute that is used in SmartGraphs (Enterprise Edition only). (cluster only)
    smart_join_attribute : str, optional
        Determines an attribute of the collection that must contain the shard key value
        of the referred-to SmartJoin collection (Enterprise Edition only). (cluster only)
    uses_revisions_as_document_ids : bool, optional
        # fixme
    sync_by_revision : bool, optional
        # fixme
    internal_validator_type : int, optional
        # fixme
    """

    id: str
    name: str
    status: CollectionStatus
    type: CollectionType
    is_system: bool
    globally_unique_id: str
    # the above attributes form the minimum version of this object.

    # these attributes are get from checksum endpoint
    checksum: Optional[str]
    revision: Optional[str]

    wait_for_sync: Optional[bool]
    collection_schema: Optional[Json]
    computed_values: Optional[List[ComputedValue]]
    key_options: Optional[KeyOptions]
    is_cache_enabled: Optional[bool]
    number_of_shards: Optional[int]
    shard_keys: Optional[List[str]]
    replication_factor: Union[int, str, None]
    write_concern: Optional[int]
    sharding_strategy: Optional[str]
    is_smart: Optional[bool]
    is_smart_child: Optional[bool]
    smart_graph_attribute: Optional[str]
    smart_join_attribute: Optional[str]

    uses_revisions_as_document_ids: Optional[bool]
    sync_by_revision: Optional[bool]
    internal_validator_type: Optional[int]

    @classmethod
    def parse_from_dict(cls, obj: dict) -> Optional[ArangoCollection]:
        if obj is None or not len(obj):
            return None

        computed_values = None
        if obj.get("computedValues", None):
            computed_values = [ComputedValue.parse_from_dict(item) for item in obj["computedValues"]]

        return ArangoCollection(
            id=obj["id"],
            name=obj["name"],
            status=obj["status"],
            type=obj["type"],
            is_system=obj["isSystem"],
            globally_unique_id=obj["globallyUniqueId"],
            checksum=obj.get("checksum", None),
            revision=obj.get("revision", None),
            wait_for_sync=obj.get("waitForSync", None),
            collection_schema=obj.get("schema", None),
            computed_values=computed_values,
            key_options=KeyOptions.parse_from_dict(obj.get("keyOptions", None)),
            is_cache_enabled=obj.get("cacheEnabled", None),
            number_of_shards=obj.get("numberOfShards", None),
            shard_keys=obj.get("shardKeys", None),
            replication_factor=obj.get("replicationFactor", None),
            write_concern=obj.get("writeConcern", None),
            sharding_strategy=obj.get("shardingStrategy", None),
            is_smart=obj.get("isSmart", None),
            is_smart_child=obj.get("isSmartChild", None),
            smart_graph_attribute=obj.get("smartGraphAttribute", None),
            smart_join_attribute=obj.get("smartJoinAttribute", None),
            uses_revisions_as_document_ids=obj.get("usesRevisionsAsDocumentIds", None),
            sync_by_revision=obj.get("syncByRevision", None),
            internal_validator_type=obj.get("internalValidatorType", None),
        )
