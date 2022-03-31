# vim-client

The command-line tools 'vim-client-*' and Python module 'vim_client' will allow you to connect to a Vim server and make it:
- Edit files or directories in new tabs,
- Compare files (similar to vimdiff),
- Evaluate expressions and return their result,
- Send commands to Vim.

You can, for example, make your shell edit or diff files from your shell (bash, zsh...).

## Requirements

- Python >= 3.0
- The Vim editor ('vim' or 'gvim' in $PATH)

## Installation

```console
sudo pip install git+https://github.com/jamescherti/vim-client
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

## License

Copyright (c) [James Cherti](https://www.jamescherti.com).

Distributed under terms of the MIT license.

## Links

- [The Git repository of "vim-client"](https://github.com/jamescherti/vim-client)
- [Vim documentation about +clientserver and "\-\-remote-*"](http://vimdoc.sourceforge.net/htmldoc/remote.html) (`:help remote.txt`)
