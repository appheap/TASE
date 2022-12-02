from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class QueryOptimizerRuleFlags(BaseModel):
    """

    Attributes
    ----------
    hidden : bool, optional
        Whether the rule is displayed to users. Internal rules are hidden.
    cluster_only : bool, optional
        Whether the rule is applicable in the cluster deployment mode only.
    can_be_disabled : bool, optional
        Whether users are allowed to disable this rule. A few rules are mandatory.
    can_create_additional_plans : bool, optional
        Whether this rule may create additional query execution plans.
    disabled_by_default : bool, optional
        Whether the optimizer considers this rule by default.
    enterprise_only : bool, optional
        Whether the rule is available in the Enterprise Edition only.

    """

    hidden: Optional[bool]
    cluster_only: Optional[bool]
    can_be_disabled: Optional[bool]
    can_create_additional_plans: Optional[bool]
    disabled_by_default: Optional[bool]
    enterprise_only: Optional[bool]

    @classmethod
    def parse_from_dict(cls, d: dict) -> Optional[QueryOptimizerRuleFlags]:
        if not d:
            return None

        return QueryOptimizerRuleFlags(
            hidden=d.get("hidden", None),
            cluster_only=d.get("clusterOnly", None),
            can_be_disabled=d.get("canBeDisabled", None),
            can_create_additional_plans=d.get("canCreateAdditionalPlans", None),
            disabled_by_default=d.get("disabledByDefault", None),
            enterprise_only=d.get("enterpriseOnly", None),
        )


class QueryOptimizerRule(BaseModel):
    """
    Attributes
    ----------
    name : str, optional
        The name of the optimizer rule as seen in query explain outputs.
    flags : QueryOptimizerRuleFlags, optional
        Flags for this rule.
    """

    name: Optional[str]
    flags: Optional[QueryOptimizerRuleFlags]

    @classmethod
    def parse_from_dict(cls, d: dict) -> Optional[QueryOptimizerRule]:
        if not d:
            return None

        return QueryOptimizerRule(
            name=d.get("name", None),
            flags=QueryOptimizerRuleFlags.parse_from_dict(d.get("flags", None)),
        )
