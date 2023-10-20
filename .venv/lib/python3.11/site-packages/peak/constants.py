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
"""Contains constants which are used across SDK modules."""
from __future__ import annotations

from enum import Enum, auto
from logging import Formatter
from typing import Any, List, Literal, TypedDict

MB = 2**20
MAX_ARTIFACT_SIZE_MB: int = 10
DOWNLOAD_CHUNK_SIZE = 128

LOG_FORMAT = Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
LOG_LEVELS = Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG"]


class _ArtifactGlob(TypedDict, total=False):
    ignore_files: list[str]


class ArtifactInfo(_ArtifactGlob):
    """TypedDict with all required fields for artifact creation.

    path: Path to the file or folder that will be compressed and used as artifact.
    ignore_files: Ignore files to be used when creating artifact.
    """

    path: str


class AutoName(Enum):
    """Enum with automatic name() values."""

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: List[Any]) -> str:  # noqa: ARG004
        """Automatically generate enum values from names."""
        return str(name).lower()


class Stage(AutoName):
    """Enum of all supported platform stages."""

    DEV = auto()
    LATEST = auto()
    TEST = auto()
    BETA = auto()
    PROD = auto()
    PARVATI = auto()


class ContentType(Enum):
    """Enum of supported content type for http request to API."""

    APPLICATION_JSON = "application/json"
    MULTIPART_FORM_DATA = "multipart/form-data"


class HttpMethods(AutoName):
    """Enum of supported HTTP methods."""

    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()


class Sources(AutoName):
    """Enum of the sources for telemetry call."""

    SDK = auto()
    CLI = auto()


__all__: List[str] = [
    "MB",
    "MAX_ARTIFACT_SIZE_MB",
    "DOWNLOAD_CHUNK_SIZE",
    "LOG_FORMAT",
    "ArtifactInfo",
    "Stage",
    "ContentType",
    "HttpMethods",
    "LOG_LEVELS",
    "Sources",
]
