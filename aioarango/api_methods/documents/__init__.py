from .create_document import CreateDocument
from .read_document import ReadDocument
from .read_document_header import ReadDocumentHeader
from .read_multiple_documents import ReadMultipleDocuments
from .update_document import UpdateDocument


class DocumentsMethods(
    CreateDocument,
    ReadDocument,
    ReadDocumentHeader,
    ReadMultipleDocuments,
    UpdateDocument,
):
    pass
