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
"""Specs client module."""
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session


class Spec(BaseClient):
    """Client class for interacting with Specs."""

    BASE_ENDPOINT = "v1/specs"

    @overload
    def list_specs(
        self,
        status: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        kind: Optional[str] = None,
        term: Optional[str] = None,
        sort: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]:
        ...

    @overload
    def list_specs(
        self,
        status: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        kind: Optional[str] = None,
        term: Optional[str] = None,
        sort: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]:
        ...

    def list_specs(
        self,
        status: Optional[List[str]] = None,
        featured: Optional[bool] = None,
        kind: Optional[str] = None,
        term: Optional[str] = None,
        sort: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """List all published App & Block Specs ordered by creation date. Returns info on the latest release of each spec.

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Specs/get_v1_specs>`__

        Args:
            status (List[str] | None): List of statuses to filter specs.
            featured (bool | None): Whether to only return featured specs.
            kind (str | None): Return specs of the kind specified.
            term (str | None): Return specs containing the specified term in name, title, description and summary.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response,
                defaults to `[]`. Valid fields are `createdAt`, `createdBy`, `name` and `title`.
            scope (List[str] | None): List of scopes to only return specs of those scopes. Valid values are `private`, `public` and `shared`.
            page_size (int | None): Number of specs to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of specs for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: An iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server encountered an unexpected condition that
                prevented it from fulfilling the request.
            StopIteration: There are no more pages to list.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/"
        params: Dict[str, Any] = {
            "status": status,
            "featured": featured,
            "kind": kind,
            "term": term,
            "sort": sort,
            "scope": scope,
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="specs",
                params=params,
                subdomain="press",
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
            subdomain="press",
        )

    @overload
    def list_spec_release_deployments(
        self,
        spec_id: str,
        version: str,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]:
        ...

    @overload
    def list_spec_release_deployments(
        self,
        spec_id: str,
        version: str,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]:
        ...

    def list_spec_release_deployments(
        self,
        spec_id: str,
        version: str,
        status: Optional[List[str]] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        sort: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Get all deployments of a App or Block spec release (ordered by most recently created to oldest).

        REFERENCE:
            🔗 `API Documentation <https://press.peak.ai/api-docs/index.htm#/Specs/get_v1_specs__specId__releases__release__deployments>`__

        Args:
            spec_id (str): The ID of the App or Block spec.
            version (str): The release version of the spec in valid semantic versioning format.
            status (List[str] | None): List of statuses to filter deployments.
            name (str | None): String to filter deployments by name.
            title (str | None): String to filter deployments by title.
            sort (List[str] | None): List of fields with desired ordering in the format `[<field>:<order>, ...]`,
                where `order` is one of `['asc', 'desc']` and field is an ordered parameter within the response.
                Valid fields are `createdAt`, `createdBy` and `name`.
            page_size (int | None): Number of specs to include per page.
            page_number (int | None): The page number to retrieve. Only used when `return_iterator` is False.
            return_iterator (bool): Whether to return an iterator object or list of specs for a specified page number, defaults to True.

        Returns:
            Iterator[Dict[str, Any] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given spec does not exist.
            InternalServerErrorException: the server encountered an unexpected condition that
                prevented it from fulfilling the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/{spec_id}/releases/{version}/deployments"

        params: Dict[str, Any] = {
            "status": status,
            "name": name,
            "title": title,
            "sort": sort,
            "pageSize": page_size,
        }

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                response_key="deployments",
                params=params,
                subdomain="press",
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
            subdomain="press",
        )


def get_client(session: Optional[Session] = None) -> Spec:
    """Returns a Spec client.

    Args:
        session (Optional[Session]): A Session Object. If no session is provided, a default session is used.

    Returns:
        Spec: the Spec client object
    """
    return Spec(session)


__all__: List[str] = ["get_client"]
