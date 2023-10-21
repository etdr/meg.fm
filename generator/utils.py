
from os import get_terminal_size
from functools import wraps
from emoji import emoji_count
from halo import Halo


# get terminal width
def gtw():
    return get_terminal_size().columns

banner_chars = {
    0: '═',
    1: '─',
    2: '┄'
}

def banner(msg, level=1, msgstart=16):
    fillchar = banner_chars[level]
    tw = gtw() - emoji_count(msg)
    banner_start = f"{fillchar * msgstart} {msg.upper()} "
    print(banner_start.ljust(tw, fillchar))

def printline(level=1):
    print(banner_chars[level] * gtw())

def halo(msg):
    def dec(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)