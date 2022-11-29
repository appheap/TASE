from aioarango.typings import Json


def format_aql_query(body: Json) -> Json:
    """
    Format AQL query data.

    Parameters
    ----------
    body : dict
        Input body.

    Returns
    -------
    dict
        Formatted body.

    """
    result = {
        "id": body["id"],
        "query": body["query"],
    }
    if "database" in body:
        result["database"] = body["database"]
    if "bindVars" in body:
        result["bind_vars"] = body["bindVars"]
    if "runTime" in body:
        print(body["runTime"])
        result["runtime"] = body["runTime"]
    if "started" in body:
        result["started"] = body["started"]
    if "state" in body:
        result["state"] = body["state"]
    if "stream" in body:
        result["stream"] = body["stream"]
    if "user" in body:
        result["user"] = body["user"]

    return result
