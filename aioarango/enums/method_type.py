from enum import Enum


class MethodType(Enum):
    GET = "get"
    PATCH = "patch"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
