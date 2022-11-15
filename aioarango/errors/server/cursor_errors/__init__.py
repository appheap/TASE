"""
Cursor Exceptions
"""

from .cursor_close_error import CursorCloseError
from .cursor_next_error import CursorNextError

__all__ = [
    "CursorCloseError",
    "CursorNextError",
]
