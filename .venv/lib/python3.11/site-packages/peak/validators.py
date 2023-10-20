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
"""Validators for peak sdk."""
from __future__ import annotations

import os
import tempfile
from typing import List

from peak.constants import MAX_ARTIFACT_SIZE_MB, MB
from peak.exceptions import FileLimitExceededException


def check_file_size(fh: tempfile.SpooledTemporaryFile[bytes], max_size: float = MAX_ARTIFACT_SIZE_MB) -> None:
    """Check file is smaller than 10MB."""
    file_size: int = _get_file_size(fh)
    if file_size > max_size * MB:
        raise FileLimitExceededException(max_size=max_size)


def _get_file_size(fh: tempfile.SpooledTemporaryFile[bytes]) -> int:
    """Get file size in bytes."""
    old_pos: int = fh.tell()
    fh.seek(0, os.SEEK_END)
    file_size_bytes: int = fh.tell()
    fh.seek(old_pos)
    return file_size_bytes


__all__: List[str] = ["check_file_size"]
