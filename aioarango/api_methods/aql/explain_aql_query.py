from typing import Optional, Sequence, MutableMapping, Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Json, Jsons, Result


class ExplainAQLQuery(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # If the query is valid, the server will respond with HTTP 200 and
        # return the optimal execution plan in the plan attribute of the response.
        # If option allPlans was set in the request, an array of plans will be returned
        # in the allPlans attribute instead.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
        # or if the query contains a parse error. The body of the response will
        # contain the error details embedded in a JSON object.
        # Omitting bind variables if the query references any will also result
        # in an HTTP 400 error.
        404,
        # The server will respond with HTTP 404 in case a non-existing collection is
        # accessed in the query.
    )

    async def explain(
        self,
        query: str,
        all_plans: bool = False,
        max_plans: Optional[int] = None,
        opt_rules: Optional[Sequence[str]] = None,
        bind_vars: Optional[MutableMapping[str, str]] = None,
    ) -> Result[Union[Json, Jsons]]:
        """
        Explain an AQL query.


        A `JSON` object with these properties is required:
            - **query**: the query which you want explained; If the query references any bind variables,
              these must also be passed in the attribute bindVars. Additional
              options for the query can be passed in the options attribute.

            - **bindVars** (object): key/value pairs representing the bind parameters.

            - **options**:

                - **allPlans**: if set to `true`, all possible execution plans will be returned. The default is `false`, meaning only the optimal plan will
                  be returned.
                - **maxNumberOfPlans**: an optional maximum number of plans that the optimizer is
                  allowed to generate. Setting this attribute to a low value allows to put a
                  cap on the amount of work the optimizer does.
                - **optimizer**:

                    - **rules** (string): A list of to-be-included or to-be-excluded optimizer rules can be put into this
                      attribute, telling the optimizer to include or exclude specific rules. To disable
                      a rule, prefix its name with a `-`, to enable a rule, prefix it with a `+`. There is
                      also a pseudo-rule `all`, which matches all optimizer rules. -`all `disables all rules.




        Notes
        -----
        - To explain how an AQL query would be executed on the server, the query string
          can be sent to the server via an HTTP POST request. The server will then validate
          the query and create an execution plan for it. The execution plan will be
          returned, but the query will not be executed.

        - The execution plan that is returned by the server can be used to estimate the
          probable performance of the query. Though the actual performance will depend
          on many different factors, the execution plan normally can provide some rough
          estimates on the amount of work the server needs to do in order to actually run
          the query.

        - By default, the explain operation will return the optimal plan as chosen by
          the query optimizer The optimal plan is the plan with the lowest total estimated
          cost. The plan will be returned in the attribute **plan** of the response object.
          If the option **allPlans** is specified in the request, the result will contain
          all plans created by the optimizer. The plans will then be returned in the
          attribute **plans**.

        - The result will also contain an attribute **warnings**, which is an array of
          warnings that occurred during optimization or execution plan creation. Additionally,
          a stats attribute is contained in the result with some optimizer statistics.
          If **allPlans** is set to `false`, the result will contain an attribute cacheable
          that states whether the query results can be cached on the server if the query
          result cache were used. The **cacheable** attribute is not present when **allPlans**
          is set to `true`.

        - Each plan in the result is a JSON object with the following attributes:

            - **nodes**: the array of execution nodes of the plan.
            - **estimatedCost**: the total estimated cost for the plan. If there are multiple
              **plans**, the optimizer will choose the plan with the lowest total cost.
            - **collections**: an array of collections used in the query.
            - **rules**: an array of rules the optimizer applied.
            - **variables**: array of variables used in the query (note: this may contain
              internal variables created by the optimizer)







        Parameters
        ----------
        query : str
            Query to explain.
        all_plans : bool, default : False
            If set to `True`, all possible execution plans are
            returned in the result. If set to `False`, only the optimal plan
            is returned.
        max_plans : int, optional
            Total number of plans generated by the optimizer.
        opt_rules : list of str, optional
            List of optimizer rules.
        bind_vars : MutableMapping, optional
            Bind variables for the query.

        Returns
        -------
        Result
            Execution plan, or plans if **all_plans** was set to `True`.

        Raises
        ------
        ValueError
            If the query has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if not query:
            raise ValueError(f"`query` has invalid value: `{query}`")

        options: Json = {"allPlans": all_plans}
        if max_plans is not None:
            options["maxNumberOfPlans"] = max_plans
        if opt_rules is not None:
            options["optimizer"] = {"rules": opt_rules}

        data: Json = {"query": query, "options": options}
        if bind_vars is not None:
            data["bindVars"] = bind_vars

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/explain",
            data=data,
        )

        def response_handler(response: Response) -> Union[Json, Jsons]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            if "plan" in response.body:
                return response.body["plan"]
            else:
                return response.body["plans"]

        return await self.execute(request, response_handler)
