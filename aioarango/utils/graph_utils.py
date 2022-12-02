from aioarango.typings import Json


def format_edge(body: Json) -> Json:
    """
    Format edge data.

    Parameters
    ----------
    body : Json
        Input body.

    Returns
    -------
    Json
        Formatted body.
    """
    edge: Json = body["edge"]
    if "_oldRev" in edge:
        edge["_old_rev"] = edge.pop("_oldRev")

    if "new" in body or "old" in body:
        result: Json = {"edge": edge}
        if "new" in body:
            result["new"] = body["new"]
        if "old" in body:
            result["old"] = body["old"]
        return result
    else:
        return edge


def format_vertex(body: Json) -> Json:
    """
    Format vertex data.

    Parameters
    ----------
    body : Json
        Input body.

    Returns
    -------
    Json
        Formatted body.
    """
    vertex: Json = body["vertex"]
    if "_oldRev" in vertex:
        vertex["_old_rev"] = vertex.pop("_oldRev")

    if "new" in body or "old" in body:
        result: Json = {"vertex": vertex}
        if "new" in body:
            result["new"] = body["new"]
        if "old" in body:
            result["old"] = body["old"]
        return result
    else:
        return vertex
