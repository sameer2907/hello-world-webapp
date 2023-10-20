#
# # Copyright © 2023 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
"""Workflow client module."""
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.exceptions import InvalidParameterException
from peak.helpers import (
    combine_dictionaries,
    map_user_options,
    variables_to_dict,
)
from peak.session import Session


class Workflow(BaseClient):
    """Client class for interacting with workflows resource."""

    BASE_ENDPOINT = "workflows/api/v1"

    @overload
    def list_workflows(
        self: Workflow,
        workflow_status: Optional[List[str]] = None,
        last_execution_status: Optional[List[str]] = None,
        last_modified_by: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]:
        ...

    @overload
    def list_workflows(
        self: Workflow,
        workflow_status: Optional[List[str]] = None,
        last_execution_status: Optional[List[str]] = None,
        last_modified_by: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]:
        ...

    def list_workflows(
        self: Workflow,
        workflow_status: Optional[List[str]] = None,
        last_execution_status: Optional[List[str]] = None,
        last_modified_by: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        name: Optional[str] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve the list of workflows.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/get-workflows>`__

        Args:
            workflow_status (List[str] | None): List of status to filter workflow. Default is None.
            last_execution_status (str | None): The last execution status of the workflow. Default is None.
            last_modified_by (str | None): The user who last modified the workflow. Default is None.
            page_size (int | None): The number of workflows per page.
            page_number (int | None): The page number to retrieve. Only used when return_iterator is False.
            name (str | None): Search workflows by name.
            return_iterator (bool): Whether to return an iterator object or list of workflows for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: An iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
            StopIteration: There are no more pages to list
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/workflows/"
        params: Dict[str, Any] = {
            "pageSize": page_size,
            "workflowStatus": workflow_status,
            "lastExecutionStatus": last_execution_status,
            "lastModifiedBy": last_modified_by,
            "searchTerm": name,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="workflows",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def create_workflow(self: Workflow, body: Dict[str, Any]) -> Dict[str, int]:
        """Create a new workflow. Workflows with only standard steps are supported.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/create-workflow>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the workflow config.

        Returns:
            Dict[str, int]: Id of the newly created workflow.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/workflows/"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )

    def create_or_update_workflow(self: Workflow, body: Dict[str, Any]) -> Dict[str, int]:
        """Creates a new workflow or updates an existing workflow based on workflow name.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/create-workflow>`__

        Args:
            body (Dict[str, Any]): A dictionary containing the workflow config.

        Returns:
            Dict[str, int]: Id of the newly created or updated workflow.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        workflow_name = body["name"] if "name" in body else ""
        response = (
            {}
            if not len(workflow_name)
            else self.list_workflows(page_size=100, return_iterator=False, name=workflow_name)
        )
        filtered_workflows = list(
            filter(lambda workflow: workflow.get("name", "") == workflow_name, response.get("workflows", [])),
        )

        if len(filtered_workflows) > 0:
            workflow_id = filtered_workflows[0]["id"]
            return self.update_workflow(workflow_id=workflow_id, body=body)

        return self.create_workflow(body=body)

    def describe_workflow(
        self: Workflow,
        workflow_id: int,
    ) -> Dict[str, Any]:
        """Retrieve details of a specific workflow. Workflows with only standard steps can be described.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/describe-workflow>`__

        Args:
            workflow_id (int): The ID of the workflow to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the details of the workflow.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/workflows/{workflow_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def update_workflow(self: Workflow, workflow_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow. Workflows with only standard steps are supported.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/update-workflow>`__

        Args:
            workflow_id (int): The ID of the workflow to update.
            body (dict): A dictionary containing the updated workflow details.

        Returns:
            Dict[str, int]: Id of the updated workflow.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            ConflictException: The workflow is in a conflicting state while deleting.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.PUT, f"{self.BASE_ENDPOINT}/workflows/{workflow_id}"
        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )

    def patch_workflow(  # noqa: C901, PLR0912
        self: Workflow,
        workflow_id: int,
        body: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        branch: Optional[str] = None,
        token: Optional[str] = None,
        command: Optional[str] = None,
        image_id: Optional[int] = None,
        image_version_id: Optional[int] = None,
        instance_type_id: Optional[int] = None,
        storage: Optional[str] = None,
        step_timeout: Optional[int] = None,
        clear_image_cache: Optional[bool] = None,
        step_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing workflow. Workflows with only standard steps are supported.

        - This function allows to efficiently modify trigger details, watchers, workflow name, and specific step attributes such as repository URL, branch, token, image ID, version ID etc.

        - By specifying `step_names`, we can globally update specified steps with provided parameters, streamlining the update process. If `step_names` is not provided, all the steps for that workflow would be updated.

        - Alternatively, we can utilize the **body** parameter to selectively modify individual step attributes across different steps. With this, we can also add new steps to the workflow by providing the parameters required by the step.

        - If both body and specific parameters are used, the latter takes precedence.

        Args:
            workflow_id (int): The ID of the workflow to patch.
            body (Dict[str, Any] | None): A dictionary containing the updated workflow details.
            name (str | None): The name of the workflow.
            repository (str | None): URL of the repository containing the required files.
            branch (str | None): The branch of the repository to use.
            token (str | None): The token to be used to access the repository.
            command (str | None): The command to run when workflow step is executed.
            image_id (int | None): The ID of the image to use for the workflow step.
            image_version_id (int | None): The ID of the image version to use for the workflow step.
            instance_type_id (int | None): The ID of the instance type to use for the workflow step.
            storage (str | None): The storage to use for the workflow step in GB. For example, "10GB".
            step_timeout (int | None): Time after which the step timeouts.
            clear_image_cache (boolean | None): Whether to clear image cache on workflow execution.
            step_names (List[str] | None): The workflow steps to update. If not provided, all steps will be updated.

        Returns:
            Dict[str, Any]: A dictionary containing the workflow ID.

        Raises:
            InvalidParameterException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            ConflictException: The workflow is in a conflicting state while deleting.
            InternalServerErrorException: The server failed to process the request.
        """
        user_options = variables_to_dict(
            name,
            repository,
            branch,
            token,
            command,
            image_id,
            image_version_id,
            instance_type_id,
            storage,
            step_timeout,
            clear_image_cache,
        )

        if not user_options and not body:
            raise InvalidParameterException(
                message="Request body or at least one parameter must be provided to update the workflow.",
            )

        workflow_details = self.describe_workflow(workflow_id=workflow_id)

        for step_name in step_names or []:
            if step_name not in workflow_details["steps"]:
                raise InvalidParameterException(
                    message=f"Step name {step_name} does not exist for workflow {workflow_id}",
                )

        # First, we modify steps in workflow details to the expected format for the API

        step_keys_to_skip = ["imageName", "imageVersion"]

        updated_workflow_details: Dict[str, Any] = {
            "name": workflow_details["name"],
            "tags": workflow_details["tags"],
            "watchers": workflow_details["watchers"],
            "triggers": [],
            "steps": {},
        }

        if workflow_details.get("triggers"):
            triggers = workflow_details["triggers"]
            if triggers[0].get("cron"):
                updated_workflow_details["triggers"] = [{"cron": triggers[0]["cron"]}]
            elif triggers[0].get("webhook"):
                updated_workflow_details["triggers"] = [{"webhook": True, "webhookPolicy": "preserve"}]

        for step_name, step in workflow_details["steps"].items():
            updated_workflow_details["steps"][step_name] = {}
            for key, value in step.items():
                if key not in step_keys_to_skip and value is not None:
                    updated_workflow_details["steps"][step_name][key] = value
                if key == "repository" and not value.get("token", {}):
                    updated_workflow_details["steps"][step_name]["repository"].pop("token", None)
                if key == "parameters" and "env" in value:  ## Describe workflow returns env as a list of dictionaries
                    env = {}
                    for env_dict in value["env"]:
                        env.update(env_dict)
                    updated_workflow_details["steps"][step_name]["parameters"]["env"] = env

        ## Second, we merge updated_workflow_details with the user provided body

        updated_body: Dict[str, Any] = updated_workflow_details.copy()

        if body:
            for key, value in body.items():
                if key == "steps":
                    for step_name, step in body["steps"].items():
                        updated_body["steps"][step_name] = combine_dictionaries(
                            updated_body["steps"].get(step_name, {}),
                            step,
                            nested_keys_to_skip=["env"],
                        )
                else:
                    updated_body[key] = value

        ## Finally, we update the body with the user provided parameters

        if user_options.get("repository"):
            user_options["url"] = user_options["repository"]
            del user_options["repository"]

        keys_mapping: Dict[str, str] = {
            "url": "repository",
            "branch": "repository",
            "token": "repository",
            "instanceTypeId": "resources",
            "storage": "resources",
        }

        user_options = map_user_options(user_options, keys_mapping)

        if user_options:
            if user_options.get("name"):
                updated_body["name"] = user_options["name"]
                del user_options["name"]
            for step_name in updated_body["steps"]:
                if not step_names or step_name in step_names:
                    updated_body["steps"][step_name] = combine_dictionaries(
                        updated_body["steps"].get(step_name, {}),
                        user_options,
                    )

        return self.update_workflow(workflow_id=workflow_id, body=updated_body)

    def delete_workflow(
        self: Workflow,
        workflow_id: int,
    ) -> Dict[None, None]:
        """Delete a workflow.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/delete-workflow>`__

        Args:
            workflow_id (int): The ID of the workflow to delete.

        Returns:
            dict: Empty dictionary object.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            ConflictException: If the workflow is in a conflicting state while deleting.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/workflows/{workflow_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def execute_workflow(
        self: Workflow,
        workflow_id: int,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Start a workflow run.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/execute-workflow>`__

        Args:
            workflow_id (int): ID of the workflow to delete.
            body: (Dict[str, Any]): The parameters to be passed while running the workflow. More details can be found in the API doc - https://service.peak.ai/workflows/api-docs/index.htm#/Workflows/execute-workflow

        Returns:
            Dict[str, str]: Execution ID of the run.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            ConflictException: The workflow is in a conflicting state and new run cannot be started.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/workflows/{workflow_id}/execute"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )

    def list_resources(
        self: Workflow,
    ) -> List[Dict[str, Any]]:
        """Lists all available resources for the workflows.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Resources/get-resources>`__

        Returns:
            Dict[str, Any]: A dictionary containing the list of available resources.

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            ConflictException: The workflow is in a conflicting state and new run cannot be started.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/resources"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def get_default_resource(
        self: Workflow,
    ) -> Dict[str, Any]:
        """Default resource values that will be used in case `resource` key is not provided for the workflows.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Resources/get-default-resources>`__

        Returns:
            Dict[str, Any]: Default resource values

        Raises:
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/resources/defaults"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    @overload
    def list_executions(
        self: Workflow,
        workflow_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]:
        ...

    @overload
    def list_executions(
        self: Workflow,
        workflow_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]:
        ...

    def list_executions(
        self: Workflow,
        workflow_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Lists executions for the given workflow.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/workflows/api-docs/index.htm#/Executions/get-workflow-executions>`__

        Args:
            workflow_id (int): ID of the workflow to fetch executions.
            date_from (str | None): The date after which the executions should be included (in ISO format). Defaults to None
            date_to (str | None): The date till which the executions should be included (in ISO format). Defaults to None
            page_size (int | None): Number of executions per page.
            page_number (int | None): Page number to fetch. Only used when return_iterator is False.
            return_iterator (bool): Whether to return an iterator object or list of executions for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: An iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given workflow does not exist.
            InternalServerErrorException: The server failed to process the request.
            StopIteration: There are no more pages to list
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/workflows/executions/{workflow_id}"

        params: Dict[str, Any] = {
            "dateTo": date_to,
            "dateFrom": date_from,
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="executions",
                params=params,
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )


def get_client(session: Optional[Session] = None) -> Workflow:
    """Returns a Workflow client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Workflow: the workflow client object
    """
    return Workflow(session)


__all__: List[str] = ["get_client"]
