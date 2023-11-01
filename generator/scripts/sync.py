
import subprocess
import re

from sync_server_db import post_uuids




aws_process = subprocess.run(['./your_shell_script.sh'], capture_output=True, text=True)

uuid_patt = re.compile(r'info/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12})\.')

uuids = []

for line in aws_process.stdout.split('\n'):
	m = uuid_patt.search(line)
	if m:
		uuids.append(m.group(1))

post_uuids(uuids)