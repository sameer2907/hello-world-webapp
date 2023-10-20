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
"""Template module which handles all things related to templates."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import jinja2
import yaml
from jinja2 import Environment
from jinja2.ext import Extension

from peak import exceptions
from peak.helpers import remove_none_values


def _parse_jinja_template(template_path: Path, params: Dict[str, Any]) -> str:
    """Read, parse and render the Jinja template text."""
    jinja_loader = _CustomJinjaLoader()
    jinja_env = jinja2.Environment(  # TODO: show warning if variable not found in params  # noqa: TD002, TD003, RUF100
        loader=jinja_loader,
        autoescape=False,  # noqa: S701
        extensions=[_IncludeWithIndentation],
    )
    jinja_template: jinja2.Template = jinja_env.get_template(str(template_path))
    return jinja_template.render(params, os_env=os.environ)


def load_template(file: Union[Path, str], params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Load a template file through `Jinja` into a dictionary.

    This function performs the following steps:
        * Passes the `YAML` file to be loaded and parsed through **`Jinja`**
        * **`Jinja`** substitutes the variables with their values as they are found in `params`
        * Loads any other files that are referenced using the Jinja `{% include %}` directive, if it is present.
        * Updates the `context` key path within `image` definitions with respect to its relative parent file path.
        * Loads the rendered YAML file into a `dictionary`.

    Args:
        file (Union[Path, str]): Path to the templated `YAML` file to be loaded.
        params (Dict[str, Any] | None, optional): Named parameters to be passed to Jinja. Defaults to `{}`.

    Returns:
        Dict[str, Any]: Dictionary containing the rendered YAML file
    """
    params = {} if params is None else params
    file = Path(file)
    template: str = _parse_jinja_template(file, params)
    parsed_data: Dict[str, Any] = yaml.safe_load(template)
    return remove_none_values(parsed_data)


class _CustomJinjaLoader(jinja2.BaseLoader):
    """Custom Jinja loader class which handles the include directive.

    Inspired from the jinja2.FileSystemLoader class.
    """

    def __init__(
        self,
        search_path: Optional[List[str]] = None,
        encoding: str = "utf-8",
    ) -> None:
        """Initialize all variables.

        Args:
            search_path (List[str] | None, optional): Path(s) of the directory to search file in.
            encoding (str): Encoding to use when reading files. Defaults to "utf-8".
        """
        if search_path is None:
            search_path = ["."]

        self.search_path: List[str] = [os.fspath(p) for p in search_path]
        self.encoding: str = encoding
        self.root_file_path: Optional[str] = None
        self.build_context_regex: re.Pattern[str] = re.compile(r"^(\s*context\s*:\s+)(.+)$", flags=re.MULTILINE)
        self.seen_files: Set[Path] = set()

    def _update_image_build_context(self, source: str, file_parent_dir: str) -> str:
        """Updates the context key in image definition to the relative path of the file where it is being imported.

        Args:
            source (str): Content of the file
            file_parent_dir (str): Directory where the file is located

        Returns:
            str: Content of the file with updated context value if present.
        """
        if self.root_file_path is None:
            return source

        def substitute(match: re.Match[str]) -> str:
            """Substitute the context key with the relative path of the file where it is being imported."""
            context_path: str = match.group(2)
            context_path = context_path.strip().strip('"').strip("'")
            final_path: str = str(Path(file_parent_dir) / Path(context_path))
            final_relative_path: str = os.path.relpath(final_path, self.root_file_path)
            return f"{match.group(1)}{final_relative_path}"

        return self.build_context_regex.sub(substitute, source)

    def get_source(self, _: jinja2.Environment, template_path: str) -> Tuple[str, str, Callable[[], bool]]:
        """Searches and reads the template file.

        Args:
            _ (jinja2.Environment): Jinja environment variable.
            template_path (str): Path of the template file.

        # noqa: DAR401
        Raises:
            jinja2.TemplateNotFound: The template file is not found on given path.

        Returns:
            Tuple[str, str, Callable[[], bool]]: Tuple containing 3 variables
                1. Content of the template file
                2. Normalized path where the file was found
                3. Function which checks if the file was modified (not useful in this case)
        """
        template_path = template_path.strip()
        for search_path in self.search_path:
            # Use posixpath even on Windows to avoid "drive:" or UNC
            # segments breaking out of the search directory.
            file_path: str = str(Path(search_path) / Path(template_path))

            if Path(file_path).is_file():
                break
        else:
            error_msg: str = f"File does not exist at path: {template_path!r}"
            raise jinja2.TemplateNotFound(error_msg)

        file_path_obj = Path(file_path)
        absolute_file_path: Path = file_path_obj.resolve()

        if absolute_file_path in self.seen_files:
            error_msg = f"Failed to render template, circular include directive found at {absolute_file_path!r}"
            raise exceptions.InvalidTemplateException(error_msg)

        file_parent_dir = str(file_path_obj.parent)
        with Path(file_path).open(encoding=self.encoding) as f:
            contents: str = f.read()
            contents = self._update_image_build_context(contents, file_parent_dir)

        self.seen_files.add(absolute_file_path)
        self.search_path.append(file_parent_dir)
        if self.root_file_path is None:
            self.root_file_path = file_parent_dir

        return contents, os.path.normpath(file_path), lambda: True


class _IncludeWithIndentation(Extension):
    """Override Jinja include directive to preserve indentation.

    Inspired from: https://github.com/stereobutter/jinja2_workarounds
    """

    @staticmethod
    def _include_statement_regex(block_start: str, block_end: str) -> re.Pattern[str]:
        """Get the compiled regex for finding the include directives in template."""
        return re.compile(
            rf"""
            (^.*)
            (?=
                (
                    {re.escape(block_start)}
                    (?P<block_start_modifier> [\+|-]?)
                    (?P<statement>
                        \s*include
                        \s+.*?
                    )
                    (?P<block_end_modifier> [\+|-]?)
                    {re.escape(block_end)}
                )
            )
            .*$
            """,
            flags=re.MULTILINE | re.VERBOSE,
        )

    def preprocess(self, source: str, _: Optional[str], __: Optional[str] = None) -> str:
        """Enclose all include directives.

        For all the regex matches in the text, enclose the include block
        with indent filter blocks and return updated text.
        """
        env: Environment = self.environment

        block_start: str = env.block_start_string
        block_end: str = env.block_end_string
        pattern: re.Pattern[str] = self._include_statement_regex(block_start=block_start, block_end=block_end)
        re.compile("\n")

        def add_indentation_filter(match: re.Match[str]) -> str:
            """Add indent filter to include blocks."""
            content_before_include: str | Any = match.group(1)
            include_statement: str | Any = match.group("statement").replace("indent content", "")

            block_start_modifier: str | Any = match.group("block_start_modifier") or ""
            block_end_modifier: str | Any = match.group("block_end_modifier") or ""

            start_filter: str = (
                f"{block_start + block_start_modifier} filter indent({len(content_before_include)}) {block_end}"
            )
            include_block: str = f"{block_start} {include_statement} {block_end}"
            end_filter: str = f"{block_start} endfilter {block_end_modifier + block_end}"

            return f"{content_before_include}{start_filter}{include_block}{end_filter}"

        return pattern.sub(add_indentation_filter, source)


__all__: List[str] = ["load_template"]
