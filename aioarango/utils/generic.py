from aioarango.typings import Json


def format_body(body: Json) -> Json:
    """
    Format generic response body.

    Parameters
    ----------
    body : dict
        Input body

    Returns
    -------
    dict
        Formatted body.

    """
    body.pop("error", None)
    body.pop("code", None)
    return body
