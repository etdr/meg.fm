from os import chdir, listdir
from dotenv import dotenv_values
from ruamel.yaml import YAML

CONTENT_DIR = dotenv_values()['CONTENT_DIR']

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

chdir(f"{CONTENT_DIR}/info")
filenames = [f for f in listdir() if f.endswith('.yaml')]

for fn in filenames:
	with open(fn, 'rt', encoding='utf-8') as f:
		md = yaml.load(f)
		
	# modify this line
	if 'artwork' in md:
		md.pop('artwork')
		md['sources'] = {
			'description': "gpt-4",
			'metadata': "gpt-4",
			'artwork': "openai",
			'music': "audiocraft"
		}
	if 'sysprompt_versions' in md:
		md.pop('sysprompt_versions')
	
	with open(fn, 'wt', encoding='utf-8') as f:
		yaml.dump(md, f)
