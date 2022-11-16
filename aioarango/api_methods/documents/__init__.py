from .create_document import CreateDocument
from .create_multiple_documents import CreateMultipleDocuments
from .read_document import ReadDocument
from .read_document_header import ReadDocumentHeader
from .read_multiple_documents import ReadMultipleDocuments
from .remove_document import RemoveDocument
from .remove_multiple_documents import RemoveMultipleDocuments
from .replace_document import ReplaceDocument
from .update_document import UpdateDocument
from .update_documents import UpdateDocuments


class DocumentsMethods(
    CreateDocument,
    CreateMultipleDocuments,
    ReadDocument,
    ReadDocumentHeader,
    ReadMultipleDocuments,
    RemoveDocument,
    RemoveMultipleDocuments,
    ReplaceDocument,
    UpdateDocument,
    UpdateDocuments,
):
    pass
