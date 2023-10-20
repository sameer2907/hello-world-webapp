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
"""Version command for peak-cli."""
import platform
import sys

import typer
from peak import __version__
from rich.console import Console

console = Console()


def display_version(print_version: bool) -> None:
    """Display version of this tool.

    Args:
        print_version (bool): Print version and exit

    Raises:
        Exit: Exit the program
    """
    if print_version:
        peak_version = __version__
        major = sys.version_info.major
        minor = sys.version_info.minor
        micro = sys.version_info.micro
        python_version = f"Python=={major}.{minor}.{micro}"
        platform_version = f"System=={platform.system()}({platform.release()})"
        console.print(f"peak-cli=={peak_version}\n{python_version}\n{platform_version}")
        raise typer.Exit()
