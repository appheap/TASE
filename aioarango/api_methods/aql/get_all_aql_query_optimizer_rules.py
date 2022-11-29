from typing import List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, QueryOptimizerRule
from aioarango.typings import Result


class GetAllAQLQueryOptimizerRules(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # is returned if the list of optimizer rules can be retrieved successfully.
    )

    async def get_all_aql_query_optimizer_rules(self) -> Result[List[QueryOptimizerRule]]:
        """
        Return all AQL optimizer rules.

        Notes
        -----
        On success, A list of json documents with these Properties is returned:
            - **name**: The name of the optimizer rule as seen in query explain outputs.
            - **flags**:

                - **hidden**: Whether the rule is displayed to users. Internal rules are hidden.
                - **clusterOnly**: Whether the rule is applicable in the cluster deployment mode only.
                - **canBeDisabled**: Whether users are allowed to disable this rule. A few rules are mandatory.
                - **canCreateAdditionalPlans**: Whether this rule may create additional query execution plans.
                - **disabledByDefault**: Whether the optimizer considers this rule by default.
                - **enterpriseOnly**: Whether the rule is available in the `Enterprise Edition` only.


        Returns
        -------
        Result
            List of all query optimizer rules.


        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/query/rules",
        )

        def response_handler(response: Response) -> List[QueryOptimizerRule]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            items = []
            for rule in response.body:
                items.append(QueryOptimizerRule.parse_from_dict(rule))
            return items

        return await self.execute(request, response_handler)
