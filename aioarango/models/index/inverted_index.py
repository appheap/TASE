from __future__ import annotations

from typing import Optional, Any, Dict, List, Union

from pydantic import BaseModel

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType, CompressionType, SortType, InvertedIndexFeaturesType


class ConsolidationPolicy(BaseModel):
    """
    Attributes
    ----------
    type : str, optional
        The segment candidates for the "consolidation" operation are selected based
        upon several possible configurable formulas as defined by their types.

        The supported types are:
            - "tier" (default): consolidate based on segment byte size and live

    segmentsBytesFloor : int, optional
         Defines the value (in bytes) to treat all smaller segments as equal for
        consolidation selection. Default: `2097152`
    segmentsBytesMax : int, optional
        The maximum allowed size of all consolidated segments in bytes. Default: `5368709120`
    segmentsMax : int, optional
        The maximum number of segments that are evaluated as candidates for consolidation. Default: `10`
    segmentsMin : int, optional
        The minimum number of segments that are evaluated as candidates for consolidation. Default: `1`
    minScore : int, optional
        Filter out consolidation candidates with a score less than this. Default: `0`
    """

    type: Optional[str]
    segmentsBytesFloor: Optional[int]
    segmentsBytesMax: Optional[int]
    segmentsMax: Optional[int]
    segmentsMin: Optional[int]
    minScore: Optional[int]


class PrimarySortField(BaseModel):
    """
    Attributes
    ----------
    field : str
        An attribute path. The `.` character denotes sub-attributes.
    direction : SortType
        The sorting direction. Possible values are "asc" and "desc".
    """

    filed: str
    direction: SortType


class InvertedIndexPrimarySort(BaseModel):
    """
    Attributes
    ----------
    fields : list of PrimarySortField
        An array of the fields to sort the index by and the direction to sort each field in.
    compression : CompressionType
        Defines how to compress the primary sort data. Possible values are: "lz4" and "none".
    """

    fields: List[PrimarySortField]
    compression: CompressionType


class StoredValuesField(BaseModel):
    """
    Attributes
    ----------
    fields : list of str
        A list of attribute paths. The `.` character denotes sub-attributes.
    compression : CompressionType
        Defines how to compress the attribute values. Possible values are "lz4" and "none".
    """

    fields: List[str]
    compression: CompressionType


class InvertedIndexNestedAttribute(BaseModel):
    """
     Index the specified sub-objects that are stored in an array. Other than with the `fields` property,

     Attributes
     ----------
     name : str
        An attribute path. The `.` character denotes sub-attributes.
    analyzer : str, optional
        The name of an Analyzer to use for this field.
        Default: the value defined by the top-level `analyzer` option.
    features : list of InvertedIndexFeaturesType, optional
        A list of Analyzer features to use for this field. They define what features are
        enabled for the `analyzer`. Possible features are: "frequency", "norm", "position", and "offset". Default: the value of the top-level features option, or if not set, the
        features defined by the Analyzer itself.
    search_field : bool, optional
        This option only applies if you use the inverted index in a `search-alias` Views.
        You can set the option to `true` to get the same behavior as with `arangosearch`
        Views regarding the indexing of array values for this field. If enabled, both,
        array and primitive values (strings, numbers, etc.) are accepted. Every element
        of an array is indexed according to the `trackListPositions` option.
        If set to `false`, it depends on the attribute path. If it explicitly expand an
        array (`[*]`), then the elements are indexed separately. Otherwise, the array is
        indexed as a whole, but only `geopoint` and `aql` Analyzers accept array inputs.
        You cannot use an array expansion if `searchField` is enabled.
        Default: the value defined by the top-level `searchField` option.
    """

    name: str
    analyzer: Optional[str]
    features: Optional[List[InvertedIndexFeaturesType]]
    search_field: Optional[bool]

    def to_db(self) -> Dict[str, Any]:
        data = {"name": self.name}

        if self.analyzer is not None:
            data["analyzer"] = self.analyzer

        if self.features is not None and len(self.features):
            data["features"] = [str(item.value) for item in self.features]

        if self.search_field is not None:
            data["searchField"] = self.search_field

        return data


