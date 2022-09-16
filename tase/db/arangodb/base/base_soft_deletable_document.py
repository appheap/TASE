from typing import Optional

from pydantic import BaseModel, Field


class BaseSoftDeletableDocument(BaseModel):
    is_soft_deleted: bool = Field(default=False)
    soft_deleted_at: Optional[int] = Field(default=None)
    is_soft_deleted_time_precise: Optional[bool] = Field(default=None)

    def __init_subclass__(cls, **kwargs):
        extra = getattr(cls, "_extra_do_not_update_fields", None)
        if extra is None:
            extra = []
        else:
            extra = list(extra)

        extra.append("is_soft_deleted")
        extra.append("soft_deleted_at")
        extra.append("is_soft_deleted_time_precise")

        setattr(cls, "_extra_do_not_update_fields", tuple(extra))
