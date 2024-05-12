#!/usr/bin/env python3

"""
https://stackoverflow.com/questions/7938402
Terminal in broken state (invisible text / no echo) after exit() during input() / raw_input()
"""

import os
import sys
import atexit
import subprocess

def some_function():
    # break terminal
    sys.stdout.buffer.write(os.urandom(1024))

def main():
    # register the exit handler only in the main function
    # when some_function is called from somewhere else
    # then the caller is responsible for cleanup
    atexit.register(exit_handler)
    some_function()

def exit_handler():
    # fix terminal after binary output
    # no. "stty sane" fails to reset the terminal cursor
    # stty is part of coreutils
    #subprocess.call(["stty", "sane"])
    # tput is part of ncurses
    subprocess.call(["tput", "init"])

if __name__ == "__main__":
    main()
