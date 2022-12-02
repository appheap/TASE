from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class EdgeDefinition(BaseModel):
    """
    Definitions for the relations of the graph.

    Attributes
    ----------
    collection : str
         Name of the edge collection, where the edge are stored in.
    from_ : list of str
         List of vertex collection names.
    to : list of str
         List of vertex collection names. Edges in collection can only be inserted if their **_to** is in any of the collections here.
    """

    collection: str
    from_: List[str]
    to: List[str]

    @classmethod
    def parse_edge_definition_dict(
        cls,
        edge_def_body: dict,
    ) -> Optional[EdgeDefinition]:
        if edge_def_body is None or not len(edge_def_body):
            return None

        return EdgeDefinition(
            collection=edge_def_body["collection"],
            from_=edge_def_body["from"],
            to=edge_def_body["to"],
        )
