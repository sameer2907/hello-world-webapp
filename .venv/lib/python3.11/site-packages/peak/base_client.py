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
"""Base client class."""
from __future__ import annotations

from typing import List, Optional

from peak.session import Session, _get_default_session


class BaseClient:
    """Base client class."""

    session: Session

    def __init__(self, session: Optional[Session] = None) -> None:
        """Assigns a session to the client. If no session is provided, a default session is used.

        Args:
            session (Optional[Session]): Session object of a tenant. Defaults to None.

        Raises:
            TypeError: If the session object is invalid.
        """
        invalid_session_error = f"Invalid session object, expected Session but got {type(session)}"
        if session is not None:
            if not isinstance(session, Session):
                raise TypeError(invalid_session_error)
            self.session = session
        else:
            self.session = _get_default_session()


__all__: List[str] = ["BaseClient"]
