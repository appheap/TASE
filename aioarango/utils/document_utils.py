from typing import Union, Optional, Tuple

from aioarango.errors.client.document_errors import DocumentParseError
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
    aioarango.errors.client.document_errors.DocumentParseError
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
    aioarango.errors.client.document_errors.DocumentParseError
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
    revisions_must_match: Optional[bool] = None,
) -> Tuple[str, Headers]:
    """
    Prepare document ID and request headers.

    Parameters
    ----------
    document : Json
        Document body
    id_prefix : str
        ID prefix for this document
    revisions_must_match : bool, default : None
        Whether to check for revision match or mismatch

    Returns
    -------
    tuple
        Document ID and request headers

    Raises
    ------
    aioarango.errors.client.document_errors.DocumentParseError
        If `key` and `ID` are missing from the document body.
    """
    doc_id = extract_id(document, id_prefix)
    if revisions_must_match is None or "_rev" not in document:
        return doc_id, {}
    return doc_id, {"If-Match": document["_rev"]} if revisions_must_match else {"If-None-Match": document["_rev"]}


def prep_from_doc(
    document: Union[str, Json],
    id_prefix: str,
    rev: Optional[str],
    revisions_must_match: Optional[bool] = None,
) -> Tuple[str, Union[str, Json], Json]:
    """
    Prepare document ID, body and request headers.

    Parameters
    ----------
    document : str or Json
        Document ID, key or body
    id_prefix : str
        ID prefix for this document
    rev : str, optional
        Revision key
    revisions_must_match : bool, default : None
        Whether to check for revision match or mismatch


    Returns
    -------
    tuple
        Document ID, body and request headers.

    Raises
    ------
    aioarango.errors.client.document_errors.DocumentParseError
        If `key` and `ID` are missing from the document body, or if collection name is invalid.

    """
    if isinstance(document, dict):
        doc_id = extract_id(document, id_prefix)
        rev = rev or document.get("_rev")

        if revisions_must_match is None or rev is None:
            return doc_id, doc_id, {}
        else:
            headers = {"If-Match": rev} if revisions_must_match else {"If-None-Match": rev}
            return doc_id, doc_id, headers
    else:
        if "/" in document:
            doc_id = validate_id(document, id_prefix)
        else:
            doc_id = id_prefix + document

        if revisions_must_match is None or rev is None:
            return doc_id, doc_id, {}
        else:
            headers = {"If-Match": rev} if revisions_must_match else {"If-None-Match": rev}
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
    aioarango.errors.client.document_errors.DocumentParseError
        If `key` and `ID` are missing from the document body.
    """
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
    """
    if "_id" in body and "_key" not in body:
        doc_id = validate_id(body["_id"], id_prefix)
        body = body.copy()
        body["_key"] = doc_id[len(id_prefix) :]
    return body
