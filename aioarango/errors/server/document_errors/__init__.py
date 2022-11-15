"""
Document Exceptions
"""

from .document_count_error import DocumentCountError
from .document_delete_error import DocumentDeleteError
from .document_get_error import DocumentGetError
from .document_ids_error import DocumentIDsError
from .document_in_error import DocumentInError
from .document_insert_error import DocumentInsertError
from .document_keys_error import DocumentKeysError
from .document_replace_error import DocumentReplaceError
from .document_revision_error import DocumentRevisionError
from .document_update_error import DocumentUpdateError

__all__ = [
    "DocumentCountError",
    "DocumentDeleteError",
    "DocumentGetError",
    "DocumentIDsError",
    "DocumentInError",
    "DocumentInsertError",
    "DocumentKeysError",
    "DocumentReplaceError",
    "DocumentRevisionError",
    "DocumentUpdateError",
]
