# vim-client - send commands to the Vim editor

The **command-line tools `vim-client-edit`, `vim-client-diff`** and the **Python module `vim_client`** will allow you to connect to a Vim server and make it:
- Edit files or directories in new tabs,
- Compare files (similar to vimdiff),
- Evaluate expressions and return their result,
- Send commands to Vim.

It will allow you, for example, to make Vim edit or diff files from outside of Vim (e.g. from a shell like Bash, Zsh, etc.).

## Requirements

- Python >= 3.0
- The Vim editor ('vim' or 'gvim' in $PATH. Vim must be compiled with |+clientserver|, which is the case of most Vim distributions, because the Python module **vim_client** uses command-line arguments `vim --remote-*`)

## Installation

```console
sudo pip install vim-client
```

## The 'vim-client-\*' command-line tools

Open files/directories in new tabs:
```console
vim-client-edit file1 file2 file3
```

Compare up to eight files:
```console
vim-client-diff file1 file2
```

## Recommendations

### Add aliases to ~/.bashrc

It is recommended to add the following aliases to your `~/.bashrc`:
```sh
alias gvim=vim-client-edit
alias vim=vim-client-edit
alias vi=vim-client-edit
alias vimdiff=vim-client-diff
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
Exec=vim-client-edit %F
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
Exec=vim-client-diff %F
Terminal=false
Type=Application
Keywords=Text;editor;
Icon=gvim
Categories=Utility;TextEditor;
StartupNotify=false
MimeType=text/english;text/plain;text/x-makefile;text/x-c++hdr;text/x-c++src;text/x-chdr;text/x-csrc;text/x-java;text/x-moc;text/x-pascal;text/x-tcl;text/x-tex;application/x-shellscript;text/x-c;text/x-c++;
```

## License

Copyright (c) [James Cherti](https://www.jamescherti.com).

Distributed under terms of the MIT license.

## Links

- [vim-client @PyPI](https://pypi.org/project/vim-client/)
- [vim-client @GitHub](https://github.com/jamescherti/vim-client)
- [Vim documentation about +clientserver and 'vim \-\-remote'](http://vimdoc.sourceforge.net/htmldoc/remote.html) (`:help remote.txt`)
