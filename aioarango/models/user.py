from typing import Optional

from pydantic import BaseModel, Field

from aioarango.typings import Json


class User(BaseModel):
    """
    A database user.

    Attributes
    ----------
    user : str
        The name of the user as a string. This is mandatory.
    password : str
        The user password as a string. If not specified, it will default to an empty string.
    active : bool, default : True
        An optional flag that specifies whether the user is active. If not specified, this will default to true.
    extra : Json, optional
        A JSON object with extra user information. It is used by the web interface
        to store graph viewer settings and saved queries. Should not be set or
        modified by end users, as custom attributes will not be preserved.
    """

    user: str
    password: str
    active: Optional[bool] = Field(default=True)
    extra: Optional[Json] = Field(default_factory=dict)
