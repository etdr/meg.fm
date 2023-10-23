from os import chdir, listdir
from dotenv import dotenv_values
from ruamel.yaml import YAML

CONTENT_DIR = dotenv_values()['CONTENT_DIR']

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

chdir(f"{CONTENT_DIR}/info")
filenames = [f for f in listdir() if f.endswith('.yaml')]

for fn in filenames:
	with open(fn, 'rt') as f:
		y = yaml.load(f)
		
	# modify this line
	
	with open(fn, 'wt') as f:
		yaml.dump(y, f)
