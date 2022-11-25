from __future__ import annotations

from typing import Optional, List, Union

from pydantic import BaseModel

from aioarango.enums import CollectionStatus, CollectionType
from aioarango.typings import Json
from .computed_value import ComputedValue
from .key_options import KeyOptions


class ArangoCollection(BaseModel):
    id: str
    name: str
    status: CollectionStatus
    type: CollectionType
    is_system: bool
    globally_unique_id: str

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
            is_smart=obj.get("isSmartChild", None),
            smart_graph_attribute=obj.get("smartGraphAttribute", None),
            smart_join_attribute=obj.get("smartJoinAttribute", None),
            uses_revisions_as_document_ids=obj.get("usesRevisionsAsDocumentIds", None),
            sync_by_revision=obj.get("syncByRevision", None),
            internal_validator_type=obj.get("internalValidatorType", None),
        )
