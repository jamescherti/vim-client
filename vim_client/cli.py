#!/usr/bin/env python
#
# Copyright (c) James Cherti
#
# Distributed under terms of the MIT license.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
"""The command-line interfaces.

- vim-client-edit
- vim-client-diff

"""

import os
import re
import shutil
import sys
from argparse import ArgumentParser, Namespace
from typing import Tuple

from . import VimClient, VimClientError, DEFAULT_VIM


def cli_init(description: str,
             usage: str,
             vim_type: str) -> Tuple[VimClient, Namespace]:
    arg_parser = ArgumentParser(
        description=description,
        usage=usage,
    )

    arg_parser.add_argument(
        "paths",
        metavar="files_or_dirs",
        type=str,
        nargs="*",
        help="Paths to the files/directories.",
    )

    arg_parser.add_argument(
        "--servername",
        default="",
        help=("The name of the Vim server to connect to "
              "(By default, connect to one of the running Vim servers)."),
    )

    arg_parser.add_argument(
        "--vim-bin",
        default=None,
        action="append",
        help=(
            "Path to the Vim binary (Default: ['vim', 'gvim'])."
        ),
    )

    arg_parser.add_argument(
        "--fallback-vim-bin",
        default=None,
        action="append",
        help=(
            "Path to the Vim command that is executed when no Vim server is "
            "listening (Default: ['vim', 'gvim'])."
        ),
    )

    arg_parser.add_argument(
        "--serverlist",
        default=False,
        action="store_true",
        help="List the names of all Vim servers that can be found.",
    )

    args = arg_parser.parse_args()

    vim_server_name = ("^" + re.escape(args.servername) + "$"
                       if args.servername else ".*")
    vim_client = None
    try:
        vim_client = VimClient(
            server_name_regex=vim_server_name,
            list_vim_bin=args.vim_bin,
        )
    except VimClientError as err:
        if not args.fallback_vim_bin:
            print(f"Warning: {err}", file=sys.stderr)

    if not vim_client:
        list_vim_cmd = []
        if args.fallback_vim_bin:
            list_vim_cmd = args.fallback_vim_bin
        elif args.vim_bin:
            list_vim_cmd = args.vim_bin
        else:
            list_vim_cmd = DEFAULT_VIM

        vim_cmd = ""
        vim_bin_path = ""
        for vim_cmd in list_vim_cmd:
            if vim_type == "vimdiff":
                vim_cmd = f"{vim_cmd}diff"

            vim_bin_path = shutil.which(vim_cmd)  # type: ignore
            if vim_bin_path:
                break

        if not vim_bin_path:
            print(f"Error: Command not found: {vim_cmd}",
                  file=sys.stderr)
            sys.exit(1)

        try:
            os.execl(vim_bin_path, *([vim_bin_path] + args.paths))
        except OSError as err:
            print(f"Error: Could not execute '{vim_cmd}': {err}",
                  file=sys.stderr)
            sys.exit(1)

        sys.exit(1)

    if args.serverlist:
        vim_client.exec_vim(["--serverlist"])
        sys.exit(0)

    return (vim_client, args)


def cli_edit():
    """The command-line tool: 'vim-client-edit'.

    Connect to a Vim server and edit files/directories.

    """
    cmdname = os.path.basename(sys.argv[0])
    vim_client, args = cli_init(
        description=("Connect to a Vim server and make it edit "
                     "files/directories."),
        usage="%(prog)s [files_or_dirs]",
        vim_type="vim",
    )

    # Pre-commands
    pre_commands = []
    pre_commands += ["call foreground()"]

    # Post-commands
    post_commands = []

    # Paths
    list_paths = [os.path.abspath(filename) for filename in args.paths]
    if not list_paths:
        list_paths = ["."]

    # Edit the file/directory
    try:
        vim_client.edit(list_paths,
                        cwd=os.getcwd(),
                        pre_commands=pre_commands,
                        post_commands=post_commands)
    except VimClientError as err:
        print(f"{cmdname}: fatal: {err}.", file=sys.stderr)
        sys.exit(1)


def cli_diff():
    """The command-line tool: 'vim-client-diff'.

    Connect to a Vim server and show the differences between files.

    """
    cmdname = os.path.basename(sys.argv[0])
    vim_client, args = cli_init(
        description=("Connect to a Vim server and show the differences "
                     "between files."),
        usage="%(prog)s <file1> <file2> [file3]...",
        vim_type="vimdiff",
    )

    if len(args.paths) < 2:
        args.print_usage()
        sys.exit(1)

    if len(args.paths) > 8:
        print(f"{cmdname}: cannot diff more than 8 files",
              file=sys.stderr)
        sys.exit(1)

    for filename in args.paths:
        if not os.path.isfile(filename):
            print(f"{cmdname}: {filename}: no such file or directory",
                  file=sys.stderr)
            sys.exit(1)

    try:
        pre_commands = []
        diff_commands = []
        file1 = os.path.abspath(args.paths[0])
        for filename in args.paths[1:]:
            filename = os.path.abspath(filename)
            diff_commands.append(
                vim_client.cmd_escape("silent diffsplit", filename),
            )

        pre_commands += ["call foreground()"]
        vim_client.edit(file1,
                        cwd=os.getcwd(),
                        pre_commands=pre_commands,
                        post_commands=diff_commands)
    except VimClientError as err:
        print(f"{cmdname}: fatal: {err}.", file=sys.stderr)
        sys.exit(1)
