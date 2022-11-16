from .create_document import CreateDocument
from .read_document import ReadDocument
from .read_document_header import ReadDocumentHeader
from .read_multiple_documents import ReadMultipleDocuments
from .remove_document import RemoveDocument
from .replace_document import ReplaceDocument
from .update_document import UpdateDocument
from .update_documents import UpdateDocuments


class DocumentsMethods(
    CreateDocument,
    ReadDocument,
    ReadDocumentHeader,
    ReadMultipleDocuments,
    RemoveDocument,
    ReplaceDocument,
    UpdateDocument,
    UpdateDocuments,
):
    pass
