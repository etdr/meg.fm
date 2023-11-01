
from os import listdir
from os.path import splitext

from sync_server_db import post_uuids

INFO_DIR = "/home/winfield/projects/meg.fm/content/info"


uuids = [splitext(f)[0] for f in listdir(INFO_DIR) if f.endswith('.yaml')]

post_uuids(uuids)



