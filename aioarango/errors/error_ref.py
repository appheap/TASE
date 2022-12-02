from pydantic import BaseModel

from .error_ import errors
from .error_type import ErrorType


class Error(BaseModel):
    type: ErrorType
    code: int
    title: str
    category: str
    description: str


unknown_error = Error(
    type=ErrorType.UNKNOWN,
    code=-1,
    title="UNKNOWN_ERROR",
    category="UNKNOWN",
    description="Will be raised when the server error is not known to the client.",
)

empty_error = Error(
    type=ErrorType.EMPTY_PLACEHOLDER,
    code=-2,
    title="EMPTY_PLACEHOLDER",
    category="EMPTY_PLACEHOLDER",
    description="",
)


class ErrorReference:
    def __init__(self):
        self.ref = {}
        for category_name, items in errors.items():
            for error in items.values():
                self.ref[error["error_num"]] = Error(
                    type=error["error_num"],
                    code=error["error_num"],
                    title=error["title"],
                    category=category_name,
                    description=error["description"],
                )

    def get_error(self, error_number: int) -> Error:
        if error_number is None:
            return empty_error
        if isinstance(error_number, str):
            try:
                error_number = int(error_number)
            except ValueError:
                return unknown_error
        return self.ref.get(error_number, unknown_error)


_error_reference = ErrorReference()


def get_error(error_number: int) -> Error:
    return _error_reference.get_error(error_number)


print("Running...")

__all__ = [
    "get_error",
    "Error",
    "unknown_error",
    "empty_error",
]
