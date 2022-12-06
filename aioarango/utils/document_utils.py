import collections
from typing import Union, Optional, Tuple, List, Callable

from aioarango.errors import DocumentParseError, ArangoServerError
from aioarango.models import Response, Request
from aioarango.typings import Json, Headers


def validate_id(
    doc_id: str,
    id_prefix: str,
) -> str:
    """
    Check the collection name in the document ID.

    Parameters
    ----------
    doc_id : str
        Document ID
    id_prefix : str
        ID prefix for this document

    Returns
    -------
    str
        Verified document ID

    Raises
    ------
    aioarango.errors.DocumentParseError
        If collection name is invalid.
    """
    if not doc_id.startswith(id_prefix):
        raise DocumentParseError(f'bad collection name in document ID "{doc_id}"')
    return doc_id


def extract_id(
    body: Json,
    id_prefix: str,
) -> str:
    """
    Extract the document ID from document body.

    Parameters
    ----------
    body : Json
        Document body
    id_prefix : str
        ID prefix for this document

    Returns
    -------
    str
        Document ID

    Raises
    ------
    aioarango.errors.DocumentParseError
        If `key` and `ID` are missing from the body.
    """
    try:
        if "_id" in body:
            return validate_id(body["_id"], id_prefix)
        else:
            key: str = body["_key"]
            return id_prefix + key
    except KeyError:
        raise DocumentParseError('field "_key" or "_id" required')


def prep_from_body(
    document: Json,
    id_prefix: str,
    check_for_revisions_match: Optional[bool] = None,
    check_for_revisions_mismatch: Optional[bool] = None,
) -> Tuple[str, Headers]:
    """
    Prepare document ID and request headers.

    Parameters
    ----------
    document : Json
        Document body
    id_prefix : str
        ID prefix for this document
    check_for_revisions_match : bool, default : None
        Whether the revisions must match or not
    check_for_revisions_mismatch : bool, default : None
        Whether the revisions must mismatch or not

    Returns
    -------
    tuple
        Document ID and request headers

    Raises
    ------
    aioarango.errors.DocumentParseError
        If `key` and `ID` are missing from the document body or the document is `None`.
    """
    if document is None:
        raise DocumentParseError(f"document cannot be `None`")

    doc_id = extract_id(document, id_prefix)
    if (not check_for_revisions_match and not check_for_revisions_mismatch) or "_rev" not in document:
        return doc_id, {}
    if check_for_revisions_match:
        return doc_id, {"If-Match": document["_rev"]}
    if check_for_revisions_mismatch:
        return doc_id, {"If-None-Match": document["_rev"]}


def prep_from_doc(
    document: Union[str, Json],
    id_prefix: str,
    rev: Optional[str] = None,
    check_for_revisions_match: Optional[bool] = None,
    check_for_revisions_mismatch: Optional[bool] = None,
) -> Tuple[str, Union[str, Json], Json]:
    """
    Prepare document ID, body and request headers.

    Parameters
    ----------
    document : str or Json
        Document ID, key or body
    id_prefix : str
        ID prefix for this document
    rev : str, default : None
        Revision key
    check_for_revisions_match : bool, default : None
        Whether the revisions must match or not
    check_for_revisions_mismatch : bool, default : None
        Whether the revisions must mismatch or not


    Returns
    -------
    tuple
        Document ID, body and request headers.

    Raises
    ------
    aioarango.errors.DocumentParseError
        If `key` and `ID` are missing from the document body, or the document is `None` or if collection name is invalid.

    """
    if document is None:
        raise DocumentParseError(f"document cannot be `None`")

    if isinstance(document, dict):
        doc_id = extract_id(document, id_prefix)
        rev = rev or document.get("_rev", None)

        if (not check_for_revisions_match and not check_for_revisions_mismatch) or rev is None:
            return doc_id, doc_id, {}
        else:
            if check_for_revisions_match:
                headers = {"If-Match": rev}
            elif check_for_revisions_mismatch:
                headers = {"If-None-Match": rev}
            else:
                headers = {}

            return doc_id, doc_id, headers
    else:
        if "/" in document:
            doc_id = validate_id(document, id_prefix)
        else:
            doc_id = id_prefix + document

        if (check_for_revisions_match is None and check_for_revisions_mismatch is None) is None or rev is None:
            return doc_id, doc_id, {}
        else:
            if check_for_revisions_match:
                headers = {"If-Match": rev}
            elif check_for_revisions_mismatch:
                headers = {"If-None-Match": rev}
            else:
                headers = {}
            return doc_id, doc_id, headers


def ensure_key_in_body(
    body: Json,
    id_prefix: str,
) -> Json:
    """
    Return the document body with "_key" field populated.

    Parameters
    ----------
    body : Json
        Document body
    id_prefix : str
        ID prefix for this document

    Returns
    -------
    Json
        Document body with `key` field

    Raises
    ------
    aioarango.errors.DocumentParseError
        If `key` and `ID` are missing from the document body or the body is `None`.
    """
    if body is None:
        raise DocumentParseError(f"body cannot be `None`")

    if "_key" in body:
        return body
    elif "_id" in body:
        doc_id = validate_id(body["_id"], id_prefix)
        body = body.copy()
        body["_key"] = doc_id[len(id_prefix) :]
        return body
    raise DocumentParseError('field "_key" or "_id" required')


def ensure_key_from_id(
    body: Json,
    id_prefix: str,
) -> Json:
    """
    Return the body with "_key" field if it has "_id" field.

    Parameters
    ----------
    body : Json
        Document body
    id_prefix : str
        ID prefix for this document

    Returns
    -------
    Json
        Document body with "_key" field if it has "_id" field.

    Raises
    ------
    aioarango.errors.DocumentParseError
        If collection name is invalid or the body is `None`.
    """
    if body is None:
        raise DocumentParseError(f"body cannot be `None`")

    if "_id" in body and "_key" not in body:
        doc_id = validate_id(body["_id"], id_prefix)
        body = body.copy()
        body["_key"] = doc_id[len(id_prefix) :]
    return body


def populate_doc_or_error(
    response: Response,
    request: Request,
    prep_bulk_err_response_function: Callable,
) -> List[Union[Json, ArangoServerError]]:
    results = collections.deque()

    if response is None or request is None:
        return list(results)

    for doc_or_error in response.body:
        if "_id" in doc_or_error:
            if "_oldRev" in doc_or_error:
                doc_or_error["_old_rev"] = doc_or_error.pop("_oldRev")
            results.append(doc_or_error)
        else:
            sub_resp = prep_bulk_err_response_function(response, doc_or_error)
            results.append(ArangoServerError(sub_resp, request))

    return list(results)
