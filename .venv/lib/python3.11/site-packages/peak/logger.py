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
"""Logger for the Peak SDK."""
from __future__ import annotations

import logging
import sys
from typing import List

from peak.constants import LOG_FORMAT, LOG_LEVELS

logger: logging.Logger = logging.getLogger("peak-sdk")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(LOG_FORMAT)
logger.addHandler(stream_handler)
logger.propagate = False


def set_log_level(log_level: LOG_LEVELS) -> None:
    """Update log level for Peak logger.

    Args:
        log_level (LOG_LEVELS): new logging level for the logger.
    """
    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(log_level)


__all__: List[str] = ["logger"]
