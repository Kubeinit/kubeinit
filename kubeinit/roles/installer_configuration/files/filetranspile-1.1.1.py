#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Take a fake root and appends them into a provided ignition configuration."""

import abc
import argparse
import json
import os
import pathlib
import stat
from urllib.parse import quote

import yaml

__version__ = "1.1.1"


class FileTranspilerError(Exception):
    """Base exception for FileTranspiler errors."""

    pass


class IgnitionSpec(abc.ABC):
    """Base class for IgnitionSpec classes."""

    def __init__(self, ignition_cfg, cli_args):
        """
        Initialize a spec merger.

        :param ignition_cfg: loaded ignition config json
        :type ignition_cfg: dict
        :param cli_args: Command line arguments
        :type cli_args: argparse.Namespace
        """
        self.ignition_cfg = ignition_cfg
        self.fake_root = cli_args.fake_root
        self.dereference_symlinks = cli_args.dereference_symlinks

    @abc.abstractmethod
    def file_to_ignition(self, file_path, file_contents, mode):
        """
        Turn a file into an ignition snippet.

        :param file_path: Path to where the file should be placed.
        :type file_path: str
        :param file_contents: The raw contents of the file
        :type file_contents: str
        :param mode: Octal mode to use (will translate to decimal)
        :type mode: int
        :returns: Ignition config snippet
        :rtype: dict
        """
        raise NotImplementedError("Must be implemented in a subclass")

    @abc.abstractmethod
    def link_to_ignition(self, file_path, target_path):
        """
        Turn a symbolic link into an ignition snippet.

        :param file_path: Path to where the file should be placed.
        :type file_path: str
        :param target_path: The target path of the symbolic link
        :type target_path: str
        :returns: Ignition config snippet
        :rtype: dict
        """
        raise NotImplementedError("Must be implemented in a subclass")

    def merge_with_ignition(self, ignition_cfg, files, links):
        """
        Merge file snippets into the ignition config.

        :param ignition_cfg: Ignition structure to append to
        :type ignition_cfg: dict
        :param files: List of Ignition file snippets
        :type files: list
        :returns: Merged ignition dict
        :rtype: dict
        """
        # Check that the storage exists
        storage_check = ignition_cfg.get("storage")
        if storage_check is None:
            ignition_cfg["storage"] = {}

        if files:
            # Check that files entry exists
            files_check = ignition_cfg["storage"].get("files")
            if files_check is None:
                ignition_cfg["storage"]["files"] = []

            for a_file in files:
                ignition_cfg["storage"]["files"].append(a_file)

        if links:
            # Check that links entry exists
            links_check = ignition_cfg["storage"].get("links")
            if links_check is None:
                ignition_cfg["storage"]["links"] = []

            for a_link in links:
                ignition_cfg["storage"]["links"].append(a_link)

        return ignition_cfg

    def merge(self):
        """
        Merge the fakeroot into the ignition config.

        :returns: The merged ignition config
        :rtype: dict
        """
        # Walk through the files and append them for merging
        all_files = []
        all_links = []
        for root, _, files in os.walk(self.fake_root):
            for file in files:
                path = os.path.sep.join([root, file])
                host_path = path.replace(self.fake_root, "")
                if not host_path.startswith(os.path.sep):
                    host_path = os.path.sep + host_path
                if os.path.islink(path):
                    # If we are dereferencing symlinks then treat it as
                    # a file
                    if self.dereference_symlinks:
                        source_path = str(pathlib.Path(path).resolve())
                        # Ensure the path is within the fakeroot
                        if not source_path.startswith(os.path.realpath(self.fake_root)):
                            raise FileTranspilerError(
                                "link: {} is not in the fake root: {}".format(
                                    source_path, self.fake_root
                                )
                            )
                        mode = oct(stat.S_IMODE(os.stat(source_path).st_mode))
                        with open(source_path, "r") as file_obj:
                            snippet = self.file_to_ignition(
                                host_path, file_obj.read(), mode
                            )
                            all_files.append(snippet)
                    else:
                        target_path = os.readlink(path)
                        snippet = self.link_to_ignition(host_path, target_path)
                        all_links.append(snippet)
                else:
                    mode = oct(stat.S_IMODE(os.stat(path).st_mode))
                    with open(path, "r") as file_obj:
                        snippet = self.file_to_ignition(
                            host_path, file_obj.read(), mode
                        )
                    all_files.append(snippet)

        # Merge the and output the results
        merged_ignition = self.merge_with_ignition(
            self.ignition_cfg, all_files, all_links
        )
        return merged_ignition


