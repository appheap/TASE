from __future__ import annotations

from typing import Optional, List, Type

from pydantic import BaseModel

from . import InlineButton
from .inline_button_type import InlineButtonType


class InlineButtonData(BaseModel):
    __button_type__: InlineButtonType = InlineButtonType.BASE
    __registry__ = dict()

    @property
    def type(self) -> InlineButtonType:
        return self.__button_type__

    @classmethod
    def get_type_value(cls) -> int:
        return int(cls.__button_type__.value)

    def __init_subclass__(cls, **kwargs):
        InlineButtonData.__registry__[cls.get_type_value()] = cls

    @classmethod
    def get_button_data(
        cls,
        button_type: InlineButtonType,
    ) -> Optional[Type[InlineButtonData]]:
        if button_type is None and button_type not in (
            InlineButtonType.BASE,
            InlineButtonType.UNKNOWN,
            InlineButtonType.INVALID,
        ):
            return None

        return cls.__registry__.get(button_type.value, None)

    @classmethod
    def generate_data(cls, *args, **kwargs) -> Optional[str]:
        raise NotImplementedError

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        raise NotImplementedError

    @classmethod
    def parse_from_string(
        cls,
        data: str,
    ) -> Optional[InlineButtonData]:
        if not data:
            return None

        if not data.startswith("#") and "|" not in data:
            return None

        if data.startswith("#"):
            data = data[1:]
            sep = " " if "|" not in data else "|"
        else:
            sep = "|"

        data_split_lst = data.strip().split(sep)
        button_type_str = data_split_lst[0]
        if not button_type_str:
            return None

        try:
            button_type_int = int(button_type_str)
        except ValueError:
            # fixme: an alias is used, find the button type by the given alias.
            button = InlineButton.find_button_by_alias(button_type_str)
            if button:
                button_type = button.__type__
            else:
                button_type = None
        else:
            try:
                button_type = InlineButtonType(button_type_int)
            except ValueError:
                # given button type is not valid
                return None

        if not button_type or button_type in (InlineButtonType.BASE, InlineButtonType.UNKNOWN, InlineButtonType.INVALID):
            return None

        button_data = cls.get_button_data(button_type)
        if not button_data:
            return None

        return button_data.__parse__(data_split_lst)
