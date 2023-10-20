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
"""Session module for Peak API."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from peak import exceptions
from peak.constants import DOWNLOAD_CHUNK_SIZE, ContentType, HttpMethods, Stage
from peak.handler import Handler
from peak.helpers import get_base_domain
from peak.logger import logger

DEFAULT_SESSION = None


def _get_default_session() -> Session:
    """Get the global default session object. Creates one if not already created and re-uses it.

    Returns:
        Session: The default session object
    """
    global DEFAULT_SESSION  # noqa: PLW0603
    if DEFAULT_SESSION is None:
        logger.debug("Creating DEFAULT_SESSION object")
        DEFAULT_SESSION = Session()

    logger.debug("DEFAULT_SESSION already present, reusing the object")
    return DEFAULT_SESSION


class Session:
    """A session stores credentials which are used to authenticate the requests.

    By default, a DEFAULT_SESSION is created which reads the credentials from the env variables.
    Custom Session objects can be created and used if you want to work with multiple tenants.
    """

    auth_token: str
    stage: Stage
    base_domain: str
    handler: Handler

    def __init__(
        self,
        auth_token: Optional[str] = None,
        stage: Optional[str] = None,
    ) -> None:
        """Initialize a session for the Peak API.

        Args:
            auth_token (str | None): Authentication token. Both API Key and Bearer tokens are supported.
                Picks up from `API_KEY` environment variable if not provided.
            stage (str | None): Name of the stage where tenant is created. Default is `prod`.
        """
        self.base_domain: str = ""
        self._set_auth_token(auth_token)
        self._set_stage(stage)
        self._set_base_domain()
        self.handler = Handler()

    def create_request(
        self,
        endpoint: str,
        method: HttpMethods,
        content_type: ContentType,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        ignore_files: Optional[list[str]] = None,
        subdomain: Optional[str] = "service",
    ) -> Any:
        """Prepares a request to be sent over the network.

        Adds auth_token to the headers and creates URL using STAGE.
        To be used with endpoints which returns JSON parsable response.

        Args:
            endpoint (str): The endpoint to send the request to.
            method (HttpMethods): The HTTP method to use.
            content_type (ContentType): The content type of the request.
            params (Dict[str, Any], optional): params to send to the request, defaults to None
            body (Dict[str, Any], optional): body to send to the request, defaults to None
            path (Optional[str] optional): path to the file or folder that will be compressed and used as artifact, required for multipart requests.
            ignore_files(Optional[list[str]]): Ignore files to be used when creating artifact, used only for multipart requests.
            subdomain (Optional[str]): Subdomain for the endpoint. Defaults to `service`.

        Returns:
            Any: response dict object.
        """
        headers: Dict[str, str] = {"Authorization": self.auth_token}
        base_domain: str = get_base_domain(stage=self.stage.value, subdomain=subdomain)
        url: str = f"{base_domain}/{endpoint}"
        return self.handler.make_request(
            url,
            method,
            content_type=content_type,
            headers=headers,
            params=params or {},
            body=body or {},
            path=path,
            ignore_files=ignore_files,
            session_meta={
                "stage": self.stage,
            },
        ).json()

    def create_generator_request(
        self,
        endpoint: str,
        method: HttpMethods,
        content_type: ContentType,
        response_key: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        subdomain: Optional[str] = "service",
    ) -> Iterator[Dict[str, Any]]:
        """Prepares a request to be sent over the network.

        Adds auth_token to the headers and creates URL using STAGE.
        Returns an iterator which automatically handles pagination and returns a new page at each iteration.
        To be used with list endpoints only, which returns `pageNumber`, `pageCount` keys in response.

        # noqa: DAR201

        Args:
            endpoint (str): The endpoint to send the request to.
            method (HttpMethods): The HTTP method to use.
            content_type (ContentType): The content type of the request.
            response_key (str): key in the response dict which contains actual list data.
            params (Optional[Dict[str, Any]]): params to send to the request.
            body (Optional[Dict[str, Any]]): body to send to the request.
            path (Optional[str]): path to the file or folder that will be compressed and used as artifact.
            subdomain (Optional[str]): Subdomain for the endpoint. Defaults to `service`.

        Yields:
            Iterator[Dict[str, Any]]: paginated response json, element wise.

        Raises:
            StopIteration: There are no more pages to list
        """
        page_number: int = 1
        page_count: int = 1
        params = params or {}
        while page_number <= page_count:
            params = {**params, "pageNumber": page_number}
            response = self.create_request(
                endpoint,
                method,
                content_type,
                params=params,
                body=body,
                path=path,
                subdomain=subdomain,
            )
            page_count = response["pageCount"]
            yield from response[response_key]
            page_number += 1
        return f"No more {response_key} to list"

    def create_download_request(
        self,
        endpoint: str,
        method: HttpMethods,
        content_type: ContentType,
        download_path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Prepares a request to be sent over the network.

        Adds auth_token to the headers and creates URL using STAGE.
        To be used for file download requests.

        Args:
            endpoint (str): The endpoint to send the request to.
            method (HttpMethods): The HTTP method to use.
            content_type (ContentType): The content type of the request.
            download_path (str): Path where the downloaded file will be stored.
            params (Dict[str, Any], optional): params to send to the request, defaults to None
            body (Dict[str, Any], optional): body to send to the request, only used in multipart requests, defaults to None

        Raises:
            InvalidPathException: The download_path is invalid.
        """
        headers: Dict[str, str] = {"Authorization": self.auth_token}
        url: str = f"{self.base_domain}/{endpoint}"
        response: Any = self.handler.make_request(
            url,
            method,
            content_type=content_type,
            headers=headers,
            params=params or {},
            body=body or {},
            request_kwargs={
                "stream": True,
                "allow_redirects": True,
            },
        )
        try:
            with Path(download_path).open("wb") as fd:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    fd.write(chunk)
        except IsADirectoryError:
            raise exceptions.InvalidPathException(
                download_path,
                "Path should include the name with which the downloaded file should be stored.",
            ) from None

    def _set_base_domain(self) -> None:
        self.base_domain = get_base_domain(stage=self.stage.value)

    def _set_auth_token(self, auth_token: Optional[str]) -> None:
        if auth_token is not None:
            self.auth_token = auth_token
            return

        logger.info("auth_token not given, searching for API_KEY in env variables")
        if not os.environ.get("API_KEY"):
            raise exceptions.MissingEnvironmentVariableException(env_var="API_KEY")
        self.auth_token = os.environ["API_KEY"]

    def _set_stage(self, stage: Optional[str]) -> None:
        if stage is not None:
            self.stage = Stage(stage)
            return

        logger.info("stage not given, searching for STAGE in env variables")
        if not os.environ.get("STAGE"):
            logger.info("STAGE environment variable is not set, defaulting to PROD")
            self.stage = Stage.PROD
            return
        self.stage = Stage(os.environ["STAGE"])


__all__: List[str] = ["Session", "_get_default_session"]
