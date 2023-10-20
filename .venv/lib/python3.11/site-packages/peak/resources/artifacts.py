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
"""Artifact client module."""
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, overload

from peak.base_client import BaseClient
from peak.constants import ArtifactInfo, ContentType, HttpMethods
from peak.session import Session


class Artifact(BaseClient):
    """Artifact client class."""

    BASE_ENDPOINT = "artifacts/api/v1"

    @overload
    def list_artifacts(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[False],
    ) -> Dict[str, Any]:
        ...

    @overload
    def list_artifacts(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: Literal[True] = True,
    ) -> Iterator[Dict[str, Any]]:
        ...

    def list_artifacts(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        *,
        return_iterator: bool = True,
    ) -> Iterator[Dict[str, Any]] | Dict[str, Any]:
        """Retrieve a list of artifacts.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/get_api_v1_artifacts>`__

        Args:
            page_size (int | None): The number of artifacts per page.
            page_number (int | None): The page number to retrieve. Only used when return_iterator is False.
            return_iterator (bool): Whether to return an iterator object or a list of artifacts, defaults to True.

        Returns:
            Iterator[Dict[str, Any]] | Dict[str, Any]: an iterator object which returns an element per iteration, until there are no more elements to return.
            If `return_iterator` is set to False, a dictionary containing the list and pagination details is returned instead.

            Set `return_iterator` to True if you want automatic client-side pagination, or False if you want server-side pagination.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/artifacts/"
        params = {"pageSize": page_size}

        if return_iterator:
            return self.session.create_generator_request(
                endpoint,
                method,
                content_type=ContentType.APPLICATION_JSON,
                params=params,
                response_key="artifacts",
            )

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params={**params, "pageNumber": page_number},
        )

    def create_artifact(
        self,
        name: str,
        artifact: ArtifactInfo,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new artifact.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/post_api_v1_artifacts>`__

        Args:
            name (str): Name of the artifact.
            artifact (ArtifactInfo):    Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.
            description (str | None): A brief description of the artifact.

        Returns:
            Dict[str, Any]: `Id` and `Version` of the created artifact.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            PayloadTooLargeException: The artifact exceeds maximum size.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.POST, f"{self.BASE_ENDPOINT}/artifacts/"
        body: Dict[str, Any] = {"name": name, "description": description}

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body=body,
            path=artifact["path"],
            ignore_files=artifact.get("ignore_files"),
        )

    def describe_artifact(
        self,
        artifact_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve details of a specific artifact with list of its versions.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/get_api_v1_artifacts__artifactId_>`__

        Args:
            artifact_id (str): The ID of the artifact to retrieve.
            page_number (int | None): The page number to retrieve.
            page_size (int | None): The number of versions per page.

        Returns:
            Dict[str, Any]: a dictionary containing the details of the artifact.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/artifacts/{artifact_id}"
        params = {"pageNumber": page_number, "pageSize": page_size}

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params=params,
        )

    def delete_artifact(self, artifact_id: str) -> Dict[None, None]:
        """Delete an artifact with all its versions.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/delete_api_v1_artifacts__artifactId_>`__

        Args:
            artifact_id (str): The ID of the artifact to delete.

        Returns:
            dict: Empty dictionary object.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/artifacts/{artifact_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def create_artifact_version(
        self,
        artifact_id: str,
        artifact: ArtifactInfo,
    ) -> Dict[str, int]:
        """Create a new version of the artifact.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/put_api_v1_artifacts__artifactId_>`__

        Args:
            artifact_id (str): ID of the artifact for which a new version is to be created.
            artifact (ArtifactInfo):    Mapping of artifact attributes that specifies how the artifact will be generated,
                                        it accepts two keys `path`, which is required and `ignore_files` which is optional, and defaults to `.dockerignore`, it is strongly advised that users use `ignore_files` when generating artifacts to avoid copying any extra files in artifact.

        Returns:
            Dict[str, int]: version number.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            PayloadTooLargeException: The artifact exceeds maximum size.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.PUT, f"{self.BASE_ENDPOINT}/artifacts/{artifact_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.MULTIPART_FORM_DATA,
            body={},
            path=artifact["path"],
            ignore_files=artifact.get("ignore_files"),
        )

    def update_artifact(self, artifact_id: str, body: Dict[str, Any]) -> Dict[None, None]:
        """Update an artifact's metadata.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/patch_api_v1_artifacts__artifactId_>`__

        Args:
            artifact_id (str): ID of the artifact to be updated.
            body (Dict[str, Any]): dictionary containing new metadata for artifact.

        Returns:
            dict: Empty dict object.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.PATCH, f"{self.BASE_ENDPOINT}/artifacts/{artifact_id}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            body=body,
        )

    def delete_artifact_version(self, artifact_id: str, version: int) -> Dict[None, None]:
        """Delete a version of an artifact.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/delete_api_v1_artifacts__artifactId___version_>`__

        Args:
            artifact_id (str): ID of the artifact.
            version (int): Artifact version number to delete.

        Returns:
            dict: Empty dict object.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            UnprocessableEntityException: The server was unable to process the request.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.DELETE, f"{self.BASE_ENDPOINT}/artifacts/{artifact_id}/{version}"

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
        )

    def download_artifact(self, artifact_id: str, download_path: str, version: Optional[int] = None) -> None:
        """Download a version of the artifact.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/artifacts/api-docs/index.htm#/artifacts/get_api_v1_artifacts__artifactId__download>`__

        Args:
            artifact_id (str): ID of the artifact to download.
            download_path (str): Path (including filename) where the downloaded file will be stored.
            version (int | None): Artifact version to download. If no version is given then latest version is downloaded.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/artifacts/{artifact_id}"

        endpoint = f"{endpoint}/download" if version is None else f"{endpoint}/{version}/download"

        self.session.create_download_request(
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            download_path=download_path,
        )


def get_client(session: Optional[Session] = None) -> Artifact:
    """Returns an Artifact client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Artifact: the artifact client object
    """
    return Artifact(session)


__all__: List[str] = ["get_client"]
