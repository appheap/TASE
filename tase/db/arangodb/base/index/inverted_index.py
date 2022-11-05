from __future__ import annotations

from typing import Optional, Any, Dict, List

from pydantic import BaseModel

from .base_arango_index import BaseArangoIndex
from ...enums import ArangoIndexType


class ConsolidationPolicy(BaseModel):
    type: Optional[str]
    segmentsBytesFloor: Optional[int]
    segmentsBytesMax: Optional[int]
    segmentsMax: Optional[int]
    segmentsMin: Optional[int]
    minScore: Optional[int]


class InvertedIndex(BaseArangoIndex):
    type = ArangoIndexType.INVERTED

    in_background: Optional[bool]
    parallelism: Optional[int]
    primary_sort: Optional[Dict[str, Any]]
    stored_values: Optional[List[Dict[str, Any]]]
    analyzer: Optional[str]
    features: Optional[List[str]]
    include_all_fields: Optional[bool]
    track_list_positions: Optional[bool]
    search_field: Optional[bool]
    cleanup_interval_step: Optional[int]
    commit_interval_msec: Optional[int]
    consolidation_interval_msec: Optional[int]
    consolidation_policy: Optional[ConsolidationPolicy]
    write_buffer_idle: Optional[int]
    write_buffer_active: Optional[int]
    write_buffer_size_max: Optional[int]

    def to_db(self) -> Dict[str, Any]:
        data = super(InvertedIndex, self).to_db()

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        if self.parallelism is not None:
            data["parallelism"] = self.parallelism

        if self.primary_sort is not None:
            data["PrimarySort"] = self.primary_sort

        if self.stored_values is not None:
            data["storedValues"] = self.stored_values

        if self.analyzer is not None:
            data["analyzer"] = self.analyzer

        if self.include_all_fields is not None:
            data["includeAllFields"] = self.include_all_fields

        if self.track_list_positions is not None:
            data["trackListPositions"] = self.track_list_positions

        if self.search_field is not None:
            data["searchField"] = self.search_field

        if self.cleanup_interval_step is not None:
            data["cleanupIntervalStep"] = self.cleanup_interval_step

        if self.commit_interval_msec is not None:
            data["commitIntervalMsec"] = self.commit_interval_msec

        if self.consolidation_interval_msec is not None:
            data["consolidationIntervalMsec"] = self.consolidation_interval_msec

        if self.consolidation_policy is not None:
            data["consolidationPolicy"] = self.consolidation_policy.dict()

        if self.write_buffer_idle is not None:
            data["writebufferIdle"] = self.write_buffer_idle

        if self.write_buffer_active is not None:
            data["writebufferActive"] = self.write_buffer_active

        if self.write_buffer_size_max is not None:
            data["writebufferSizeMax"] = self.write_buffer_size_max

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[InvertedIndex]:
        index = InvertedIndex(**obj)

        index.in_background = obj.get("inBackground", None)
        index.primary_sort = obj.get("primarySort", None)
        index.stored_values = obj.get("storedValues", None)
        index.include_all_fields = obj.get("includeAllFields", None)
        index.track_list_positions = obj.get("trackListPositions", None)
        index.search_field = obj.get("searchField", None)
        index.cleanup_interval_step = obj.get("cleanupIntervalStep", None)
        index.commit_interval_msec = obj.get("commitIntervalMsec", None)
        index.consolidation_interval_msec = obj.get("consolidationIntervalMsec", None)

        if obj.get("consolidationPolicy", None):
            index.consolidation_policy = ConsolidationPolicy(**obj.get("consolidationPolicy"))

        index.write_buffer_idle = obj.get("writebufferIdle", None)
        index.write_buffer_active = obj.get("writebufferActive", None)
        index.write_buffer_size_max = obj.get("writebufferSizeMax", None)

        return index
