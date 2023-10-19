
from os import get_terminal_size
from emoji import emoji_count


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

