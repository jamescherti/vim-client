#!/usr/bin/env python
"""Install 'vim_client' module and the command-line tools."""

from pathlib import Path
from setuptools import find_packages, setup

CURRENT_DIRECTORY = Path(__file__).parent.resolve()
LONG_DESCRIPTION = (CURRENT_DIRECTORY / "README.md") \
    .read_text(encoding="utf-8")

setup(
    name="vim-client",
    version="1.0.5",
    description=("Connect to Vim server, edit files, evaluate Vim "
                 "expressions, and send commands to Vim."),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/jamescherti/vim-client",
    author="James Cherti",
    keywords="vim, server, remote, edit, client, clientserver",
    packages=find_packages(),
    python_requires=">=3.6, <4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",

        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Editors",

        "Operating System :: Unix",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],

    entry_points={
        "console_scripts": [
            "vim-client-edit=vim_client.cli:cli_edit",
            "vim-client-diff=vim_client.cli:cli_diff",
        ],
    },

    project_urls={
        "Bug Reports": "https://github.com/jamescherti/vim-client/issues",
        "Source": "https://github.com/jamescherti/vim-client",
    },
)
