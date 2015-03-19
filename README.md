dropbox-generator
=================

Static site generator using Dropbox and Python.

Uses the [PyStatGen package](https://github.com/jg-you/PyStatGen).

One time generation (local):
    
    python3.4 __generate -c configuration.yml

Watcher (pushes to github page):

    cd /path/to/source/
    python3.4 /path/to/dropbox-generator/__generate -c configuration.yml
