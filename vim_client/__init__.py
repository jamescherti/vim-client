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
"""Communicate with Vim server."""

import os
import re
import sys
from copy import deepcopy
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError, check_output  # nosec B404
from typing import List, Union


DEFAULT_VIM = ["vim", "gvim"]


class VimClientError(Exception):
    """Exception raised by VimClient()."""


class VimClient:
    """Communicate with Vim via 'vim --remote*' command-line options."""

    def __init__(self, server_name_regex: str, list_vim_bin: List[str]):
        """Init VimClient.

        :server_name_regex: Regex that is used to find the Vim server.
        :list_vim_bin: List of paths to the Vim binary.

        """
        self.vim_bin = ""
        self._find_vim_bin(list_vim_bin)

        self.vim_server_name = ""
        self._find_vim_server_name(server_name_regex)

    def _fnameescape(self, string: str):
        string = string.replace("'", "''")
        return self.expr(f"fnameescape('{string}')")[0]

    def cmd_escape(self, cmd: str, arg: str):
        arg = self._fnameescape(arg)
        return f"{cmd} {arg}"

    def _find_vim_bin(self, list_vim_bin: List[str]):
        list_vim_commands = list_vim_bin if list_vim_bin else DEFAULT_VIM

        for bin_name in list_vim_commands:
            bin_path = which(bin_name)
            if bin_path:
                self.vim_bin = bin_path
                return

        raise VimClientError(
            f"The Vim command was not found: {list_vim_commands}"
        )

    def _find_vim_server_name(self, regex: str):
        vim_server_list = self._vim_server_list()
        for server_name in vim_server_list:
            if re.search(regex, server_name, re.I):
                self.vim_server_name = server_name
                return

        if vim_server_list:
            raise VimClientError(
                f"The regular expression '{regex}' does not match any of the "
                f"running Vim servers: {vim_server_list}"
            )
        else:
            raise VimClientError(
                f"The Vim server is not listening (the following command "
                f"returned an empty list: '{self.vim_bin} --serverlist')"
            )

    def _vim_server_list(self) -> List[str]:
        result: List[str] = []
        try:
            cmd_output = check_output([self.vim_bin, "--serverlist"])
        except CalledProcessError:
            return result

        for line in cmd_output.decode().splitlines():
            line = line.strip()
            if line:
                result.append(line)

        return result

    def edit(self,
             files: Union[List[str], str, List[Path], Path],
             cwd: Union[Path, str, None] = None,
             open_in: str = "current_window",
             pre_commands: Union[List[str], None] = None,
             post_commands: Union[List[str], None] = None):
        """Make Vim server edit files/directories.

        Parameters:

        :files: List of files/directories.

        :cwd: Current working directory (default: current directory).

        :pre_commands: A list of Vim commands that will be executed before the
        files/directories are opened.

        :post_commands: A list of Vim commands that will be executed after the
        files/directories are opened.

        :open_in: Possible values: "tab", "split", "vsplit", "current_window"
                                   (Default: "current_window").

        """
        if not files:
            return

        if isinstance(files, (Path, str)):
            files = [Path(files)]
        else:
            files = [Path(item).absolute() for item in files]

        if cwd:
            cwd = Path(cwd).absolute()

        if pre_commands is None:
            pre_commands = []

        if post_commands is None:
            post_commands = []

        open_in_commands = []
        if open_in == "split":
            open_in_commands = ["split"]
        elif open_in == "vsplit":
            open_in_commands = ["vsplit"]
        elif open_in == "tab":
            open_in_commands = ["tabnew"]
        elif open_in == "current_window":
            open_in_commands = []
        else:
            raise ValueError(f"'open_in': {open_in} is an invalid value. "
                             "The valid values are: "
                             "'tab', 'split', 'vsplit', 'current_window'.")

        commands = []
        for filename in files:
            commands += open_in_commands
            if cwd:
                commands += [self.cmd_escape("lcd", str(cwd))]

            commands += pre_commands

            commands += [self.cmd_escape("edit", str(filename))]

            commands += post_commands

        self.send_commands(commands)

    def ping(self):
        """Check if Vim is listening to commands."""
        if self.expr("1024")[0].strip() != "1024":
            raise VimClientError(f"The Vim server '{self.vim_server_name}' "
                                 "is not responding")

    def expr(self, expression: str) -> List[str]:
        """Send 'expression' to the Vim server and return its result."""
        result: List[str] = []
        try:
            result = self.run_vim_remote_get_output(
                ["--remote-expr"] + [expression],
            )
        except CalledProcessError:
            pass

        if not result:
            err_str = (f"The Vim server '{self.vim_server_name}' has not "
                       f"responded to the expression: {expression}")
            raise VimClientError(err_str)

        return result

    def send_commands(self, commands: Union[str, List[str]]):
        """Send commands to the Vim server.

        :commands: List of Vim commands.

        """
        if not commands:
            return

        if isinstance(commands, str):
            commands = [commands]

        vim_commands = ""
        send = False
        for command in commands:
            if send:
                vim_commands += " | "

            vim_commands += command
            send = True

        if send:
            self.expr(
                f"""execute('{vim_commands.replace("'", "''")}')"""
            )

    def exec_vim(self, args: List[str]):
        """Execute Vim, replacing the current process."""
        os.execl(self.vim_bin, *([self.vim_bin] + args))
        sys.exit(1)

    def run_vim_remote_get_output(self, args: List[str]) -> List[str]:
        """Execute 'vim --servername <server-name> <args>'."""
        vim_args = self._build_vim_remote_cmd_args(args=args)
        return check_output([self.vim_bin] + vim_args) \
            .decode().splitlines()

    def _build_vim_remote_cmd_args(self, args: List[str]) -> List[str]:
        vim_args: List[str] = []
        vim_args += ["--servername", self.vim_server_name]
        vim_args += deepcopy(args)
        return vim_args
