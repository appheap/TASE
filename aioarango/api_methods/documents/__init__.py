from .create_document import CreateDocument
from .read_document import ReadDocument
from .read_document_header import ReadDocumentHeader


class DocumentsMethods(
    CreateDocument,
    ReadDocument,
    ReadDocumentHeader,
):
    pass
