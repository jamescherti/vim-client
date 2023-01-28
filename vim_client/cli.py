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

import argparse
import os
import re
import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from typing import Tuple

from . import DEFAULT_VIM, VimClient, VimClientError


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
        help=("This option allows specifying the Vim server to connect to. "
              "If no value is provided, an attempt will be made to connect "
              "to any available Vim servers. "
              "If no Vim server is currently listening, a new instance of Vim "
              "will be launched with the '--servername SERVERNAME' option, "
              "which will start a new Vim server."),
    )

    arg_parser.add_argument(
        "--vim-bin",
        default=None,
        action="append",
        help=(
            "Path to the Vim binary (Default: ['vim', 'gvim']). "
            "This Vim binary will be utilized for connecting to a Vim server "
            "instance, as well as for launching a new instance of Vim if no "
            "Vim server is currently listening."
        ),
    )

    arg_parser.add_argument(
        "--serverlist",
        default=False,
        action="store_true",
        help="List the names of all Vim servers that can be found.",
    )

    arg_parser.add_argument(
        "-d",
        "--diff",
        default=False,
        action="store_true",
        help=("Start in diff mode. Works like 'vim-client-diff'."
              if vim_type == "vim" else argparse.SUPPRESS),
    )

    arg_parser.add_argument(
        "-o",
        "--split",
        action="store_const",
        const="split",
        help="Edit files/directories in stacked horizontal splits.",
        dest="open_in",
    )

    arg_parser.add_argument(
        "-O",
        "--vsplit",
        action="store_const",
        const="vsplit",
        help="Edit files/directories in side-by-side vertical splits.",
        dest="open_in",
    )

    arg_parser.add_argument(
        "-p",
        "--tab",
        action="store_const",
        const="tab",
        help="Edit files/directories in separate tabs.",
        dest="open_in",
    )

    args = arg_parser.parse_args()

    if vim_type == "vim" and args.diff:
        cli_diff()
        sys.exit(0)

    vim_server_name = ("^" + re.escape(args.servername) + "$"
                       if args.servername else ".*")
    vim_client = None
    try:
        vim_client = VimClient(
            server_name_regex=vim_server_name,
            list_vim_bin=args.vim_bin,
        )
    except VimClientError as err:
        if not args.vim_bin:
            print(f"Warning: {err}", file=sys.stderr)

    if not vim_client:
        list_vim_cmd = []
        if args.vim_bin:
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
            vim_args = ([vim_bin_path] +
                        ((["--servername"] + [args.servername])
                         if args.servername else []) + args.paths)
            print(f"[RUN] {subprocess.list2cmdline(vim_args)}",
                  file=sys.stderr)
            os.execl(vim_bin_path, *(vim_args))
        except OSError as err:
            print(f"Error: Could not execute '{vim_cmd}': {err}",
                  file=sys.stderr)
            sys.exit(1)

        sys.exit(1)

    if args.serverlist:
        vim_client.exec_vim(["--serverlist"])
        sys.exit(0)

    if vim_type == "vimdiff" and len(args.paths) < 2:
        arg_parser.print_usage()
        sys.exit(1)

    if not args.open_in:
        args.open_in = "current_window"

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
                        open_in=args.open_in,
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
                        open_in=args.open_in,
                        pre_commands=pre_commands,
                        post_commands=diff_commands)
    except VimClientError as err:
        print(f"{cmdname}: fatal: {err}.", file=sys.stderr)
        sys.exit(1)