class InvertedIndexField(BaseModel):
    """
    Object to specify options for the fields.

    Attributes
    ----------
    name : str
        An attribute path. The `.` character denotes sub-attributes.
    analyzer : str, optional
        The name of an Analyzer to use for this field.
        Default: the value defined by the top-level `analyzer` option, or if not set,
        the default `identity` Analyzer.
    features : list of InvertedIndexFeaturesType, optional
        A list of Analyzer features to use for this field. They define what features are
        enabled for the analyzer. Possible features are: "frequency", "norm", "position", and "offset. Default: the value of the top-level features option, or if not set, the
        features defined by the Analyzer itself.
    include_all_features : bool, optional
        This option only applies if you use the inverted index in a `search-alias` Views.
        If set to `true`, then all sub-attributes of this field are indexed, excluding
        any sub-attributes that are configured separately by other elements in the
        `fields` array (and their sub-attributes). The `analyzer` and `features`
        properties apply to the sub-attributes.
        If set to `false`, then sub-attributes are ignored. The default value is defined
        by the top-level `includeAllFields` option, or `false` if not set.
    search_field : bool, optional
        This option only applies if you use the inverted index in a `search-alias` Views.
        You can set the option to `true` to get the same behavior as with `arangosearch`
        Views regarding the indexing of array values for this field. If enabled, both,
        array and primitive values (strings, numbers, etc.) are accepted. Every element
        of an array is indexed according to the `trackListPositions` option.
        If set to `false`, it depends on the attribute path. If it explicitly expand an
        array ([*]), then the elements are indexed separately. Otherwise, the array is
        indexed as a whole, but only `geopoint` and `aql` Analyzers accept array inputs.
        You cannot use an array expansion if `searchField` is enabled.
        Default: the value defined by the top-level `searchField` option, or `false` if
        not set.
    track_list_positions : bool, optional
        This option only applies if you use the inverted index in a `search-alias `Views.
        If set to `true`, then track the value position in arrays for array values.
        For example, when querying a document like `{ attr: [ "valueX", "valueY", "valueZ" ] }`,
        you need to specify the array element, e.g. `doc.attr[1] == "valueY"`.
        If set to `false`, all values in an array are treated as equal alternatives.
        You don't specify an array element in queries, e.g. `doc.attr == "valueY"`, and
        all elements are searched for a match.
        Default: the value defined by the top-level `trackListPositions` option, or
        `false` if not set.
    nested : InvertedIndexNestedAttribute, optional
        Index the specified sub-objects that are stored in an array. Other than with the
        `fields` property, the values get indexed in a way that lets you query for
        co-occurring values. For example, you can search the sub-objects and all the
        conditions need to be met by a single sub-object instead of across all of them.
        This property is available in the `Enterprise Edition` only.
    """

    name: str
    analyzer: Optional[str]
    features: Optional[List[InvertedIndexFeaturesType]]
    include_all_fields: Optional[bool]
    search_field: Optional[bool]
    track_list_positions: Optional[bool]
    nested: Optional[InvertedIndexNestedAttribute]

    def to_db(self) -> Dict[str, Any]:
        data = {"name": self.name}
        if self.analyzer is not None:
            data["analyzer"] = self.analyzer

        if self.features is not None and len(self.features):
            data["features"] = [str(item.value) for item in self.features]

        if self.include_all_fields is not None:
            data["includeAllFields"] = self.include_all_fields

        if self.search_field is not None:
            data["searchField"] = self.search_field

        if self.track_list_positions is not None:
            data["trackListPositions"] = self.track_list_positions

        if self.nested is not None:
            data["nested"] = self.nested.to_db()

        return data


