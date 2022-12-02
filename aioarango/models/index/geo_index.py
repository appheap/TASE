from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class GeoIndex(BaseArangoIndex):
    """
    Geo-Spatial Index

    Attributes
    ----------
    type : IndexType
        Type of the index. must be equal to "geo".
    name : str
        An easy-to-remember name for the index to look it up or refer to it in index hints.
        Index names are subject to the same character restrictions as collection names.
        If omitted, a name is auto-generated so that it is unique with respect to the collection, e.g. idx_832910498.
    fields : list of str
        An array with one or two attribute paths.
        If it is an array with one attribute path location, then a geo-spatial
        index on all documents is created using location as path to the
        coordinates. The value of the attribute must be an array with at least two
        double values. The array must contain the latitude (first value) and the
        longitude (second value). All documents, which do not have the attribute
        path or with value that are not suitable, are ignored.
        If it is an array with two attribute paths latitude and longitude,
        then a geo-spatial index on all documents is created using latitude
        and longitude as paths the latitude and the longitude. The value of
        the attribute latitude and of the attribute longitude must a
        double. All documents, which do not have the attribute paths or which
        values are not suitable, are ignored.
    ordered : bool, optional
        If a geo-spatial index on a location is constructed
        and geoJson is `true`, then the order within the array is longitude
        followed by latitude. This corresponds to the format described in http://geojson.org/geojson-spec.html#positions .
    in_background : bool, optional
        The optional attribute `inBackground` can be set to `true` to create the index
        in the background, which will not write-lock the underlying collection for
        as long as if the index is built in the foreground. The default value is `false`.

    """

    type = IndexType.GEO

    in_background: Optional[bool]
    ordered: Optional[bool]
    legacy_polygons: Optional[bool]
    worst_indexed_level: Optional[int]
    best_indexed_level: Optional[int]

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
        index.ordered = obj.get("geo_json", None)
        return index
