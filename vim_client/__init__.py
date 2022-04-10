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
from pathlib import Path
from copy import deepcopy
from shutil import which
from subprocess import check_output  # nosec B404
from typing import List, Union


class VimClientError(Exception):
    """Exception raised by VimClient()."""


class VimEscape:
    """Escape functions."""

    @staticmethod
    def escape_all(string: str):
        """Escape all characters."""
        return re.sub(r'(.)', r'\\\1', string)

    @staticmethod
    def escape(string: str, chars: str):
        """Escape the characters in 'chars' that occur in 'string'."""
        result = ""
        for char in string:
            if char in chars:
                result += "\\"

            result += char

        return result

    @staticmethod
    def cmd_escape_all(cmd: str, arg: str = ""):
        """Escape the argument of a Vim command.

        >>> cmd_escape("lcd", "/etc")

        """
        result = cmd
        if arg:
            result += " " + VimEscape.escape_all(arg)
        return result


class VimClient:
    """Communicate with Vim via 'vim --remote*' command-line options."""

    def __init__(self, regex_server_name: str, replace_process=False):
        self.vim_bin = self._find_vim_bin()
        self.vim_server_name = self._find_server_name(regex_server_name)
        self.replace_process = replace_process

    # pylint: disable=no-self-use
    def _find_vim_bin(self) -> str:
        for bin_name in ["vim", "gvim"]:
            bin_path = which(bin_name)
            if bin_path:
                return bin_path
        return bin_name

    def _find_server_name(self, regex: str) -> str:
        for server_name in self._serverlist():
            if re.search(regex, server_name, re.I):
                vim_server_name = server_name
                return vim_server_name

        raise VimClientError("The Vim server is not listening")

    def _serverlist(self) -> List[str]:
        cmd_output = check_output([self.vim_bin, "--serverlist"])
        result = []
        for line in cmd_output.decode().splitlines():
            line = line.strip()
            if line:
                result.append(line)

        return result

    def edit(self,
             files: Union[List[str], str, List[Path], Path],
             tab=True,
             silent=True,
             wait=False,
             cwd: Union[Path, str, None] = None,
             extra_commands: Union[List[str], None] = None):
        """Make the Vim server edit a list of files.

        Parameters:

        :silent: do not complain if there is no server.
        :wait: wait for files to be edited.
        :tab: edit the file in a new tab.
        :cwd: current working directory (default: current directory).
        :extra_commands: list of extra Vim commands.

        """
        if not files:
            return

        option = "--remote"
        if tab:
            option += "-tab"

        if wait:
            option += "-wait"

        if silent:
            option += "-silent"

        if isinstance(files, (Path, str)):
            files = [Path(files)]
        else:
            files = [Path(item).absolute() for item in files]

        if cwd is None:
            cwd = os.getcwd()
        else:
            cwd = Path(cwd).absolute()

        if extra_commands is None:
            extra_commands = []

        for filename in files:
            commands = [
                "tabnew",
                VimEscape.cmd_escape_all("silent edit", str(filename)),
            ]

            if cwd:
                commands += [
                    VimEscape.cmd_escape_all("silent lcd", str(cwd))
                ]

            commands += ["call foreground()"]
            commands += extra_commands
            self.send_commands(commands)

    def expr(self, keys: str) -> List[str]:
        """Send 'keys' to the Vim server."""
        result = self._vim_remote(["--remote-expr"] + [keys])
        if result:
            return result

        err_str = (f"The Vim server '{self.vim_server_name}' has not "
                   f"responded to the expression: {keys}")
        raise VimClientError(err_str)

    def ping(self):
        """Check if Vim is listening to commands."""
        if self.expr("1024")[0].strip() != "1024":
            raise VimClientError(f"The Vim server '{self.vim_server_name}' "
                                 "is not responding")

    def send_commands(self, commands: Union[str, List[str]]):
        """Send commands the Vim server.

        >> self.send_commands('tabnew', 'lcd /etc', 'edit fstab')

        """
        if not commands:
            return

        if isinstance(commands, str):
            commands = [commands]

        remote_send_args = ""
        remote_send_args += "<C-w>"
        send = False
        for command in commands:
            remote_send_args += f":{command}<CR>"
            send = True

        if send:
            self._vim_remote(["--remote-send"] + [remote_send_args])

    def _vim_remote(self, args: List[str]) -> List[str]:
        """Execute 'vim --servername <server-name> <args>'."""
        vim_args: List[str] = []
        vim_args += ["--servername", self.vim_server_name]
        vim_args += deepcopy(args)

        if self.replace_process:
            os.execl(self.vim_bin, *([self.vim_bin] + vim_args))
            sys.exit(1)
        else:
            return check_output([self.vim_bin] + vim_args) \
                .decode().splitlines()
