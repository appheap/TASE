from .create_cursor import CreateCursor
from .delete_cursor import DeleteCursor
from .read_cursor_next_batch import ReadCursorNextBatch


class CursorsMethods(
    CreateCursor,
    DeleteCursor,
    ReadCursorNextBatch,
):
    pass
