from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from aioarango.enums import ComputeOnType
from aioarango.typings import Json


class ComputedValue(BaseModel):
    """
    A computed value.
    """

    name: str
    """
    The name of the target attribute. Can only be a top-level attribute, but you
    may return a nested object. Cannot be `_key`, `_id`, `_rev`, `_from`, `_to`,
    or a `shard key` attribute.
    """

    expression: str
    """
    An AQL `RETURN` operation with an expression that computes the desired value.
    """

    overwrite: bool
    """
    Whether the computed value takes precedence over a user-provided or existing attribute.
    """

    compute_on: List[ComputeOnType]
    """
    An array of strings that defines on which write operations the value is computed. The possible values are "insert", "update", and "replace".
    The default is ["insert", "update", "replace"].
    """

    keep_null: bool
    """
    Whether the target attribute shall be set if the expression evaluates to `null`.
    You can set the option to `false` to not set (or unset) the target attribute if
    the expression returns `null`. The default is `true`.
    """

    fail_on_warning: bool
    """
    Whether the write operation fails if the expression produces a warning. The default is `false`.
    """

    @classmethod
    def parse_from_dict(cls, d: dict) -> Optional[ComputedValue]:
        if d is None or not len(d):
            return None

        return ComputedValue(
            name=d["name"],
            expression=d["expression"],
            overwrite=d["overwrite"],
            compute_on=d["computeOn"],
            keep_null=d["keepNull"],
            fail_on_warning=d["failOnWarning"],
        )

    def parse_for_arangodb(self) -> Json:
        """
        Parse the object to be used in ArangoDB API.

        Returns
        -------
        Json
            A dictionary containing the values of the `computedOn` object.

        """
        return {
            "name": self.name,
            "expression": self.expression,
            "overwrite": self.overwrite,
            "computeOn": [item.value for item in self.compute_on],
            "keepNull": self.keep_null,
            "failOnWarning": self.fail_on_warning,
        }
