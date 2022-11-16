"""
Document Exceptions
"""

from .document_count_error import DocumentCountError
from .document_delete_error import DocumentDeleteError
from .document_get_error import DocumentGetError
from .document_ids_error import DocumentIDsError
from .document_illegal_error import DocumentIllegalError
from .document_illegal_key_error import DocumentIllegalKeyError
from .document_in_error import DocumentInError
from .document_insert_error import DocumentInsertError
from .document_keys_error import DocumentKeysError
from .document_parse_error import DocumentParseError
from .document_replace_error import DocumentReplaceError
from .document_revision_match_error import DocumentRevisionMatchError
from .document_revision_mismatch_error import DocumentRevisionMisMatchError
from .document_unique_constraint_error import DocumentUniqueConstraintError
from .document_update_error import DocumentUpdateError

__all__ = [
    "DocumentCountError",
    "DocumentDeleteError",
    "DocumentGetError",
    "DocumentIDsError",
    "DocumentIllegalError",
    "DocumentIllegalKeyError",
    "DocumentInError",
    "DocumentInsertError",
    "DocumentKeysError",
    "DocumentParseError",
    "DocumentReplaceError",
    "DocumentRevisionMatchError",
    "DocumentRevisionMisMatchError",
    "DocumentUniqueConstraintError",
    "DocumentUpdateError",
]
