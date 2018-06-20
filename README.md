# Unison-Indicator

## Install Unison in your PC


We choose version 2.48.3, which is stable and is the one that comes in Ubuntu.

Version 2.48.15v3 fixes a compilation problem!

We need to download the unison-fsmonitor or compile it!


## Get passwordless SSH access with key to your server

    ssh-keygen -t rsa -C "myemail@example.com"
    ssh-copy-id -i ~/.ssh/id_rsa user@host

If your server is a Raspberry Pi or another ARM-based computer...

### Install Unison and unison-fsmonitor in Raspberry pi

Unless you want a different version, you can just download my binaries to your raspberry pi:

    wget ... # To ~/bin, which should be in the path

Otherwise, you can compile it yourself with the following commands:

    # Install compiler
    sudo apt-get update
    sudo apt-get install ocaml build-essential

    # Get sources and compile them
    wget https://github.com/bcpierce00/unison/archive/v2.48.15v3.tar.gz
    tar xf v2.48.15v3.tar.gz
    cd unison-2.48.15v3
    make UISTYLE=text
    # It may fail with an error like "/bin/sh: 2: etags: not found",
    # but the binary is compiled successfully

    # Install
    mv src/unison ~/bin/
    mv src/unison-fsmonitor ~/bin/

## Configure your unison profile in your PC

    root = ...    # Source of data
    root = ...    # Where to sync
    ...           # Paths
    batch = true

### N backups of your files

* Backups -> explain where to find them

## Test that everything works

We can now run unison:

    unison victor
    ...

And we see what it did.

## Get the Unison-Indicator and add it to run at Startup

I developed a Dropbox-like indicator (200 lines of Python, find it in github).

[GIF with the indicator]

We can add it at startup and Unison will always run.

## Sync when hard drive plugins

Apart from the online sync/backup of my files, I find it very convenient to have
a hard drive dedicated to be an offline backup of my files.

I configured a Systemd service to run Unison-indicator agains this hard drive whenever
it is plugged in. This way it syncs and I see it in the indicator at the same time:

    [Init]
    ...
