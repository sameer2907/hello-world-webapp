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
"""Compression module to create zip file to be used as artifact."""
from __future__ import annotations

import contextlib
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable, Iterator, Optional, Set

from pathspec import PathSpec

from peak import constants, exceptions, output

ZIP_COMPRESSION = zipfile.ZIP_DEFLATED


@contextlib.contextmanager
def compress(path: str, ignore_files: Optional[list[str]] = None) -> Iterator[tempfile.SpooledTemporaryFile[bytes]]:
    """Creates compressed zip of the files in path.

    Args:
        path (str): Path of the folder to create zip file.
        ignore_files (Optional[list[str]]): Ignorefiles to use when creating zip file.

    Yields:
        Iterator[tempfile.SpooledTemporaryFile[bytes]]: Bytes of the zip file in chunks.

    Raises:
        InvalidPathException: Given path is invalid and cannot be traversed.
        FileLimitExceededException: Compressed directory size exceeded the max limits.
    """
    path_obj = Path(path)
    if not path_obj.is_dir():
        raise exceptions.InvalidPathException(path, "Either the path does not exist or is not a directory.")
    included_files = get_files_to_include(path, ignore_files)
    parent_directories: Set[Path] = set()

    with tempfile.SpooledTemporaryFile() as tmp_file:
        with zipfile.ZipFile(tmp_file, "w", compression=ZIP_COMPRESSION) as zf:
            for file in included_files:
                zf.write(path_obj / file, file)
                parent_directories.update(Path(file).parents)
                if tmp_file.tell() > constants.MAX_ARTIFACT_SIZE_MB * constants.MB:
                    raise exceptions.FileLimitExceededException(constants.MAX_ARTIFACT_SIZE_MB)

            # include directories as API backend need directories explicitly included
            relative_root_path = Path(".")
            if relative_root_path in parent_directories:
                parent_directories.remove(relative_root_path)
            for directory in parent_directories:
                zf.write(path_obj / directory, directory)

        tmp_file.seek(0)
        yield tmp_file


def print_zip_content(zip_file: tempfile.SpooledTemporaryFile[bytes]) -> None:
    """Prints content of the zip file to stdout.

    Args:
        zip_file (BinaryIO): Opened zip file in binary format.
    """
    with zipfile.ZipFile(zip_file, "r") as zf:
        zf.printdir()


def get_files_to_include(path: str, ignore_files: Optional[list[str]] = None) -> Iterator[str]:
    """Get a list of file paths to be included.

    Args:
        path (str): Root path from where to start the traversal.
        ignore_files (Optional[list[str]]): Path of ignorefiles to use, defaults to .dockerignore.

    Yields:
        Iterator[str]: Path of files to be included.
    """
    path_obj = Path(path)
    ignore_pathspec = _load_ignore_patterns(path_obj, ignore_files)
    yield from ignore_pathspec.match_tree(path, follow_links=True)


def _reverse_pattern(pattern: str) -> str:
    """Converts the inclusion pattern to exclusion and vice-versa.

    This is needed because PathSpec will return the files that matches the patterns
    but we want the opposite, i.e. we want to exclude the files which match the
    patterns in ignorefiles.

    Args:
        pattern (str): Pattern to process

    Returns:
        str: Processed pattern
    """
    pattern = pattern.strip()
    if not pattern or pattern.startswith("#"):
        return pattern
    if pattern.startswith("!"):
        return pattern[1:]
    return "!" + pattern


def _load_ignore_patterns(path_obj: Path, ignore_files: Optional[list[str]]) -> PathSpec:
    """Reads ignorefiles and loads all patterns into PathSpec.

    Args:
        path_obj (Path): Root path relative to which ignore_files would be searched.
        ignore_files (list[str]): Path of ignorefiles relative to where the script is running

    Returns:
        PathSpec: PathSpec object with all patterns

    Raises:
        InvalidPathException: Given path is invalid and cannot be traversed.
    """
    if ignore_files is None or len(ignore_files) == 0:
        # use .dockerignore as default if no ignore file is provided
        default_ignore = path_obj / ".dockerignore"
        ignore_files = [os.fspath(default_ignore)] if default_ignore.exists() else []

    all_patterns: list[str] = [
        "*",
    ]  # include everything, apply ignore patterns on top of it, if this is given nothing will be included
    for ignore_file in ignore_files:
        ignore_file_path = path_obj / ignore_file
        normalized_ignore_path = ignore_file_path.resolve().relative_to(path_obj.resolve())
        # ignorefiles should only be at root level
        if len(normalized_ignore_path.parents) != 1:
            raise exceptions.InvalidPathException(
                ignore_file,
                "Ignore file should be present at root level of given path.",
            )

        patterns = ignore_file_path.open("r").read().splitlines()
        all_patterns.extend(
            map(
                _reverse_pattern,
                patterns,
            ),
        )
    return PathSpec.from_lines("gitwildmatch", all_patterns)


def print_file_tree(files: Iterable[str]) -> None:
    """Prints list of files in tree format.

    Args:
        files (list[str]): List of file paths
    """
    writer = output.Writer(ignore_debug_mode=True)
    files_dict = _build_files_dict(files)

    def _print_tree(files_dict: dict[str, dict], indent: str) -> None:  # type: ignore[type-arg]
        for key, value in files_dict.items():
            writer.write(f"{indent}{key}")
            if value:
                new_indent = "|   " if indent else "├── "
                _print_tree(value, new_indent + indent)

    _print_tree(files_dict, "")


def _build_files_dict(files: Iterable[str]) -> dict[str, dict]:  # type: ignore[type-arg]
    """Builds a nested dictionary from list of files.

    Args:
        files (list[str]): List of file paths to process.

    Returns:
        dict[str, dict]: Nested dict file tree structure.
    """
    files_dict: dict[str, dict] = {}  # type: ignore[type-arg]
    for f in files:
        components = os.path.normpath(f).split(os.sep)
        current_dir = files_dict
        for directory in components[:-1]:
            if directory not in current_dir:
                current_dir[directory] = {}
            current_dir = current_dir[directory]
        if components[-1] not in current_dir:
            current_dir[components[-1]] = {}
    return files_dict