class InvertedIndex(BaseArangoIndex):
    """
    Inverted Index.

    Attributes
    ----------
    type : IndexType
        Type of the index. Must be equal to "inverted"
    name : str
        An easy-to-remember name for the index to look it up or refer to it in index hints.
        Index names are subject to the same character restrictions as collection names.
        If omitted, a name is auto-generated so that it is unique with respect to the
        collection, e.g. idx_832910498.
    fields : list of str or InvertedIndexField
         An array of attribute paths as strings to index the fields with the default
        options, or objects to specify options for the fields.
    search_field : bool, optional
        This option only applies if you use the inverted index in a `search-alias` Views.
        You can set the option to `true` to get the same behavior as with `arangosearch`
        Views regarding the indexing of array values as the default. If enabled, both,
        array and primitive values (strings, numbers, etc.) are accepted. Every element
        of an array is indexed according to the `trackListPositions` option.
        If set to `false`, it depends on the attribute path. If it explicitly expand an
        array (`[*]`), then the elements are indexed separately. Otherwise, the array is
        indexed as a whole, but only `geopoint` and `aql` Analyzers accept array inputs.
        You cannot use an array expansion if `searchField` is enabled.
    stored_values : list of StoredValuesField, optional
        The optional `storedValues` attribute can contain an array of paths to additional
        attributes to store in the index. These additional attributes cannot be used for
        index lookups or for sorting, but they can be used for projections. This allows an
        index to fully cover more queries and avoid extra document lookups.
    primary_sort : InvertedIndexPrimarySort, optional
        ?
    analyzer : str, optional
        The name of an Analyzer to use by default. This Analyzer is applied to the
        values of the indexed fields for which you don't define Analyzers explicitly.
    features : list of InvertedIndexFeaturesType, optional
        A list of Analyzer features to use by default. They define what features are
        enabled for the default analyzer. Possible features are "frequency", "norm", "position", and "offset. The default is an empty array.
    include_all_fields : bool, optional
        This option only applies if you use the inverted index in a `search-alias` Views.
        If set to `true`, then all document attributes are indexed, excluding any
        sub-attributes that are configured in the fields array (and their sub-attributes).
        The analyzer and features properties apply to the sub-attributes.
        The default is `false`.

        **Warning**: Using `includeAllFields` for a lot of attributes in combination
        with complex Analyzers may significantly slow down the indexing process.
    track_list_positions : bool, optional
        This option only applies if you use the inverted index in a `search-alias` Views.
        If set to `true`, then track the value position in arrays for array values.
        For example, when querying a document like `{ attr: [ "valueX", "valueY", "valueZ" ] }`,
        you need to specify the array element, e.g. `doc.attr[1] == "valueY`".
        If set to `false`, all values in an array are treated as equal alternatives.
        You don't specify an array element in queries, e.g. `doc.attr == "valueY"`, and
        all elements are searched for a match.
    parallelism : int, optional
        The number of threads to use for indexing the fields. Default: `2`
    in_background : bool, optional
        This attribute can be set to `true` to create the index
        in the background, not write-locking the underlying collection for as long as if the index is built in the foreground. The default value is `false`.
    cleanup_interval_step : int, optional
        Wait at least this many commits between removing unused files in the
        `ArangoSearch` data directory (default: `2`, to disable use: `0`).

        For the case where the consolidation policies merge segments often (i.e. a lot
        of commit+consolidate), a lower value will cause a lot of disk space to be
        wasted.
        For the case where the consolidation policies rarely merge segments (i.e. few
        inserts/deletes), a higher value will impact performance without any added
        benefits.

        **Background**:
        With every "commit" or "consolidate" operation a new state of the View
        internal data-structures is created on disk.
        Old states/snapshots are released once there are no longer any users remaining.
        However, the files for the released states/snapshots are left on disk, and
        only removed by "cleanup" operation.
    cleanup_interval_msec : int, optional
        Wait at least this many milliseconds between committing View data store
        changes and making documents visible to queries (default: `1000`, to disable use: `0`).

        For the case where there are a lot of inserts/updates, a lower value, until
        commit, will cause the index not to account for them and memory usage would
        continue to grow.
        For the case where there are a few inserts/updates, a higher value will impact
        performance and waste disk space for each commit call without any added benefits.

        **Background**:
        For data retrieval ArangoSearch Views follow the concept of
        "eventually-consistent", i.e. eventually all the data in ArangoDB will be
        matched by corresponding query expressions.
        The concept of ArangoSearch View "commit" operation is introduced to
        control the upper-bound on the time until document addition/removals are
        actually reflected by corresponding query expressions.
        Once a "commit" operation is complete all documents added/removed prior to
        the start of the "commit" operation will be reflected by queries invoked in
        subsequent ArangoDB transactions, in-progress ArangoDB transactions will
        still continue to return a repeatable-read state.
    consolidation_interval_msec : int, optional
        Wait at least this many milliseconds between applying 'consolidationPolicy' to
        consolidate View data store and possibly release space on the filesystem (default: `1000`, to disable use: `0`).

        For the case where there are a lot of data modification operations, a higher
        value could potentially have the data store consume more space and file handles.
        For the case where there are a few data modification operations, a lower value
        will impact performance due to no segment candidates available for
        consolidation.

        **Background**:
        For data modification ArangoSearch Views follow the concept of a
        "versioned data store". Thus, old versions of data may be removed once there
        are no longer any users of the old data. The frequency of the cleanup and
        compaction operations are governed by 'consolidationIntervalMsec' and the
        candidates for compaction are selected via 'consolidationPolicy'.
    consolidation_policy : ConsolidationPolicy, optional
        Defines the kind of policy is used for consolidation.
    write_buffer_idle : int, optional
        Maximum number of writers (segments) cached in the pool (default: `64`, use `0` to disable)
    write_buffer_active : int, optional
        Maximum number of concurrent active writers (segments) that perform a
        transaction. Other writers (segments) wait till current active writers
        (segments) finish (default: `0`, use `0` to disable)
    write_buffer_size_max : int, optional
        Maximum memory byte size per writer (segment) before a writer (segment) flush
        is triggered. `0` value turns off this limit for any writer (buffer) and data
        will be flushed periodically based on the value defined for the flush thread
        (ArangoDB server startup option). `0` value should be used carefully due to
        high potential memory consumption
        (default: `33554432`, use `0` to disable)
    version : int, optional
        ?
    """

    type = IndexType.INVERTED

    fields: List[Union[str, InvertedIndexField]]

    in_background: Optional[bool]
    parallelism: Optional[int]
    primary_sort: Optional[InvertedIndexPrimarySort]
    stored_values: Optional[List[StoredValuesField]]
    analyzer: Optional[str]
    features: Optional[List[InvertedIndexFeaturesType]]
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
    version: Optional[int]

    def to_db(self) -> Dict[str, Any]:
        data = super(InvertedIndex, self).to_db()

        if self.fields is not None and len(self.fields):
            data["fields"] = [field.to_db() if isinstance(field, InvertedIndexField) else field for field in self.fields]

        if self.features is not None and len(self.features):
            data["features"] = [str(item.value) for item in self.features]

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        if self.parallelism is not None:
            data["parallelism"] = self.parallelism

        if self.primary_sort is not None:
            data["PrimarySort"] = self.primary_sort.dict()

        if self.stored_values is not None and len(self.stored_values):
            data["storedValues"] = [item.dict() for item in self.stored_values]

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
        return index
