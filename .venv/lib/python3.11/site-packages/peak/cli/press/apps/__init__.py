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
"""Apps Module."""
import typer
from peak.cli.press.apps import deployments, specs

app = typer.Typer(
    help="Create and manage App specs and deployments.",
    short_help="Create and manage App specs and deployments.",
)
app.add_typer(
    specs.app,
    name="specs",
    help="Create and manage App specs which are blueprint for Peak Apps.",
    short_help="Create and manage App Specs.",
)
app.add_typer(
    deployments.app,
    name="deployments",
    help="Create and manage App deployments which are the actual instance of the App.",
    short_help="Create and manage App Deployments.",
)
