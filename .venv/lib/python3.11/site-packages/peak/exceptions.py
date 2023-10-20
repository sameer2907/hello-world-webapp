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
"""Exceptions for the Peak API."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Type


class PeakBaseException(Exception):
    """Base exception class for the Peak SDK."""

    ...


class HttpExceptionsRegistryMeta(type):
    """Registry metaclass."""

    REGISTRY: Dict[int, Any] = defaultdict(lambda: Exception)

    def __new__(
        cls: "Type[HttpExceptionsRegistryMeta]",
        name: str,
        bases: Tuple[Any, ...],
        attrs: Dict[str, Any],
    ) -> HttpExceptionsRegistryMeta:
        """This method runs whenever a new class (that uses this class as its metaclass) is defined.

        This method automatically adds the exception classes to its Registry.
        It uses the `STATUS_CODE` attribute of the class as key and the class itself as value in registry.
        Ref: https://charlesreid1.github.io/python-patterns-the-registry.html

        Args:
            name (str): Name of the child class
            bases (tuple): Tuple of the child class's inheritance tree
            attrs (dict): Name and value pairs of all the attributes defined in the child class

        Returns:
            HttpExceptionsRegistryMeta: the child class itself, forward annotated for type checking
        """
        new_cls: "HttpExceptionsRegistryMeta" = type.__new__(cls, name, bases, attrs)
        status_code: Optional[int] = attrs.get("STATUS_CODE", None)
        if status_code:
            cls.REGISTRY[status_code] = new_cls
        return new_cls


class BaseHttpException(PeakBaseException, metaclass=HttpExceptionsRegistryMeta):
    """Base registry class for registering all exceptions."""

    STATUS_CODE: ClassVar[int]


class BadRequestException(BaseHttpException):
    """The provided inputs are invalid."""

    STATUS_CODE = 400


class UnauthorizedException(BaseHttpException):
    """The authentication credentials are invalid or expired."""

    STATUS_CODE = 401


class ForbiddenException(BaseHttpException):
    """User does not have permissions to perform the operation."""

    STATUS_CODE = 403


class NotFoundException(BaseHttpException):
    """Resource does not exist."""

    STATUS_CODE = 404


class ConflictException(BaseHttpException):
    """There is a conflict with the current state of the target resource."""

    STATUS_CODE = 409


class PayloadTooLargeException(BaseHttpException):
    """The provided file size is larger than the maximum limits."""

    STATUS_CODE = 413


class UnprocessableEntityException(BaseHttpException):
    """The server understands the request, but it was unable to process the contained instructions."""

    STATUS_CODE = 422


class InternalServerErrorException(BaseHttpException):
    """The server encountered an unexpected condition that prevented it from fulfilling the request."""

    STATUS_CODE = 500


class InvalidPathException(PeakBaseException):
    """The provided path is invalid and cannot be processed."""

    def __init__(self, path: str | Path, message: str = "") -> None:
        """Throw exception with custom message.

        Args:
            path (str | Path): Path which is invalid.
            message (str): Any extra message to add to exception.
        """
        super().__init__(f"Invalid path: {path!r}. {message}")


class MissingEnvironmentVariableException(PeakBaseException):
    """Required environment variable not found."""

    def __init__(self, env_var: str, *, message: str = "") -> None:
        """Throw exception with custom message.

        Args:
            env_var (str): Name of env variable which is not present.
            message (str): Any extra message to add to exception.
        """
        error_message: str = f"{env_var} environment variable is not set or is empty."
        super().__init__(f"{error_message} {message}")


class FileLimitExceededException(PeakBaseException):
    """Limits on the file are exceeded."""

    def __init__(self, max_size: int | float, *, message: str = "", units: str = "MB") -> None:
        """Throw exception with custom message.

        Args:
            max_size (int): Maximum size of the file.
            message (str): Additional message to add to exception.
            units (str): Units of the maximum size.
        """
        error_message: str = f"Compressed directory size is over {max_size}{units}."
        super().__init__(f"{error_message} {message}")


class InvalidTemplateException(PeakBaseException):
    """The given template is invalid and could not be compiled."""

    def __init__(self, message: str) -> None:
        """Throw exception with custom message.

        Args:
            message (str): Message of the exception.
        """
        super().__init__(message)


class BadParameterException(PeakBaseException):
    """Raises exception for invalid parameters."""

    def __init__(self, param: str, *, message: str = "") -> None:
        """Throw exception with custom message.

        Args:
            param (str): Raw parameter input from the CLI.
            message (str): Additional message to add to exception.
        """
        error_message: str = f"Unable to parse: {param}"
        super().__init__(f"{error_message} {message}")


class InvalidParameterException(PeakBaseException):
    """Raises exception for invalid parameters."""

    def __init__(self, *, message: str = "") -> None:
        """Throw exception with custom message.

        Args:
            message (str): Additional message to add to exception.
        """
        super().__init__(message)


__all__: List[str] = [
    "HttpExceptionsRegistryMeta",
    "BaseHttpException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "PayloadTooLargeException",
    "UnprocessableEntityException",
    "InternalServerErrorException",
    "InvalidPathException",
    "MissingEnvironmentVariableException",
    "FileLimitExceededException",
    "BadParameterException",
    "InvalidParameterException",
]
