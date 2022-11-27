from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class GeoIndex(BaseArangoIndex):
    type = IndexType.GEO

    in_background: Optional[bool]
    ordered: Optional[bool]
    legacy_polygons: Optional[bool]

    def to_db(
        self,
    ) -> Dict[str, Any,]:
        data = super(GeoIndex, self).to_db()

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        if self.ordered is not None:
            data["geoJson"] = self.ordered

        if self.legacy_polygons is not None:
            data["legacyPolygons"] = self.legacy_polygons

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[GeoIndex]:
        index = GeoIndex(**obj)
        index.ordered = obj.get("geoJson", None)
        return index
