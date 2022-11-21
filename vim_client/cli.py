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
"""The command-line interfaces: 'vim-client-edit' and 'vim-client-diff'."""

import os
import sys
import argparse

from . import VimEscape, VimClient, VimClientError


def get_vim_args():
    """Return Vim command-line arguments.

    Ignore the options (like '-d' or '--diff') for backward compatibility.

    """
    vim_args = []
    double_dash_found = False
    for arg in sys.argv[1:]:
        if arg == "--" and not double_dash_found:
            double_dash_found = True
            continue

        if arg.startswith('-'):
            continue

        if arg != "--" or double_dash_found:
            vim_args.append(arg)

    return vim_args


def cli_edit():
    """The command-line tool 'vim-client-edit'.

    Connect to a Vim server and edit a file.

    """
    cmdname = os.path.basename(sys.argv[0])

    usage = "%(prog)s [files_or_dirs]"
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     usage=usage)
    parser.add_argument("paths", metavar="files_or_dirs", type=str, nargs="*",
                        help="Paths to the files/directories")
    args = parser.parse_args()

    # Pre-commands
    pre_commands = []

    # Post-commands
    post_commands = []
    post_commands += ["call foreground()"]
    post_commands += ["echon ''"]  # Clear the command-line

    # Paths
    list_paths = [os.path.abspath(filename) for filename in args.paths]
    if not list_paths:
        list_paths = ["."]

    # Edit the file/directory
    try:
        vim_client = VimClient(".*")
        vim_client.edit(list_paths,
                        cwd=os.getcwd(),
                        pre_commands=pre_commands,
                        post_commands=post_commands)
    except VimClientError as err:
        print(f"{cmdname}: fatal: {err}.", file=sys.stderr)
        sys.exit(1)


def cli_diff():
    """The command-line tool 'vim-client-diff'.

    Connect to a Vim server and show the difference between two files.

    """
    cmdname = os.path.basename(sys.argv[0])
    vim_args = get_vim_args()

    if len(vim_args) < 2:
        print(f"Usage: {cmdname} <file1> <file2>", file=sys.stderr)
        sys.exit(1)

    if len(vim_args) > 8:
        print(f"{cmdname}: cannot diff remote than 8 files",
              file=sys.stderr)
        sys.exit(1)

    for filename in vim_args:
        if not os.path.isfile(filename):
            print(f"{cmdname}: {filename}: no such file or directory",
                  file=sys.stderr)
            sys.exit(1)

    try:
        vim_client = VimClient(".*")
        post_commands = []
        file1 = os.path.abspath(vim_args[0])
        for filename in vim_args[1:]:
            filename = os.path.abspath(filename)
            post_commands.append(
                VimEscape.cmd_escape_all("silent diffsplit", filename)
            )

        post_commands += ["call foreground()"]
        post_commands += ["echon ''"]  # Clear the command-line
        vim_client.edit(file1, cwd=os.getcwd(), post_commands=post_commands)
    except VimClientError as err:
        print(f"{cmdname}: fatal: {err}.", file=sys.stderr)
        sys.exit(1)
