from __future__ import annotations

from typing import List, Any, Dict, Optional

from pydantic import BaseModel, Field

from aioarango.enums import IndexType
from .index_figures import IndexFigures


class BaseArangoIndex(BaseModel):
    id: Optional[str]
    version: int = Field(default=1)
    type: IndexType
    name: str
    fields: List[str]
    selectivity: Optional[float]
    figures: Optional[IndexFigures]
    is_newly_created: Optional[bool]

    def to_db(self) -> Dict[str, Any]:
        if self.type is None or self.type == IndexType.UNKNOWN:
            raise ValueError("Invalid value for `type`")

        if self.name is None or not len(self.name):
            raise ValueError("Invalid value for `name`")

        if self.fields is None or not len(self.fields):
            raise ValueError("Invalid value for `fields`")

        data = {
            "type": self.type.value,
            "name": f"{self.name}__{self.version}",
            "fields": self.fields,
        }

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[BaseArangoIndex]:
        """
        Parse the object from a dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary to parse the object from.

        Returns
        -------
        BaseArangoIndex, optional
            Parse index if parsing was successful.

        Raises
        ------
        ValueError
            If the `type` attribute of the dictionary in invalid.

        """
        if obj is None or not len(obj):
            return None

        if "type" in obj:
            try:
                index_type = IndexType(obj["type"])
            except Exception:
                print(obj)
                raise ValueError("Invalid value for `type`")
            else:
                from aioarango.models.index import EdgeIndex
                from aioarango.models.index import FullTextIndex
                from aioarango.models.index import GeoIndex
                from aioarango.models.index import HashIndex
                from aioarango.models.index import InvertedIndex
                from aioarango.models.index import PersistentIndex
                from aioarango.models.index import PrimaryIndex
                from aioarango.models.index import SkipListIndex
                from aioarango.models.index import TTLIndex
                from aioarango.models.index import MultiDimensionalIndex

                if "figures" in obj:
                    obj["figures"] = IndexFigures.parse_from_dict(obj.pop("figures"))

                if "selectivityEstimate" in obj:
                    obj["selectivity"] = obj.pop("selectivityEstimate")

                if "cacheEnabled" in obj:
                    obj["cache_enabled"] = obj.pop("cacheEnabled")

                if "storedValues" in obj:
                    obj["stored_values"] = obj.pop("storedValues")

                if "inBackground" in obj:
                    obj["in_background"] = obj.pop("inBackground")

                if "minLength" in obj:
                    obj["min_length"] = obj.pop("minLength")

                if "legacyPolygons" in obj:
                    obj["legacy_polygons"] = obj.pop("legacyPolygons")

                if "primarySort" in obj:
                    obj["primary_sort"] = obj.pop("primarySort")

                if "includeAllFields" in obj:
                    obj["include_all_fields"] = obj.pop("includeAllFields")

                if "trackListPositions" in obj:
                    obj["track_list_positions"] = obj.pop("trackListPositions")

                if "searchField" in obj:
                    obj["search_field"] = obj.pop("searchField")

                if "cleanupIntervalStep" in obj:
                    obj["cleanup_interval_step"] = obj.pop("cleanupIntervalStep")

                if "commitIntervalMsec" in obj:
                    obj["commit_interval_msec"] = obj.pop("commitIntervalMsec")

                if "consolidationIntervalMsec" in obj:
                    obj["consolidation_interval_msec"] = obj.pop("consolidationIntervalMsec")

                if "writebufferIdle" in obj:
                    obj["write_buffer_idle"] = obj.pop("writebufferIdle")

                if "writebufferActive" in obj:
                    obj["write_buffer_active"] = obj.pop("writebufferActive")

                if "writebufferSizeMax" in obj:
                    obj["write_buffer_size_max"] = obj.pop("writebufferSizeMax")

                if "consolidationPolicy" in obj:
                    obj["consolidation_policy"] = obj.pop("consolidationPolicy")

                if "fieldValueTypes" in obj:
                    obj["field_value_type"] = obj.pop("fieldValueTypes")

                if "expireAfter" in obj:
                    obj["expiry_time"] = obj.pop("expireAfter")

                if "isNewlyCreated" in obj:
                    obj["is_newly_created"] = obj.pop("isNewlyCreated")

                if "worstIndexedLevel" in obj:
                    obj["worst_indexed_level"] = obj.pop("worstIndexedLevel")

                if "maxNumCoverCells" in obj:
                    obj["max_num_cover_cells"] = obj.pop("maxNumCoverCells")

                if "geoJson" in obj:
                    obj["geo_json"] = obj.pop("geoJson")

                if index_type == IndexType.EDGE:
                    index = EdgeIndex.from_db(obj)
                elif index_type == IndexType.FULL_TEXT:
                    index = FullTextIndex.from_db(obj)
                elif index_type == IndexType.GEO:
                    index = GeoIndex.from_db(obj)
                elif index_type == IndexType.HASH:
                    index = HashIndex.from_db(obj)
                elif index_type == IndexType.INVERTED:
                    index = InvertedIndex.from_db(obj)
                elif index_type == IndexType.MULTI_DIMENSIONAL:
                    index = MultiDimensionalIndex.from_db(obj)
                elif index_type == IndexType.PERSISTENT:
                    index = PersistentIndex.from_db(obj)
                elif index_type == IndexType.PRIMARY:
                    index = PrimaryIndex.from_db(obj)
                elif index_type == IndexType.SKIPLIST:
                    index = SkipListIndex.from_db(obj)
                elif index_type == IndexType.TTL:
                    index = TTLIndex.from_db(obj)
                else:
                    raise ValueError("Invalid value for `type`")

                if "__" in index.name:
                    name, version = index.name.split("__")
                    index.name = name
                    index.version = int(version)

                return index

        else:
            raise ValueError("Invalid value for `type`")
