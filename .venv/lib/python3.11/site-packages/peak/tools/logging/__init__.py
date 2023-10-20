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
"""Logging module, a wrapper around `structlog <https://www.structlog.org/en/stable/>`_ library."""

from __future__ import annotations

import logging
import os
from typing import Any, List, MutableMapping, Optional, Union

import structlog

from .log_handler import LogHandler
from .log_level import LogLevel
from .utils import mask_nested_pii_data

__title__ = "logging"
__author__ = "PEAK AI"
__license__ = "Apache License, Version 2.0"
__copyright__ = "2023, Peak AI"
__status__ = "production"
__date__ = "28 August 2023"

__all__: list[str] = [
    "get_logger",
    "LogLevel",
    "PeakLogger",
    "LogHandler",
]


# ---------------------------------------------------------------------------
# Utility private functions
# ---------------------------------------------------------------------------


def _pii_masking_processor(
    _: str,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Masks sensitive PII data present in event_dict."""
    return mask_nested_pii_data(event_dict)


def _default_context_processor(
    _: str,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Add the standard attribute to the event_dict."""
    attributes_to_add: dict[str, Any] = {
        "source": "peak-sdk",
        "runtime": os.getenv("PEAK_RUNTIME"),
        "press_deployment_id": os.getenv("PRESS_DEPLOYMENT_ID"),
        "run_id": os.getenv("PEAK_RUN_ID"),
        "exec_id": os.getenv("PEAK_EXEC_ID"),
        "stage": os.getenv("STAGE"),
        "tenant_name": os.getenv("TENANT_NAME", os.getenv("TENANT")),
        "tenant_id": os.getenv("TENANT_ID"),
        "api_name": os.getenv("PEAK_API_NAME"),
        "api_id": os.getenv("PEAK_API_ID"),
        "step_name": os.getenv("PEAK_STEP_NAME"),
        "step_id": os.getenv("PEAK_STEP_ID"),
        "webapp_name": os.getenv("PEAK_WEBAPP_NAME"),
        "webapp_id": os.getenv("PEAK_WEBAPP_ID"),
        "workflow_name": os.getenv("PEAK_WORKFLOW_NAME"),
        "workflow_id": os.getenv("PEAK_WORKFLOW_ID"),
        "workspace_name": os.getenv("PEAK_WORKSPACE_NAME"),
        "workspace_id": os.getenv("PEAK_WORKSPACE_ID"),
        "image_name": os.getenv("PEAK_IMAGE_NAME"),
        "image_id": os.getenv("PEAK_IMAGE_ID"),
    }

    for attr, value in attributes_to_add.items():
        if value:
            event_dict[attr] = value

    return event_dict


# ---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to the structlog.
# ---------------------------------------------------------------------------


def get_logger(
    name: Optional[str] = None,
    level: LogLevel = LogLevel.INFO,
    pretty_print: Optional[bool] = None,
    handlers: Optional[List[LogHandler]] = None,
    file_name: Optional[str] = None,
) -> PeakLogger:
    """Return a logger with the specified settings.

    Args:
        name (Optional[str], optional): Name of the logger. Defaults to None.
        level (LogLevel): Log level. Defaults to LogLevel.INFO.
        pretty_print (Optional[bool], optional): Whether to enable pretty printing for JSON format. Defaults to False.
        handlers (Optional[List[Handlers]], optional): List of log handlers (CONSOLE, FILE). Defaults to CONSOLE.
        file_name (Optional[str], optional): Filename for FILE handler. Required if FILE handler is used. Defaults to None.

    Returns:
        PeakLogger: A logger instance configured with the specified settings.

    Raises:
        ValueError: If the `file_name` is not provided for FILE handler.

    """
    _log_level: int = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else level.value
    _processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _pii_masking_processor,
        _default_context_processor,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.EventRenamer("message"),
    ]
    if pretty_print:
        _processors.append(structlog.processors.JSONRenderer(indent=2, sort_keys=True))
    else:
        _processors.append(structlog.processors.JSONRenderer(indent=None, sort_keys=True))
    handlers_list: list[Any] = []
    if not handlers or LogHandler.CONSOLE in handlers:
        handlers_list.append(logging.StreamHandler())  # Console handler
    if handlers and LogHandler.FILE in handlers:
        if file_name:
            handlers_list.append(logging.FileHandler(file_name))  # File handler
        else:
            msg = "filename must be provided for FILE handler."
            raise ValueError(msg)
    logging.basicConfig(level=_log_level, handlers=handlers_list, format="")
    structlog.configure(
        processors=_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(_log_level),
        cache_logger_on_first_use=True,
    )

    return PeakLogger(structlog.get_logger(name))


# ---------------------------------------------------------------------------
# Wrapper Logger class
# ---------------------------------------------------------------------------


class PeakLogger:
    """Wrapper class for logging with various log levels."""

    def __init__(self, logger: Any) -> None:
        """Initialize with a logger object.

        Args:
            logger (Any): Logger object to wrap.
        """
        self._logger = logger

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a DEBUG level message.

        Args:
            message (str): The log message.
            *args: Additional positional arguments to be passed to the logger.
            **kwargs: Additional keyword arguments to be passed to the logger.
        """
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an INFO level message.

        Args:
            message (str): The log message.
            *args: Additional positional arguments to be passed to the logger.
            **kwargs: Additional keyword arguments to be passed to the logger.
        """
        self._logger.info(message, *args, **kwargs)

    def warn(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a WARNING level message.

        Args:
            message (str): The log message.
            *args: Additional positional arguments to be passed to the logger.
            **kwargs: Additional keyword arguments to be passed to the logger.
        """
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR level message.

        Args:
            message (str): The log message.
            *args: Additional positional arguments to be passed to the logger.
            **kwargs: Additional keyword arguments to be passed to the logger.
        """
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a CRITICAL level message.

        Args:
            message (str): The log message.
            *args: Additional positional arguments to be passed to the logger.
            **kwargs: Additional keyword arguments to be passed to the logger.
        """
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR level message with exception info.

        Args:
            message (str): The log message.
            *args: Additional positional arguments to be passed to the logger.
            **kwargs: Additional keyword arguments to be passed to the logger.
        """
        self._logger.exception(message, *args, **kwargs)

    def bind(self, context: Union[dict[str, Any], None] = None, **kwargs: Any) -> None:
        """Bind contextual information to the logger, enriching log messages.

        This method allows attaching context data to the logger, such as additional information
        or system details, to provide more context in log messages.

        Args:
            context (Union[dict[str, Any], None]): A dictionary or None for contextual information.
            **kwargs: Additional key-value pairs to enhance context.
        """
        if context is None:
            context = {}

        if kwargs:
            # file deepcode ignore AttributeLoadOnNone: false positive
            context.update(kwargs)

        self._logger = self._logger.bind(**context)

    def unbind(self, keys: list[str]) -> None:
        """Unbind specified keys from the logger's context.

        Args:
            keys (list[str]): List of keys to unbind.
        """
        context: dict[str, Any] | dict[Any, Any] = structlog.get_context(self._logger)

        for key in keys:
            if key in context:
                del context[key]

        # Rebind the modified context to the logger
        self._logger = self._logger.bind(**context)

    def set_log_level(self, level: LogLevel) -> None:
        """Set the log level of the root logger.

        Args:
            level (LogLevel): Log level to set.
        """
        if self._is_valid_log_level(level):
            logging.getLogger().setLevel(level.value)

    def _is_valid_log_level(self, level: LogLevel) -> bool:
        """Check if a given log level is valid."""
        return level in LogLevel
