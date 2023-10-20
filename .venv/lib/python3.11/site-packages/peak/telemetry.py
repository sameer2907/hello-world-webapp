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
"""Decorator for sending telemetry data for each request."""
from __future__ import annotations

import platform
import threading
import uuid
from contextlib import suppress
from functools import wraps
from typing import Any, Callable, Dict, Optional

import requests

import peak.config
from peak.constants import ContentType, HttpMethods, Stage
from peak.exceptions import BaseHttpException
from peak.helpers import get_base_domain

from ._version import __version__

F = Callable[..., requests.Response]
session_id = str(uuid.uuid4())


def get_status_code(error: Optional[Exception]) -> int | None:
    """It takes an exception object and returns the status code associated with it.

    Args:
        error (Optional[Exception]): The exception object to check

    Returns:
        int | None: The status code related to the error or None if no status code found
    """
    if not error:
        return 200

    if isinstance(error, BaseHttpException):
        return error.STATUS_CODE

    return None


def telemetry(make_request: F) -> F:
    """A decorator that wraps over the make_request function to send telemetry requests as required.

    Args:
        make_request (F): The make_request function to wrap in the decorator

    Returns:
        F: the wrapped function that sends telemetry data for each request
    """

    def get_telemetry_url(session_meta: Optional[Dict[str, Any]] = None) -> str:
        """Returns the telemetry url for the given stage.

        Args:
            session_meta (Optional[Dict[str, Any]]): Session metadata object that contains information like stage

        Returns:
            str: The telemetry URL
        """
        stage = Stage.PROD
        if session_meta:
            stage = session_meta["stage"] if "stage" in session_meta else Stage.PROD
        base_domain = get_base_domain(stage.value, "service")
        return f"{base_domain}/resource-usage/api/v1/telemetry"

    def get_telemetry_data() -> Dict[str, Any]:
        return {
            "sdkVersion": __version__,
            "os": platform.platform(),
            "hostname": platform.uname().node,
            "pythonVersion": platform.python_version(),
            "sessionId": session_id,
            "requestId": str(uuid.uuid4()),
        }

    @wraps(make_request)
    def wrapper(
        self: Any,
        url: str,
        method: HttpMethods,
        content_type: ContentType,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        request_kwargs: Optional[Dict[str, int | bool | str | float]] = None,
        ignore_files: Optional[list[str]] = None,
        session_meta: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """A decorator that wraps over the make_request function to send telemetry requests as required.

        Args:
            self (Any): the object instance of Handler class on which the make_request call is being made
            url (str): url to send the request to
            method (HttpMethods): The HTTP method to use, e.g. get, post, put, delete
            content_type (ContentType): content type of the request
            headers (Dict[str, str]): headers to send with the request
            params (Dict[str, Any]): params to send to the request
            body (Dict[str, Any]): body to send to the request
            path (str): path to the file or folder that will be compressed and used as artifact, defaults to None
            request_kwargs(Dict[str, int | bool | str | float] | None): extra arguments to be passed when making the request.
            ignore_files(Optional[list[str]]): Ignore files to be used when creating artifact
            session_meta(Dict[str, Any]): Metadata about the session object, like - stage

        Returns:
            requests.Response: response json

        Raises:
            BaseHttpException: The http request failed.
            Exception: Some other error occurred.
        """

        def make_telemetry_request(
            res: Optional[requests.Response] = None,
            error: Optional[Exception] = None,
        ) -> None:
            telemetry_url = get_telemetry_url(session_meta)

            telemetry_body = {
                "response": res.json() if method != HttpMethods.GET and res else None,
                "error": str(error) if error else None,
                "url": url,
                "requestMethod": method.value,
                "statusCode": get_status_code(error),
                "source": peak.config.SOURCE.value,
                **get_telemetry_data(),
            }

            with suppress(Exception):
                make_request(
                    self,
                    telemetry_url,
                    HttpMethods.POST,
                    ContentType.APPLICATION_JSON,
                    headers=headers,
                    body=telemetry_body,
                )

        def trigger_usage_collection(
            res: Optional[Any] = None,
            error: Optional[Exception] = None,
        ) -> None:
            if peak.config.DEBUG_MODE:
                return

            thr = threading.Thread(
                target=make_telemetry_request,
                kwargs={
                    "res": res,
                    "error": error,
                },
            )

            thr.start()

        try:
            custom_headers = {f"x-peak-{key}": value for (key, value) in get_telemetry_data().items()}
            custom_headers = {
                **custom_headers,
                **(headers or {}),
            }

            res = make_request(
                self,
                url,
                method,
                content_type=content_type,
                headers=custom_headers,
                params=params or {},
                body=body or {},
                path=path,
                ignore_files=ignore_files,
                request_kwargs=request_kwargs,
            )

            trigger_usage_collection(res=res)
        except Exception as e:
            trigger_usage_collection(error=e)
            raise
        else:
            return res

    return wrapper
