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
"""Supported Log handlers."""
from enum import Enum


class LogHandler(Enum):
    """Enumeration of log handlers to be used in logging.

    Each enum member corresponds to a specific handler defined in the logging module.
    This enum provides a convenient way to specify handlers when configuring loggers.

    Attributes:
        CONSOLE: Represents a console handler, intended for displaying logs in the console.
        FILE: Represents a file handler, intended for writing logs to a file.
    """

    CONSOLE = "CONSOLE"
    FILE = "FILE"
