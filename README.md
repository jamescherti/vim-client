# vim-client - send commands to the Vim editor

The **command-line tools `vim-client-edit`, `vim-client-diff`** and the **Python module `vim_client`** will allow you to connect to a Vim server and make it:
- Edit files or directories in new tabs,
- Compare files (similar to vimdiff),
- Evaluate expressions and return their result,
- Send commands to Vim.

It will allow you, for example, to make Vim edit or diff files from outside of Vim (e.g. from a shell like Bash, Zsh, etc.).

## Requirements

- Python >= 3.0,
- The Vim editor ('vim' or 'gvim' in $PATH. Vim must be compiled with |+clientserver|, which is the case of most Vim distributions, because the Python module **vim_client** uses command-line arguments `vim --remote-*`)

## Installation

```console
sudo pip install vim-client
```

## The 'vim-client-\*' command-line tools

Edit a file in a new tab:
```console
vim-client-edit file1
```

Compare two files:
```console
vim-client-diff file1 file2
```

### Add aliases to ~/.bashrc

It is recommended to add the following aliases to your `~/.bashrc`:
```sh
alias gvim=vim-client-edit
alias vim=vim-client-edit
alias vi=vim-client-edit
alias vimdiff=vim-client-diff
```

### Add to ~/.vimrc

If you prefer to start diff mode with vertical splits:
```viml
set diffopt+=vertical
```

## License

Copyright (c) [James Cherti](https://www.jamescherti.com).

Distributed under terms of the MIT license.

## Links

- [vim-client @PyPI](https://pypi.org/project/vim-client/)
- [vim-client @GitHub](https://github.com/jamescherti/vim-client)
- [Vim documentation about +clientserver and 'vim \-\-remote'](http://vimdoc.sourceforge.net/htmldoc/remote.html) (`:help remote.txt`)
