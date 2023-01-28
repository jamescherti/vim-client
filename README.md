# vim-client - send commands to the Vim editor

The **command-line tools `vim-client-edit`, `vim-client-diff`** and the **Python module `vim_client`** will allow you to connect to a Vim server and make it:
- Edit files or directories in new tabs,
- Compare files (similar to vimdiff),
- Evaluate expressions and return their result,
- Send commands to Vim.

It will allow you, for example, to make Vim edit or diff files from outside of Vim (e.g. from a shell like Bash, Zsh, etc.).

## License

Copyright (c) [James Cherti](https://www.jamescherti.com).

Distributed under terms of the MIT license.

## Requirements

- Python >= 3.0
- The Vim editor ('vim' or 'gvim' in $PATH. Vim must be compiled with |+clientserver|, which is the case of most Vim distributions, because the Python module **vim_client** uses command-line arguments `vim --remote-*`)

## Installation

```console
sudo pip install vim-client
```

## The 'vim-client-\*' command-line tools

Edit a file in the current window/tab:
```console
vim-client-edit file1
```

Edit multiple files/directories in separate tabs:
```console
vim-client-edit --tab file1 file2 file3
```

Edit multiple files/directories in stacked horizontal splits:
```console
vim-client-edit --split file1 file2
```

Edit multiple files/directories in side-by-side vertical splits (To open vertical splits on the right of the current window, use the Vim option `set splitright`):
```console
vim-client-edit --vsplit file1 file2
```

Edit and compare up to eight files in a new tab:
```console
vim-client-diff --tab file1 file2
```

## Recommendations

### Add aliases to ~/.bashrc

It is recommended to add the following aliases to your `~/.bashrc`:
```sh
alias gvim='vim-client-edit --tab'
alias vim='vim-client-edit --tab'
alias vi='vim-client-edit --tab'
alias vimdiff='vim-client-diff --tab'
```

### Start diff mode with vertical splits (vim-client-diff)

Add the following line to your `~/.vimrc`:
```viml
set diffopt+=vertical
```

### Create desktop launchers
File: `/usr/local/share/applications/vim-client-edit.desktop`
```
[Desktop Entry]
Name=vim-client-edit
GenericName=Vim Client Edit
Comment=Vim Client Edit
Exec=vim-client-edit --tab %F
Terminal=false
Type=Application
Keywords=Text;editor;
Icon=gvim
Categories=Utility;TextEditor;
StartupNotify=false
MimeType=text/english;text/plain;text/x-makefile;text/x-c++hdr;text/x-c++src;text/x-chdr;text/x-csrc;text/x-java;text/x-moc;text/x-pascal;text/x-tcl;text/x-tex;application/x-shellscript;text/x-c;text/x-c++;
```

File: `/usr/local/share/applications/vim-client-diff.desktop`
```
[Desktop Entry]
Name=vim-client-diff
GenericName=Vim Client Diff
Comment=Vim Client Diff
Exec=vim-client-diff --tab %F
Terminal=false
Type=Application
Keywords=Text;editor;
Icon=gvim
Categories=Utility;TextEditor;
StartupNotify=false
MimeType=text/english;text/plain;text/x-makefile;text/x-c++hdr;text/x-c++src;text/x-chdr;text/x-csrc;text/x-java;text/x-moc;text/x-pascal;text/x-tcl;text/x-tex;application/x-shellscript;text/x-c;text/x-c++;
```

## Links

- [vim-client @PyPI](https://pypi.org/project/vim-client/)
- [vim-client @GitHub](https://github.com/jamescherti/vim-client)
- [Vim documentation about +clientserver and 'vim \-\-remote'](http://vimdoc.sourceforge.net/htmldoc/remote.html) (`:help remote.txt`)
