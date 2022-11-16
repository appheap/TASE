from .create_document import CreateDocument
from .read_document import ReadDocument
from .read_document_header import ReadDocumentHeader
from .read_multiple_documents import ReadMultipleDocuments


class DocumentsMethods(
    CreateDocument,
    ReadDocument,
    ReadDocumentHeader,
    ReadMultipleDocuments,
):
    pass