class SpecV2(IgnitionSpec):
    """Spec v2 implementation for merging files."""

    def file_to_ignition(self, file_path, file_contents, mode):
        """
        Turn a file into an ignition snippet.

        :param file_path: Path to where the file should be placed.
        :type file_path: str
        :param file_contents: The raw contents of the file
        :type file_contents: str
        :param mode: Octal mode to use (will translate to decimal)
        :type mode: int
        :returns: Ignition config snippet
        :rtype: dict
        """
        return {
            "path": file_path,
            "filesystem": "root",
            "mode": int(mode, 8),
            "contents": {"source": "data:,{}".format(quote(file_contents))},
        }

    def link_to_ignition(self, file_path, target_path):
        """
        Turn a symbolic link into an ignition snippet.

        :param file_path: Path to where the file should be placed.
        :type file_path: str
        :param target_path: The target path of the symbolic link
        :type target_path: str
        :returns: Ignition config snippet
        :rtype: dict
        """
        return {
            "path": file_path,
            "filesystem": "root",
            "target": target_path,
            "hard": False,
        }


class SpecV3(IgnitionSpec):
    """Spec v3 implementation for merging files."""

    def file_to_ignition(self, file_path, file_contents, mode):
        """
        Turn a file into an ignition snippet.

        :param file_path: Path to where the file should be placed.
        :type file_path: str
        :param file_contents: The raw contents of the file
        :type file_contents: str
        :param mode: Octal mode to use (will translate to decimal)
        :type mode: int
        :returns: Ignition config snippet
        :rtype: dict
        """
        return {
            "path": file_path,
            "mode": int(mode, 8),
            "overwrite": True,
            "contents": {"source": "data:,{}".format(quote(file_contents))},
        }

    def link_to_ignition(self, file_path, target_path):
        """
        Turn a symbolic link into an ignition snippet.

        :param file_path: Path to where the file should be placed.
        :type file_path: str
        :param target_path: The target path of the symbolic link
        :type target_path: str
        :returns: Ignition config snippet
        :rtype: dict
        """
        return {
            "path": file_path,
            "overwrite": True,
            "target": target_path,
            "hard": False,
        }


def loader(ignition_file):
    """
    Load the ignition json into a structure.

    Senses the ignition spec version, and
    returns the structure and it's spec class.

    :param ignition_file: Path to the ignition file to parse
    :type ignition_file: str
    :returns: The ignition structure and spec class
    :rtype: tuple
    :raises: FileTranspilerError
    """
    try:
        with open(ignition_file, "r") as f:
            ignition_cfg = json.load(f)
        ignition_version = ignition_cfg["ignition"]["version"]
        version_tpl = ignition_version.split(".")

        if version_tpl[0] == "2":
            return ignition_cfg, SpecV2
        elif version_tpl[0] == "3":
            return ignition_cfg, SpecV3
        raise FileTranspilerError("Unkown ignition spec: {}".format(ignition_version))
    except (KeyError, IndexError) as err:
        raise FileTranspilerError("Unable to find version in spec: {}".format(err))
    except json.JSONDecodeError as err:
        raise FileTranspilerError("Unable to read JSON: {}".format(err))


def main():
    """Execute the main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--ignition", help="Path to ignition file to use as the base"
    )
    parser.add_argument(
        "-f", "--fake-root", help="Path to the fake root", required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Where to output the file. If empty, will print to stdout",
    )
    parser.add_argument(
        "-p",
        "--pretty",
        default=False,
        action="store_true",
        help="Make the output pretty",
    )
    parser.add_argument(
        "--dereference-symlinks",
        default=False,
        action="store_true",
        help=(
            "Write out file contents instead of making symlinks "
            "NOTE: Target files must exist in the fakeroot"
        ),
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "yaml"],
        help="What format of file to write out. `yaml` or `json` (default)",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s {}".format(__version__)
    )

    args = parser.parse_args()

    # Open the base ignition file and load it
    if args.ignition is not None:
        # Get the ignition config
        try:
            ignition_cfg, spec_cls = loader(args.ignition)
            ignition_spec = spec_cls(ignition_cfg, args)

        except FileTranspilerError as err:
            parser.error(err)
    else:
        # Default to empty spec 2.3.0
        ignition_cfg = {"ignition": {"version": "2.3.0"}}
        ignition_spec = SpecV2(ignition_cfg, args)

    # Merge the and output the results
    merged_ignition = ignition_spec.merge()

    if args.format == "json":
        if args.pretty:
            ignition_out = json.dumps(
                merged_ignition, sort_keys=True, indent=4, separators=(",", ": ")
            )
        else:
            ignition_out = json.dumps(merged_ignition)
    else:
        ignition_out = yaml.safe_dump(merged_ignition)
    if args.output:
        with open(args.output, "w") as out_f:
            out_f.write(ignition_out)
    else:
        print(ignition_out)


if __name__ == "__main__":
    main()
