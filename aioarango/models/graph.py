from __future__ import annotations

import collections
from typing import List, Optional, Union

from pydantic import BaseModel

from .edge_definition import EdgeDefinition


class Graph(BaseModel):
    """
    Attributes
    ----------
    name : str
        Name of the graph.
    id : str
        ID of this graph.
    key : str
        Key of this graph.
    rev : str
        Revision of this graph. Can be used to make sure to not override concurrent modifications to this graph.
    number_of_shards : int, optional
        Number of shards created for every new collection in the graph.
    replication_factor : str or int, optional
        The replication factor used for every new collection in the graph.
        Can also be the string "satellite" for a SatelliteGraph (Enterprise Edition only).
    is_smart : bool, optional
         Whether the graph is a **SmartGraph** (Enterprise Edition only).
    is_disjoint : bool, optional
        Whether the graph is a Disjoint **SmartGraph** (Enterprise Edition only).
    smart_graph_attribute : str, optional
         Name of the sharding attribute in the **SmartGraph** case (Enterprise Edition only).
    is_satellite : bool, optional
        Flag if the graph is a **SatelliteGraph** (Enterprise Edition only) or not.
    write_concern : int, optional
        Default write concern for new collections in the graph.
        It determines how many copies of each shard are required to be
        in sync on the different DB-Servers. If there are less then these many copies
        in the cluster a shard will refuse to write. Writes to shards with enough
        up-to-date copies will succeed at the same time however. The value of
        **write_concern** can not be larger than **replication_factor**. (cluster only)
    edge_definitions : list of EdgeDefinition, optional
        An array of definitions for the relations of the graph.
    orphan_collections : list of str, optional
        An array of additional vertex collections.
        Documents within these collections do not have edges within this graph.
    """

    name: str
    id: str
    key: str
    rev: str

    number_of_shards: Optional[int]
    replication_factor: Union[int, str, None]
    is_smart: Optional[bool]
    is_disjoint: Optional[bool]
    smart_graph_attribute: Optional[str]
    is_satellite: Optional[bool]
    write_concern: Optional[int]

    edge_definitions: Optional[List[EdgeDefinition]]
    orphan_collections: Optional[List[str]]

    @classmethod
    def parse_graph_dict(
        cls,
        graph_body: dict,
    ) -> Optional[Graph]:
        graph_dict = {
            "id": graph_body["_id"],
            "key": graph_body["_key"],
            "rev": graph_body["_rev"],
            "name": graph_body["name"],
            "number_of_shards": graph_body.get("numberOfShards", None),
            "replication_factor": graph_body.get("replicationFactor", None),
            "is_smart": graph_body.get("isSmart", None),
            "is_disjoint": graph_body.get("isDisjoint", None),
            "smart_graph_attribute": graph_body.get("smartGraphAttribute", None),
            "is_satellite": graph_body.get("isSatellite", None),
            "write_concern": graph_body.get("writeConcern", None),
        }
        edge_defs = collections.deque()
        for edge_def_body in graph_body["edgeDefinitions"]:
            edge_defs.append(EdgeDefinition.parse_edge_definition_dict(edge_def_body))

        if len(edge_defs):
            graph_dict["edge_definitions"] = list(edge_defs)

        if "orphanCollections" in graph_body:
            graph_dict["orphan_collections"] = graph_body["orphanCollections"]

        return Graph.parse_obj(graph_dict)
